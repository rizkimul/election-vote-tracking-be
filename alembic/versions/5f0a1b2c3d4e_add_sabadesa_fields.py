"""Add SABADESA fields - username, event location, attendee demographics

Revision ID: 5f0a1b2c3d4e
Revises: 4e0ed57666ec
Create Date: 2024-12-22 19:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f0a1b2c3d4e'
down_revision: Union[str, None] = '4e0ed57666ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # User table - add username column
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Make nik nullable for new users using username
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('nik', nullable=True)
    
    # Event table - add kecamatan and desa columns
    op.add_column('events', sa.Column('kecamatan', sa.String(), nullable=True))
    op.add_column('events', sa.Column('desa', sa.String(), nullable=True))
    
    # Make dapil nullable (it's now optional, kecamatan is primary)
    with op.batch_alter_table('events') as batch_op:
        batch_op.alter_column('dapil', nullable=True)
    
    # Attendee table - add new demographic fields
    op.add_column('attendees', sa.Column('identifier_type', sa.String(), server_default='NIK', nullable=True))
    op.add_column('attendees', sa.Column('alamat', sa.String(), nullable=True))
    op.add_column('attendees', sa.Column('jenis_kelamin', sa.String(), nullable=True))
    op.add_column('attendees', sa.Column('pekerjaan', sa.String(), nullable=True))
    op.add_column('attendees', sa.Column('usia', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Attendee table - remove new demographic fields
    op.drop_column('attendees', 'usia')
    op.drop_column('attendees', 'pekerjaan')
    op.drop_column('attendees', 'jenis_kelamin')
    op.drop_column('attendees', 'alamat')
    op.drop_column('attendees', 'identifier_type')
    
    # Event table - restore dapil as required, remove new columns
    with op.batch_alter_table('events') as batch_op:
        batch_op.alter_column('dapil', nullable=False)
    op.drop_column('events', 'desa')
    op.drop_column('events', 'kecamatan')
    
    # User table - restore nik as required, remove username
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('nik', nullable=False)
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'username')
