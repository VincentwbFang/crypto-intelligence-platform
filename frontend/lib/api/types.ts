export type OHLCVRow = {
  exchange: string;
  symbol: string;
  timeframe: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type MarketSnapshot = {
  symbol: string;
  timeframe: string;
  latest_close: number;
  previous_close: number;
  return_pct: number;
  high: number;
  low: number;
  volume: number;
  candle_count: number;
  timestamp: string;
};

export type OHLCVResponse = {
  symbol: string;
  timeframe: string;
  data: OHLCVRow[];
};

export type MarketIngestRequest = {
  exchange: string;
  symbols: string[];
  timeframe: string;
  limit: number;
};

export type MarketIngestResponse = {
  exchange: string;
  timeframe: string;
  results: Record<string, number>;
};

export type SignalScores = {
  trend_score: number;
  momentum_score: number;
  volume_score: number;
  volatility_risk_score: number;
  relative_strength_score: number;
  overall_signal_score: number;
};

export type SignalIndicators = {
  ema_20: number | null;
  ema_50: number | null;
  ema_200: number | null;
  rsi_14: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  atr_14: number | null;
  volume_zscore_20: number | null;
  realized_volatility_20: number | null;
};

export type RelativeStrengthResult = {
  reference_symbol: string;
  return_24h: number | null;
  reference_return_24h: number | null;
  relative_return_24h: number | null;
  return_7d: number | null;
  reference_return_7d: number | null;
  relative_return_7d: number | null;
  relative_strength_score: number;
  explanation: string;
};

export type DataQualityResult = {
  candle_count: number;
  min_required_candles: number;
  has_sufficient_data: boolean;
  missing_indicator_warning: boolean;
};

export type AIExplanationResponse = {
  enabled: boolean;
  message?: string | null;
  error?: string | null;
  plain_english_summary?: string | null;
  why_this_signal?: string[] | null;
  why_triggered?: string[] | null;
  main_risks?: string[] | null;
  risk_context?: string[] | null;
  what_to_monitor?: string[] | null;
  confidence_commentary?: string | null;
  limitations?: string[] | null;
  disclaimer?: string | null;
  compliance_warnings?: string[] | null;
};

export type SignalResponse = {
  symbol: string;
  timeframe: string;
  timestamp: string | null;
  latest_close: number | null;
  scores: SignalScores;
  signal_direction: "bullish" | "bearish" | "neutral" | "mixed" | string;
  setup_type: string;
  risk_level: "low" | "medium" | "high" | "extreme" | string;
  indicators: SignalIndicators;
  relative_strength: RelativeStrengthResult;
  risk_notes: string[];
  data_quality: DataQualityResult;
  explanation: string;
  ai_explanation?: AIExplanationResponse | null;
};

export type SignalRankResponse = {
  symbols: string[];
  timeframe: string;
  data: SignalResponse[];
};

export type AlertResponse = {
  id: number;
  symbol: string;
  timeframe: string;
  timestamp: string;
  alert_type: string;
  severity: "info" | "low" | "medium" | "high" | "critical" | string;
  title: string;
  message: string;
  status: "open" | "acknowledged" | "resolved" | "dismissed" | string;
  source?: string | null;
  signal_score?: number | null;
  risk_level?: string | null;
  setup_type?: string | null;
  dedup_key: string;
  raw_payload?: Record<string, unknown> | null;
  created_at?: string | null;
  updated_at?: string | null;
  resolved_at?: string | null;
};

export type AlertListResponse = {
  data: AlertResponse[];
};

export type AlertEvaluateRequest = {
  symbols: string[];
  timeframe: string;
  limit: number;
  send_notifications: boolean;
};

export type AlertEvaluateResponse = {
  symbols: string[];
  timeframe: string;
  results: Array<{
    symbol: string;
    timeframe: string;
    generated_alerts: number;
    deduplicated_alerts: number;
    alerts: AlertResponse[];
  }>;
  generated_alerts: number;
  deduplicated_alerts: number;
  alerts: AlertResponse[];
  notifications?: NotificationResult[] | null;
};

export type AlertFilters = {
  symbol?: string;
  timeframe?: string;
  severity?: string;
  alert_type?: string;
  status?: string;
  limit?: number;
};

export type NotificationResult = {
  alert_id?: number | null;
  status: string;
  deliveries: Array<Record<string, string | number | boolean | null>>;
};

export type BacktestStrategyInfo = {
  name: string;
  description: string;
  default_parameters: Record<string, string | number | boolean>;
  supported_positioning: string;
};

export type BacktestRunRequest = {
  symbol: string;
  timeframe: string;
  strategy_name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  fee_bps: number;
  slippage_bps: number;
  max_position_pct: number;
  parameters: Record<string, string | number | boolean>;
};

export type BacktestMetrics = {
  initial_capital: number;
  final_equity: number;
  total_return_pct: number;
  max_drawdown_pct: number;
  sharpe_ratio: number | null;
  win_rate: number;
  profit_factor: number | null;
  total_trades: number;
  average_trade_return_pct: number;
  average_holding_period_bars: number;
  exposure_time_pct: number;
};

export type BacktestTrade = {
  id?: number | null;
  run_id?: string | null;
  symbol: string;
  side: string;
  entry_time: string;
  entry_price: number;
  exit_time: string;
  exit_price: number;
  quantity: number;
  notional: number;
  fee: number;
  slippage: number;
  pnl: number;
  pnl_pct: number;
  holding_period_bars: number;
  exit_reason: string;
  created_at?: string | null;
};

export type EquityCurvePoint = {
  timestamp: string;
  equity: number;
  cash: number;
  position_value: number;
  drawdown_pct: number;
};

export type BacktestRun = {
  run_id: string;
  symbol: string;
  timeframe: string;
  strategy_name: string;
  parameters: Record<string, unknown>;
  initial_capital: number;
  final_equity?: number | null;
  total_return_pct?: number | null;
  max_drawdown_pct?: number | null;
  sharpe_ratio?: number | null;
  win_rate?: number | null;
  profit_factor?: number | null;
  total_trades?: number | null;
  status: string;
  started_at?: string | null;
  completed_at?: string | null;
  error_message?: string | null;
  created_at?: string | null;
};

export type BacktestDetail = BacktestRun & {
  metrics?: BacktestMetrics | null;
  trades: BacktestTrade[];
  equity_curve: EquityCurvePoint[];
  data_quality?: Record<string, unknown> | null;
  disclaimer?: string | null;
};

export type AIBacktestExplanation = {
  enabled: boolean;
  message?: string | null;
  error?: string | null;
  plain_english_summary?: string | null;
  performance_interpretation?: string[] | null;
  risk_interpretation?: string[] | null;
  strategy_behavior?: string[] | null;
  main_weaknesses?: string[] | null;
  what_to_validate_next?: string[] | null;
  limitations?: string[] | null;
  disclaimer?: string | null;
  compliance_warnings?: string[] | null;
};

export type PaperAccount = {
  id?: number | null;
  account_id: string;
  name: string;
  initial_balance: number;
  cash_balance: number;
  equity: number;
  realized_pnl: number;
  unrealized_pnl: number;
  total_fees: number;
  status: string;
  created_at?: string | null;
  updated_at?: string | null;
};

export type PaperOrder = {
  id?: number | null;
  order_id: string;
  account_id: string;
  symbol: string;
  timeframe: string;
  side: string;
  order_type: string;
  quantity?: number | null;
  notional: number;
  requested_price?: number | null;
  filled_price?: number | null;
  status: string;
  source?: string | null;
  signal_id?: string | null;
  reason?: string | null;
  fee?: number | null;
  slippage?: number | null;
  created_at?: string | null;
  filled_at?: string | null;
  cancelled_at?: string | null;
  risk?: Record<string, unknown> | null;
};

export type PaperPosition = {
  id?: number | null;
  account_id: string;
  symbol: string;
  quantity: number;
  average_entry_price: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  opened_at?: string | null;
  updated_at?: string | null;
  status: string;
};

export type PaperTrade = {
  id?: number | null;
  trade_id?: string | null;
  account_id?: string | null;
  symbol: string;
  side: string;
  entry_time?: string | null;
  entry_price: number;
  exit_time?: string | null;
  exit_price?: number | null;
  quantity?: number | null;
  notional?: number | null;
  fee?: number | null;
  slippage?: number | null;
  realized_pnl?: number | null;
  realized_pnl_pct?: number | null;
  source?: string | null;
  strategy_name?: string | null;
  exit_reason?: string | null;
  created_at?: string | null;
};

export type PaperEquitySnapshot = {
  id?: number | null;
  account_id: string;
  timestamp?: string | null;
  cash_balance: number;
  equity: number;
  realized_pnl: number;
  unrealized_pnl: number;
  total_fees: number;
  open_positions_count: number;
  created_at?: string | null;
};

export type PaperPortfolio = {
  account: PaperAccount;
  positions: PaperPosition[];
  open_orders: PaperOrder[];
  equity_snapshot?: PaperEquitySnapshot | null;
};

export type PaperPerformance = {
  initial_balance: number;
  current_equity: number;
  total_return_pct: number;
  realized_pnl: number;
  unrealized_pnl: number;
  total_fees: number;
  total_trades: number;
  win_rate: number;
  profit_factor?: number | null;
  max_drawdown_pct: number;
  open_positions_count: number;
  exposure_pct: number;
};

export type SignalPaperExecutionResult = {
  enabled: boolean;
  message?: string | null;
  signal?: SignalResponse | Record<string, unknown> | null;
  action_taken?: string | null;
  order?: PaperOrder | Record<string, unknown> | null;
  reason?: string | null;
  disclaimer: string;
};

export type AIPaperTradingExplanation = {
  enabled: boolean;
  message?: string | null;
  error?: string | null;
  plain_english_summary?: string | null;
  performance_observations?: string[] | null;
  risk_observations?: string[] | null;
  position_notes?: string[] | null;
  what_to_monitor?: string[] | null;
  limitations?: string[] | null;
  disclaimer?: string | null;
  compliance_warnings?: string[] | null;
};

export type AuthUser = {
  user_id: string;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  default_workspace_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  last_login_at?: string | null;
};

export type Workspace = {
  workspace_id: string;
  name: string;
  slug: string;
  owner_user_id: string;
  plan: string;
  status: string;
  role?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type WorkspaceMember = {
  id?: number | null;
  workspace_id: string;
  user_id: string;
  role: string;
  status: string;
  invited_by_user_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
  workspace?: Workspace | null;
};

export type UserPreference = {
  user_id: string;
  default_symbol: string;
  default_timeframe: string;
  theme: string;
  dashboard_layout: Record<string, unknown>;
  created_at?: string | null;
  updated_at?: string | null;
};

export type WatchlistSymbol = {
  id?: number | null;
  symbol: string;
  display_order: number;
  created_at?: string | null;
};

export type Watchlist = {
  watchlist_id: string;
  workspace_id: string;
  name: string;
  created_by_user_id: string;
  created_at?: string | null;
  updated_at?: string | null;
  symbols: WatchlistSymbol[];
};

export type UsageSummary = {
  workspace_id: string;
  usage: Record<string, number>;
  plan?: string | null;
  limits?: Record<string, number | boolean> | null;
};

export type PlanLimits = {
  workspace_id: string;
  plan: string;
  limits: Record<string, number | boolean>;
};

export type SystemHealth = {
  status: string;
  service: string;
  version: string;
  environment: string;
};

export type SystemReady = {
  status: "ready" | "not_ready" | string;
  checks: Record<string, "ok" | "failed" | string>;
};

export type SystemVersion = {
  version: string;
  service: string;
  environment: string;
};

export type RelativeStrengthSnapshot = {
  id: number;
  symbol: string;
  base_symbol: string;
  price: number | null;
  btc_price: number | null;
  return_1h: number | null;
  return_24h: number | null;
  return_7d: number | null;
  return_30d: number | null;
  btc_return_1h: number | null;
  btc_return_24h: number | null;
  btc_return_7d: number | null;
  btc_return_30d: number | null;
  excess_return_1h: number | null;
  excess_return_24h: number | null;
  excess_return_7d: number | null;
  excess_return_30d: number | null;
  relative_price: number | null;
  relative_trend_score: number | null;
  volume_score: number | null;
  brsi_score: number | null;
  brsi_change_1h: number | null;
  brsi_change_4h: number | null;
  brsi_change_24h: number | null;
  status: string;
  created_at: string;
};

export type RelativeStrengthRankingResponse = {
  data: RelativeStrengthSnapshot[];
};

export type RelativeStrengthHistoryResponse = {
  symbol: string;
  data: RelativeStrengthSnapshot[];
};

export type RelativeStrengthAlert = {
  id: number;
  symbol: string;
  alert_type: string;
  alert_level: string;
  title: string;
  message: string;
  brsi_score: number | null;
  previous_brsi_score: number | null;
  change_value: number | null;
  is_read: boolean;
  created_at: string;
};

export type RelativeStrengthAlertListResponse = {
  data: RelativeStrengthAlert[];
};

export type NewsAISummary = {
  headline_cn?: string | null;
  summary_cn?: string | null;
  why_it_matters?: string | null;
  affected_symbols?: string[] | null;
  market_impact?: string | null;
  risk_level?: string | null;
  watch_points?: string[] | null;
  not_financial_advice?: boolean | null;
  llm_generated?: boolean | null;
};

export type NewsAnalysis = {
  symbols: string[];
  sectors: string[];
  main_symbol?: string | null;
  relevance_score: number;
  impact_score: number;
  sentiment_score: number;
  urgency_level: "low" | "medium" | "high" | "critical" | string;
  time_decay_score: number;
  impact_direction: "bullish" | "bearish" | "mixed" | "neutral" | string;
  ai_summary_json?: NewsAISummary | null;
  analyzed_at: string;
};

export type NewsItem = {
  id: number;
  title: string;
  url: string;
  source: string;
  source_type: string;
  published_at: string;
  published_at_estimated: boolean;
  summary_raw?: string | null;
  content_raw?: string | null;
  language?: string | null;
  duplicate_count: number;
  analysis?: NewsAnalysis | null;
};

export type NewsLatestResponse = {
  data: NewsItem[];
};

export type NewsBroadcast = {
  id?: number | null;
  broadcast_type: string;
  title: string;
  content_cn: string;
  top_symbols: string[];
  top_news_ids: number[];
  overall_sentiment?: string | null;
  created_at?: string | null;
};

export type NewsBriefingResponse = {
  data: NewsBroadcast;
};

export type NewsAlert = {
  id: number;
  news_item_id: number;
  alert_type: string;
  severity: string;
  message_cn: string;
  is_sent: boolean;
  sent_channels: string[];
  created_at: string;
  news?: {
    title: string;
    url: string;
    source: string;
    published_at: string;
  } | null;
  analysis?: {
    symbols: string[];
    urgency_level: string;
    impact_score: number;
    impact_direction: string;
  } | null;
};

export type NewsAlertsResponse = {
  data: NewsAlert[];
};

export type NewsSourcesResponse = {
  rss: { enabled: boolean; feeds: string[] };
  gdelt: { enabled: boolean; query: string };
  newsapi: { enabled: boolean };
  cryptopanic: { enabled: boolean };
};
