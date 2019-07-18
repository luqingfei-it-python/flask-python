"""empty message

Revision ID: 7bd9ee31140d
Revises: 0e4649017bf9
Create Date: 2019-04-27 21:14:42.566990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bd9ee31140d'
down_revision = '0e4649017bf9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sl_good_info', sa.Column('status', sa.String(length=32), server_default='false', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sl_good_info', 'status')
    # ### end Alembic commands ###