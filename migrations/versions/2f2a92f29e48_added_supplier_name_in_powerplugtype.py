"""added-supplier_name-in-powerplugtype

Revision ID: 2f2a92f29e48
Revises: b0fe60bd1a49
Create Date: 2025-05-23 01:51:21.681236

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "2f2a92f29e48"
down_revision: Union[str, None] = "b0fe60bd1a49"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'amperage' column (not nullable)
    op.add_column(
        "powerplugtype",
        sa.Column("supplier_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    )


def downgrade() -> None:
    # Drop 'amperage' column
    op.drop_column("powerplugtype", "supplier_name")
