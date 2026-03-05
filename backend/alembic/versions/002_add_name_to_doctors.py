"""Add name column to doctors table

Revision ID: 002_add_name_to_doctors
Revises: 001_initial
Create Date: 2026-03-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_name_to_doctors'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add name column to doctors table and migrate data from users table."""
    # Add name column (nullable initially to allow constraint creation)
    op.add_column('doctors', sa.Column('name', sa.String(255), nullable=True))
    
    # Populate doctor names from users table
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE doctors
        SET name = users.name
        FROM users
        WHERE doctors.user_id = users.id
    """))
    
    # Make name column NOT NULL after populating
    op.alter_column('doctors', 'name', nullable=False)
    
    # Create index on name if needed
    op.create_index('idx_doctors_name', 'doctors', ['name'])


def downgrade() -> None:
    """Remove name column from doctors table."""
    op.drop_index('idx_doctors_name', table_name='doctors')
    op.drop_column('doctors', 'name')
