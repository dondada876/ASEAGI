#!/bin/bash
# Quick push script for PROJ344 Dashboard

echo "╔═══════════════════════════════════════════════╗"
echo "║   PUSHING PROJ344 DASHBOARD TO GITHUB        ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "Repository: https://github.com/dondada876/ASEAGI.git"
echo "Files: 16 files, 5,446 lines of code"
echo ""
echo "⚠️  You'll be prompted for:"
echo "   Username: dondada876"
echo "   Password: Use Personal Access Token (NOT your password)"
echo ""
echo "   Get token: https://github.com/settings/tokens"
echo "   Scope needed: ✅ repo (Full control)"
echo ""
echo "─────────────────────────────────────────────────"
echo ""

# Navigate to repository
cd ~/proj344-dashboard

# Show current status
echo "📊 Repository Status:"
git log --oneline -1
echo ""
git status -sb
echo ""

# Push to GitHub
echo "🚀 Pushing to GitHub..."
echo ""
git push -u origin main

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════╗"
    echo "║   ✅ SUCCESS! CODE PUSHED TO GITHUB          ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
    echo "🌐 View your repository:"
    echo "   https://github.com/dondada876/ASEAGI"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Deploy to Streamlit Cloud: https://streamlit.io/cloud"
    echo "   2. Connect your GitHub repo"
    echo "   3. Main file: proj344_master_dashboard.py"
    echo "   4. Add secrets (SUPABASE_URL, SUPABASE_KEY)"
    echo "   5. Deploy!"
    echo ""
else
    echo ""
    echo "╔═══════════════════════════════════════════════╗"
    echo "║   ❌ PUSH FAILED                              ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
    echo "Troubleshooting:"
    echo "   • Check your username and token"
    echo "   • Get token: https://github.com/settings/tokens"
    echo "   • Make sure token has 'repo' scope"
    echo "   • Try: gh auth login (if you have GitHub CLI)"
    echo ""
fi
