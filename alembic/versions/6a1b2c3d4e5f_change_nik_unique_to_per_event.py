"""change_nik_unique_to_per_event

Revision ID: 6a1b2c3d4e5f
Revises: 5f0a1b2c3d4e
Create Date: 2025-12-24 00:53:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a1b2c3d4e5f'
down_revision: Union[str, None] = '5f0a1b2c3d4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old unique constraint on nik only (SQLite syntax)
    # Note: SQLite doesn't support DROP CONSTRAINT, need to recreate table
    # For PostgreSQL/MySQL, use:
    # op.drop_constraint('unique_attendee_nik', 'attendees', type_='unique')
    
    # For SQLite, we need to handle differently based on if constraint exists
    # Using batch mode for SQLite compatibility
    with op.batch_alter_table('attendees', schema=None) as batch_op:
        # Try to drop old constraint if exists
        try:
            batch_op.drop_constraint('unique_attendee_nik', type_='unique')
        except:
            pass  # Constraint might not exist
        
        # Add new composite unique constraint
        batch_op.create_unique_constraint('unique_attendee_per_event', ['event_id', 'nik'])


def downgrade() -> None:
    with op.batch_alter_table('attendees', schema=None) as batch_op:
        batch_op.drop_constraint('unique_attendee_per_event', type_='unique')
        batch_op.create_unique_constraint('unique_attendee_nik', ['nik'])
