"""update user

Revision ID: 4b167ac20cd5
Revises: 4443661f2bfc
Create Date: 2025-02-05 05:29:11.653511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b167ac20cd5'
down_revision: Union[str, None] = '4443661f2bfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user_external_id', sa.Integer(), nullable=False))
    op.drop_constraint('uq_users_external_id', 'users', type_='unique')
    op.create_unique_constraint(op.f('uq_users_user_external_id'), 'users', ['user_external_id'])
    op.drop_column('users', 'external_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('external_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(op.f('uq_users_user_external_id'), 'users', type_='unique')
    op.create_unique_constraint('uq_users_external_id', 'users', ['external_id'])
    op.drop_column('users', 'user_external_id')
    # ### end Alembic commands ###
