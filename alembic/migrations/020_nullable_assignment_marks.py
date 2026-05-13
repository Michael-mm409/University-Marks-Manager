"""Make assignment marks nullable and clear zero placeholders outside course 1.

If you are using a real Alembic setup, place this file under the configured
versions directory and make sure `down_revision` matches your latest revision.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# Alembic identifiers. Update down_revision to match your local revision chain if needed.
revision = "020_nullable_assignment_marks"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("assignments") as batch_op:
            batch_op.alter_column(
                "weighted_mark",
                existing_type=sa.Float(),
                nullable=True,
                existing_server_default=None,
            )
            batch_op.alter_column(
                "unweighted_mark",
                existing_type=sa.Float(),
                nullable=True,
                existing_server_default=None,
            )
    else:
        op.alter_column(
            "assignments",
            "weighted_mark",
            existing_type=sa.Float(),
            nullable=True,
            server_default=None,
        )
        op.alter_column(
            "assignments",
            "unweighted_mark",
            existing_type=sa.Float(),
            nullable=True,
            server_default=None,
        )
    op.execute(
        """
        UPDATE assignments
        SET weighted_mark = NULL,
            unweighted_mark = NULL
        WHERE unweighted_mark = 0
          AND subject_id IN (
              SELECT s.id
              FROM subjects AS s
              JOIN semesters AS sem ON sem.id = s.semester_id
              WHERE sem.course_id != 1
          )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE assignments
        SET weighted_mark = 0,
            unweighted_mark = 0
        WHERE weighted_mark IS NULL
           OR unweighted_mark IS NULL
        """
    )
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("assignments") as batch_op:
            batch_op.alter_column(
                "unweighted_mark",
                existing_type=sa.Float(),
                nullable=False,
                existing_server_default=None,
                server_default=sa.text("0"),
            )
            batch_op.alter_column(
                "weighted_mark",
                existing_type=sa.Float(),
                nullable=False,
                existing_server_default=None,
                server_default=sa.text("0"),
            )
    else:
        op.alter_column(
            "assignments",
            "unweighted_mark",
            existing_type=sa.Float(),
            nullable=False,
            server_default=sa.text("0"),
        )
        op.alter_column(
            "assignments",
            "weighted_mark",
            existing_type=sa.Float(),
            nullable=False,
            server_default=sa.text("0"),
        )
