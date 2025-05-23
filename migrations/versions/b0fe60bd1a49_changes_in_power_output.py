"""changes_in_power_output

Revision ID: b0fe60bd1a49
Revises: 1973ed1b1a56
Create Date: 2025-05-23 01:21:26.364898

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "b0fe60bd1a49"
down_revision: Union[str, None] = "1973ed1b1a56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'amperage' column (not nullable)
    op.add_column("poweroutput", sa.Column("amperage", sa.Integer(), nullable=False))
    # Alter 'charging_speed' to be nullable
    op.alter_column(
        "poweroutput",
        "charging_speed",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=True,
    )


def downgrade() -> None:
    # Drop 'amperage' column
    op.drop_column("poweroutput", "amperage")
    # Alter 'charging_speed' to be NOT NULL
    op.alter_column(
        "poweroutput",
        "charging_speed",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=False,
    )
