"""Add gpa_scale to courses and seed 7-Point Australian GradeScale rows."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "022_add_course_gpa_scale"
down_revision = "021_add_assignment_category"
branch_labels = None
depends_on = None

_SEVEN_PT_ROWS = [
    ("HD", "High Distinction",    85.0,  7.0),
    ("D",  "Distinction",         75.0,  6.0),
    ("C",  "Credit",              65.0,  5.0),
    ("P",  "Pass",                50.0,  4.0), # Fixed from 50.01 to 50.0
    ("PS", "Pass Supplementary",  50.0,  4.0),
    ("F",  "Fail",                 0.0,  0.0),
]


def upgrade() -> None:
    bind = op.get_bind()
    
    # Use the generic sa.inspect() which natively accepts an active Connection
    inspector = sa.inspect(bind)
    existing_columns = [col["name"] for col in inspector.get_columns("courses")]

    # 1. Add gpa_scale column to courses ONLY if it does not exist
    if "gpa_scale" not in existing_columns:
        if bind.dialect.name == "sqlite":
            with op.batch_alter_table("courses") as batch_op:
                batch_op.add_column(
                    sa.Column("gpa_scale", sa.Integer(), nullable=True, server_default="4")
                )
        else:
            op.add_column(
                "courses",
                sa.Column("gpa_scale", sa.Integer(), nullable=True, server_default="4"),
            )
        print("Successfully added 'gpa_scale' column to 'courses' table.")
    else:
        print("'gpa_scale' column already exists in 'courses' table. Skipping column creation.")

    # Back-fill existing rows to 4 (Standard)
    bind.execute(sa.text("UPDATE courses SET gpa_scale = 4 WHERE gpa_scale IS NULL"))

    # 2. Seed 7-Point Australian GradeScale rows if not present
    existing = bind.execute(
        sa.text("SELECT id FROM grade_scales WHERE scale_name = '7-Point Australian' LIMIT 1")
    ).first()
    if not existing:
        for grade, label, min_mark, gpa_point in _SEVEN_PT_ROWS:
            bind.execute(
                sa.text(
                    "INSERT INTO grade_scales (scale_name, grade, label, min_mark, gpa_point, band_type) "
                    "VALUES (:sn, :g, :l, :mm, :gp, 'both')"
                ),
                {"sn": "7-Point Australian", "g": grade, "l": label, "mm": min_mark, "gp": gpa_point},
            )
        print("Successfully seeded 7-Point Australian GradeScale rows.")
    else:
        print("7-Point Australian scale already seeded. Skipping data insertion.")


def downgrade() -> None:
    bind = op.get_bind()

    # Remove 7-Point Australian scale rows
    bind.execute(
        sa.text("DELETE FROM grade_scales WHERE scale_name = '7-Point Australian'")
    )

    # Remove gpa_scale column
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("courses") as batch_op:
            batch_op.drop_column("gpa_scale")
    else:
        op.drop_column("courses", "gpa_scale")
