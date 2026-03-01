"""Initial migration - Create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    userRole = postgresql.ENUM('admin', 'doctor', 'patient', name='userrole')
    userRole.create(op.get_bind(), checkfirst=True)
    
    appointmentStatus = postgresql.ENUM('scheduled', 'completed', 'cancelled', 'no_show', 'rescheduled', name='appointmentstatus')
    appointmentStatus.create(op.get_bind(), checkfirst=True)
    
    gender = postgresql.ENUM('male', 'female', 'other', name='gender')
    gender.create(op.get_bind(), checkfirst=True)
    
    bloodGroup = postgresql.ENUM('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', name='bloodgroup')
    bloodGroup.create(op.get_bind(), checkfirst=True)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', userRole, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Create doctors table
    op.create_table(
        'doctors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('specialization', sa.String(length=255), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=False),
        sa.Column('license_number', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('idx_doctors_user_id', 'doctors', ['user_id'])
    op.create_index('idx_doctors_specialization', 'doctors', ['specialization'])
    op.create_index('idx_doctors_license_number', 'doctors', ['license_number'])
    
    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', gender, nullable=True),
        sa.Column('blood_group', bloodGroup, nullable=True),
        sa.Column('medical_history', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('idx_patients_user_id', 'patients', ['user_id'])
    op.create_index('idx_patients_gender', 'patients', ['gender'])
    
    # Create appointments table
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('appointment_date', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('status', appointmentStatus, nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reminder_sent', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_appointments_doctor_id', 'appointments', ['doctor_id'])
    op.create_index('idx_appointments_patient_id', 'appointments', ['patient_id'])
    op.create_index('idx_appointments_date', 'appointments', ['appointment_date'])
    op.create_index('idx_appointments_status', 'appointments', ['status'])
    op.create_index('idx_appointments_doctor_date', 'appointments', ['doctor_id', 'appointment_date'])
    
    # Create medical_records table
    op.create_table(
        'medical_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=True),
        sa.Column('disease_name', sa.String(length=255), nullable=False),
        sa.Column('diagnosis', sa.Text(), nullable=False),
        sa.Column('prescription_text', sa.Text(), nullable=True),
        sa.Column('dosage', sa.String(length=255), nullable=True),
        sa.Column('follow_up_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_medical_records_patient_id', 'medical_records', ['patient_id'])
    op.create_index('idx_medical_records_doctor_id', 'medical_records', ['doctor_id'])
    op.create_index('idx_medical_records_created_at', 'medical_records', ['created_at'])
    op.create_index('idx_medical_records_follow_up_date', 'medical_records', ['follow_up_date'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_medical_records_follow_up_date', table_name='medical_records')
    op.drop_index('idx_medical_records_created_at', table_name='medical_records')
    op.drop_index('idx_medical_records_doctor_id', table_name='medical_records')
    op.drop_index('idx_medical_records_patient_id', table_name='medical_records')
    op.drop_table('medical_records')
    
    op.drop_index('idx_appointments_doctor_date', table_name='appointments')
    op.drop_index('idx_appointments_status', table_name='appointments')
    op.drop_index('idx_appointments_date', table_name='appointments')
    op.drop_index('idx_appointments_patient_id', table_name='appointments')
    op.drop_index('idx_appointments_doctor_id', table_name='appointments')
    op.drop_table('appointments')
    
    op.drop_index('idx_patients_gender', table_name='patients')
    op.drop_index('idx_patients_user_id', table_name='patients')
    op.drop_table('patients')
    
    op.drop_index('idx_doctors_license_number', table_name='doctors')
    op.drop_index('idx_doctors_specialization', table_name='doctors')
    op.drop_index('idx_doctors_user_id', table_name='doctors')
    op.drop_table('doctors')
    
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
    
    # Drop enum types
    sa.Enum(name='bloodgroup').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='gender').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='appointmentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
