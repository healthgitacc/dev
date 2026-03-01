-- PostgreSQL initialization script for hospital database
-- Creates extensions and initial setup

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for cryptographic functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Display success message
SELECT 'Hospital Database Initialization Complete' as status;
