#!/bin/bash
# Quick start dashboard

echo "Starting Smart Grid Demand Response Dashboard..."
echo ""
echo "🌐 Dashboard will open at: http://localhost:8501"
echo ""
echo "📚 Features:"
echo "   • Real-time grid status visualization"
echo "   • Thermostat device monitoring"
echo "   • Demand response execution"
echo "   • Dataset analytics"
echo "   • Performance metrics"
echo ""
echo "Press Ctrl+C to stop"
echo ""

streamlit run dashboard.py --logger.level=info
