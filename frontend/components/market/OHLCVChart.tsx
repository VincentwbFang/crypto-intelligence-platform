"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp
} from "lightweight-charts";

import { EmptyState } from "@/components/common/EmptyState";
import type { OHLCVRow } from "@/lib/api/types";

export function OHLCVChart({ rows }: { rows: OHLCVRow[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!containerRef.current || !rows.length) {
      return;
    }

    const chart = createChart(containerRef.current, {
      height: 360,
      layout: {
        background: { color: "#ffffff" },
        textColor: "#0f172a"
      },
      grid: {
        vertLines: { color: "#e2e8f0" },
        horzLines: { color: "#e2e8f0" }
      },
      rightPriceScale: {
        borderColor: "#cbd5e1"
      },
      timeScale: {
        borderColor: "#cbd5e1"
      }
    });
    const candleSeries = chart.addCandlestickSeries({
      upColor: "#059669",
      downColor: "#dc2626",
      borderVisible: false,
      wickUpColor: "#059669",
      wickDownColor: "#dc2626"
    });
    candleSeries.setData(
      rows.map((row) => ({
        time: Math.floor(new Date(row.timestamp).getTime() / 1000) as UTCTimestamp,
        open: row.open,
        high: row.high,
        low: row.low,
        close: row.close
      }))
    );
    chart.timeScale().fitContent();

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;

    const resizeObserver = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        chart.applyOptions({ width: Math.floor(entry.contentRect.width) });
      }
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
    };
  }, [rows]);

  if (!rows.length) {
    return <EmptyState message="No OHLCV rows are available for charting." />;
  }

  return (
    <div
      aria-label="OHLCV candlestick chart"
      className="h-[360px] w-full rounded-lg border bg-card"
      ref={containerRef}
    />
  );
}
