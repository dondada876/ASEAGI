"""
ASEAGI Control Plane - Flask API
Manages Vast.ai instances, job queue, and Telegram webhooks
"""

import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, request, jsonify
from supabase import create_client, Client
import redis
import boto3
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
VASTAI_API_KEY = os.getenv("VASTAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION", "nyc3")
DOCKER_IMAGE = os.getenv("DOCKER_IMAGE", "aseagi/document-processor")

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

# Telegram bot
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


class VastAIController:
    """Manages Vast.ai GPU instances"""

    @staticmethod
    def list_instances() -> List[Dict]:
        """List all running instances"""
        try:
            result = subprocess.run(
                ['vastai', 'show', 'instances', '--raw'],
                capture_output=True,
                text=True,
                check=True
            )
            instances = json.loads(result.stdout)
            return instances if instances else []
        except Exception as e:
            logger.error(f"Failed to list instances: {e}")
            return []

    @staticmethod
    def launch_instance(job_count: int = 1) -> Optional[Dict]:
        """Launch GPU instance for processing"""
        try:
            # Search for available GPUs (RTX 3080 or better)
            result = subprocess.run([
                'vastai', 'search', 'offers',
                '--type', 'on-demand',
                '--gpu_name', 'RTX_3080',
                '--reliability', '0.95',
                '--disk_space', '20',
                '--order', 'dph_total',  # Sort by price
                '--raw'
            ], capture_output=True, text=True, check=True)

            offers = json.loads(result.stdout)
            if not offers:
                logger.warning("No GPU offers available")
                return None

            # Take cheapest offer
            offer_id = offers[0]['id']

            # Launch instance
            launch_result = subprocess.run([
                'vastai', 'create', 'instance', str(offer_id),
                '--image', DOCKER_IMAGE,
                '--disk', '20',
                '--env', f'SUPABASE_URL={SUPABASE_URL}',
                '--env', f'SUPABASE_KEY={SUPABASE_KEY}',
                '--env', f'S3_ENDPOINT={S3_ENDPOINT}',
                '--env', f'S3_ACCESS_KEY={S3_ACCESS_KEY}',
                '--env', f'S3_SECRET_KEY={S3_SECRET_KEY}',
                '--env', f'S3_BUCKET={S3_BUCKET}',
                '--env', f'ANTHROPIC_API_KEY={os.getenv("ANTHROPIC_API_KEY")}',
                '--raw'
            ], capture_output=True, text=True, check=True)

            instance = json.loads(launch_result.stdout)
            logger.info(f"Launched Vast.ai instance: {instance.get('new_contract')}")

            # Log to Supabase
            supabase.table('vastai_instances').insert({
                'instance_id': instance.get('new_contract'),
                'launched_at': datetime.utcnow().isoformat(),
                'job_count': job_count,
                'status': 'launching'
            }).execute()

            return instance
        except Exception as e:
            logger.error(f"Failed to launch instance: {e}")
            return None

    @staticmethod
    def destroy_instance(instance_id: int) -> bool:
        """Destroy GPU instance"""
        try:
            subprocess.run(
                ['vastai', 'destroy', 'instance', str(instance_id)],
                check=True
            )
            logger.info(f"Destroyed Vast.ai instance: {instance_id}")

            # Update Supabase
            supabase.table('vastai_instances').update({
                'destroyed_at': datetime.utcnow().isoformat(),
                'status': 'destroyed'
            }).eq('instance_id', instance_id).execute()

            return True
        except Exception as e:
            logger.error(f"Failed to destroy instance: {e}")
            return False


class JobQueue:
    """Manages document processing job queue"""

    @staticmethod
    def add_job(file_path: str, metadata: Dict) -> str:
        """Add job to queue"""
        job_id = f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"

        # Add to Redis queue
        redis_client.lpush('job_queue', json.dumps({
            'job_id': job_id,
            'file_path': file_path,
            'metadata': metadata,
            'created_at': datetime.utcnow().isoformat()
        }))

        # Log to Supabase
        supabase.table('processing_jobs').insert({
            'job_id': job_id,
            'file_path': file_path,
            'status': 'queued',
            'created_at': datetime.utcnow().isoformat(),
            'metadata': metadata
        }).execute()

        logger.info(f"Added job to queue: {job_id}")
        return job_id

    @staticmethod
    def get_queue_size() -> int:
        """Get current queue size"""
        return redis_client.llen('job_queue')

    @staticmethod
    def check_and_launch() -> None:
        """Check queue and launch instance if needed"""
        queue_size = JobQueue.get_queue_size()
        instances = VastAIController.list_instances()
        active_instances = [i for i in instances if i.get('actual_status') == 'running']

        # Launch if queue has jobs and no instances running
        if queue_size > 0 and len(active_instances) == 0:
            logger.info(f"Queue has {queue_size} jobs, launching instance...")
            VastAIController.launch_instance(job_count=queue_size)


