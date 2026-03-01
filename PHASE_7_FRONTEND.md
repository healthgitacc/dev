# Phase 7: Frontend Development - Hospital Management System

## Phase 7 Objectives

**Goal:** Build a complete, production-ready Next.js frontend with authentication, role-based dashboards, appointment management, medical records, and user management.

**Status:** 🚀 IN PROGRESS

---

## Project Structure - Frontend

```
frontend/
├── app/
│   ├── layout.tsx                      # Root layout
│   ├── providers.tsx                   # Client providers
│   ├── globals.css                     # Global styles
│   ├── (auth)/                         # Auth routes group
│   │   ├── layout.tsx
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── forgot-password/page.tsx
│   ├── (protected)/                    # Protected routes group
│   │   ├── layout.tsx                  # Navigation layout
│   │   ├── dashboard/page.tsx          # Role-based dashboard
│   │   ├── profile/page.tsx            # User profile
│   │   ├── change-password/page.tsx
│   │   ├── appointments/
│   │   │   ├── page.tsx               # List appointments
│   │   │   ├── create/page.tsx        # Create appointment
│   │   │   ├── [id]/page.tsx          # View appointment
│   │   │   └── [id]/reschedule/page.tsx
│   │   ├── medical-records/
│   │   │   ├── page.tsx               # List records
│   │   │   ├── [id]/page.tsx          # View record
│   │   │   └── create/page.tsx        # Create record
│   │   ├── doctors/
│   │   │   ├── page.tsx               # List doctors (for patients)
│   │   │   ├── [id]/page.tsx          # View doctor profile
│   │   │   └── profile/page.tsx       # Doctor edit profile
│   │   ├── patients/
│   │   │   ├── page.tsx               # List patients (for doctors/admin)
│   │   │   ├── [id]/page.tsx          # View patient details
│   │   │   └── [id]/records/page.tsx  # Patient's medical records
│   │   ├── users/
│   │   │   ├── page.tsx               # User management (admin only)
│   │   │   └── [id]/page.tsx          # User details (admin only)
│   │   └── admin/
│   │       ├── page.tsx               # Admin dashboard
│   │       ├── appointments/page.tsx  # Manage all appointments
│   │       ├── reports/page.tsx       # System reports
│   │       └── settings/page.tsx      # System settings
│   └── error.tsx                       # Error page
├── components/
│   ├── common/
│   │   ├── Header.tsx                 # Top navigation
│   │   ├── Sidebar.tsx                # Left sidebar
│   │   ├── Footer.tsx                 # Footer
│   │   ├── LoadingSpinner.tsx         # Loading indicator
│   │   ├── ErrorAlert.tsx             # Error message
│   │   ├── SuccessAlert.tsx           # Success message
│   │   └── Modal.tsx                  # Modal dialog
│   ├── forms/
│   │   ├── LoginForm.tsx              # Login form
│   │   ├── RegisterForm.tsx           # Registration form
│   │   ├── ChangePasswordForm.tsx     # Password change form
│   │   ├── AppointmentForm.tsx        # Create/edit appointment
│   │   ├── MedicalRecordForm.tsx      # Create/edit medical record
│   │   ├── ProfileForm.tsx            # User profile edit form
│   │   └── FilterBar.tsx              # Search/filter component
│   ├── tables/
│   │   ├── AppointmentTable.tsx       # Appointments list
│   │   ├── PatientTable.tsx           # Patients list
│   │   ├── DoctorTable.tsx            # Doctors list
│   │   ├── MedicalRecordTable.tsx     # Medical records list
│   │   └── UserTable.tsx              # Users list (admin)
│   ├── cards/
│   │   ├── AppointmentCard.tsx        # Single appointment
│   │   ├── PatientCard.tsx            # Single patient
│   │   ├── DoctorCard.tsx             # Single doctor
│   │   ├── StatCard.tsx               # Dashboard stat card
│   │   └── AppointmentStatusCard.tsx  # Status display
│   ├── auth/
│   │   ├── ProtectedRoute.tsx         # Route protection
│   │   ├── RoleGuard.tsx              # Role-based access
│   │   └── AuthCheck.tsx              # Auth status check
│   └── dashboard/
│       ├── AdminDashboard.tsx         # Admin overview
│       ├── DoctorDashboard.tsx        # Doctor overview
│       ├── PatientDashboard.tsx       # Patient overview
│       ├── UpcomingAppointments.tsx   # Appointments widget
│       ├── StatisticsBanner.tsx       # Statistics
│       └── QuickActions.tsx           # Quick action buttons
├── lib/
│   ├── api.ts                         # Axios client
│   ├── auth-store.ts                  # Zustand auth store
│   ├── hooks.ts                       # Custom React hooks
│   ├── utils.ts                       # Utility functions
│   ├── constants.ts                   # Constants & config
│   ├── types.ts                       # TypeScript types
│   └── validation.ts                  # Zod schemas
├── middleware.ts                      # Next.js middleware
├── .env.example
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## Phase 7 Implementation Roadmap

### Step 1: Core Infrastructure Setup ✅ DONE
- ✅ Next.js 14 with App Router
- ✅ TailwindCSS configuration
- ✅ TypeScript setup
- ✅ Zustand auth store
- ✅ Axios API client

### Step 2: Types & Validation
**Files to create:**
- `lib/types.ts` - TypeScript interfaces
- `lib/constants.ts` - Global constants
- `lib/validation.ts` - Zod validation schemas

**Tasks:**
- Define all data types (User, Appointment, MedicalRecord, etc.)
- Create validation schemas for forms
- Set up constants for API endpoints, roles, statuses

### Step 3: Authentication Pages
**Files to create:**
- `app/(auth)/layout.tsx` - Auth layout
- `app/(auth)/login/page.tsx` - Login page
- `app/(auth)/register/page.tsx` - Register page
- `app/(auth)/forgot-password/page.tsx` - Forgot password
- `components/forms/LoginForm.tsx`
- `components/forms/RegisterForm.tsx`

**Tasks:**
- Build login/register forms with validation
- Integrate with backend auth endpoints
- Handle token storage and auth state
- Create forgot password flow

### Step 4: Common Components
**Files to create:**
- `components/common/Header.tsx` - Top navbar
- `components/common/Sidebar.tsx` - Navigation sidebar
- `components/common/Footer.tsx` - Footer
- `components/common/LoadingSpinner.tsx`
- `components/common/ErrorAlert.tsx`
- `components/common/SuccessAlert.tsx`
- `components/common/Modal.tsx`

**Tasks:**
- Responsive navigation
- Role-based menu items
- Alert components for feedback

### Step 5: Protected Routes & Middleware
**Files to create:**
- `middleware.ts` - Route protection middleware
- `components/auth/ProtectedRoute.tsx`
- `components/auth/RoleGuard.tsx`

**Tasks:**
- Implement route guards
- Handle redirects to login
- Enforce role-based access

### Step 6: Dashboard Pages
**Files to create:**
- `app/(protected)/layout.tsx` - Protected layout with nav
- `app/(protected)/dashboard/page.tsx` - Main dashboard
- `components/dashboard/AdminDashboard.tsx`
- `components/dashboard/DoctorDashboard.tsx`
- `components/dashboard/PatientDashboard.tsx`

**Tasks:**
- Build role-specific dashboards
- Display statistics and widgets
- Quick action buttons

### Step 7: User Profile & Settings
**Files to create:**
- `app/(protected)/profile/page.tsx`
- `app/(protected)/change-password/page.tsx`
- `components/forms/ProfileForm.tsx`
- `components/forms/ChangePasswordForm.tsx`

**Tasks:**
- Profile viewing and editing
- Password change with validation
- Profile image upload (optional)

### Step 8: Appointment Management
**Files to create:**
- `app/(protected)/appointments/page.tsx`
- `app/(protected)/appointments/create/page.tsx`
- `app/(protected)/appointments/[id]/page.tsx`
- `app/(protected)/appointments/[id]/reschedule/page.tsx`
- `components/forms/AppointmentForm.tsx`
- `components/tables/AppointmentTable.tsx`
- `components/cards/AppointmentCard.tsx`

**Tasks:**
- List appointments with filtering
- Create new appointments
- View appointment details
- Reschedule appointments
- Cancel appointments
- Display conflict warnings

### Step 9: Medical Records
**Files to create:**
- `app/(protected)/medical-records/page.tsx`
- `app/(protected)/medical-records/create/page.tsx`
- `app/(protected)/medical-records/[id]/page.tsx`
- `components/forms/MedicalRecordForm.tsx`
- `components/tables/MedicalRecordTable.tsx`

**Tasks:**
- List medical records
- Create/edit records
- View record details
- Filter by patient/date

### Step 10: Doctor Management
**Files to create:**
- `app/(protected)/doctors/page.tsx`
- `app/(protected)/doctors/[id]/page.tsx`
- `app/(protected)/doctors/profile/page.tsx`
- `components/tables/DoctorTable.tsx`
- `components/cards/DoctorCard.tsx`

**Tasks:**
- List doctors with specialization filter
- View doctor profiles
- Doctor edit their profile

### Step 11: Patient Management
**Files to create:**
- `app/(protected)/patients/page.tsx`
- `app/(protected)/patients/[id]/page.tsx`
- `app/(protected)/patients/[id]/records/page.tsx`
- `components/tables/PatientTable.tsx`
- `components/cards/PatientCard.tsx`

**Tasks:**
- List patients (for doctors/admin)
- View patient details
- View patient medical records
- Search and filter

### Step 12: Admin Section
**Files to create:**
- `app/(protected)/admin/page.tsx` - Admin dashboard
- `app/(protected)/admin/appointments/page.tsx` - Manage appointments
- `app/(protected)/admin/reports/page.tsx` - System reports
- `app/(protected)/admin/settings/page.tsx` - Settings
- `app/(protected)/users/page.tsx` - User management
- `components/tables/UserTable.tsx`

**Tasks:**
- System statistics and reports
- User management (activate/deactivate)
- System settings
- Appointment management

### Step 13: Testing & Deployment
**Tasks:**
- Test all pages and flows
- Verify API integration
- Responsive design testing
- Build and deployment setup

---

## Technology Stack - Frontend

```
Next.js 14             App Router, SSR, Optimization
React 18              UI components, hooks
TypeScript 5.3        Type safety
TailwindCSS 3.3       Styling
Zustand 4.4           State management
React Hook Form 7.48  Form handling
Zod 3.22              Validation
Axios 1.6             HTTP client
js-cookie 3.0         Cookie management
date-fns 2.30         Date utilities
@heroicons 2.0        UI icons
```

---

## API Integration

### Authentication Endpoints
```
POST   /api/auth/register          # Register new user
POST   /api/auth/login             # Login user
POST   /api/auth/change-password   # Change password
GET    /api/auth/me                # Get current user
```

### User Endpoints
```
GET    /api/users                  # List users (admin)
GET    /api/users/{id}             # Get user details
PUT    /api/users/{id}             # Update user
DELETE /api/users/{id}             # Delete user (soft delete)
POST   /api/users/{id}/activate    # Activate user (admin)
POST   /api/users/{id}/deactivate  # Deactivate user (admin)
GET    /api/users/stats            # Get statistics
```

### Doctor Endpoints
```
GET    /api/doctors                # List doctors
GET    /api/doctors/{id}           # Get doctor details
PUT    /api/doctors/{id}           # Update doctor profile
GET    /api/doctors/specialization/{spec}  # Filter by specialization
```

### Patient Endpoints
```
GET    /api/patients               # List patients
GET    /api/patients/{id}          # Get patient details
PUT    /api/patients/{id}          # Update patient profile
GET    /api/patients/blood-group/{bg}  # Filter by blood group
GET    /api/patients/gender/{gender}   # Filter by gender
```

### Appointment Endpoints
```
GET    /api/appointments           # List appointments
POST   /api/appointments           # Create appointment
GET    /api/appointments/{id}      # Get appointment details
PATCH  /api/appointments/{id}      # Update appointment (status, time)
POST   /api/appointments/{id}/reschedule  # Reschedule appointment
DELETE /api/appointments/{id}      # Cancel appointment
GET    /api/appointments/reminders # Get reminders
```

### Medical Records Endpoints
```
GET    /api/medical-records        # List records
POST   /api/medical-records        # Create record
GET    /api/medical-records/{id}   # Get record details
PUT    /api/medical-records/{id}   # Update record
DELETE /api/medical-records/{id}   # Delete record
```

---

## Development Commands

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build
npm run build

# Start production
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## Environment Configuration

**`.env.local`**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Hospital Management System
```

