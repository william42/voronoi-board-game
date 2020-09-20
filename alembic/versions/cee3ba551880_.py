"""Creates the basic user system.

Revision ID: cee3ba551880
Revises: 
Create Date: 2020-09-19 17:03:37.354440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cee3ba551880'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('user_extra_data_json', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )


def downgrade():
    op.drop_table('users')
