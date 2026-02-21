# -*- coding: utf-8 -*-
"""
God Mode - Live Agent Monitoring Dashboard
Real-time visualization of autonomous agent conversations
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import sys
import os

# Add dashboard_v3/ and project root to path
PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
DASH_DIR  = os.path.dirname(PAGES_DIR)
ROOT_DIR  = os.path.dirname(DASH_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, DASH_DIR)


from layout import setup_page_config, render_navigation, apply_groww_theme
from database_manager import get_recent_thoughts, get_workflow_stats, get_recent_trades

# Page setup
setup_page_config("Monitor", "🧠")

# Apply theme
apply_groww_theme()

# Navigation
render_navigation()

# Custom CSS for God Mode
st.markdown("""
<style>
    /* Glass card styling */
    .god-mode-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Agent message styling */
    .agent-message {
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 8px;
        border-left: 3px solid var(--accent-color);
        background: rgba(0, 0, 0, 0.05);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }
    
    .agent-scout { border-left-color: #3b82f6; } /* Blue */
    .agent-analyst { border-left-color: #10b981; } /* Green */
    .agent-risk { border-left-color: #f59e0b; } /* Orange */
    .agent-trader { border-left-color: #ef4444; } /* Red */
    .agent-supervisor { border-left-color: #8b5cf6; } /* Purple */
    
    /* Live indicator */
    .live-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Stat cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #111827;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem; color: #111827;'>
        <span class='live-indicator'></span>SYSTEM MONITOR
    </h1>
    <p style='color: #6b7280; font-size: 1.1rem;'>Real-time Autonomous Agent Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Statistics Row
st.markdown("### System Statistics")

# Get stats
try:
    stats = get_workflow_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['total_runs']}</div>
            <div class='stat-label'>Total Workflows</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['successful_trades']}</div>
            <div class='stat-label'>Trades Executed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        success_rate = (stats['successful_trades'] / stats['total_runs'] * 100) if stats['total_runs'] > 0 else 0
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{success_rate:.1f}%</div>
            <div class='stat-label'>Success Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['avg_errors']}</div>
            <div class='stat-label'>Avg Errors</div>
        </div>
        """, unsafe_allow_html=True)
    
except Exception as e:
    st.error(f"Error loading stats: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# Main content area
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### Live Agent Thoughts")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh (every 5 seconds)", value=False)
    
    # Live feed container
    feed_container = st.container()
    
    with feed_container:
        try:
            thoughts_df = get_recent_thoughts(limit=50)
            
            if len(thoughts_df) == 0:
                st.info("No agent activity yet. Start the autonomous runner to see live thoughts!")
            else:
                # Display thoughts in reverse chronological order
                for _, row in thoughts_df.iterrows():
                    agent_name = row['agent_name']
                    message = row['message']
                    timestamp = row['timestamp']
                    
                    # Determine agent class for styling
                    agent_class = f"agent-{agent_name.lower()}"
                    
                    st.markdown(f"""
                    <div class='agent-message {agent_class}'>
                        <div style='font-size: 0.75rem; color: #6b7280; margin-bottom: 0.25rem;'>
                            {timestamp} • Iteration {row.get('iteration', 0)}
                        </div>
                        <div style='color: #374151;'>
                            <strong>{agent_name}:</strong> {message}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error loading agent thoughts: {e}")

with col_right:
    st.markdown("### Recent Trades")
    
    try:
        trades_df = get_recent_trades(limit=10)
        
        if len(trades_df) == 0:
            st.info("No trades executed yet")
        else:
            for _, trade in trades_df.iterrows():
                # Trade card
                side_color = "#10b981" if trade['side'] == 'BUY' else "#ef4444"
                
                st.markdown(f"""
                <div style='background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid {side_color}; border: 1px solid #e5e7eb;'>
                    <div style='font-size: 0.75rem; color: #6b7280;'>{trade['timestamp']}</div>
                    <div style='font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0; color: #111827;'>
                        {trade['side']} {trade['ticker'].replace('.NS', '')}
                    </div>
                   <div style='font-size: 0.9rem; color: #4b5563;'>
                        {trade['quantity']} shares @ ₹{trade['price']:,.2f}
                    </div>
                    <div style='font-size: 0.85rem; color: #6b7280; margin-top: 0.5rem;'>
                        Total: ₹{trade['total_value']:,.2f} | Fee: ₹{trade['brokerage']:.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error loading trades: {e}")

# Emergency Controls
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### Emergency Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=True):
        # Kill autonomous process
        try:
            os.system("taskkill /F /IM python.exe /FI \"WINDOWTITLE eq run_autonomous*\"")
            st.success("Autonomous system stopped!")
        except Exception as e:
            st.error(f"Error stopping system: {e}")

with col2:
    if st.button("Clear Old Logs", use_container_width=True):
        try:
            from database_manager import clear_old_data
            clear_old_data(days=7)
            st.success("Cleared logs older than 7 days")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing logs: {e}")

with col3:
    if st.button("Export Data", use_container_width=True):
        try:
            thoughts_df = get_recent_thoughts(limit=1000)
            csv = thoughts_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"agent_thoughts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error exporting: {e}")

# Auto-refresh logic
if auto_refresh:
    time.sleep(5)
    st.rerun()

st.markdown("---")
st.caption("Sentinel Hive Monitor • Monitoring Autonomous AI Agents")
