"use client";

import { useEffect, useRef } from "react";
import { createChart, type IChartApi, type UTCTimestamp } from "lightweight-charts";

import { EmptyState } from "@/components/common/EmptyState";
import type { EquityCurvePoint } from "@/lib/api/types";

export function EquityCurveChart({ points }: { points: EquityCurvePoint[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current || !points.length) {
      return;
    }
    const chart = createChart(containerRef.current, {
      height: 280,
      layout: { background: { color: "#ffffff" }, textColor: "#0f172a" },
      grid: { vertLines: { color: "#e2e8f0" }, horzLines: { color: "#e2e8f0" } }
    });
    const series = chart.addLineSeries({ color: "#2563eb", lineWidth: 2 });
    series.setData(
      points.map((point) => ({
        time: Math.floor(new Date(point.timestamp).getTime() / 1000) as UTCTimestamp,
        value: point.equity
      }))
    );
    chart.timeScale().fitContent();
    chartRef.current = chart;

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
    };
  }, [points]);

  if (!points.length) {
    return <EmptyState message="No equity curve is available for this run." />;
  }
  return <div aria-label="Equity curve chart" className="h-[280px] w-full" ref={containerRef} />;
}
