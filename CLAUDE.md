# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎯 Project Status: 100% Complete

**Backend**: ✅ 100% Complete
**Frontend**: ✅ 100% Complete
**Deployment**: ✅ Ready for Production

### Implemented Features

**Student Portal (7 views)**:
- Login & Authentication
- Dashboard (GPA, credits, enrollments, attendance summary)
- Courses (current enrollments)
- Grades (GPA calculator, graded courses)
- Attendance (records and summaries by section)
- Library (checkouts, history, fines)
- Financial Aid (aid records, totals)

**Faculty Portal (3 views)**:
- Dashboard (sections overview, assignments, student counts)
- Sections (view enrollments, manage attendance)
- Assignments (create/view assignments, grade submissions)

**Shared Views (2 views)**:
- Course Catalog (browse all courses, filter, search, view sections)
- Events (campus events with filters, registration ready)

**Backend APIs (7 apps)**:
- users, academics, assessments, attendance, library, services, facilities
- All CRUD operations + custom actions
- Role-based permissions (student/faculty/staff)
- JWT authentication with token refresh

## Common Development Commands

### Backend (Django REST API)

```bash
# Initial setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure environment variables

# Database setup
python manage.py makemigrations
python manage.py migrate

# Import CSV data (18,331 records)
python manage.py import_data

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver  # http://localhost:8000
```

### Frontend (Vue 3 + Vite)

```bash
cd frontend
npm install
cp .env.example .env  # Configure API URL

# Development server
npm run dev  # http://localhost:5173

# Production build
npm run build
npm run preview
```

### API Documentation
- Swagger UI: http://localhost:8000/api/docs/
- API Schema: http://localhost:8000/api/schema/

## Architecture Overview

### Backend Structure

Django project with **domain-driven app architecture**. Each app follows the pattern:
- `models.py` → Database models
- `serializers.py` → DRF serializers
- `views.py` → API viewsets
- `urls.py` → Route configuration

**Apps:**
- `users/` - Custom User model with role-based profiles (Student, Faculty, Staff)
- `academics/` - Department, Course, Section, Enrollment
- `assessments/` - Assignment, Submission
- `attendance/` - AttendanceRecord
- `library/` - Book, Checkout
- `services/` - FinancialAid, ParkingPermit, Event
- `facilities/` - Building, Room

**Key Configuration:**
- Custom user model: `AUTH_USER_MODEL = 'users.User'`
- Settings module: `config/settings.py`
- Root URL config: `config/urls.py`

### Frontend Structure

Vue 3 SPA with **role-based routing** and **lazy-loaded components**.

**Directory Layout:**
- `src/views/` - Page components organized by role (auth/, student/, faculty/, courses/, events/)
- `src/stores/` - Pinia stores (auth.js, courses.js, student.js)
- `src/services/` - API clients (api.js contains axios instance with interceptors)
- `src/router/` - Vue Router with navigation guards
- `src/components/layout/` - Layout components (Header, Sidebar, Layout)

**Path aliases:**
- `@/` resolves to `src/`

## Authentication & Authorization

### JWT Flow
1. Login: `POST /api/auth/login/` → returns `access` and `refresh` tokens
2. Axios interceptor adds `Bearer {access}` to all requests
3. On 401 error: automatically refresh using `refresh` token
4. New `access` token stored and request retried
5. If refresh fails: redirect to `/login`

**Token Storage:** LocalStorage (`access_token`, `refresh_token`, `user`)

### Role-Based Access

**User Roles:**
- `student` - StudentProfile
- `faculty` - FacultyProfile
- `staff` - StaffProfile

**Router Navigation Guards** (src/router/index.js):
- Check `meta.requiresAuth` and redirect unauthenticated users to `/login`
- Check `meta.roles` array and enforce role-based access
- Auto-redirect authenticated users from `/login` to role-appropriate dashboard

**Default Password (after import_data):** `password123` for all users

## Data Import System

The `import_data` management command imports CSV files from `data/` directory in **dependency order**:

1. Departments, Buildings
2. Rooms (requires Buildings)
3. Students, Faculty, Staff (creates User + Profile)
4. Courses (requires Departments)
5. Sections (requires Courses, Faculty, Rooms)
6. Enrollments (requires Students, Sections)
7. Assignments (requires Sections)
8. Submissions (requires Assignments, Students)
9. Attendance (requires Enrollments)
10. Books, Checkouts, FinancialAid, ParkingPermit, Events

**Total Records:** 18,331 across 17 entity types

**Usage:**
```bash
python manage.py import_data [--data-dir path/to/csvs]
```

## 🚀 Complete Deployment Guide

### Prerequisites
- Render account (for backend + PostgreSQL)
- Vercel account (for frontend)
- GitHub repository (optional but recommended)

---

## Backend Deployment (Render)

### Step 1: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `campus-portal-db`
   - **Database**: `campus_portal`
   - **User**: (auto-generated)
   - **Region**: Choose closest to your users
   - **Plan**: Free or Starter
4. Click "Create Database"
5. **Save the Internal Database URL** (will be used automatically)

### Step 2: Create Web Service

