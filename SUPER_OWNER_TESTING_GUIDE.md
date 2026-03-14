# Super Owner Testing Guide

## Super Owner Credentials

**Email:** `super.owner@example.com`  
**Password:** `superowner123`  
**Role:** `super_owner`  
**User ID:** `34`

## Testing Instructions

### Step 1: Login as Super Owner

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "super.owner@example.com",
  "password": "superowner123"
}
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 34,
    "name": "Super Owner Admin",
    "email": "super.owner@example.com",
    "role": "super_owner",
    "is_active": true
  }
}
```

**Save the `access_token` for subsequent requests.**

### Step 2: Test Hospital Management (Should Work)

Use the JWT token in the Authorization header: `Bearer <access_token>`

#### 1. List All Hospitals
**Endpoint:** `GET /api/admin/hospitals/`

**Expected:** 200 OK with list of hospitals

#### 2. Create New Hospital
**Endpoint:** `POST /api/admin/hospitals/`

**Request Body:**
```json
{
  "name": "Test Super Owner Hospital",
  "email": "test.hospital@example.com",
  "phone": "+1234567890",
  "address": "123 Test Street, Test City"
}
```

**Expected:** 201 Created with new hospital details

#### 3. Get Hospital by ID
**Endpoint:** `GET /api/admin/hospitals/{hospital_id}`

**Expected:** 200 OK with hospital details

#### 4. Update Hospital
**Endpoint:** `PUT /api/admin/hospitals/{hospital_id}`

**Request Body:**
```json
{
  "name": "Updated Hospital Name",
  "email": "updated.hospital@example.com",
  "phone": "+0987654321",
  "address": "456 Updated Address"
}
```

**Expected:** 200 OK with updated hospital details

#### 5. Activate/Deactivate Hospital
**Activate:** `PATCH /api/admin/hospitals/{hospital_id}/activate`  
**Deactivate:** `PATCH /api/admin/hospitals/{hospital_id}/deactivate`

**Expected:** 200 OK with updated status

### Step 3: Test Access Restrictions (Should Be Blocked)

These endpoints should return **403 Forbidden** for Super Owner:

#### 1. Patient Data (Blocked)
**Endpoint:** `GET /api/patients/`  
**Expected:** 403 Forbidden

**Endpoint:** `GET /api/patients/{patient_id}`  
**Expected:** 403 Forbidden

#### 2. Doctor Data (Blocked)
**Endpoint:** `GET /api/doctors/`  
**Expected:** 403 Forbidden

**Endpoint:** `GET /api/doctors/{doctor_id}`  
**Expected:** 403 Forbidden

#### 3. Appointment Data (Blocked)
**Endpoint:** `GET /api/appointments/`  
**Expected:** 403 Forbidden

**Endpoint:** `GET /api/appointments/{appointment_id}`  
**Expected:** 403 Forbidden

#### 4. Medical Records (Blocked)
**Endpoint:** `GET /api/medical-records/`  
**Expected:** 403 Forbidden

**Endpoint:** `GET /api/medical-records/{record_id}`  
**Expected:** 403 Forbidden

## Expected Behavior Summary

### ✅ **Super Owner CAN Access:**
- `/api/admin/hospitals/*` - All hospital management operations
- Hospital CRUD operations
- Hospital activation/deactivation
- Hospital statistics

### ❌ **Super Owner CANNOT Access:**
- `/api/patients/*` - All patient data and PII
- `/api/doctors/*` - All doctor data and PII  
- `/api/appointments/*` - All appointment data
- `/api/medical-records/*` - All medical records

## Testing Tools

### Using curl

```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"super.owner@example.com","password":"superowner123"}'

# Get JWT token from response, then test hospital management
curl -X GET "http://localhost:8000/api/admin/hospitals/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test access restriction (should return 403)
curl -X GET "http://localhost:8000/api/patients/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using Postman

1. Create a new collection for Super Owner testing
2. Add login request to get JWT token
3. Use token in subsequent requests
4. Test both allowed and blocked endpoints

## Verification Checklist

- [ ] Super Owner can login successfully
- [ ] Super Owner can list hospitals
- [ ] Super Owner can create new hospitals
- [ ] Super Owner can update hospitals
- [ ] Super Owner can activate/deactivate hospitals
- [ ] Super Owner CANNOT access patient data (403)
- [ ] Super Owner CANNOT access doctor data (403)
- [ ] Super Owner CANNOT access appointment data (403)
- [ ] Super Owner CANNOT access medical records (403)

## Troubleshooting

### If Login Fails:
- Verify database connection
- Check if Super Owner user exists in database
- Verify password is correct

### If Hospital Endpoints Fail:
- Ensure JWT token is included in Authorization header
- Check if hospital_id is valid
- Verify database permissions

### If Access Restrictions Don't Work:
- Check middleware implementation
- Verify role checking logic
- Ensure endpoints are properly protected

## Security Verification

The Super Owner implementation ensures:
- ✅ **Privacy Protection**: No access to patient, doctor, or medical data
- ✅ **Role Separation**: Clear separation between hospital management and operational data
- ✅ **Access Control**: Proper middleware blocking unauthorized endpoints
- ✅ **Data Isolation**: Super Owner only sees hospital-level information

This implementation successfully provides hospital management capabilities while maintaining strict privacy controls for sensitive healthcare data.