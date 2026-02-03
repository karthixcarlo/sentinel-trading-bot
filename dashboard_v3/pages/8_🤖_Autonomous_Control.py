# -*- coding: utf-8 -*-
"""
Autonomous Control Center - Start/Stop and Monitor the AI Trading Bot

Full-featured control panel for the autonomous multi-agent system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import subprocess
from datetime import datetime
import time

# Import database and theme
from database_manager import get_recent_thoughts, get_workflow_stats, get_recent_trades
from premium_theme import inject_premium_theme
from navigation import render_top_navigation
from dashboard_v3.market_hours import is_market_open, get_market_status

# Page config
st.set_page_config(
    page_title="Autonomous Control - Sentinel",
    page_icon="🤖",
    layout="wide"
)

# Inject premium theme
inject_premium_theme()

# Render top navigation
render_top_navigation()

# Custom CSS
st.markdown("""
<style>
    /* Control panel card */
    .control-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    
    /* Status indicator */
    .status-running {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    .status-stopped {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #ef4444;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        50% { opacity: 0.7; box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
    }
    
    /* Big action button */
    .big-button {
        font-size: 1.2rem !important;
        padding: 1.5rem 3rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* Market status card */
    .market-status {
        background: rgba(0, 0, 0, 0.3);
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #10b981;
        margin-bottom: 1rem;
    }
    
    /* Agent feed */
    .agent-message {
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 8px;
        border-left: 3px solid var(--accent-color);
        background: rgba(0, 0, 0, 0.2);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }
    
    .agent-scout { border-left-color: #3b82f6; }
    .agent-analyst { border-left-color: #10b981; }
    .agent-risk { border-left-color: #f59e0b; }
    .agent-trader { border-left-color: #ef4444; }
    .agent-supervisor { border-left-color: #8b5cf6; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem;'>
        🤖 AUTONOMOUS CONTROL CENTER
    </h1>
    <p style='color: #a1a1aa; font-size: 1.1rem;'>Start, Stop, and Monitor Your AI Trading Bot</p>
</div>
""", unsafe_allow_html=True)


def is_autonomous_running() -> bool:
    """
    Check if autonomous system is currently running
    
    Returns:
        bool: True if running
    """
    try:
        # Windows-specific: Check using tasklist
        if os.name == 'nt':
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True
            )
            
            # Check if run_autonomous.py is in the output
            return 'run_autonomous' in result.stdout.lower()
        else:
            # Unix-based: use ps
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            return 'run_autonomous.py' in result.stdout
            
    except Exception:
        return False


def start_autonomous():
    """
    Start the autonomous trading system
    """
    try:
        # Get project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Start in background
        subprocess.Popen(
            [sys.executable, 'run_autonomous.py'],
            cwd=project_root,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        return True
    except Exception as e:
        st.error(f"Failed to start: {e}")
        return False


def stop_autonomous():
    """
    Stop the autonomous trading system
    """
    try:
        if os.name == 'nt':
            # Windows: Kill python processes running run_autonomous.py
            subprocess.run(
                ['taskkill', '/F', '/FI', 'WINDOWTITLE eq *run_autonomous*'],
                capture_output=True
            )
            return True
        else:
            # Unix: pkill
            subprocess.run(['pkill', '-f', 'run_autonomous.py'])
            return True
            
    except Exception as e:
        st.error(f"Failed to stop: {e}")
        return False


# Check current status
is_running = is_autonomous_running()

# System Status Card
st.markdown("### 🎮 System Control")

col1, col2 = st.columns([2, 1])

with col1:
    # Status display
    if is_running:
        st.markdown("""
        <div class='control-card'>
            <h2 style='margin-bottom: 1rem;'>
                <span class='status-running'></span>
                SYSTEM ACTIVE
            </h2>
            <p style='color: #10b981; font-size: 1.1rem; margin-bottom: 0;'>
                ✅ Autonomous agent is running and scanning the market
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Stop button
        if st.button("🛑 STOP AUTONOMOUS SYSTEM", key="stop_btn", use_container_width=True, type="secondary"):
            with st.spinner("Stopping autonomous system..."):
                if stop_autonomous():
                    st.success("✅ System stopped successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("⚠️ No running process found")
    else:
        st.markdown("""
        <div class='control-card'>
            <h2 style='margin-bottom: 1rem;'>
                <span class='status-stopped'></span>
                SYSTEM STOPPED
            </h2>
            <p style='color: #ef4444; font-size: 1.1rem; margin-bottom: 0;'>
                ⚠️ Autonomous agent is not running
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Start button
        if st.button("🚀 START AUTONOMOUS SYSTEM", key="start_btn", use_container_width=True, type="primary"):
            with st.spinner("Starting autonomous system..."):
                if start_autonomous():
                    st.success("✅ System started successfully!")
                    st.info("💡 A new terminal window will open. You can minimize it.")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Failed to start system")

with col2:
    # Market status
    market_open, status_msg = is_market_open()
    market_details = get_market_status()
    
    status_color = "#10b981" if market_open else "#ef4444"
    
    st.markdown(f"""
    <div class='market-status' style='border-left-color: {status_color};'>
        <div style='font-size: 0.875rem; color: #a1a1aa; margin-bottom: 0.5rem;'>MARKET STATUS</div>
        <div style='font-size: 1.25rem; font-weight: 600; color: {status_color}; margin-bottom: 0.5rem;'>
            {status_msg}
        </div>
        <div style='font-size: 0.85rem; color: #71717a;'>
            {market_details['day_type']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Divider
st.markdown("<br>", unsafe_allow_html=True)

# Statistics Row
st.markdown("### 📊 Performance Metrics")

try:
    stats = get_workflow_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Runs", stats['total_runs'], delta=None)
    
    with col2:
        st.metric("Trades Executed", stats['successful_trades'], delta=None)
    
    with col3:
        success_rate = (stats['successful_trades'] / stats['total_runs'] * 100) if stats['total_runs'] > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%", delta=None)
    
    with col4:
        st.metric("Avg Errors", stats['avg_errors'], delta=None)
except Exception as e:
    st.error(f"Error loading stats: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# Live Feed Section
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 🧠 Live Agent Activity")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("🔄 Auto-refresh (every 5 seconds)", value=is_running, key="auto_refresh")
    
    # Live feed
    try:
        thoughts_df = get_recent_thoughts(limit=50)
        
        if len(thoughts_df) == 0:
            st.info("💤 No agent activity yet. Start the autonomous system to see live updates!")
        else:
            # Display thoughts
            for _, row in thoughts_df.iterrows():
                agent_name = row['agent_name']
                message = row['message']
                timestamp = row['timestamp']
                
                agent_class = f"agent-{agent_name.lower()}"
                
                emoji_map = {
                    'Scout': '🕵️',
                    'Analyst': '🧠',
                    'Risk': '🛡️',
                    'Trader': '⚡',
                    'Supervisor': '👔',
                    'System': '⚙️'
                }
                
                emoji = emoji_map.get(agent_name, '🤖')
                
                st.markdown(f"""
                <div class='agent-message {agent_class}'>
                    <div style='font-size: 0.75rem; color: #71717a; margin-bottom: 0.25rem;'>
                        {timestamp}
                    </div>
                    <div>
                        <strong>{emoji} {agent_name}:</strong> {message}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error loading activity: {e}")

with col_right:
    st.markdown("### ⚡ Recent Trades")
    
    try:
        trades_df = get_recent_trades(limit=10)
        
        if len(trades_df) == 0:
            st.info("📊 No trades yet")
        else:
            for _, trade in trades_df.iterrows():
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
                        Total: ₹{trade['total_value']:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error loading trades: {e}")

# Auto-refresh logic
if auto_refresh:
    time.sleep(5)
    st.rerun()

# Footer
st.markdown("""
<div style='text-align: center; padding: 2rem 0; color: #71717a; font-size: 0.875rem;'>
    🤖 Sentinel Autonomous Trading System • Powered by LangGraph & Gemini AI
</div>
""", unsafe_allow_html=True)
