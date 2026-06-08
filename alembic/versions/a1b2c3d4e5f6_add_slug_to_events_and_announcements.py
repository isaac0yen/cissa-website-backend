"""add slug to events and announcements

Adds a unique, indexed `slug` column to the `events` and `announcements`
tables. Existing rows are backfilled with slugs generated from their titles,
with numeric suffixes to resolve collisions, before the NOT NULL and UNIQUE
constraints are applied. This makes the migration safe to run against a
populated production database.

Revision ID: a1b2c3d4e5f6
Revises: 9caa01a0b6cb
Create Date: 2026-06-08 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.utils.slug import unique_slug_from_seen


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "9caa01a0b6cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _backfill(table: str) -> None:
    """Populate the slug column for all existing rows in `table`."""
    conn = op.get_bind()
    rows = conn.execute(
        sa.text(f"SELECT id, title FROM {table}")
    ).fetchall()

    seen: set[str] = set()
    for row in rows:
        slug = unique_slug_from_seen(row.title, seen)
        conn.execute(
            sa.text(f"UPDATE {table} SET slug = :slug WHERE id = :id"),
            {"slug": slug, "id": row.id},
        )


def upgrade() -> None:
    # 1. add the column as nullable so existing rows don't violate NOT NULL
    op.add_column("events", sa.Column("slug", sa.String(), nullable=True))
    op.add_column("announcements", sa.Column("slug", sa.String(), nullable=True))

    # 2. backfill slugs for existing rows from their titles
    _backfill("events")
    _backfill("announcements")

    # 3. now that every row has a value, enforce NOT NULL + UNIQUE + index
    op.alter_column("events", "slug", existing_type=sa.String(), nullable=False)
    op.create_unique_constraint("uq_events_slug", "events", ["slug"])
    op.create_index(op.f("ix_events_slug"), "events", ["slug"], unique=True)

    op.alter_column(
        "announcements", "slug", existing_type=sa.String(), nullable=False
    )
    op.create_unique_constraint(
        "uq_announcements_slug", "announcements", ["slug"]
    )
    op.create_index(
        op.f("ix_announcements_slug"), "announcements", ["slug"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_announcements_slug"), table_name="announcements")
    op.drop_constraint("uq_announcements_slug", "announcements", type_="unique")
    op.drop_column("announcements", "slug")

    op.drop_index(op.f("ix_events_slug"), table_name="events")
    op.drop_constraint("uq_events_slug", "events", type_="unique")
    op.drop_column("events", "slug")
