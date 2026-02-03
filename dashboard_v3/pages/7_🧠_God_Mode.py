# -*- coding: utf-8 -*-
"""
God Mode - Live Agent Monitoring Dashboard

Real-time visualization of autonomous agent conversations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Import database and theme
from database_manager import get_recent_thoughts, get_workflow_stats, get_recent_trades
from premium_theme import inject_premium_theme
from navigation import render_top_navigation

# Page config
st.set_page_config(
    page_title="God Mode - Sentinel",
    page_icon="🧠",
    layout="wide"
)

# Inject premium theme
inject_premium_theme()

# Render top navigation
render_top_navigation()

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
        background: rgba(0, 0, 0, 0.2);
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
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #fff;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #a1a1aa;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Emergency button */
    .stButton>button {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem;'>
        <span class='live-indicator'></span>GOD MODE
    </h1>
    <p style='color: #a1a1aa; font-size: 1.1rem;'>Autonomous Agent Monitoring Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Statistics Row
st.markdown("### 📊 System Statistics")

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
    st.markdown("### 🧠 Live Agent Thoughts")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("🔄 Auto-refresh (every 5 seconds)", value=False)
    
    # Live feed container
    feed_container = st.container()
    
    with feed_container:
        try:
            thoughts_df = get_recent_thoughts(limit=50)
            
            if len(thoughts_df) == 0:
                st.info("💤 No agent activity yet. Start the autonomous runner to see live thoughts!")
            else:
                # Display thoughts in reverse chronological order
                for _, row in thoughts_df.iterrows():
                    agent_name = row['agent_name']
                    message = row['message']
                    timestamp = row['timestamp']
                    
                    # Determine agent class for styling
                    agent_class = f"agent-{agent_name.lower()}"
                    
                    # Agent emoji map
                    emoji_map = {
                        'Scout': '🕵️',
                        'Analyst': '🧠',
                        'Risk': '🛡️',
                        'Trader': '⚡',
                        'Supervisor': '👔'
                    }
                    
                    emoji = emoji_map.get(agent_name, '🤖')
                    
                    st.markdown(f"""
                    <div class='agent-message {agent_class}'>
                        <div style='font-size: 0.75rem; color: #71717a; margin-bottom: 0.25rem;'>
                            {timestamp} • Iteration {row.get('iteration', 0)}
                        </div>
                        <div>
                            <strong>{emoji} {agent_name}:</strong> {message}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error loading agent thoughts: {e}")

with col_right:
    st.markdown("### ⚡ Recent Trades")
    
    try:
        trades_df = get_recent_trades(limit=10)
        
        if len(trades_df) == 0:
            st.info("📊 No trades executed yet")
        else:
            for _, trade in trades_df.iterrows():
                # Trade card
                side_color = "#10b981" if trade['side'] == 'BUY' else "#ef4444"
                
                st.markdown(f"""
                <div style='background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid {side_color};'>
                    <div style='font-size: 0.75rem; color: #71717a;'>{trade['timestamp']}</div>
                    <div style='font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0;'>
                        {trade['side']} {trade['ticker'].replace('.NS', '')}
                    </div>
                   <div style='font-size: 0.9rem; color: #a1a1aa;'>
                        {trade['quantity']} shares @ ₹{trade['price']:,.2f}
                    </div>
                    <div style='font-size: 0.85rem; color: #71717a; margin-top: 0.5rem;'>
                        Total: ₹{trade['total_value']:,.2f} | Fee: ₹{trade['brokerage']:.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error loading trades: {e}")

# Emergency Controls
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### ⚠️ Emergency Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=True):
        # Kill autonomous process
        try:
            os.system("taskkill /F /IM python.exe /FI \"WINDOWTITLE eq run_autonomous*\"")
            st.success("✅ Autonomous system stopped!")
        except Exception as e:
            st.error(f"Error stopping system: {e}")

with col2:
    if st.button("🔄 Clear Old Logs", use_container_width=True):
        try:
            from database_manager import clear_old_data
            clear_old_data(days=7)
            st.success("✅ Cleared logs older than 7 days")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing logs: {e}")

with col3:
    if st.button("📊 Export Data", use_container_width=True):
        try:
            thoughts_df = get_recent_thoughts(limit=1000)
            csv = thoughts_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
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

# Footer
st.markdown("""
<div style='text-align: center; padding: 2rem 0; color: #71717a; font-size: 0.875rem;'>
    🧠 Sentinel Hive God Mode • Monitoring Autonomous AI Agents
</div>
""", unsafe_allow_html=True)
