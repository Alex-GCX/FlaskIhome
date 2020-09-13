"""empty message

Revision ID: 21d5f9cad4ac
Revises: 75639e57b527
Create Date: 2020-08-31 23:07:40.078215

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '21d5f9cad4ac'
down_revision = '75639e57b527'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ih_orders', 'order_num',
               existing_type=mysql.VARCHAR(length=30),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ih_orders', 'order_num',
               existing_type=mysql.VARCHAR(length=30),
               nullable=False)
    # ### end Alembic commands ###
