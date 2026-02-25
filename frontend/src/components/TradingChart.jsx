import React, { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries, HistogramSeries, createSeriesMarkers } from 'lightweight-charts';
import { Activity } from 'lucide-react';
import { BASE_URL } from '../api';

export default function TradingChart({ symbol = "RELIANCE.NS", userId }) {
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        // Clean up any previous chart instance
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

                // Create chart inside the fixed-height container div
                const chart = createChart(chartContainerRef.current, {
                    layout: {
                        background: { type: 'solid', color: '#FFFFFF' },
                        textColor: '#444444',
                    },
                    grid: {
                        vertLines: { color: '#F0F2F6' },
                        horzLines: { color: '#F0F2F6' },
                    },
                    width: chartContainerRef.current.clientWidth,
                    height: chartContainerRef.current.clientHeight,
                    rightPriceScale: { borderColor: '#E8E9F1' },
                    timeScale: {
                        borderColor: '#E8E9F1',
                        timeVisible: true,
                        secondsVisible: false,
                    },
                });
                chartRef.current = chart;

                // Candlestick series — v5 API: addSeries(SeriesType, options)
                const candlestickSeries = chart.addSeries(CandlestickSeries, {
                    upColor: '#00D09C',
                    downColor: '#EB5B3C',
                    borderVisible: false,
                    wickUpColor: '#00D09C',
                    wickDownColor: '#EB5B3C',
                });
                candlestickSeries.setData(ohlc);

                // Volume histogram — overlaid at the bottom 20% of the chart
                const volumeSeries = chart.addSeries(HistogramSeries, {
                    color: '#26a69a',
                    priceFormat: { type: 'volume' },
                    priceScaleId: 'volume',
                });
                volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });
                volumeSeries.setData(volume);

                // Trade markers — v5 API uses createSeriesMarkers(), not series.setMarkers()
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

                chart.timeScale().fitContent();
                setLoading(false);

                // Responsive resize
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
    }, [symbol, userId]);

    return (
        <div className="bg-white rounded-xl border border-groww-gray/20 shadow-sm w-full" style={{ contain: 'layout' }}>
            {/* Header — outside the chart container so chart can't overlap it */}
            <div className="flex items-center justify-between px-6 pt-5 pb-4">
                <h2 className="text-lg font-bold flex items-center text-groww-dark">
                    <Activity size={20} className="mr-2 text-groww-green" /> {symbol} Advanced Chart
                </h2>
                <span className="text-xs font-mono text-groww-gray bg-groww-light-gray px-2 py-1 rounded">Daily (1M)</span>
            </div>

            {/* Chart area — bounded, strictly 400px */}
            <div className="relative px-2 pb-4" style={{ height: '400px' }}>
                {loading && (
                    <div className="absolute inset-0 z-10 bg-white/90 flex flex-col items-center justify-center rounded-lg">
                        <Activity className="animate-spin text-groww-green mb-2" size={32} />
                        <p className="text-groww-gray font-medium text-sm">Loading Chart Data...</p>
                    </div>
                )}
                {error && !loading && (
                    <div className="absolute inset-0 z-10 bg-white/90 flex flex-col items-center justify-center rounded-lg">
                        <Activity size={32} className="text-groww-gray/30 mb-2" />
                        <p className="text-groww-gray text-sm font-medium">Chart unavailable — backend offline</p>
                        <p className="text-groww-gray/60 text-xs mt-1">Start the FastAPI server to load live data</p>
                    </div>
                )}
                {/* Actual chart target div — lightweight-charts mounts inside here */}
                <div ref={chartContainerRef} className="w-full h-full" />
            </div>
        </div>
    );
}
