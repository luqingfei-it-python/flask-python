"""add trade_no

Revision ID: 32d0fe0ddabd
Revises: b2288b5807dd
Create Date: 2019-03-20 21:24:55.344949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32d0fe0ddabd'
down_revision = 'b2288b5807dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ih_order_info', sa.Column('trade_no', sa.String(length=80), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ih_order_info', 'trade_no')
    # ### end Alembic commands ###