1. In Render Dashboard, click "New +" → "Web Service"
2. Connect your repository OR use "Public Git repository"
3. Configure:
   - **Name**: `campus-portal-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py import_data
     ```
   - **Start Command**:
     ```bash
     gunicorn config.wsgi:application
     ```
   - **Plan**: Free or Starter

4. Add Environment Variables (in "Environment" section):
   ```
   SECRET_KEY=your-super-secret-key-change-this-in-production-min-50-chars
   DEBUG=False
   ALLOWED_HOSTS=campus-portal-backend.onrender.com,localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
   JWT_ACCESS_TOKEN_LIFETIME=5
   JWT_REFRESH_TOKEN_LIFETIME=10080
   DATABASE_URL=[Auto-populated by Render when you link database]
   PYTHON_VERSION=3.11.0
   ```

5. Link PostgreSQL Database:
   - Scroll to "Environment" section
   - Click "Add Environment Variable"
   - Select your PostgreSQL database from dropdown
   - This auto-populates `DATABASE_URL`

6. Click "Create Web Service"

### Step 3: First Deploy

1. Wait for build to complete (5-10 minutes)
2. Check build logs for errors
3. Once deployed, note your backend URL: `https://campus-portal-backend.onrender.com`

### Step 4: Create Superuser (Optional)

1. Go to your web service
2. Click "Shell" tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts to create admin account
5. Access admin panel at: `https://campus-portal-backend.onrender.com/admin/`

### Step 5: Verify Backend

Test API endpoints:
- Health check: `https://campus-portal-backend.onrender.com/api/docs/`
- Should see Swagger UI
- Test login with imported data (email from `data/students.csv`, password: `password123`)

### Step 6: Subsequent Deploys

**IMPORTANT**: After first successful deploy, update Build Command to remove data import:

```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

This prevents duplicate data on every redeploy.

---

## Frontend Deployment (Vercel)

### Step 1: Prepare for Deploy

1. Ensure `VITE_API_BASE_URL` in `.env` points to your Render backend
2. Test locally with production backend:
   ```bash
   cd frontend
   VITE_API_BASE_URL=https://campus-portal-backend.onrender.com npm run dev
   ```

### Step 2: Deploy to Vercel

**Option A: Using Vercel CLI** (Recommended)

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login:
   ```bash
   vercel login
   ```

3. Deploy from frontend directory:
   ```bash
   cd frontend
   vercel
   ```

4. Follow prompts:
   - Setup and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N**
   - Project name? `campus-portal-frontend`
   - Which directory? **./** (current directory)
   - Override settings? **N**

5. Add environment variable:
   ```bash
   vercel env add VITE_API_BASE_URL
   ```
   - Value: `https://campus-portal-backend.onrender.com`
   - Environments: Production, Preview, Development

6. Redeploy with environment variable:
   ```bash
   vercel --prod
   ```

**Option B: Using Vercel Dashboard**

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. Add Environment Variables:
   - Key: `VITE_API_BASE_URL`
   - Value: `https://campus-portal-backend.onrender.com`
   - Environments: ✓ Production ✓ Preview ✓ Development

6. Click "Deploy"

### Step 3: Update Backend CORS

1. Go back to Render dashboard
2. Open your backend web service
3. Update `CORS_ALLOWED_ORIGINS` environment variable:
   ```
   https://campus-portal-frontend.vercel.app,http://localhost:5173
   ```
4. Save and redeploy

### Step 4: Verify Frontend

1. Visit your Vercel URL: `https://campus-portal-frontend.vercel.app`
2. Test login with:
   - Any email from `data/students.csv` or `data/faculty_professors.csv`
   - Password: `password123`
3. Verify all features work (dashboard, courses, grades, etc.)

---

## Custom Domain Setup (Optional)

### Backend Custom Domain (Render)

1. In Render dashboard, go to your web service
2. Click "Settings" → "Custom Domains"
3. Click "Add Custom Domain"
4. Enter your domain: `api.yourcampus.edu`
5. Add CNAME record in your DNS:
   - **Host**: `api`
   - **Value**: `campus-portal-backend.onrender.com`
   - **TTL**: 3600

### Frontend Custom Domain (Vercel)

1. In Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add domain: `portal.yourcampus.edu`
4. Follow Vercel's DNS configuration instructions
5. Update backend CORS to include new domain

---

## Monitoring & Maintenance

### Render Monitoring

- **Logs**: Available in "Logs" tab
- **Metrics**: View CPU, memory, bandwidth in "Metrics" tab
- **Alerts**: Set up in "Settings" → "Alerts"
- **Auto-deploy**: Enable in "Settings" → "Auto-Deploy" for main branch

### Vercel Monitoring

- **Analytics**: Enable in project settings
- **Deployments**: View all deployments and rollback if needed
- **Preview Deployments**: Every PR gets automatic preview URL

### Database Backups (Render PostgreSQL)

1. Go to your PostgreSQL database
2. Click "Backups" tab
3. Enable automatic daily backups
4. Set retention period (7 days minimum)
5. Can manually create backup before major changes

### Performance Optimization

