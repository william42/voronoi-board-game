"""adds player1_id, player2_id to table.

Revision ID: 5af9bcb11f37
Revises: cee3ba551880
Create Date: 2020-09-20 14:34:03.030078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5af9bcb11f37'
down_revision = 'cee3ba551880'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('games', schema=None) as batch_op:
        batch_op.add_column(sa.Column('player1_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('player2_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_games_player1_id_users'), 'users', ['player1_id'], ['user_id'])
        batch_op.create_foreign_key(batch_op.f('fk_games_player2_id_users'), 'users', ['player2_id'], ['user_id'])


def downgrade():
    with op.batch_alter_table('games', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_games_player2_id_users'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_games_player1_id_users'), type_='foreignkey')
        batch_op.drop_column('player2_id')
        batch_op.drop_column('player1_id')
