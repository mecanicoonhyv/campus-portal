import csv
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db import transaction

from apps.users.models import User, StudentProfile, FacultyProfile, StaffProfile
from apps.facilities.models import Building, Room
from apps.academics.models import Department, Course, Section, Enrollment
from apps.assessments.models import Assignment, Submission
from apps.attendance.models import AttendanceRecord
from apps.library.models import Book, Checkout
from apps.services.models import FinancialAid, ParkingPermit, Event


class Command(BaseCommand):
    help = 'Import data from CSV files in the data/ directory'
    DEFAULT_PASSWORD = 'password123'

    def __init__(self):
        super().__init__()
        self.data_dir = 'data'
        self.imported_counts = {}
        self.default_password_hash = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir',
            type=str,
            default='data',
            help='Directory containing CSV files (default: data/)'
        )

    def handle(self, *args, **options):
        self.data_dir = options['data_dir']

        if not os.path.exists(self.data_dir):
            self.stdout.write(self.style.ERROR(f'Data directory "{self.data_dir}" not found'))
            return

        if self.default_password_hash is None:
            # Hash the default password once to avoid repeated heavy PBKDF2 work
            self.default_password_hash = make_password(self.DEFAULT_PASSWORD)

        self.stdout.write(self.style.SUCCESS('Starting data import...'))

        try:
            with transaction.atomic():
                # Import in correct order respecting dependencies
                self.import_departments()
                self.import_buildings()
                self.import_rooms()
                self.import_students()
                self.import_faculty()
                self.import_staff()
                self.import_courses()
                self.import_sections()
                self.import_enrollments()
                self.import_assignments()
                self.import_submissions()
                self.import_attendance()
                self.import_library_books()
                self.import_library_checkouts()
                self.import_financial_aid()
                self.import_parking()
                self.import_events()

            self.stdout.write(self.style.SUCCESS('\n=== Import Summary ==='))
            for model_name, count in self.imported_counts.items():
                self.stdout.write(self.style.SUCCESS(f'{model_name}: {count} records'))

            total = sum(self.imported_counts.values())
            self.stdout.write(self.style.SUCCESS(f'\nTotal records imported: {total}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Import failed: {str(e)}'))
            raise

    def read_csv(self, filename):
        """Read CSV file and return list of dictionaries"""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
            return []

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def get_value(self, row, *keys, default=''):
        """Return the first non-empty value for the provided keys."""
        sentinel = object()
        for key in keys:
            value = row.get(key, sentinel)
            if value is sentinel:
                continue
            if value not in (None, '', 'NULL'):
                return value
        return default

    def parse_int(self, value, default=0):
        if value in (None, '', 'NULL'):
            return default
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default

    def parse_decimal(self, value, default=Decimal('0.00')):
        if value in (None, '', 'NULL'):
            return default
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return default

    def parse_date(self, value):
        if value in (None, '', 'NULL'):
            return None
        for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        # handle datetime strings with time component
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None

    def parse_datetime(self, value):
        if value in (None, '', 'NULL'):
            return None

        parsed = None
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d'):
            try:
                parsed = datetime.strptime(value, fmt)
                break
            except ValueError:
                continue

        if parsed is None:
            return None

        if timezone.is_naive(parsed):
            try:
                return timezone.make_aware(parsed, timezone.get_current_timezone())
            except Exception:
                # Fallback to naive datetime if timezone conversion fails
                return parsed
        return parsed

    def parse_time(self, value):
        if value in (None, '', 'NULL'):
            return None
        for fmt in ('%H:%M:%S', '%H:%M'):
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                continue
        return None

    def parse_bool(self, value, default=False):
        if value in (None, '', 'NULL'):
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {'true', '1', 'yes', 'y'}

    def import_departments(self):
        self.stdout.write('Importing departments...')
        rows = self.read_csv('departments.csv')
        for row in rows:
            name = self.get_value(row, 'name', 'department_name')
            head = self.get_value(row, 'head', 'dean')
            budget = self.parse_decimal(self.get_value(row, 'budget', 'annual_budget', default='0'))
            phone = self.get_value(row, 'phone', 'contact_number')
            email = self.get_value(row, 'email', 'department_email')
            building = self.get_value(row, 'building', 'building_name', 'location')
            description = self.get_value(row, 'description', 'details', 'department_description')

            Department.objects.get_or_create(
                department_id=row['department_id'],
                defaults={
                    'name': name,
                    'head': head,
                    'budget': budget,
                    'phone': phone,
                    'email': email,
                    'building': building,
                    'description': description,
                }
            )
        self.imported_counts['Departments'] = len(rows)

    def import_buildings(self):
        self.stdout.write('Importing buildings...')
        rows = self.read_csv('buildings.csv')
        for row in rows:
            name = self.get_value(row, 'name', 'building_name')
            address = self.get_value(row, 'address', 'building_address', 'location')
            capacity = self.parse_int(self.get_value(row, 'capacity', default=None), default=None)
            floors = self.parse_int(self.get_value(row, 'floors', default=1), default=1)
            year_built = self.parse_int(self.get_value(row, 'year_built', 'built_year'), default=None)
            facilities = self.get_value(row, 'facilities', 'accessibility')
            description = self.get_value(row, 'description', 'status', 'notes')

            Building.objects.get_or_create(
                building_id=row['building_id'],
                defaults={
                    'name': name,
                    'address': address,
                    'capacity': capacity if capacity is not None else 0,
                    'floors': floors if floors is not None else 1,
                    'year_built': year_built,
                    'facilities': facilities,
                    'description': description,
                }
            )
        self.imported_counts['Buildings'] = len(rows)

    def import_rooms(self):
        self.stdout.write('Importing rooms...')
        rows = self.read_csv('rooms.csv')
        for row in rows:
            building = Building.objects.filter(building_id=row['building_id']).first()
            if building:
                room_type = self.get_value(row, 'room_type', 'type')
                equipment = self.get_value(row, 'equipment', 'resources')
                description = self.get_value(row, 'description', 'status')
                capacity = self.parse_int(self.get_value(row, 'capacity', default=30), default=30)

                Room.objects.get_or_create(
                    room_id=row['room_id'],
                    defaults={
                        'building': building,
                        'room_number': row['room_number'],
                        'room_type': room_type or 'Classroom',
                        'capacity': capacity,
                        'equipment': equipment,
                        'description': description,
                    }
                )
        self.imported_counts['Rooms'] = len(rows)

    def import_students(self):
        self.stdout.write('Importing students...')
        rows = self.read_csv('students.csv')
        count = 0
        for row in rows:
            dob = self.parse_date(self.get_value(row, 'date_of_birth'))
            enrollment_date = self.parse_date(self.get_value(row, 'enrollment_date'))
            address = self.get_value(row, 'address', 'street_address')
            city = self.get_value(row, 'city', 'town')
            state = self.get_value(row, 'state', 'province')
            zip_code = self.get_value(row, 'zip_code', 'postal_code')
            gpa = self.parse_decimal(self.get_value(row, 'gpa', default='0.00'), default=Decimal('0.00'))

            user, created = User.objects.get_or_create(
                email=row['email'],
                defaults={
                    'username': row['email'].split('@')[0],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone': row.get('phone', ''),
                    'role': 'student',
                    'date_of_birth': dob,
                    'address': address,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code,
                    'password': self.default_password_hash,  # Default password
                }
            )

            if created:
                StudentProfile.objects.create(
                    user=user,
                    student_id=row['student_id'],
                    enrollment_date=enrollment_date or datetime.today().date(),
                    major=row['major'],
                    year_level=row['year_level'],
                    gpa=gpa,
                    status=row.get('status', 'Active'),
                    emergency_contact=row.get('emergency_contact', ''),
                    emergency_phone=row.get('emergency_phone', ''),
                )
                count += 1
        self.imported_counts['Students'] = count

    def import_faculty(self):
        self.stdout.write('Importing faculty...')
        rows = self.read_csv('faculty_professors.csv')
        count = 0
        for row in rows:
            hire_date = self.parse_date(self.get_value(row, 'hire_date'))
            salary = self.parse_decimal(self.get_value(row, 'salary', default='0.00'))
            office_building = self.get_value(row, 'office_building', 'building', 'office_location')
            office_number = self.get_value(row, 'office_number', 'office', 'office_room')
            specialization = self.get_value(row, 'specialization', 'focus_area')
            status = self.get_value(row, 'status', 'employment_status', default='Active')
            education = self.get_value(row, 'education', 'degree', default='PhD')
            years_experience = self.parse_int(self.get_value(row, 'years_experience', 'experience_years', default=0), default=0)
            publications = self.parse_int(self.get_value(row, 'publications', default=0), default=0)
            is_professor = self.parse_bool(self.get_value(row, 'is_professor', 'tenured', default=False))

            user, created = User.objects.get_or_create(
                email=row['email'],
                defaults={
                    'username': row['email'].split('@')[0],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone': row.get('phone', ''),
                    'role': 'faculty',
                    'password': self.default_password_hash,
                }
            )

            if created:
                FacultyProfile.objects.create(
                    user=user,
                    faculty_id=row['faculty_id'],
                    department=row['department'],
                    rank=row['rank'],
                    hire_date=hire_date or datetime.today().date(),
                    salary=salary,
                    office_building=office_building,
                    office_number=office_number,
                    specialization=specialization,
                    status=status,
                    education=education,
                    years_experience=years_experience,
                    research_areas=row.get('research_areas', ''),
                    publications=publications,
                    is_professor=is_professor,
                )
                count += 1
        self.imported_counts['Faculty'] = count

    def import_staff(self):
        self.stdout.write('Importing staff...')
        rows = self.read_csv('staff.csv')
        count = 0
        for row in rows:
            hire_date = self.parse_date(self.get_value(row, 'hire_date'))
            salary = self.parse_decimal(self.get_value(row, 'salary', default='0.00'))
            office_building = self.get_value(row, 'office_building', 'building')
            office_number = self.get_value(row, 'office_number', 'office', 'office_room')
            status = self.get_value(row, 'status', 'employment_status', default='Active')

            user, created = User.objects.get_or_create(
                email=row['email'],
                defaults={
                    'username': row['email'].split('@')[0],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone': row.get('phone', ''),
                    'role': 'staff',
                    'password': self.default_password_hash,
                }
            )

            if created:
                StaffProfile.objects.create(
                    user=user,
                    staff_id=row['staff_id'],
                    department=row['department'],
                    position=row['position'],
                    hire_date=hire_date or datetime.today().date(),
                    salary=salary,
                    office_building=office_building,
                    office_number=office_number,
                    status=status,
                )
                count += 1
        self.imported_counts['Staff'] = count

    def import_courses(self):
        self.stdout.write('Importing courses...')
        rows = self.read_csv('courses.csv')
        for row in rows:
            department_name = self.get_value(row, 'department', 'department_name')
            dept = Department.objects.filter(name__iexact=department_name).first()
            credits = self.parse_int(self.get_value(row, 'credits', default=3), default=3)
            level = self.get_value(row, 'level', 'course_level', default='Undergraduate')
            status = self.get_value(row, 'status', 'course_status', default='Active')
            Course.objects.get_or_create(
                course_id=row['course_id'],
                defaults={
                    'course_name': row['course_name'],
                    'department': dept,
                    'credits': credits,
                    'description': row.get('description', ''),
                    'prerequisites': row.get('prerequisites', ''),
                    'level': level,
                    'status': status,
                }
            )
        self.imported_counts['Courses'] = len(rows)

    def import_sections(self):
        self.stdout.write('Importing sections...')
        rows = self.read_csv('sections.csv')
        for row in rows:
            course = Course.objects.filter(course_id=row['course_id']).first()
            faculty = FacultyProfile.objects.filter(faculty_id=row['instructor_id']).first()
            room_identifier = self.get_value(row, 'room', 'room_id')
            room = Room.objects.filter(room_id=room_identifier).first() if room_identifier else None
            if not room and room_identifier:
                building_name, _, room_number = room_identifier.rpartition(' ')
                if building_name and room_number:
                    building = Building.objects.filter(name__iexact=building_name).first()
                    if building:
                        room = Room.objects.filter(building=building, room_number=room_number).first()

            if course:
                Section.objects.get_or_create(
                    section_id=row['section_id'],
                    defaults={
                        'course': course,
                        'section_number': row['section_number'],
                        'semester': self.get_value(row, 'semester', 'term'),
                        'year': self.parse_int(self.get_value(row, 'year', default=datetime.today().year), default=datetime.today().year),
                        'instructor': faculty,
                        'instructor_name': row['instructor_name'],
                        'instructor_rank': row.get('instructor_rank', ''),
                        'meeting_days': row['meeting_days'],
                        'meeting_time': row['meeting_time'],
                        'room': room,
                        'capacity': self.parse_int(self.get_value(row, 'capacity', default=30), default=30),
                        'enrolled': self.parse_int(self.get_value(row, 'enrolled', default=0), default=0),
                        'status': self.get_value(row, 'status', 'section_status', default='Open'),
                    }
                )
        self.imported_counts['Sections'] = len(rows)

    def import_enrollments(self):
        self.stdout.write('Importing enrollments...')
        rows = self.read_csv('enrollments.csv')
        for row in rows:
            student = StudentProfile.objects.filter(student_id=row['student_id']).first()
            section = Section.objects.filter(section_id=row['section_id']).first()
            course = Course.objects.filter(course_id=row['course_id']).first()

            if student and section and course:
                enrollment_date = self.parse_date(self.get_value(row, 'enrollment_date'))
                grade_points = self.parse_decimal(self.get_value(row, 'grade_points'), default=Decimal('0.00'))
                credits_attempted = self.parse_int(self.get_value(row, 'credits_attempted', default=0), default=0)
                credits_earned = self.parse_int(self.get_value(row, 'credits_earned', default=0), default=0)
                defaults = {
                    'student': student,
                    'student_name': row.get('student_name', student.user.get_full_name() if student.user_id else ''),
                    'section': section,
                    'course': course,
                    'semester': self.get_value(row, 'semester', 'term'),
                    'enrollment_date': enrollment_date or datetime.today().date(),
                    'status': row.get('status', 'Enrolled'),
                    'grade': row.get('grade', ''),
                    'grade_points': grade_points,
                    'credits_attempted': credits_attempted,
                    'credits_earned': credits_earned,
                }

                # Prevent UNIQUE constraint violations when CSV rows contain duplicate
                # student/section pairs by updating the existing record instead of
                # attempting a fresh insert.
                enrollment = Enrollment.objects.filter(enrollment_id=row['enrollment_id']).first()
                if not enrollment:
                    enrollment = Enrollment.objects.filter(student=student, section=section).first()

                if enrollment:
                    for field, value in defaults.items():
                        setattr(enrollment, field, value)
                    enrollment.save(update_fields=list(defaults.keys()))
                else:
                    Enrollment.objects.create(
                        enrollment_id=row['enrollment_id'],
                        **defaults,
                    )
        self.imported_counts['Enrollments'] = len(rows)

    def import_assignments(self):
        self.stdout.write('Importing assignments...')
        rows = self.read_csv('assignments.csv')
        for row in rows:
            section = Section.objects.filter(section_id=row['section_id']).first()
            course = Course.objects.filter(course_id=row['course_id']).first()

            if section and course:
                due_date = self.parse_date(self.get_value(row, 'due_date'))
                Assignment.objects.get_or_create(
                    assignment_id=row['assignment_id'],
                    defaults={
                        'section': section,
                        'course': course,
                        'title': row['title'],
                        'type': row['type'],
                        'description': row.get('description', ''),
                        'total_points': self.parse_int(self.get_value(row, 'total_points', default=100), default=100),
                        'due_date': due_date or datetime.today().date(),
                        'status': row.get('status', 'Active'),
                    }
                )
        self.imported_counts['Assignments'] = len(rows)

    def import_submissions(self):
        self.stdout.write('Importing submissions...')
        rows = self.read_csv('submissions.csv')
        for row in rows:
            assignment = Assignment.objects.filter(assignment_id=row['assignment_id']).first()
            student = StudentProfile.objects.filter(student_id=row['student_id']).first()

            if assignment and student:
                submission_dt = self.parse_datetime(self.get_value(row, 'submission_date'))
                graded_dt = self.parse_datetime(self.get_value(row, 'graded_date'))
                points_earned = self.parse_decimal(self.get_value(row, 'points_earned'), default=None)
                defaults = {
                    'assignment': assignment,
                    'student': student,
                    'student_name': row.get('student_name', student.user.get_full_name() if student.user_id else ''),
                    'submission_date': submission_dt,
                    'content': row.get('content', ''),
                    'points_earned': points_earned,
                    'feedback': row.get('feedback', ''),
                    'graded_date': graded_dt,
                    'status': row.get('status', 'Submitted'),
                }

                # Update existing submissions (matched by ID or assignment/student) to
                # avoid unique constraint violations when CSV rows contain duplicates.
                submission = Submission.objects.filter(submission_id=row['submission_id']).first()
                if not submission:
                    submission = Submission.objects.filter(assignment=assignment, student=student).first()

                if submission:
                    for field, value in defaults.items():
                        setattr(submission, field, value)
                    submission.save(update_fields=list(defaults.keys()))
                else:
                    Submission.objects.create(
                        submission_id=row['submission_id'],
                        **defaults,
                    )
        self.imported_counts['Submissions'] = len(rows)

    def import_attendance(self):
        self.stdout.write('Importing attendance records...')
        rows = self.read_csv('attendance.csv')
        for row in rows:
            student = StudentProfile.objects.filter(student_id=row['student_id']).first()
            section = Section.objects.filter(section_id=row['section_id']).first()

            if student and section:
                record_id = self.get_value(row, 'record_id', 'attendance_id')
                attendance_date = self.parse_date(self.get_value(row, 'date'))
                notes = self.get_value(row, 'notes', 'comments')
                defaults = {
                    'student': student,
                    'student_name': row.get('student_name', student.user.get_full_name() if student.user_id else ''),
                    'section': section,
                    'course_id': row['course_id'],
                    'date': attendance_date or datetime.today().date(),
                    'status': row.get('status', 'Present'),
                    'notes': notes,
                }

                # Update existing attendance (matched by ID or unique triple) so
                # duplicate CSV rows do not violate the unique constraint.
                attendance = AttendanceRecord.objects.filter(record_id=record_id).first()
                if not attendance:
                    attendance = AttendanceRecord.objects.filter(
                        student=student,
                        section=section,
                        date=defaults['date'],
                    ).first()

                if attendance:
                    for field, value in defaults.items():
                        setattr(attendance, field, value)
                    attendance.save(update_fields=list(defaults.keys()))
                else:
                    AttendanceRecord.objects.create(
                        record_id=record_id,
                        **defaults,
                    )
        self.imported_counts['Attendance Records'] = len(rows)

    def import_library_books(self):
        self.stdout.write('Importing library books...')
        rows = self.read_csv('library_books.csv')
        for row in rows:
            publication_year = self.parse_int(self.get_value(row, 'publication_year'), default=None)
            category = self.get_value(row, 'category', 'genre')
            location = self.get_value(row, 'location', 'shelf_location')
            copies_total = self.parse_int(self.get_value(row, 'copies_total', default=1), default=1)
            copies_available = self.parse_int(self.get_value(row, 'copies_available', default=1), default=1)
            status = self.get_value(row, 'status', 'availability', default='Available')
            Book.objects.get_or_create(
                book_id=row['book_id'],
                defaults={
                    'isbn': row.get('isbn', ''),
                    'title': row['title'],
                    'author': row['author'],
                    'publisher': row.get('publisher', ''),
                    'publication_year': publication_year,
                    'category': category,
                    'location': location,
                    'copies_total': copies_total,
                    'copies_available': copies_available,
                    'status': status,
                    'description': row.get('description', '') or category,
                }
            )
        self.imported_counts['Library Books'] = len(rows)

    def import_library_checkouts(self):
        self.stdout.write('Importing library checkouts...')
        rows = self.read_csv('library_checkouts.csv')
        for row in rows:
            book = Book.objects.filter(book_id=row['book_id']).first()
            student = StudentProfile.objects.filter(student_id=row['student_id']).first()

            if book and student:
                checkout_date = self.parse_date(self.get_value(row, 'checkout_date'))
                due_date = self.parse_date(self.get_value(row, 'due_date'))
                return_date = self.parse_date(self.get_value(row, 'return_date'))
                fine_amount = self.parse_decimal(self.get_value(row, 'fine_amount', default='0.00'), default=Decimal('0.00'))
                Checkout.objects.get_or_create(
                    checkout_id=row['checkout_id'],
                    defaults={
                        'book': book,
                        'student': student,
                        'student_name': row['student_name'],
                        'checkout_date': checkout_date or datetime.today().date(),
                        'due_date': due_date or datetime.today().date(),
                        'return_date': return_date,
                        'status': self.get_value(row, 'status', default='Active'),
                        'fine_amount': fine_amount,
                    }
                )
        self.imported_counts['Library Checkouts'] = len(rows)

    def import_financial_aid(self):
        self.stdout.write('Importing financial aid...')
        rows = self.read_csv('financial_aid.csv')
        for row in rows:
            student = StudentProfile.objects.filter(student_id=row['student_id']).first()

            if student:
                aid_type = self.get_value(row, 'type', 'aid_type')
                award_name = self.get_value(row, 'name', 'award_name', default=aid_type)
                amount = self.parse_decimal(self.get_value(row, 'amount', default='0.00'))
                academic_year = self.get_value(row, 'academic_year', 'year')
                if academic_year and isinstance(academic_year, (int, float)):
                    academic_year = str(int(academic_year))
                semester = self.get_value(row, 'semester', 'term')
                status = self.get_value(row, 'status', 'award_status', default='Pending')
                disbursement_date = self.parse_date(self.get_value(row, 'disbursement_date', 'date_awarded'))
                description = self.get_value(row, 'description', 'requirements', 'notes')
                FinancialAid.objects.get_or_create(
                    aid_id=row['aid_id'],
                    defaults={
                        'student': student,
                        'student_name': row['student_name'],
                        'type': aid_type,
                        'name': award_name,
                        'amount': amount,
                        'academic_year': academic_year or '',
                        'semester': semester,
                        'status': status,
                        'disbursement_date': disbursement_date,
                        'description': description,
                    }
                )
        self.imported_counts['Financial Aid'] = len(rows)

    def import_parking(self):
        self.stdout.write('Importing parking permits...')
        rows = self.read_csv('parking.csv')
        for row in rows:
            student_id = self.get_value(row, 'student_id', 'owner_id')
            student = StudentProfile.objects.filter(student_id=student_id).first()

            if student:
                student_name = row.get('student_name') or student.user.get_full_name() if student.user_id else ''
                permit_type = self.get_value(row, 'permit_type', 'permit_category', default='Student')
                lot_number = self.get_value(row, 'lot_number', 'lot_assigned')
                vehicle_make = self.get_value(row, 'vehicle_make', 'make')
                vehicle_model = self.get_value(row, 'vehicle_model', 'model')
                vehicle_year = self.parse_int(self.get_value(row, 'vehicle_year', default=datetime.today().year), default=datetime.today().year)
                license_plate = self.get_value(row, 'license_plate', 'plate', '')
                issue_date = self.parse_date(self.get_value(row, 'issue_date'))
                expiration_date = self.parse_date(self.get_value(row, 'expiration_date', 'expiry_date'))
                status = self.get_value(row, 'status', 'permit_status', default='Active')
                ParkingPermit.objects.get_or_create(
                    permit_id=row['permit_id'],
                    defaults={
                        'student': student,
                        'student_name': student_name,
                        'permit_type': permit_type,
                        'lot_number': lot_number,
                        'vehicle_make': vehicle_make,
                        'vehicle_model': vehicle_model,
                        'vehicle_year': vehicle_year,
                        'license_plate': license_plate,
                        'issue_date': issue_date or datetime.today().date(),
                        'expiration_date': expiration_date or datetime.today().date(),
                        'status': status,
                    }
                )
        self.imported_counts['Parking Permits'] = len(rows)

    def import_events(self):
        self.stdout.write('Importing events...')
        rows = self.read_csv('events.csv')
        for row in rows:
            name = self.get_value(row, 'name', 'title')
            event_type = self.get_value(row, 'type', 'event_type')
            description = self.get_value(row, 'description', 'details')
            event_date = self.parse_date(self.get_value(row, 'date'))
            start_time = self.parse_time(self.get_value(row, 'start_time'))
            end_time = self.parse_time(self.get_value(row, 'end_time'))
            location = self.get_value(row, 'location', 'venue')
            capacity = self.parse_int(self.get_value(row, 'capacity', default=0), default=0)
            registered = self.parse_int(self.get_value(row, 'registered', default=0), default=0)
            status = self.get_value(row, 'status', 'event_status', default='Scheduled')
            organizer = self.get_value(row, 'organizer', 'host', 'coordinator', default='')
            default_time = datetime.strptime('00:00', '%H:%M').time()
            Event.objects.get_or_create(
                event_id=row['event_id'],
                defaults={
                    'name': name,
                    'type': event_type,
                    'description': description,
                    'date': event_date or datetime.today().date(),
                    'start_time': start_time or default_time,
                    'end_time': end_time or default_time,
                    'location': location,
                    'organizer': organizer,
                    'capacity': capacity,
                    'registered': registered,
                    'status': status,
                }
            )
        self.imported_counts['Events'] = len(rows)
