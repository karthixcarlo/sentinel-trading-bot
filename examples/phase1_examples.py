"""
Example usage of Project Sentinel Phase 1 modules

Demonstrates how to use SignalSynchronizer, SlippageSimulator, and ConservativeRiskModel
in a realistic trading scenario.
"""

from datetime import datetime, timedelta
from sentinel import (
    TimestampedSignal,
    SignalSynchronizer,
    MarketCondition,
    SlippageSimulator,
    ConservativeRiskModel
)


def example_signal_synchronization():
    """
    Example: Synchronizing price and news signals
    """
    print("=" * 60)
    print("EXAMPLE 1: Signal Synchronization")
    print("=" * 60)
    
    # Create synchronizer with 5-minute windows
    sync = SignalSynchronizer(window_size=timedelta(minutes=5))
    
    # Simulate receiving signals from different sources
    now = datetime.utcnow()
    
    # Price signal from yfinance (1-min delayed)
    price_signal = TimestampedSignal(
        signal_type="PRICE",
        value=150.25,
        event_time=now - timedelta(minutes=1),
        metadata={"source": "yfinance", "ticker": "AAPL"}
    )
    
    # News sentiment signal (real-time)
    news_signal = TimestampedSignal(
        signal_type="NEWS",
        value=78.5,  # Bullish sentiment score
        event_time=now,
        metadata={"source": "web_scraping", "headline": "Apple announces new product"}
    )
    
    # Technical indicator signal
    technical_signal = TimestampedSignal(
        signal_type="TECHNICAL",
        value=65.0,  # RSI
        event_time=now - timedelta(seconds=30),
        metadata={"indicator": "RSI", "period": 14}
    )
    
    # Add signals to synchronizer
    sync.add_signal(price_signal)
    sync.add_signal(news_signal)
    sync.add_signal(technical_signal)
    
    # Get synchronized window
    window = sync.get_synchronized_window(
        required_types=["PRICE", "NEWS", "TECHNICAL"]
    )
    
    print(f"\nWindow Status: {window['status']}")
    
    if window["status"] == "READY":
        print(f"Signal Count: {window['signal_count']}")
        print(f"Window: {window['window']}")
        print("\nSignals in window:")
        for signal in window["signals"]:
            print(f"  - {signal}")
        
        # Extract values for decision making
        price = next(s.value for s in window["signals"] if s.signal_type == "PRICE")
        news_score = next(s.value for s in window["signals"] if s.signal_type == "NEWS")
        rsi = next(s.value for s in window["signals"] if s.signal_type == "TECHNICAL")
        
        print(f"\nDecision Inputs:")
        print(f"  Price: ${price:.2f}")
        print(f"  News Sentiment: {news_score:.1f}/100 (Bullish)")
        print(f"  RSI: {rsi:.1f} (Not Overbought)")
        print(f"\n  → Consensus: BUY signal")
    
    # Show metrics
    metrics = sync.get_metrics()
    print(f"\nSynchronizer Metrics:")
    print(f"  Signals Received: {metrics['signals_received']}")
    print(f"  Windows Completed: {metrics['windows_completed']}")
    print(f"  Drop Rate: {metrics['drop_rate']:.2%}")


def example_slippage_simulation():
    """
    Example: Simulating realistic order fills
    """
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Slippage Simulation")
    print("=" * 60)
    
    # Create simulator for normal market conditions
    simulator = SlippageSimulator(
        condition=MarketCondition.NORMAL,
        spread_bps=5.0
    )
    
    # Simulate a market buy order
    print("\n--- Market Buy Order ---")
    market_fill = simulator.simulate_fill(
        order_type="MARKET",
        side="BUY",
        intended_price=150.0,
        size=100,
        symbol="AAPL"
    )
    
    print(f"Intended: {market_fill.intended_qty} shares @ ${market_fill.intended_price:.2f}")
    print(f"Actual Fill: {market_fill.filled_qty} shares @ ${market_fill.actual_fill_price:.4f}")
    print(f"Slippage: {market_fill.slippage_pct:.3f}% (${market_fill.slippage_cost:.2f})")
    print(f"Fill Ratio: {market_fill.fill_ratio:.2%}")
    
    # Simulate a limit buy order (better execution)
    print("\n--- Limit Buy Order ---")
    limit_fill = simulator.simulate_fill(
        order_type="LIMIT",
        side="BUY",
        intended_price=150.0,
        size=100,
        symbol="AAPL"
    )
    
    print(f"Intended: {limit_fill.intended_qty} shares @ ${limit_fill.intended_price:.2f}")
    print(f"Actual Fill: {limit_fill.filled_qty} shares @ ${limit_fill.actual_fill_price:.4f}")
    print(f"Slippage: {limit_fill.slippage_pct:.3f}% (${limit_fill.slippage_cost:.2f})")
    
    # Compare market vs limit
    print(f"\n--- Comparison ---")
    print(f"Market Order Slippage: {market_fill.slippage_pct:.3f}%")
    print(f"Limit Order Slippage: {limit_fill.slippage_pct:.3f}%")
    print(f"Savings: ${market_fill.slippage_cost - limit_fill.slippage_cost:.2f}")
    
    # Test volatile conditions
    print("\n--- Volatile Market Conditions ---")
    simulator.set_condition(MarketCondition.VOLATILE)
    
    volatile_fill = simulator.simulate_fill(
        order_type="MARKET",
        side="BUY",
        intended_price=150.0,
        size=100,
        symbol="AAPL"
    )
    
    print(f"Slippage in Volatile Market: {volatile_fill.slippage_pct:.3f}%")
    print(f"Cost: ${volatile_fill.slippage_cost:.2f}")
    
    # Show cumulative statistics
    stats = simulator.get_statistics()
    print(f"\n--- Cumulative Statistics ---")
    print(f"Total Fills: {stats['total_fills']}")
    print(f"Average Slippage: {stats['avg_slippage_pct']:.3f}%")
    print(f"Total Slippage Cost: ${stats['total_slippage_cost']:.2f}")
    print(f"Complete Fill Rate: {stats['complete_fill_rate']:.2%}")


