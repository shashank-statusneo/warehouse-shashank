"""first migration warehouse project

Revision ID: d07aa5347e51
Revises: 
Create Date: 2023-06-07 07:55:40.385923

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd07aa5347e51'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth_user',
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=100), nullable=True),
    sa.Column('mobile_number', sa.String(length=100), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('category',
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('token_block_list',
    sa.Column('jti', sa.String(length=36), nullable=False),
    sa.Column('type', sa.String(length=16), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('token_block_list', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_token_block_list_jti'), ['jti'], unique=False)

    op.create_table('user',
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('department', sa.String(length=100), nullable=True),
    sa.Column('function', sa.String(length=100), nullable=True),
    sa.Column('mobile_number', sa.String(length=13), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('warehouse',
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('input_benchmark_productivity',
    sa.Column('warehouse_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('productivity_experienced_employee', sa.Float(), nullable=False),
    sa.Column('productivity_new_employee', sa.Float(), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('soft_delete_flag', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['auth_user.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['auth_user.id'], ),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouse.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('warehouse_id', 'category_id')
    )
    op.create_table('input_demand',
    sa.Column('warehouse_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('demand', sa.Integer(), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('soft_delete_flag', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['auth_user.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['auth_user.id'], ),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouse.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('warehouse_id', 'category_id', 'date')
    )
    op.create_table('input_requirements',
    sa.Column('warehouse_id', sa.Integer(), nullable=True),
    sa.Column('num_current_employees', sa.Integer(), nullable=False),
    sa.Column('plan_from_date', sa.Date(), nullable=True),
    sa.Column('plan_to_date', sa.Date(), nullable=True),
    sa.Column('percentage_absent_expected', sa.Float(), nullable=False),
    sa.Column('day_working_hours', sa.Integer(), nullable=False),
    sa.Column('cost_per_employee_per_month', sa.Integer(), nullable=False),
    sa.Column('total_hiring_budget', sa.Integer(), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('soft_delete_flag', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['auth_user.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['auth_user.id'], ),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouse.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('input_requirements')
    op.drop_table('input_demand')
    op.drop_table('input_benchmark_productivity')
    op.drop_table('warehouse')
    op.drop_table('user')
    with op.batch_alter_table('token_block_list', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_token_block_list_jti'))

    op.drop_table('token_block_list')
    op.drop_table('category')
    op.drop_table('auth_user')
    # ### end Alembic commands ###
