-- Fix doctor sequence issue by manually setting it to the correct value

-- Step 1: Find the next available ID
WITH existing_ids AS (
    SELECT id FROM doctors
    UNION
    SELECT id FROM users
),
max_id AS (
    SELECT COALESCE(MAX(id), 0) as max_existing FROM existing_ids
),
next_available AS (
    SELECT max_existing + 1 as next_id FROM max_id
)
SELECT next_id FROM next_available;

-- Step 2: Reset the sequence to the next available ID
SELECT setval('doctors_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM doctors), false);

-- Step 3: Verify the fix
SELECT 'doctors sequence reset to: ' || currval('doctors_id_seq');

-- Step 4: Test by inserting a test doctor
INSERT INTO doctors (user_id, name, specialization, experience_years, license_number, created_at, updated_at)
VALUES (999, 'Test Doctor', 'Test Specialization', 1, 'TEST123', NOW(), NOW());

-- Step 5: Clean up the test doctor
DELETE FROM doctors WHERE name = 'Test Doctor' AND license_number = 'TEST123';

-- Step 6: Final verification
SELECT 'Next doctor ID will be: ' || nextval('doctors_id_seq');