def example_risk_management():
    """
    Example: Conservative position sizing and risk management
    """
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Conservative Risk Management")
    print("=" * 60)
    
    # Create risk model with $10,000 account
    risk_model = ConservativeRiskModel(account_balance=10000.0)
    
    # Show risk parameters
    summary = risk_model.get_risk_summary()
    print(f"\nAccount Balance: ${summary['account_balance']:.2f}")
    print(f"Max Position Value: ${summary['max_position_value']:.2f} (5% of account)")
    print(f"Max Risk Per Trade: ${summary['max_risk_per_trade']:.2f} (1% of account)")
    print(f"Hurdle Rate: {summary['hurdle_rate_pct']:.2f}%")
    print(f"Total Cost Per Roundtrip: {summary['total_cost_per_roundtrip_pct']:.3f}%")
    
    # Calculate position size for a trade
    print("\n--- Position Sizing Example ---")
    entry_price = 150.0
    stop_loss = 147.0  # 2% stop
    
    shares, risk_params = risk_model.calculate_position_size(
        entry_price=entry_price,
        stop_loss_price=stop_loss,
        confidence=0.8,  # 80% confidence
        volatility_adjustment=1.0
    )
    
    print(f"\nTrade Setup:")
    print(f"  Entry Price: ${entry_price:.2f}")
    print(f"  Stop Loss: ${risk_params.stop_loss_price:.2f} ({((stop_loss-entry_price)/entry_price)*100:.1f}%)")
    print(f"  Take Profit: ${risk_params.take_profit_price:.2f} (2:1 R/R)")
    
    print(f"\nPosition Sizing:")
    print(f"  Shares: {shares}")
    print(f"  Position Value: ${risk_params.position_value:.2f}")
    print(f"  Portfolio Exposure: {risk_params.portfolio_exposure_pct:.2f}%")
    
    print(f"\nRisk/Reward:")
    print(f"  Max Loss: ${risk_params.max_loss_amount:.2f}")
    print(f"  Expected Profit: ${risk_params.expected_profit:.2f}")
    print(f"  Risk/Reward Ratio: 1:{risk_params.risk_reward_ratio:.1f}")
    
    # Test expected return adjustment
    print("\n--- Expected Return Adjustment ---")
    raw_return = 0.015  # 1.5% expected
    adjusted_return = risk_model.adjust_expected_return(raw_return)
    
    print(f"Raw Expected Return: {raw_return:.2%}")
    print(f"Adjusted Return (after costs): {adjusted_return:.2%}")
    print(f"Cost Drag: {(raw_return - adjusted_return):.2%}")
    
    # Validate the trade
    print("\n--- Trade Validation ---")
    is_valid, reason = risk_model.validate_trade(
        expected_return=adjusted_return,
        position_size=shares,
        entry_price=entry_price,
        stop_loss_price=stop_loss
    )
    
    print(f"Trade Valid: {is_valid}")
    print(f"Reason: {reason}")
    
    # Test a trade that fails validation
    print("\n--- Failed Trade Example ---")
    low_return = 0.003  # 0.3% - below hurdle
    adjusted_low = risk_model.adjust_expected_return(low_return)
    
    is_valid_low, reason_low = risk_model.validate_trade(
        expected_return=adjusted_low,
        position_size=shares,
        entry_price=entry_price,
        stop_loss_price=stop_loss
    )
    
    print(f"Raw Expected Return: {low_return:.2%}")
    print(f"Adjusted Return: {adjusted_low:.2%}")
    print(f"Trade Valid: {is_valid_low}")
    print(f"Reason: {reason_low}")


