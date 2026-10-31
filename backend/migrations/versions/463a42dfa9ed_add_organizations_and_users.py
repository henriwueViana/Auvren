
"""add organizations and users

Revision ID: 463a42dfa9ed
Revises: 955e4092e89a
"""

from alembic import op
import sqlalchemy as sa


revision = "463a42dfa9ed"
down_revision = "955e4092e89a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Criar organizações.
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # 2. Criar usuários.
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "organization_id",
            sa.Integer(),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.String(20),
            server_default="agent",
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # 3. Criar índices dos usuários.
    op.create_index(
        "ix_users_organization_id",
        "users",
        ["organization_id"],
    )
    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
    )

    # 4. Adicionar organização aos chamados, inicialmente permitindo NULL.
    op.add_column(
        "tickets",
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )

    # 5. Criar a organização padrão.
    connection = op.get_bind()

    organization_id = connection.execute(
        sa.text(
            """
            INSERT INTO organizations (name)
            VALUES (:name)
            RETURNING id
            """
        ),
        {"name": "Auvren - Organização padrão"},
    ).scalar_one()

    # 6. Associar os chamados existentes à organização padrão.
    connection.execute(
        sa.text(
            """
            UPDATE tickets
            SET organization_id = :organization_id
            WHERE organization_id IS NULL
            """
        ),
        {"organization_id": organization_id},
    )

    # 7. Tornar a associação obrigatória.
    op.alter_column(
        "tickets",
        "organization_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # 8. Criar a chave estrangeira e o índice.
    op.create_foreign_key(
        "fk_tickets_organization_id",
        "tickets",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_tickets_organization_id",
        "tickets",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_tickets_organization_id", table_name="tickets")
    op.drop_constraint(
        "fk_tickets_organization_id",
        "tickets",
        type_="foreignkey",
    )
    op.drop_column("tickets", "organization_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_organization_id", table_name="users")
    op.drop_table("users")

    op.drop_table("organizations")
