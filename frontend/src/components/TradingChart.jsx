import React, { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries, HistogramSeries, createSeriesMarkers } from 'lightweight-charts';
import { Activity } from 'lucide-react';
import { BASE_URL } from '../api';
import { useTheme } from '../ThemeContext';

export default function TradingChart({ symbol = "RELIANCE.NS", userId, compact = false }) {
    const { isDark } = useTheme();
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        if (chartRef.current) {
            chartRef.current.remove();
            chartRef.current = null;
        }

        const fetchChartData = async () => {
            try {
                setLoading(true);
                setError(false);

                const url = userId
                    ? `${BASE_URL}/api/market/ohlcv/${symbol}?user_id=${encodeURIComponent(userId)}`
                    : `${BASE_URL}/api/market/ohlcv/${symbol}`;

                const response = await fetch(url);
                if (!response.ok) throw new Error('API error');
                const { ohlc, volume, trades } = await response.json();

                if (!ohlc || ohlc.length === 0) throw new Error('No data');

                const bgColor = isDark ? '#0A0A0A' : '#F9FAFB';
                const textColor = isDark ? '#9CA3AF' : '#4B5563';
                const gridColor = isDark ? '#1E1E1E' : '#E5E7EB';
                const borderColor = isDark ? '#1E1E1E' : '#E5E7EB';

                const chart = createChart(chartContainerRef.current, {
                    layout: {
                        background: { type: 'solid', color: bgColor },
                        textColor,
                        fontSize: compact ? 10 : 12,
                    },
                    grid: {
                        vertLines: { color: gridColor + '20' },
                        horzLines: { color: gridColor + '40' },
                    },
                    width: chartContainerRef.current.clientWidth,
                    height: chartContainerRef.current.clientHeight,
                    rightPriceScale: {
                        borderColor,
                        visible: !compact,
                    },
                    timeScale: {
                        borderColor,
                        timeVisible: !compact,
                        secondsVisible: false,
                        visible: !compact,
                    },
                    crosshair: compact ? { mode: 0 } : undefined,
                });
                chartRef.current = chart;

                const candlestickSeries = chart.addSeries(CandlestickSeries, {
                    upColor: '#00D09C',
                    downColor: '#EB5B3C',
                    borderVisible: false,
                    wickUpColor: '#00D09C',
                    wickDownColor: '#EB5B3C',
                });
                candlestickSeries.setData(ohlc);

                if (!compact) {
                    const volumeSeries = chart.addSeries(HistogramSeries, {
                        color: '#00D09C40',
                        priceFormat: { type: 'volume' },
                        priceScaleId: 'volume',
                    });
                    volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });
                    volumeSeries.setData(volume);

                    if (trades && trades.length > 0) {
                        const markers = trades
                            .map(trade => ({
                                time: trade.time,
                                position: trade.side === 'BUY' ? 'belowBar' : 'aboveBar',
                                color: trade.side === 'BUY' ? '#00D09C' : '#EB5B3C',
                                shape: trade.side === 'BUY' ? 'arrowUp' : 'arrowDown',
                                text: `${trade.side} ${trade.qty}`,
                            }))
                            .sort((a, b) => a.time.localeCompare(b.time));
                        createSeriesMarkers(candlestickSeries, markers);
                    }
                }

                chart.timeScale().fitContent();
                setLoading(false);

                const ro = new ResizeObserver(() => {
                    if (chart && chartContainerRef.current) {
                        chart.applyOptions({
                            width: chartContainerRef.current.clientWidth,
                            height: chartContainerRef.current.clientHeight,
                        });
                    }
                });
                ro.observe(chartContainerRef.current);
                return () => ro.disconnect();

            } catch (err) {
                console.error('TradingChart Error:', err);
                setError(true);
                setLoading(false);
            }
        };

        fetchChartData();

        return () => {
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
        };
    }, [symbol, userId, compact, isDark]);

    const chartHeight = compact ? '100%' : '400px';

    return (
        <div className="bg-dark-card rounded-xl border border-dark-border w-full" style={{ contain: 'layout' }}>
            {/* Header — hidden in compact mode */}
            {!compact && (
                <div className="flex items-center justify-between px-6 pt-5 pb-4">
                    <h2 className="text-lg font-bold flex items-center text-dark-text">
                        <Activity size={20} className="mr-2 text-accent-green" /> {symbol} Advanced Chart
                    </h2>
                    <span className="text-xs font-mono text-dark-muted bg-dark-bg px-2 py-1 rounded border border-dark-border">6M Daily</span>
                </div>
            )}

            {/* Chart area */}
            <div className={`relative ${compact ? '' : 'px-2 pb-4'}`} style={{ height: chartHeight }}>
                {loading && (
                    <div className="absolute inset-0 z-10 bg-dark-card/90 flex flex-col items-center justify-center rounded-lg">
                        <Activity className="animate-spin text-accent-green mb-2" size={compact ? 20 : 32} />
                        {!compact && <p className="text-dark-muted font-medium text-sm">Loading Chart Data...</p>}
                    </div>
                )}
                {error && !loading && (
                    <div className="absolute inset-0 z-10 bg-dark-card/90 flex flex-col items-center justify-center rounded-lg">
                        <Activity size={compact ? 20 : 32} className="text-dark-muted/30 mb-2" />
                        {!compact && (
                            <>
                                <p className="text-dark-muted text-sm font-medium">Chart unavailable</p>
                                <p className="text-dark-muted/60 text-xs mt-1">Backend offline</p>
                            </>
                        )}
                    </div>
                )}
                <div ref={chartContainerRef} className="w-full h-full" />
            </div>
        </div>
    );
}
