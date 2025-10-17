# University Portal Backend

Django REST API for university student and faculty portal system.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Import Data from CSV

```bash
python manage.py import_data
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/api/docs/`
- Schema: `http://localhost:8000/api/schema/`

## Default Login Credentials

After importing data, all users have the default password: `password123`

Example logins:
- Students: Use any email from `students.csv`
- Faculty: Use any email from `faculty_professors.csv`
- Staff: Use any email from `staff.csv`

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Obtain JWT token
- `POST /api/auth/refresh/` - Refresh JWT token

### Users
- `GET /api/users/` - User endpoints

### Academics
- `GET /api/academics/` - Academic endpoints (courses, sections, enrollments)

### Assessments
- `GET /api/assessments/` - Assignment and submission endpoints

### Attendance
- `GET /api/attendance/` - Attendance tracking endpoints

### Library
- `GET /api/library/` - Library books and checkouts

### Services
- `GET /api/services/` - Financial aid, parking, events

### Facilities
- `GET /api/facilities/` - Buildings and rooms

## Deployment on Render

### Prerequisites
1. PostgreSQL database on Render
2. Environment variables configured

### Build Command
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py import_data && python manage.py collectstatic --noinput
```

### Start Command
```bash
gunicorn config.wsgi:application
```

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string (auto-provided by Render)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Your Render domain
- `CORS_ALLOWED_ORIGINS`: Your frontend Vercel URL

## Project Structure

```
backend/
├── config/              # Project settings
├── apps/
│   ├── users/          # User authentication & profiles
│   ├── academics/      # Courses, sections, enrollments
│   ├── assessments/    # Assignments & submissions
│   ├── attendance/     # Attendance tracking
│   ├── library/        # Library system
│   ├── services/       # Financial aid, parking, events
│   └── facilities/     # Buildings & rooms
├── manage.py
└── requirements.txt
```

## Database Models

- **Users**: Custom user model with Student, Faculty, Staff profiles
- **Academics**: Departments, Courses, Sections, Enrollments
- **Assessments**: Assignments, Submissions
- **Attendance**: Attendance records
- **Library**: Books, Checkouts
- **Services**: Financial Aid, Parking Permits, Events
- **Facilities**: Buildings, Rooms

## Data Import

The `import_data` management command imports all CSV files from the `data/` directory in the correct order, respecting foreign key relationships.

Imported entities:
- 1,000 students
- 100 faculty members
- 50 staff members
- 200 courses
- 400 sections
- 3,000 enrollments
- 1,500 assignments
- 4,965 submissions
- 4,000 attendance records
- 1,000 library books
- 800 library checkouts
- 600 financial aid records
- 400 parking permits
- 100 events
- 12 buildings
- 194 rooms
- 10 departments

Total: 18,331 records
