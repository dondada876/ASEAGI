#!/bin/bash
# Setup DigitalOcean Spaces (S3-compatible storage)

set -e

echo "💾 DigitalOcean Spaces Setup"
echo "============================"

# Load environment
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

source .env

# Check required variables
if [ -z "$S3_ENDPOINT" ] || [ -z "$S3_ACCESS_KEY" ] || [ -z "$S3_SECRET_KEY" ] || [ -z "$S3_BUCKET" ]; then
    echo "❌ Missing S3 configuration in .env"
    echo "Required: S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET"
    exit 1
fi

# Install AWS CLI (s3cmd alternative)
if ! command -v aws &> /dev/null; then
    echo "📦 Installing AWS CLI..."
    pip3 install awscli
fi

# Configure AWS CLI for DigitalOcean Spaces
echo "🔧 Configuring AWS CLI for Spaces..."

mkdir -p ~/.aws

cat > ~/.aws/credentials <<EOF
[default]
aws_access_key_id = $S3_ACCESS_KEY
aws_secret_access_key = $S3_SECRET_KEY
EOF

cat > ~/.aws/config <<EOF
[default]
region = $S3_REGION
output = json
EOF

echo "✅ Credentials configured"

# Test connection and create bucket structure
echo "🔍 Testing connection to Spaces..."

# Create bucket (will fail if exists, that's ok)
aws s3 mb s3://$S3_BUCKET --endpoint-url=$S3_ENDPOINT 2>/dev/null || echo "Bucket already exists"

# Create folder structure
echo "📁 Creating folder structure..."

aws s3api put-object --bucket $S3_BUCKET --key raw/ --endpoint-url=$S3_ENDPOINT
aws s3api put-object --bucket $S3_BUCKET --key processed/ --endpoint-url=$S3_ENDPOINT
aws s3api put-object --bucket $S3_BUCKET --key archive/ --endpoint-url=$S3_ENDPOINT

echo "✅ Folder structure created:"
echo "  - raw/          (uploaded documents)"
echo "  - processed/    (OCR results)"
echo "  - archive/      (old documents)"

# Set CORS policy for Telegram webhooks
echo "🔒 Setting CORS policy..."

cat > /tmp/cors.json <<EOF
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF

aws s3api put-bucket-cors --bucket $S3_BUCKET --cors-configuration file:///tmp/cors.json --endpoint-url=$S3_ENDPOINT

rm /tmp/cors.json

echo "✅ CORS policy set"

# List contents
echo "📦 Current bucket contents:"
aws s3 ls s3://$S3_BUCKET/ --endpoint-url=$S3_ENDPOINT

echo ""
echo "✅ Spaces setup complete!"
echo ""
echo "📍 Bucket URL: $S3_ENDPOINT/$S3_BUCKET"
echo ""
echo "🔧 Useful commands:"
echo "  # List files"
echo "  aws s3 ls s3://$S3_BUCKET/ --endpoint-url=$S3_ENDPOINT --recursive"
echo ""
echo "  # Upload file"
echo "  aws s3 cp file.pdf s3://$S3_BUCKET/raw/ --endpoint-url=$S3_ENDPOINT"
echo ""
echo "  # Download file"
echo "  aws s3 cp s3://$S3_BUCKET/raw/file.pdf . --endpoint-url=$S3_ENDPOINT"
echo ""
echo "  # Sync folder"
echo "  aws s3 sync /local/folder s3://$S3_BUCKET/raw/ --endpoint-url=$S3_ENDPOINT"