---

## Key Features to Implement

### Authentication
- ✅ JWT token-based auth
- ✅ Login/Register flows
- ✅ Password management
- ✅ Protected routes
- ✅ Auto-logout on token expiry

### Role-Based Access Control
- ✅ Admin dashboard & management
- ✅ Doctor scheduler & patient management
- ✅ Patient appointment booking & records view

### Appointment Management
- ✅ List/filter appointments
- ✅ Create with doctor/time selection
- ✅ Reschedule functionality
- ✅ Cancel with confirmation
- ✅ View appointment details

### Medical Records
- ✅ Create new records
- ✅ View/edit records
- ✅ Filter by patient/date
- ✅ Search functionality

### User Management (Admin)
- ✅ List all users
- ✅ Activate/deactivate users
- ✅ View user details
- ✅ Filter by role

### Dashboard Widgets
- ✅ Upcoming appointments
- ✅ System statistics
- ✅ Quick actions
- ✅ Recent activities

---

## Testing Checklist

- [ ] Authentication flows work correctly
- [ ] Protected routes redirect to login
- [ ] Role-based access enforced
- [ ] All forms validate properly
- [ ] API integration working
- [ ] Modal dialogs function correctly
- [ ] Responsive design on mobile/tablet/desktop
- [ ] Loading states display correctly
- [ ] Error messages clear and helpful
- [ ] Success messages show after actions
- [ ] Pagination works correctly
- [ ] Filters and search functional

---

## Next Steps

1. ✅ Create Phase 7 documentation (THIS FILE)
2. ⏳ Create types and constants
3. ⏳ Create validation schemas
4. ⏳ Build authentication UI (login/register)
5. ⏳ Build navigation and layouts
6. ⏳ Build protected routes middleware
7. ⏳ Build dashboard pages
8. ⏳ Build appointment management
9. ⏳ Build medical records
10. ⏳ Build user management
11. ⏳ Full integration testing
12. ⏳ Deployment preparation

---

**Started:** February 24, 2026  
**Backend Ready:** Phase 6 Complete ✅  
**Frontend Status:** 🚀 In Development  
