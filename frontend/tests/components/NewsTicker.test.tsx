import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { NewsTicker } from "@/components/news/NewsTicker";
import type { NewsItem } from "@/lib/api/types";

const baseNewsItem: NewsItem = {
  id: 1,
  title: "Bitcoin ETF flow update",
  url: "https://example.com/news",
  source: "Example",
  source_type: "rss",
  published_at: "2026-06-03T12:00:00Z",
  published_at_estimated: false,
  summary_raw: null,
  content_raw: null,
  language: "en",
  duplicate_count: 0,
  analysis: {
    symbols: ["BTC"],
    sectors: ["ETF"],
    relevance_score: 90,
    impact_score: 82,
    sentiment_score: 35,
    urgency_level: "high",
    time_decay_score: 100,
    impact_direction: "mixed",
    ai_summary_json: null,
    analyzed_at: "2026-06-03T12:01:00Z"
  }
};

describe("NewsTicker", () => {
  it("renders high-priority news in the ticker", () => {
    render(<NewsTicker items={[baseNewsItem]} />);

    expect(screen.getAllByText("Bitcoin ETF flow update").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Example").length).toBeGreaterThan(0);
  });

  it("does not render when there are no high or critical items", () => {
    render(
      <NewsTicker
        items={[
          {
            ...baseNewsItem,
            analysis: {
              ...baseNewsItem.analysis!,
              urgency_level: "low"
            }
          }
        ]}
      />
    );

    expect(screen.queryByText("Bitcoin ETF flow update")).not.toBeInTheDocument();
  });
});
