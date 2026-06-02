from app.core.config import settings
from app.tasks.news_tasks import NewsScheduler


def test_news_scheduler_initializes_jobs(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ENABLE_NEWS_SCHEDULER", True)
    scheduler = NewsScheduler(settings)
    scheduler.start()
    try:
        job_ids = {job.id for job in scheduler.scheduler.get_jobs()}
        assert "fetch_crypto_news" in job_ids
        assert "analyze_unprocessed_news" in job_ids
        assert "generate_intraday_briefing" in job_ids
        assert "generate_morning_briefing" in job_ids
        assert "check_breaking_news_alerts" in job_ids
    finally:
        scheduler.shutdown()
