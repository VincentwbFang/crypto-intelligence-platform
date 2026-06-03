from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


TOP_30_USDT_SYMBOLS = (
    "BTC/USDT,ETH/USDT,BNB/USDT,SOL/USDT,XRP/USDT,DOGE/USDT,ADA/USDT,"
    "TRX/USDT,TON/USDT,LINK/USDT,AVAX/USDT,SUI/USDT,XLM/USDT,BCH/USDT,"
    "HBAR/USDT,LTC/USDT,DOT/USDT,UNI/USDT,APT/USDT,NEAR/USDT,ICP/USDT,"
    "ETC/USDT,ARB/USDT,OP/USDT,FIL/USDT,ATOM/USDT,INJ/USDT,SEI/USDT,"
    "HYPE/USDT,PEPE/USDT"
)


class Settings(BaseSettings):
    APP_NAME: str = "crypto-intelligence-platform"
    APP_VERSION: str = "0.1.0"
    DEPLOYMENT_ENV: str = "local"
    SERVICE_NAME: str = "crypto-intelligence-platform"
    ENV: str = "local"
    DEBUG: bool = False
    DATABASE_URL: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/crypto_intelligence"
    )
    REDIS_URL: str = "redis://localhost:6379/0"
    LOG_LEVEL: str = "INFO"
    DEFAULT_EXCHANGE: str = "okx"
    DEFAULT_SYMBOLS: str = TOP_30_USDT_SYMBOLS
    DEFAULT_TIMEFRAME: str = "1h"
    MARKET_DATA_LIMIT: int = 200
    MARKET_TOP_N: int = 30
    MARKET_BACKFILL_YEARS: int = 3
    MARKET_BACKFILL_TIMEFRAME: str = "1h"
    MARKET_BACKFILL_BATCH_LIMIT: int = 300
    MARKET_BACKFILL_QUOTE: str = "USDT"
    MARKET_TOP_SYMBOLS: str = TOP_30_USDT_SYMBOLS
    MARKET_EXCLUDE_SYMBOLS: str = "USDT,USDC,STETH,WBTC,DAI,USDE,BUSD,FDUSD"
    COINGECKO_MARKETS_URL: str = "https://api.coingecko.com/api/v3/coins/markets"
    ENABLE_MARKET_DATA_SCHEDULER: bool = True
    MARKET_DATA_UPDATE_INTERVAL_SECONDS: int = 3600
    MARKET_DATA_UPDATE_LIMIT: int = 300
    MARKET_DATA_UPDATE_TIMEFRAME: str = "1h"
    MARKET_DATA_UPDATE_TOP_N: int = 30
    MARKET_DATA_UPDATE_USE_TOP_MARKET_CAP: bool = True
    MARKET_DATA_UPDATE_ON_STARTUP: bool = True
    MARKET_DATA_UPDATE_ROLLING_DAYS: int = 35
    MARKET_DATA_UPDATE_MAX_BATCHES_PER_SYMBOL: int = 8
    RELATIVE_STRENGTH_BASE_SYMBOL: str = "BTC/USDT"
    RELATIVE_STRENGTH_SYMBOLS: str = (
        "ETH/USDT,BNB/USDT,SOL/USDT,XRP/USDT,DOGE/USDT,ADA/USDT,TRX/USDT,"
        "TON/USDT,LINK/USDT,AVAX/USDT,SUI/USDT,XLM/USDT,BCH/USDT,HBAR/USDT,"
        "LTC/USDT,DOT/USDT,UNI/USDT,APT/USDT,NEAR/USDT,ICP/USDT,ETC/USDT,"
        "ARB/USDT,OP/USDT,FIL/USDT,ATOM/USDT,INJ/USDT,SEI/USDT,HYPE/USDT,"
        "PEPE/USDT"
    )
    RELATIVE_STRENGTH_TIMEFRAME: str = "1h"
    RELATIVE_STRENGTH_LOOKBACK_LIMIT: int = 900
    ENABLE_RELATIVE_STRENGTH_SCHEDULER: bool = True
    RELATIVE_STRENGTH_INTERVAL_SECONDS: int = 900
    ENABLE_AI_RELATIVE_STRENGTH_ALERT_EXPLANATION: bool = False
    ENABLE_NEWS_SCHEDULER: bool = True
    NEWS_RUN_ON_STARTUP: bool = True
    NEWS_FETCH_INTERVAL_MINUTES: int = 10
    NEWS_ANALYZE_INTERVAL_MINUTES: int = 10
    NEWS_BRIEFING_INTERVAL_MINUTES: int = 30
    NEWS_MORNING_BRIEFING_TIME: str = "08:30"
    NEWS_TIMEZONE: str = "America/New_York"
    NEWS_MAX_ITEMS_PER_FETCH: int = 50
    NEWS_DEDUPE_TITLE_SIMILARITY: float = 0.88
    NEWS_LLM_ENABLED: bool = True
    NEWS_LLM_MAX_ITEMS_PER_BATCH: int = 10
    NEWS_ALERT_ENABLED: bool = True
    NEWSAPI_API_KEY: str | None = None
    CRYPTOPANIC_API_KEY: str | None = None
    GDELT_ENABLED: bool = True
    RSS_NEWS_ENABLED: bool = True
    NEWS_RSS_FEED_URLS: str = (
        "https://www.coindesk.com/arc/outboundfeeds/rss/,"
        "https://cointelegraph.com/rss,"
        "https://decrypt.co/feed,"
        "https://www.theblock.co/rss.xml,"
        "https://www.binance.com/en/blog/rss,"
        "https://www.okx.com/help/rss,"
        "https://www.coinbase.com/blog/rss"
    )
    NEWS_GDELT_QUERY: str = (
        "Bitcoin OR Ethereum OR Solana OR stablecoin OR ETF OR SEC crypto"
    )
    ENABLE_AI_SIGNAL_EXPLANATION: bool = False
    SIGNAL_MIN_CANDLES: int = 60
    SIGNAL_DEFAULT_LIMIT: int = 200
    SIGNAL_REFERENCE_SYMBOL: str = "BTC/USDT"
    LLM_PROVIDER: str = "deepseek"
    ENABLE_LLM_JSON_MODE: bool = True
    DEEPSEEK_API_KEY: str | None = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-v4-pro"
    ENABLE_AI_SIGNAL_SUMMARY: bool = False
    ENABLE_ACTIONABLE_SIGNAL_MODE: bool = False
    ENABLE_PAPER_TRADE_SUGGESTIONS: bool = False
    ENABLE_ALERT_ENGINE: bool = True
    ENABLE_ALERT_SCHEDULER: bool = False
    ALERT_EVALUATION_INTERVAL_SECONDS: int = 300
    ALERT_DEFAULT_SYMBOLS: str = TOP_30_USDT_SYMBOLS
    ALERT_DEFAULT_TIMEFRAME: str = "1h"
    ALERT_SIGNAL_SCORE_THRESHOLD: float = 70.0
    ALERT_HIGH_RISK_THRESHOLD: float = 75.0
    ALERT_DEDUP_WINDOW_MINUTES: int = 60
    ENABLE_AI_ALERT_EXPLANATION: bool = False
    ENABLE_WEBHOOK_NOTIFICATIONS: bool = False
    ALERT_WEBHOOK_URL: str | None = None
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    FRONTEND_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    BACKTEST_DEFAULT_INITIAL_CAPITAL: float = 10000.0
    BACKTEST_DEFAULT_FEE_BPS: float = 10.0
    BACKTEST_DEFAULT_SLIPPAGE_BPS: float = 5.0
    BACKTEST_DEFAULT_MAX_POSITION_PCT: float = 1.0
    BACKTEST_DEFAULT_TIMEFRAME: str = "1h"
    BACKTEST_MIN_CANDLES: int = 100
    ENABLE_AI_BACKTEST_EXPLANATION: bool = False
    PAPER_DEFAULT_INITIAL_BALANCE: float = 10000.0
    PAPER_DEFAULT_FEE_BPS: float = 10.0
    PAPER_DEFAULT_SLIPPAGE_BPS: float = 5.0
    PAPER_MAX_POSITION_PCT: float = 0.25
    PAPER_MAX_DAILY_LOSS_PCT: float = 0.05
    PAPER_MAX_OPEN_POSITIONS: int = 5
    PAPER_ALLOW_SHORTING: bool = False
    PAPER_ALLOW_LEVERAGE: bool = False
    ENABLE_AI_PAPER_TRADING_EXPLANATION: bool = False
    ENABLE_SIGNAL_TO_PAPER_TRADE: bool = False
    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    AUTH_COOKIE_SECURE: bool = False
    AUTH_COOKIE_SAMESITE: str = "lax"
    ENABLE_AUTH: bool = True
    ENABLE_MULTI_WORKSPACE: bool = True
    DEFAULT_PLAN: str = "free"
    ENABLE_USAGE_LIMITS: bool = True
    FREE_PLAN_MAX_WATCHLIST_SYMBOLS: int = 10
    FREE_PLAN_MAX_BACKTESTS_PER_MONTH: int = 20
    FREE_PLAN_MAX_AI_EXPLANATIONS_PER_MONTH: int = 50
    FREE_PLAN_MAX_PAPER_ACCOUNTS: int = 1
    PRO_PLAN_MAX_WATCHLIST_SYMBOLS: int = 50
    PRO_PLAN_MAX_BACKTESTS_PER_MONTH: int = 500
    PRO_PLAN_MAX_AI_EXPLANATIONS_PER_MONTH: int = 1000
    PRO_PLAN_MAX_PAPER_ACCOUNTS: int = 5
    PREMIUM_PLAN_MAX_WATCHLIST_SYMBOLS: int = 200
    PREMIUM_PLAN_MAX_BACKTESTS_PER_MONTH: int = 5000
    PREMIUM_PLAN_MAX_AI_EXPLANATIONS_PER_MONTH: int = 10000
    PREMIUM_PLAN_MAX_PAPER_ACCOUNTS: int = 20
    ENABLE_JSON_LOGGING: bool = True
    ENABLE_REQUEST_LOGGING: bool = True
    ENABLE_METRICS: bool = True
    ENABLE_OTEL: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    OTEL_SERVICE_NAME: str = "crypto-intelligence-platform-api"
    ENABLE_SENTRY: bool = False
    SENTRY_DSN: str | None = None
    SENTRY_ENVIRONMENT: str = "local"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "20/minute"
    RATE_LIMIT_AI: str = "30/minute"
    RATE_LIMIT_BACKTEST: str = "10/minute"
    RATE_LIMIT_PAPER_ORDER: str = "30/minute"
    ENABLE_SECURITY_HEADERS: bool = True
    TRUSTED_HOSTS: str = "localhost,127.0.0.1,testserver"
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800
    DB_BACKUP_DIR: str = "/backups"
    LOG_REDACTION_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def default_symbols_list(self) -> list[str]:
        return [
            symbol.strip()
            for symbol in self.DEFAULT_SYMBOLS.split(",")
            if symbol.strip()
        ]

    @property
    def relative_strength_symbols_list(self) -> list[str]:
        return [
            symbol.strip()
            for symbol in self.RELATIVE_STRENGTH_SYMBOLS.split(",")
            if symbol.strip()
        ]

    @property
    def market_top_symbols_list(self) -> list[str]:
        return [
            symbol.strip()
            for symbol in self.MARKET_TOP_SYMBOLS.split(",")
            if symbol.strip()
        ]

    @property
    def market_exclude_symbols_set(self) -> set[str]:
        return {
            symbol.strip().upper()
            for symbol in self.MARKET_EXCLUDE_SYMBOLS.split(",")
            if symbol.strip()
        }

    @property
    def news_rss_feed_urls_list(self) -> list[str]:
        return [
            url.strip()
            for url in self.NEWS_RSS_FEED_URLS.split(",")
            if url.strip()
        ]

    @property
    def deepseek_model_name(self) -> str:
        return self.DEEPSEEK_MODEL.strip() or "deepseek-v4-pro"

    @property
    def alert_default_symbols_list(self) -> list[str]:
        return [
            symbol.strip()
            for symbol in self.ALERT_DEFAULT_SYMBOLS.split(",")
            if symbol.strip()
        ]

    @property
    def frontend_origins_list(self) -> list[str]:
        origins = [
            origin.strip()
            for origin in self.FRONTEND_ORIGINS.split(",")
            if origin.strip()
        ]
        for origin in self.CORS_ALLOWED_ORIGINS.split(","):
            cleaned = origin.strip()
            if cleaned and cleaned not in origins:
                origins.append(cleaned)
        return origins

    @property
    def trusted_hosts_list(self) -> list[str]:
        return [
            host.strip()
            for host in self.TRUSTED_HOSTS.split(",")
            if host.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
