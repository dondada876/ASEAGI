#!/bin/bash
# ============================================================================
# ASEAGI Queue Management Schema Deployment Script
# Deploys document_journal, processing_queue, and related tables to Supabase
# ============================================================================

set -e  # Exit on error

echo "============================================================================"
echo "ASEAGI QUEUE MANAGEMENT SCHEMA DEPLOYMENT"
echo "============================================================================"
echo ""

# ============================================================================
# STEP 1: Environment Check
# ============================================================================

echo "📋 Step 1: Checking environment..."

if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "Creating from template..."
    cat > .env << 'EOF'
# Supabase
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here
EOF
    echo "✅ Created .env file"
    echo "❌ Please edit .env with your actual keys before continuing"
    echo "   nano .env"
    exit 1
fi

source .env

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL not set in .env"
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ] || [ "$SUPABASE_SERVICE_ROLE_KEY" = "your-service-role-key-here" ]; then
    echo "❌ SUPABASE_SERVICE_ROLE_KEY not set in .env"
    echo "   You need the SERVICE ROLE key (not anon key) for schema changes"
    echo "   Get it from: Supabase Dashboard → Settings → API"
    exit 1
fi

echo "✅ Environment variables loaded"
echo "   Supabase URL: $SUPABASE_URL"
echo ""

# ============================================================================
# STEP 2: Check if schema file exists
# ============================================================================

echo "📋 Step 2: Checking schema file..."

SCHEMA_FILE="document_journal_queue_schema.sql"

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Schema file not found: $SCHEMA_FILE"
    exit 1
fi

echo "✅ Schema file found"
echo "   File: $SCHEMA_FILE"
echo "   Size: $(wc -l < $SCHEMA_FILE) lines"
echo ""

# ============================================================================
# STEP 3: Backup existing tables (if any)
# ============================================================================

echo "📋 Step 3: Backup check..."
echo "⚠️  This script will create new tables. If tables already exist, deployment may fail."
echo ""
read -p "Do you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""

# ============================================================================
# STEP 4: Deploy schema via Supabase API
# ============================================================================

echo "📋 Step 4: Deploying schema to Supabase..."
echo ""

# Read SQL file
SQL_CONTENT=$(cat "$SCHEMA_FILE")

# URL encode the SQL (basic - good enough for API call)
# Note: For production, use proper SQL migration tools

# Use Supabase REST API to execute SQL
# Note: This requires service_role key with full permissions

echo "⚙️  Method 1: Direct API deployment..."
echo "   (Note: For large schemas, use Supabase Dashboard SQL Editor instead)"
echo ""

# Option 1: Use psql if available
if command -v psql &> /dev/null; then
    echo "✅ psql found - using direct database connection"
    echo ""

    # Extract connection string from Supabase URL
    # Format: postgres://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres

    PROJECT_ID=$(echo $SUPABASE_URL | sed 's/https:\/\///' | sed 's/.supabase.co//')

    echo "To deploy via psql, run:"
    echo ""
    echo "  psql \"postgres://postgres:[YOUR-DB-PASSWORD]@db.$PROJECT_ID.supabase.co:5432/postgres\" -f $SCHEMA_FILE"
    echo ""
    echo "Get your database password from:"
    echo "  Supabase Dashboard → Settings → Database → Connection String"
    echo ""

else
    echo "⚠️  psql not found"
    echo ""
fi

# ============================================================================
# STEP 5: Manual deployment instructions
# ============================================================================

echo "============================================================================"
echo "📋 MANUAL DEPLOYMENT INSTRUCTIONS"
echo "============================================================================"
echo ""
echo "Since automated SQL deployment requires database credentials,"
echo "please deploy the schema manually using one of these methods:"
echo ""
echo "METHOD 1: Supabase Dashboard SQL Editor (RECOMMENDED)"
echo "========================================================="
echo "1. Go to: https://supabase.com/dashboard/project/$PROJECT_ID/sql"
echo "2. Click 'New Query'"
echo "3. Copy the contents of: $SCHEMA_FILE"
echo "4. Paste into the SQL editor"
echo "5. Click 'Run' (or press Cmd/Ctrl + Enter)"
echo "6. Verify tables were created successfully"
echo ""
echo "METHOD 2: psql Command Line"
echo "============================"
echo "1. Get your database password from Supabase Dashboard → Settings → Database"
echo "2. Run:"
echo "   psql \"postgres://postgres:[PASSWORD]@db.$PROJECT_ID.supabase.co:5432/postgres\" -f $SCHEMA_FILE"
echo ""
echo "METHOD 3: Supabase CLI (if installed)"
echo "======================================"
echo "1. Install Supabase CLI: https://supabase.com/docs/guides/cli"
echo "2. Link your project: supabase link --project-ref $PROJECT_ID"
echo "3. Run migration: supabase db push"
echo ""
echo "============================================================================"
echo ""

# ============================================================================
# STEP 6: Verify deployment
# ============================================================================

echo "📋 After deployment, verify with these queries:"
echo ""
echo "-- Check if tables exist"
echo "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('document_journal', 'processing_queue', 'processing_metrics_log', 'document_type_rules');"
echo ""
echo "-- Check if views exist"
echo "SELECT table_name FROM information_schema.views WHERE table_schema = 'public' AND table_name LIKE '%queue%';"
echo ""
echo "-- Test insert into journal"
echo "SELECT * FROM document_journal LIMIT 1;"
echo ""

# ============================================================================
# STEP 7: Next steps
# ============================================================================

echo "============================================================================"
echo "NEXT STEPS AFTER DEPLOYMENT"
echo "============================================================================"
echo ""
echo "1. Verify schema deployment:"
echo "   - Check that all 4 tables were created"
echo "   - Check that all views were created"
echo "   - Check that functions were created"
echo ""
echo "2. Populate document_type_rules:"
echo "   - The schema includes INSERT statements for default rules"
echo "   - Verify they were inserted"
echo ""
echo "3. Test the queue system:"
echo "   python3 queue_manager.py"
echo ""
echo "4. Start the FastAPI server with queue support:"
echo "   python3 mobile_scanner_api.py"
echo ""
echo "5. Access the queue dashboard:"
echo "   streamlit run dashboard_queue_monitor.py"
echo ""
echo "6. Test document upload:"
echo "   curl -X POST http://localhost:8000/api/upload \\"
echo "     -F 'file=@test_document.pdf' \\"
echo "     -F 'source=test'"
echo ""
echo "7. View queue stats:"
echo "   curl http://localhost:8000/api/queue/stats"
echo ""
echo "For Ashe. For Justice. For All Children. 🛡️"
echo ""
