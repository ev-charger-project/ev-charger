"""modified-powerplugtype-supplier_name-nullable

Revision ID: 828227da6f9d
Revises: 8a7604c47b94
Create Date: 2025-06-13 06:38:05.718245

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "828227da6f9d"
down_revision: Union[str, None] = "8a7604c47b94"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "powerplugtype",
        "supplier_name",
        existing_type=sa.String(),
        nullable=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "powerplugtype",
        "supplier_name",
        existing_type=sa.String(),
        nullable=False,
    )
    # ### end Alembic commands ###
