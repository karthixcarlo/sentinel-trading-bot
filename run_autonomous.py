# -*- coding: utf-8 -*-
"""
Autonomous Runner - 24/7 Sentinel Hive Operation

Runs the multi-agent trading system continuously with:
- Market hours checking
- Auto-restart on errors
- Database logging
- Performance monitoring
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime
import uuid
import pytz

from sentinel_hive import run_workflow
from sentinel_state import create_initial_state
from dashboard_v3.market_hours import is_market_open, get_market_status
from database_manager import start_workflow, end_workflow, log_agent_thought


# Configuration
SLEEP_WHEN_CLOSED = 600  # 10 minutes
SLEEP_BETWEEN_RUNS = 300  # 5 minutes
MAX_ERRORS_PER_HOUR = 10
IST = pytz.timezone('Asia/Kolkata')


def get_portfolio_state():
    """
    Get current portfolio state from session storage or database
    
    In production, this would load from persistent storage
    For now, starts with fresh capital
    
    Returns:
        dict: Portfolio state
    """
    return {
        'cash': 100000,  # ₹1 lakh virtual capital
        'positions': [],
        'orders': []
    }


def run_autonomous():
    """
    Main autonomous loop - runs 24/7
    
    Handles:
    - Market hours checking
    - Error recovery
    - Logging
    - Auto-restart
    """
    
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║       SENTINEL HIVE - Autonomous Trading System          ║
║                                                          ║
║  Status: AUTONOMOUS MODE ACTIVATED                       ║
║  Market: NSE/BSE (Indian Stock Market)                   ║
║  Mode: Paper Trading                                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    error_count = 0
    error_reset_time = datetime.now()
    run_count = 0
    
    while True:
        try:
            now = datetime.now(IST)
            
            # Reset error counter every hour
            if (now - error_reset_time).total_seconds() > 3600:
                error_count = 0
                error_reset_time = now
            
            # Check if too many errors
            if error_count >= MAX_ERRORS_PER_HOUR:
                print(f"\n⚠️  ERROR LIMIT REACHED ({error_count} errors/hour)")
                print(f"⏸️  Pausing for 1 hour...")
                time.sleep(3600)
                error_count = 0
                continue
            
            # Check market hours
            market_open, status_message = is_market_open()
            status_details = get_market_status()
            
            if not market_open:
                print(f"\n⏸  Market Closed - {status_message}")
                print(f"📅 {status_details['day_type']}")
                print(f"⏰ Next open: {status_details.get('next_open', 'Tomorrow 9:15 AM')}")
                print(f"💤 Sleeping for {SLEEP_WHEN_CLOSED // 60} minutes...")
                
                time.sleep(SLEEP_WHEN_CLOSED)
                continue
            
            # Market is open - run workflow
            run_count += 1
            workflow_id = f"auto-{uuid.uuid4().hex[:8]}"
            
            print(f"\n{'='*60}")
            print(f"🚀 RUN #{run_count} | Workflow ID: {workflow_id}")
            print(f"⏰ {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
            print(f"📈 Market Status: {status_message}")
            print(f"{'='*60}\n")
            
            # Start workflow logging
            start_workflow(workflow_id)
            
            # Create initial state
            initial_state = create_initial_state()
            initial_state['portfolio_snapshot'] = get_portfolio_state()
            initial_state['workflow_id'] = workflow_id
            
            # Log start
            log_agent_thought(
                "System",
                f"Starting autonomous workflow #{run_count}",
                initial_state,
                0,
                workflow_id
            )
            
            try:
                # Run the workflow
                result = run_workflow(initial_state, max_iterations=15)
                
                # Extract results
                final_ticker = result.get('current_ticker', 'None')
                final_signal = result.get('analyst_signal', {}).get('signal', 'WAIT')
                trade_status = result.get('trade_status', 'PENDING')
                error_list = result.get('errors', [])
                
                # Determine workflow status
                if len(error_list) > 0:
                    workflow_status = "COMPLETED_WITH_ERRORS"
                    error_count += 1
                elif trade_status == "EXECUTED":
                    workflow_status = "COMPLETED_SUCCESS"
                else:
                    workflow_status = "COMPLETED"
                
                # Log completion
                end_workflow(
                    workflow_id,
                    workflow_status,
                    final_ticker,
                    final_signal,
                    trade_status == "EXECUTED",
                    len(error_list)
                )
                
                log_agent_thought(
                    "System",
                    f"Workflow completed: {final_signal} signal for {final_ticker} | Trade: {trade_status}",
                    result,
                    result.get('iteration_count', 0),
                    workflow_id
                )
                
                print(f"\n✅ WORKFLOW COMPLETED")
                print(f"   Final Ticker: {final_ticker}")
                print(f"   Signal: {final_signal}")
                print(f"   Trade Status: {trade_status}")
                print(f"   Errors: {len(error_list)}")
                
            except Exception as workflow_error:
                print(f"\n❌ WORKFLOW ERROR: {workflow_error}")
                
                end_workflow(
                    workflow_id,
                    "FAILED",
                    error_count=1
                )
                
                log_agent_thought(
                    "System",
                    f"Workflow failed: {str(workflow_error)}",
                    {},
                    0,
                    workflow_id
                )
                
                error_count += 1
            
            # Sleep between runs
            print(f"\n💤 Sleeping for {SLEEP_BETWEEN_RUNS // 60} minutes before next run...")
            time.sleep(SLEEP_BETWEEN_RUNS)
            
        except KeyboardInterrupt:
            print("\n\n🛑 SHUTDOWN REQUESTED BY USER")
            print("👋 Stopping autonomous system...")
            break
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {e}")
            print(f"🔄 Restarting in 60 seconds...")
            error_count += 1
            time.sleep(60)
    
    print(f"\n✅ Autonomous system stopped cleanly")
    print(f"📊 Total runs completed: {run_count}")


if __name__ == "__main__":
    run_autonomous()