# Flask Routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'queue_size': JobQueue.get_queue_size(),
        'instances': len(VastAIController.list_instances())
    })


@app.route('/jobs', methods=['POST'])
def create_job():
    """Create new processing job"""
    data = request.json

    file_path = data.get('file_path')
    metadata = data.get('metadata', {})

    if not file_path:
        return jsonify({'error': 'file_path required'}), 400

    job_id = JobQueue.add_job(file_path, metadata)
    JobQueue.check_and_launch()

    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'queue_position': JobQueue.get_queue_size()
    }), 201


@app.route('/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id: str):
    """Get job status"""
    result = supabase.table('processing_jobs').select('*').eq('job_id', job_id).execute()

    if not result.data:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify(result.data[0])


@app.route('/instances', methods=['GET'])
def list_instances():
    """List Vast.ai instances"""
    instances = VastAIController.list_instances()
    return jsonify({
        'instances': instances,
        'count': len(instances)
    })


@app.route('/instances/launch', methods=['POST'])
def launch_instance():
    """Manually launch instance"""
    data = request.json or {}
    job_count = data.get('job_count', 1)

    instance = VastAIController.launch_instance(job_count)

    if instance:
        return jsonify({'success': True, 'instance': instance}), 201
    else:
        return jsonify({'error': 'Failed to launch instance'}), 500


@app.route('/instances/<int:instance_id>', methods=['DELETE'])
def destroy_instance(instance_id: int):
    """Destroy instance"""
    success = VastAIController.destroy_instance(instance_id)

    if success:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Failed to destroy instance'}), 500


@app.route('/telegram/webhook', methods=['POST'])
async def telegram_webhook():
    """Handle Telegram webhook updates"""
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        await telegram_app.process_update(update)
        return jsonify({'ok': True}), 200
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get processing statistics"""
    # Total documents
    total_docs = supabase.table('legal_documents').select('id', count='exact').execute()

    # Jobs by status
    jobs = supabase.table('processing_jobs').select('status').execute()
    status_counts = {}
    for job in jobs.data:
        status = job['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    # Cost tracking
    cost_result = supabase.rpc('get_processing_costs').execute()

    return jsonify({
        'total_documents': total_docs.count,
        'job_status': status_counts,
        'queue_size': JobQueue.get_queue_size(),
        'active_instances': len([i for i in VastAIController.list_instances()
                                  if i.get('actual_status') == 'running']),
        'costs': cost_result.data if cost_result.data else {}
    })


# Telegram Bot Handlers

async def start_command(update, context):
    """Handle /start command"""
    await update.message.reply_text(
        "🤖 ASEAGI Document Processing Bot\n\n"
        "Send me a document and I'll process it!\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/status - Check processing status\n"
        "/stats - View statistics"
    )


async def status_command(update, context):
    """Handle /status command"""
    queue_size = JobQueue.get_queue_size()
    instances = VastAIController.list_instances()
    active = len([i for i in instances if i.get('actual_status') == 'running'])

    await update.message.reply_text(
        f"📊 System Status\n\n"
        f"Queue: {queue_size} jobs\n"
        f"Instances: {active} active\n"
        f"Total documents: {supabase.table('legal_documents').select('id', count='exact').execute().count}"
    )


async def handle_document(update, context):
    """Handle document uploads"""
    try:
        # Get document
        document = update.message.document
        photo = update.message.photo[-1] if update.message.photo else None

        file_obj = document or photo
        if not file_obj:
            await update.message.reply_text("❌ No document detected")
            return

        # Download file
        file = await context.bot.get_file(file_obj.file_id)
        file_name = document.file_name if document else f"photo_{file_obj.file_id}.jpg"

        # Upload to S3
        s3_key = f"raw/{datetime.utcnow().strftime('%Y/%m/%d')}/{file_name}"

        # Download and upload
        import io
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)

        s3_client.upload_fileobj(file_bytes, S3_BUCKET, s3_key)

        # Create job
        job_id = JobQueue.add_job(s3_key, {
            'telegram_user_id': update.message.from_user.id,
            'file_name': file_name,
            'file_size': file_obj.file_size,
            'uploaded_at': datetime.utcnow().isoformat()
        })

        # Check and launch instance
        JobQueue.check_and_launch()

        await update.message.reply_text(
            f"✅ Document uploaded!\n\n"
            f"Job ID: {job_id}\n"
            f"Queue position: {JobQueue.get_queue_size()}\n\n"
            f"Processing will start automatically."
        )

    except Exception as e:
        logger.error(f"Document handling error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


# Register Telegram handlers
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CommandHandler("status", status_command))
telegram_app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))


if __name__ == '__main__':
    # Run Flask
    app.run(host='0.0.0.0', port=5000, debug=False)
