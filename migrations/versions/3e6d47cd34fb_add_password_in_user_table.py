"""Add password in user table

Revision ID: 3e6d47cd34fb
Revises: 0e4c8558d146
Create Date: 2025-05-22 21:54:59.108291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e6d47cd34fb'
down_revision = '0e4c8558d146'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('password')

    # ### end Alembic commands ###
