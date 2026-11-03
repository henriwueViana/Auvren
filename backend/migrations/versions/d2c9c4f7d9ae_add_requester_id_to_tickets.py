"""add requester id to tickets

Revision ID: d2c9c4f7d9ae
Revises: faf19f004bca
Create Date: 2026-11-03 04:58:33.096666
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d2c9c4f7d9ae"
down_revision: Union[str, Sequence[str], None] = "faf19f004bca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column(
            "requester_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_tickets_requester_id",
        "tickets",
        ["requester_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_tickets_requester_id_users",
        "tickets",
        "users",
        ["requester_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_tickets_requester_id_users",
        "tickets",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_tickets_requester_id",
        table_name="tickets",
    )

    op.drop_column(
        "tickets",
        "requester_id",
    )