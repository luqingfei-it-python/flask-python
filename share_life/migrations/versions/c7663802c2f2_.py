"""empty message

Revision ID: c7663802c2f2
Revises: 76008cb6e33d
Create Date: 2019-04-29 16:55:52.486838

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c7663802c2f2'
down_revision = '76008cb6e33d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sl_replay_info')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sl_replay_info',
    sa.Column('create_time', mysql.DATETIME(), nullable=True),
    sa.Column('update_time', mysql.DATETIME(), nullable=True),
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('comment_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('replay_type', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('content', mysql.VARCHAR(length=1024), nullable=True),
    sa.Column('from_user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('to_user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['comment_id'], ['sl_comment_info.id'], name='sl_replay_info_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
