"""Add category column to assignments."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
import re


revision = "021_add_assignment_category"
down_revision = "020_nullable_assignment_marks"
branch_labels = None
depends_on = None


def _derive_category(assessment: str) -> str:
    derived = re.sub(r"\s*[-_:]*\s*\d+\s*$", "", assessment or "").strip()
    return derived or (assessment or "Assessments")


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("assignments") as batch_op:
            batch_op.add_column(sa.Column("category", sa.String(), nullable=True))
            batch_op.create_index("ix_assignments_category", ["category"], unique=False)
    else:
        op.add_column("assignments", sa.Column("category", sa.String(), nullable=True))
        op.create_index("ix_assignments_category", "assignments", ["category"], unique=False)

    conn = op.get_bind()
    assignments = conn.execute(sa.text("SELECT id, assessment FROM assignments")).fetchall()
    for row in assignments:
        conn.execute(
            sa.text("UPDATE assignments SET category = :category WHERE id = :id"),
            {"id": row.id, "category": _derive_category(row.assessment)},
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("assignments") as batch_op:
            batch_op.drop_index("ix_assignments_category")
            batch_op.drop_column("category")
    else:
        op.drop_index("ix_assignments_category", table_name="assignments")
        op.drop_column("assignments", "category")