**Backend**:
- Enable Redis caching (upgrade to paid plan)
- Use Render's CDN for static files
- Monitor query performance in Django Debug Toolbar (dev only)

**Frontend**:
- Vercel automatically optimizes images and assets
- Enable Edge Functions for dynamic routes
- Use Vercel Analytics to track performance

---

## Troubleshooting

### Common Backend Issues

**Issue**: Build fails with "No module named..."
- **Solution**: Add missing package to `requirements.txt`

**Issue**: Database connection errors
- **Solution**: Verify `DATABASE_URL` is set and database is running

**Issue**: Static files not loading
- **Solution**: Ensure `collectstatic` runs in build command and `STATIC_ROOT` is configured

**Issue**: CORS errors
- **Solution**: Add frontend URL to `CORS_ALLOWED_ORIGINS`

**Issue**: 502 Bad Gateway
- **Solution**: Check Render logs, may be Gunicorn timeout (default 30s)

### Common Frontend Issues

**Issue**: API calls fail with 404
- **Solution**: Check `VITE_API_BASE_URL` is correctly set

**Issue**: Build fails with "command not found"
- **Solution**: Verify Node.js version and build command

**Issue**: White screen after deployment
- **Solution**: Check browser console for errors, verify base URL in vite.config.js

**Issue**: Authentication not persisting
- **Solution**: Check that tokens are stored in localStorage, verify backend JWT settings

---

## Security Checklist

- [ ] Change `SECRET_KEY` to unique random value (50+ characters)
- [ ] Set `DEBUG=False` in production
- [ ] Limit `ALLOWED_HOSTS` to actual domains
- [ ] Limit `CORS_ALLOWED_ORIGINS` to frontend domains only
- [ ] Use strong passwords for database and admin accounts
- [ ] Enable HTTPS (automatic on Render/Vercel)
- [ ] Regular database backups configured
- [ ] Environment variables not committed to Git
- [ ] Remove `python manage.py import_data` from build after first deploy
- [ ] Update default password (`password123`) for all imported users

---

## Post-Deployment Tasks

1. **Test all user flows**:
   - Student login → view dashboard, grades, attendance
   - Faculty login → view sections, assignments, grade submissions
   - Browse course catalog, events

2. **Change default passwords**:
   - Login as various test users and change passwords
   - OR create script to reset all passwords

3. **Create real superuser**:
   - Run `python manage.py createsuperuser` in Render shell
   - Delete or disable test admin accounts

4. **Set up monitoring**:
   - Configure Render alerts for downtime
   - Enable Vercel analytics
   - Set up error tracking (Sentry optional)

5. **Documentation**:
   - Share URLs with team
   - Document test user accounts
   - Create user guides for students/faculty

---

## URLs Summary

After deployment, you'll have:

- **Backend API**: `https://campus-portal-backend.onrender.com`
- **API Docs**: `https://campus-portal-backend.onrender.com/api/docs/`
- **Frontend**: `https://campus-portal-frontend.vercel.app`
- **Admin Panel**: `https://campus-portal-backend.onrender.com/admin/`

Test Credentials (after import_data):
- Any email from CSV files
- Password: `password123`

---

## Cost Estimates

**Free Tier** (suitable for development/testing):
- Render PostgreSQL Free: $0/month (1GB storage, limited connections)
- Render Web Service Free: $0/month (750 hours/month, sleeps after 15min inactivity)
- Vercel Hobby: $0/month (unlimited sites, 100GB bandwidth)
- **Total**: $0/month

**Production Tier** (recommended for real usage):
- Render PostgreSQL Starter: $7/month (256MB RAM, 1GB storage)
- Render Web Service Starter: $7/month (512MB RAM, always-on)
- Vercel Pro: $20/month (1 user, 1TB bandwidth)
- **Total**: ~$34/month

**Note**: Free tier backend sleeps after 15 minutes of inactivity (50 second cold start)

## Key Implementation Patterns

### Adding a New Django App

1. Create app: `python manage.py startapp apps/new_app`
2. Add to `INSTALLED_APPS` in `config/settings.py`
3. Create models in `apps/new_app/models.py`
4. Create serializers in `apps/new_app/serializers.py`
5. Create viewsets in `apps/new_app/views.py`
6. Create URL router in `apps/new_app/urls.py`
7. Include in `config/urls.py`: `path('api/new_app/', include('apps.new_app.urls'))`
8. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Adding a New Vue View

1. Create component in `src/views/{role}/ComponentName.vue`
2. Add lazy-loaded route in `src/router/index.js`:
```javascript
const ComponentName = () => import('@/views/{role}/ComponentName.vue')

routes.push({
  path: '/path',
  name: 'ComponentName',
  component: ComponentName,
  meta: { requiresAuth: true, roles: ['student'] }
})
```
3. Add navigation link in `src/components/layout/Sidebar.vue` (if needed)

### API Service Pattern

All API calls use the configured axios instance from `src/services/api.js`:

```javascript
import apiClient from './api'

export const getResource = () => apiClient.get('/endpoint/')
export const createResource = (data) => apiClient.post('/endpoint/', data)
```

The interceptor automatically handles authentication and token refresh.
