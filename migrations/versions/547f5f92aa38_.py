"""empty message

Revision ID: 547f5f92aa38
Revises: 8d2ee79de635
Create Date: 2020-09-02 09:53:04.294684

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '547f5f92aa38'
down_revision = '8d2ee79de635'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ih_orders', sa.Column('status', sa.Enum('WAIT_ACCEPT', 'WAIT_PAYMENT', 'PAID', 'WAIT_COMMENT', 'COMPLETED', 'CANCELLED', 'REJECTED'), nullable=True))
    op.create_index(op.f('ix_ih_orders_status'), 'ih_orders', ['status'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_ih_orders_status'), table_name='ih_orders')
    op.drop_column('ih_orders', 'status')
    # ### end Alembic commands ###