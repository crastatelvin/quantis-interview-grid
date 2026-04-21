"""create interview_sessions table

Revision ID: 0001_create_interview_sessions
Revises:
Create Date: 2026-04-21
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_interview_sessions"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "interview_sessions",
        sa.Column("session_id", sa.String(length=64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interview_type", sa.String(length=32), nullable=False),
        sa.Column("jd_analysis", sa.JSON(), nullable=False),
        sa.Column("questions", sa.JSON(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("evaluations", sa.JSON(), nullable=False),
        sa.Column("raw_jd", sa.Text(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_table("interview_sessions")

