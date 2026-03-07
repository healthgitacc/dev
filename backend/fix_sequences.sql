-- Fix PostgreSQL sequences for doctors and users tables
-- This prevents duplicate key errors when inserting new records

-- Reset doctors sequence
SELECT setval('doctors_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM doctors));

-- Reset users sequence  
SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM users));

-- Verify the sequences are fixed
SELECT 'doctors sequence reset to: ' || nextval('doctors_id_seq') - 1;
SELECT 'users sequence reset to: ' || nextval('users_id_seq') - 1;