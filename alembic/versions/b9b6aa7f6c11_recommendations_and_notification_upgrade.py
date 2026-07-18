"""recommendations and notification upgrade

Revision ID: b9b6aa7f6c11
Revises: 8f4c3deebaa2
Create Date: 2026-07-13

"""
# pylint: skip-file
# pyright: reportMissingImports=false, reportAttributeAccessIssue=false

from typing import Sequence, Union

import alembic.op as op
import sqlalchemy as sa


revision: str = "b9b6aa7f6c11"
down_revision: Union[str, Sequence[str], None] = "71486b3bf5e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("recommendations"):
        op.create_table(
            "recommendations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("lore_id", sa.Integer(), nullable=False),
            sa.Column("score", sa.Float(), nullable=False),
            sa.Column("reason", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["lore_id"], ["lore.id"]),
        )
        op.create_index("ix_recommendations_id", "recommendations", ["id"])
        op.create_index("ix_recommendations_user_id", "recommendations", ["user_id"])
        op.create_index("ix_recommendations_lore_id", "recommendations", ["lore_id"])

    notification_columns = {column["name"] for column in inspector.get_columns("notifications")}

    if "recipient_id" not in notification_columns:
        op.add_column("notifications", sa.Column("recipient_id", sa.Integer(), nullable=True))
    if "actor_id" not in notification_columns:
        op.add_column("notifications", sa.Column("actor_id", sa.Integer(), nullable=True))
    if "lore_id" not in notification_columns:
        op.add_column("notifications", sa.Column("lore_id", sa.Integer(), nullable=True))
    if "comment_id" not in notification_columns:
        op.add_column("notifications", sa.Column("comment_id", sa.Integer(), nullable=True))
    if "type" not in notification_columns:
        op.add_column("notifications", sa.Column("type", sa.String(length=50), nullable=True))

    op.execute(
        "UPDATE notifications SET recipient_id = COALESCE(recipient_id, user_id) WHERE user_id IS NOT NULL"
    )
    op.execute(
        "UPDATE notifications SET type = COALESCE(type, 'SYSTEM')"
    )

    op.alter_column("notifications", "recipient_id", nullable=False)
    op.alter_column("notifications", "type", nullable=False)

    existing_indexes = {index["name"] for index in inspector.get_indexes("notifications")}
    if "ix_notifications_recipient_id" not in existing_indexes:
        op.create_index("ix_notifications_recipient_id", "notifications", ["recipient_id"])
    if "ix_notifications_actor_id" not in existing_indexes:
        op.create_index("ix_notifications_actor_id", "notifications", ["actor_id"])
    if "ix_notifications_lore_id" not in existing_indexes:
        op.create_index("ix_notifications_lore_id", "notifications", ["lore_id"])
    if "ix_notifications_comment_id" not in existing_indexes:
        op.create_index("ix_notifications_comment_id", "notifications", ["comment_id"])

    existing_fks = {fk["name"] for fk in inspector.get_foreign_keys("notifications")}
    if "fk_notifications_recipient_id_users" not in existing_fks:
        op.create_foreign_key(
            "fk_notifications_recipient_id_users",
            "notifications",
            "users",
            ["recipient_id"],
            ["id"],
        )
    if "fk_notifications_actor_id_users" not in existing_fks:
        op.create_foreign_key(
            "fk_notifications_actor_id_users",
            "notifications",
            "users",
            ["actor_id"],
            ["id"],
        )
    if "fk_notifications_lore_id_lore" not in existing_fks:
        op.create_foreign_key(
            "fk_notifications_lore_id_lore",
            "notifications",
            "lore",
            ["lore_id"],
            ["id"],
        )
    if "fk_notifications_comment_id_comments" not in existing_fks:
        op.create_foreign_key(
            "fk_notifications_comment_id_comments",
            "notifications",
            "comments",
            ["comment_id"],
            ["id"],
        )


def downgrade() -> None:
    op.drop_index("ix_notifications_comment_id", table_name="notifications")
    op.drop_index("ix_notifications_lore_id", table_name="notifications")
    op.drop_index("ix_notifications_actor_id", table_name="notifications")
    op.drop_index("ix_notifications_recipient_id", table_name="notifications")

    op.drop_constraint("fk_notifications_comment_id_comments", "notifications", type_="foreignkey")
    op.drop_constraint("fk_notifications_lore_id_lore", "notifications", type_="foreignkey")
    op.drop_constraint("fk_notifications_actor_id_users", "notifications", type_="foreignkey")
    op.drop_constraint("fk_notifications_recipient_id_users", "notifications", type_="foreignkey")

    op.drop_column("notifications", "type")
    op.drop_column("notifications", "comment_id")
    op.drop_column("notifications", "lore_id")
    op.drop_column("notifications", "actor_id")
    op.drop_column("notifications", "recipient_id")

    op.drop_index("ix_recommendations_lore_id", table_name="recommendations")
    op.drop_index("ix_recommendations_user_id", table_name="recommendations")
    op.drop_index("ix_recommendations_id", table_name="recommendations")
    op.drop_table("recommendations")