def example_integrated_workflow():
    """
    Example: Complete workflow integrating all modules
    """
    print("\n\n" + "=" * 60)
    print("EXAMPLE 4: Integrated Trading Workflow")
    print("=" * 60)
    
    # Step 1: Synchronize signals
    print("\n[1] Synchronizing Signals...")
    sync = SignalSynchronizer(window_size=timedelta(minutes=5))
    
    now = datetime.utcnow()
    sync.add_signal(TimestampedSignal("PRICE", 150.0, now))
    sync.add_signal(TimestampedSignal("NEWS", 82.0, now))
    sync.add_signal(TimestampedSignal("TECHNICAL", 58.0, now))
    
    window = sync.get_synchronized_window(required_types=["PRICE", "NEWS", "TECHNICAL"])
    
    if window["status"] != "READY":
        print(f"  ❌ Signals not ready: {window['reason']}")
        return
    
    print(f"  ✓ Signals synchronized ({window['signal_count']} signals)")
    
    # Step 2: Make trading decision
    print("\n[2] Analyzing Signals...")
    price = next(s.value for s in window["signals"] if s.signal_type == "PRICE")
    news = next(s.value for s in window["signals"] if s.signal_type == "NEWS")
    rsi = next(s.value for s in window["signals"] if s.signal_type == "TECHNICAL")
    
    # Simple decision logic
    bullish_signals = sum([news > 70, rsi < 70, True])  # Price always counts
    decision = "BUY" if bullish_signals >= 2 else "WAIT"
    
    print(f"  Price: ${price:.2f}")
    print(f"  News Sentiment: {news:.1f}/100")
    print(f"  RSI: {rsi:.1f}")
    print(f"  → Decision: {decision}")
    
    if decision == "WAIT":
        print("\n  No trade signal. Waiting...")
        return
    
    # Step 3: Calculate position size
    print("\n[3] Calculating Position Size...")
    risk_model = ConservativeRiskModel(account_balance=10000.0)
    
    entry_price = price
    stop_loss = price * 0.98  # 2% stop
    
    shares, risk_params = risk_model.calculate_position_size(
        entry_price=entry_price,
        stop_loss_price=stop_loss,
        confidence=0.85
    )
    
    print(f"  Position: {shares} shares @ ${entry_price:.2f}")
    print(f"  Stop Loss: ${risk_params.stop_loss_price:.2f}")
    print(f"  Max Risk: ${risk_params.max_loss_amount:.2f}")
    
    # Step 4: Validate trade
    print("\n[4] Validating Trade...")
    expected_return = 0.012  # 1.2% expected
    adjusted_return = risk_model.adjust_expected_return(expected_return)
    
    is_valid, reason = risk_model.validate_trade(
        expected_return=adjusted_return,
        position_size=shares,
        entry_price=entry_price,
        stop_loss_price=stop_loss
    )
    
    print(f"  Expected Return: {adjusted_return:.2%}")
    print(f"  Valid: {is_valid} - {reason}")
    
    if not is_valid:
        print("\n  ❌ Trade rejected by risk model")
        return
    
    # Step 5: Simulate execution
    print("\n[5] Simulating Order Execution...")
    simulator = SlippageSimulator(condition=MarketCondition.NORMAL)
    
    fill = simulator.simulate_fill(
        order_type="MARKET",
        side="BUY",
        intended_price=entry_price,
        size=shares,
        symbol="AAPL"
    )
    
    print(f"  Intended: {fill.intended_qty} @ ${fill.intended_price:.2f}")
    print(f"  Filled: {fill.filled_qty} @ ${fill.actual_fill_price:.4f}")
    print(f"  Slippage: {fill.slippage_pct:.3f}% (${fill.slippage_cost:.2f})")
    
    # Step 6: Final summary
    print("\n[6] Trade Summary")
    print(f"  ✓ Trade executed successfully")
    print(f"  Position Value: ${fill.filled_qty * fill.actual_fill_price:.2f}")
    print(f"  Total Cost (slippage): ${fill.total_cost:.2f}")
    print(f"  Adjusted Entry: ${fill.actual_fill_price:.4f}")
    print(f"  Stop Loss: ${risk_params.stop_loss_price:.2f}")
    print(f"  Take Profit: ${risk_params.take_profit_price:.2f}")


if __name__ == "__main__":
    # Run all examples
    example_signal_synchronization()
    example_slippage_simulation()
    example_risk_management()
    example_integrated_workflow()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
