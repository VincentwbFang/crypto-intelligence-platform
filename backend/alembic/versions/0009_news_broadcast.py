"""add news broadcast tables

Revision ID: 0009_news_broadcast
Revises: 0008_relative_strength
Create Date: 2026-06-02 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009_news_broadcast"
down_revision: str | None = "0008_relative_strength"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "news_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at_estimated", sa.Boolean(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary_raw", sa.Text(), nullable=True),
        sa.Column("content_raw", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=True),
        sa.Column("hash_title", sa.String(length=128), nullable=False),
        sa.Column("duplicate_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_index("ix_news_items_title", "news_items", ["title"])
    op.create_index("ix_news_items_url", "news_items", ["url"])
    op.create_index("ix_news_items_source", "news_items", ["source"])
    op.create_index("ix_news_items_source_type", "news_items", ["source_type"])
    op.create_index("ix_news_items_published_at", "news_items", ["published_at"])
    op.create_index("ix_news_items_fetched_at", "news_items", ["fetched_at"])
    op.create_index("ix_news_items_language", "news_items", ["language"])
    op.create_index("ix_news_items_hash_title", "news_items", ["hash_title"])

    op.create_table(
        "news_analysis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("news_item_id", sa.Integer(), nullable=False),
        sa.Column("symbols", sa.JSON(), nullable=True),
        sa.Column("sectors", sa.JSON(), nullable=True),
        sa.Column("main_symbol", sa.String(length=32), nullable=True),
        sa.Column("relevance_score", sa.Numeric(10, 4), nullable=False),
        sa.Column("impact_score", sa.Numeric(10, 4), nullable=False),
        sa.Column("sentiment_score", sa.Numeric(10, 4), nullable=False),
        sa.Column("urgency_level", sa.String(length=32), nullable=False),
        sa.Column("time_decay_score", sa.Numeric(10, 4), nullable=False),
        sa.Column("impact_direction", sa.String(length=32), nullable=False),
        sa.Column("ai_summary_json", sa.JSON(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["news_item_id"], ["news_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("news_item_id", name="uq_news_analysis_news_item"),
    )
    op.create_index("ix_news_analysis_news_item_id", "news_analysis", ["news_item_id"])
    op.create_index("ix_news_analysis_main_symbol", "news_analysis", ["main_symbol"])
    op.create_index("ix_news_analysis_urgency_level", "news_analysis", ["urgency_level"])
    op.create_index("ix_news_analysis_impact_direction", "news_analysis", ["impact_direction"])
    op.create_index("ix_news_analysis_analyzed_at", "news_analysis", ["analyzed_at"])

    op.create_table(
        "news_broadcasts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("broadcast_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content_cn", sa.Text(), nullable=False),
        sa.Column("top_symbols", sa.JSON(), nullable=True),
        sa.Column("top_news_ids", sa.JSON(), nullable=True),
        sa.Column("overall_sentiment", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_news_broadcasts_broadcast_type", "news_broadcasts", ["broadcast_type"])
    op.create_index("ix_news_broadcasts_overall_sentiment", "news_broadcasts", ["overall_sentiment"])
    op.create_index("ix_news_broadcasts_created_at", "news_broadcasts", ["created_at"])

    op.create_table(
        "news_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("news_item_id", sa.Integer(), nullable=False),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("message_cn", sa.Text(), nullable=False),
        sa.Column("is_sent", sa.Boolean(), nullable=False),
        sa.Column("sent_channels", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["news_item_id"], ["news_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_news_alerts_news_item_id", "news_alerts", ["news_item_id"])
    op.create_index("ix_news_alerts_alert_type", "news_alerts", ["alert_type"])
    op.create_index("ix_news_alerts_severity", "news_alerts", ["severity"])
    op.create_index("ix_news_alerts_is_sent", "news_alerts", ["is_sent"])
    op.create_index("ix_news_alerts_created_at", "news_alerts", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_news_alerts_created_at", table_name="news_alerts")
    op.drop_index("ix_news_alerts_is_sent", table_name="news_alerts")
    op.drop_index("ix_news_alerts_severity", table_name="news_alerts")
    op.drop_index("ix_news_alerts_alert_type", table_name="news_alerts")
    op.drop_index("ix_news_alerts_news_item_id", table_name="news_alerts")
    op.drop_table("news_alerts")

    op.drop_index("ix_news_broadcasts_created_at", table_name="news_broadcasts")
    op.drop_index("ix_news_broadcasts_overall_sentiment", table_name="news_broadcasts")
    op.drop_index("ix_news_broadcasts_broadcast_type", table_name="news_broadcasts")
    op.drop_table("news_broadcasts")

    op.drop_index("ix_news_analysis_analyzed_at", table_name="news_analysis")
    op.drop_index("ix_news_analysis_impact_direction", table_name="news_analysis")
    op.drop_index("ix_news_analysis_urgency_level", table_name="news_analysis")
    op.drop_index("ix_news_analysis_main_symbol", table_name="news_analysis")
    op.drop_index("ix_news_analysis_news_item_id", table_name="news_analysis")
    op.drop_table("news_analysis")

    op.drop_index("ix_news_items_hash_title", table_name="news_items")
    op.drop_index("ix_news_items_language", table_name="news_items")
    op.drop_index("ix_news_items_fetched_at", table_name="news_items")
    op.drop_index("ix_news_items_published_at", table_name="news_items")
    op.drop_index("ix_news_items_source_type", table_name="news_items")
    op.drop_index("ix_news_items_source", table_name="news_items")
    op.drop_index("ix_news_items_url", table_name="news_items")
    op.drop_index("ix_news_items_title", table_name="news_items")
    op.drop_table("news_items")
