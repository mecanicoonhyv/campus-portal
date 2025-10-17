import csv
import os
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
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

    def __init__(self):
        super().__init__()
        self.data_dir = 'data'
        self.imported_counts = {}

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

    def import_departments(self):
        self.stdout.write('Importing departments...')
        rows = self.read_csv('departments.csv')
        for row in rows:
            Department.objects.get_or_create(
                department_id=row['department_id'],
                defaults={
                    'name': row['name'],
                    'head': row.get('head', ''),
                    'budget': Decimal(row.get('budget', 0)),
                    'phone': row.get('phone', ''),
                    'email': row.get('email', ''),
                    'building': row.get('building', ''),
                    'description': row.get('description', ''),
                }
            )
        self.imported_counts['Departments'] = len(rows)

    def import_buildings(self):
        self.stdout.write('Importing buildings...')
        rows = self.read_csv('buildings.csv')
        for row in rows:
            Building.objects.get_or_create(
                building_id=row['building_id'],
                defaults={
                    'name': row['name'],
                    'address': row.get('address', ''),
                    'capacity': int(row.get('capacity', 0)),
                    'floors': int(row.get('floors', 1)),
                    'year_built': int(row['year_built']) if row.get('year_built') else None,
                    'facilities': row.get('facilities', ''),
                    'description': row.get('description', ''),
                }
            )
        self.imported_counts['Buildings'] = len(rows)

    def import_rooms(self):
        self.stdout.write('Importing rooms...')
        rows = self.read_csv('rooms.csv')
        for row in rows:
            building = Building.objects.filter(building_id=row['building_id']).first()
            if building:
                Room.objects.get_or_create(
                    room_id=row['room_id'],
                    defaults={
                        'building': building,
                        'room_number': row['room_number'],
                        'room_type': row.get('room_type', 'Classroom'),
                        'capacity': int(row.get('capacity', 30)),
                        'equipment': row.get('equipment', ''),
                        'description': row.get('description', ''),
                    }
                )
        self.imported_counts['Rooms'] = len(rows)

    def import_students(self):
        self.stdout.write('Importing students...')
        rows = self.read_csv('students.csv')
        count = 0
        for row in rows:
            user, created = User.objects.get_or_create(
                email=row['email'],
                defaults={
                    'username': row['email'].split('@')[0],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone': row.get('phone', ''),
                    'role': 'student',
                    'date_of_birth': datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date() if row.get('date_of_birth') else None,
                    'address': row.get('address', ''),
                    'city': row.get('city', ''),
                    'state': row.get('state', ''),
                    'zip_code': row.get('zip_code', ''),
                    'password': make_password('password123'),  # Default password
                }
            )

            if created:
                StudentProfile.objects.create(
                    user=user,
                    student_id=row['student_id'],
                    enrollment_date=datetime.strptime(row['enrollment_date'], '%Y-%m-%d').date(),
                    major=row['major'],
                    year_level=row['year_level'],
                    gpa=Decimal(row.get('gpa', '0.00')),
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
            user, created = User.objects.get_or_create(
                email=row['email'],
                defaults={
                    'username': row['email'].split('@')[0],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone': row.get('phone', ''),
                    'role': 'faculty',
                    'password': make_password('password123'),
                }
            )

            if created:
                FacultyProfile.objects.create(
                    user=user,
                    faculty_id=row['faculty_id'],
                    department=row['department'],
                    rank=row['rank'],
                    hire_date=datetime.strptime(row['hire_date'], '%Y-%m-%d').date(),
                    salary=Decimal(row.get('salary', '0.00')),
                    office_building=row.get('office_building', ''),
                    office_number=row.get('office_number', ''),
                    specialization=row.get('specialization', ''),
                    status=row.get('status', 'Active'),
                    education=row.get('education', 'PhD'),
                    years_experience=int(row.get('years_experience', 0)),
                    research_areas=row.get('research_areas', ''),
                    publications=int(row.get('publications', 0)),
                    is_professor=row.get('is_professor', 'False').lower() == 'true',
                )
                count += 1
        self.imported_counts['Faculty'] = count

    def import_staff(self):
        self.stdout.write('Importing staff...')
        rows = self.read_csv('staff.csv')
        count = 0
        for row in rows:
            user, created = User.objects.get_or_create(
                email=row['email'],
                defaults={
                    'username': row['email'].split('@')[0],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone': row.get('phone', ''),
                    'role': 'staff',
                    'password': make_password('password123'),
                }
            )

            if created:
                StaffProfile.objects.create(
                    user=user,
                    staff_id=row['staff_id'],
                    department=row['department'],
                    position=row['position'],
                    hire_date=datetime.strptime(row['hire_date'], '%Y-%m-%d').date(),
                    salary=Decimal(row.get('salary', '0.00')),
                    office_building=row.get('office_building', ''),
                    office_number=row.get('office_number', ''),
                    status=row.get('status', 'Active'),
                )
                count += 1
        self.imported_counts['Staff'] = count

    def import_courses(self):
        self.stdout.write('Importing courses...')
        rows = self.read_csv('courses.csv')
        for row in rows:
            dept = Department.objects.filter(name__icontains=row['department']).first()
            Course.objects.get_or_create(
                course_id=row['course_id'],
                defaults={
                    'course_name': row['course_name'],
                    'department': dept,
                    'credits': int(row.get('credits', 3)),
                    'description': row.get('description', ''),
                    'prerequisites': row.get('prerequisites', ''),
                    'level': row.get('level', 'Undergraduate'),
                    'status': row.get('status', 'Active'),
                }
            )
        self.imported_counts['Courses'] = len(rows)

    def import_sections(self):
        self.stdout.write('Importing sections...')
        rows = self.read_csv('sections.csv')
        for row in rows:
            course = Course.objects.filter(course_id=row['course_id']).first()
            faculty = FacultyProfile.objects.filter(faculty_id=row['instructor_id']).first()
            room = Room.objects.filter(room_id=row['room']).first() if row.get('room') else None

            if course:
                Section.objects.get_or_create(
                    section_id=row['section_id'],
                    defaults={
                        'course': course,
                        'section_number': row['section_number'],
                        'semester': row['semester'],
                        'year': int(row['year']),
                        'instructor': faculty,
                        'instructor_name': row['instructor_name'],
                        'instructor_rank': row.get('instructor_rank', ''),
                        'meeting_days': row['meeting_days'],
                        'meeting_time': row['meeting_time'],
                        'room': room,
                        'capacity': int(row.get('capacity', 30)),
                        'enrolled': int(row.get('enrolled', 0)),
                        'status': row.get('status', 'Open'),
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
                Enrollment.objects.get_or_create(
                    enrollment_id=row['enrollment_id'],
                    defaults={
                        'student': student,
                        'student_name': row['student_name'],
                        'section': section,
                        'course': course,
                        'semester': row['semester'],
                        'enrollment_date': datetime.strptime(row['enrollment_date'], '%Y-%m-%d').date(),
                        'status': row.get('status', 'Enrolled'),
                        'grade': row.get('grade', ''),
                        'grade_points': Decimal(row.get('grade_points', '0.00')) if row.get('grade_points') else Decimal('0.00'),
                        'credits_attempted': int(row.get('credits_attempted', 0)),
                        'credits_earned': int(row.get('credits_earned', 0)),
                    }
                )
        self.imported_counts['Enrollments'] = len(rows)

    def import_assignments(self):
        self.stdout.write('Importing assignments...')
        rows = self.read_csv('assignments.csv')
        for row in rows:
            section = Section.objects.filter(section_id=row['section_id']).first()
            course = Course.objects.filter(course_id=row['course_id']).first()

            if section and course:
                Assignment.objects.get_or_create(
                    assignment_id=row['assignment_id'],
                    defaults={
                        'section': section,
                        'course': course,
                        'title': row['title'],
                        'type': row['type'],
                        'description': row.get('description', ''),
                        'total_points': int(row.get('total_points', 100)),
                        'due_date': datetime.strptime(row['due_date'], '%Y-%m-%d').date(),
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
                Submission.objects.get_or_create(
                    submission_id=row['submission_id'],
                    defaults={
                        'assignment': assignment,
                        'student': student,
                        'student_name': row['student_name'],
                        'submission_date': datetime.strptime(row['submission_date'], '%Y-%m-%d') if row.get('submission_date') else None,
                        'content': row.get('content', ''),
                        'points_earned': Decimal(row['points_earned']) if row.get('points_earned') else None,
                        'feedback': row.get('feedback', ''),
                        'graded_date': datetime.strptime(row['graded_date'], '%Y-%m-%d') if row.get('graded_date') else None,
                        'status': row.get('status', 'Submitted'),
                    }
                )
        self.imported_counts['Submissions'] = len(rows)

    def import_attendance(self):
        self.stdout.write('Importing attendance records...')
        rows = self.read_csv('attendance.csv')
        for row in rows:
            student = StudentProfile.objects.filter(student_id=row['student_id']).first()
            section = Section.objects.filter(section_id=row['section_id']).first()

            if student and section:
                AttendanceRecord.objects.get_or_create(
                    record_id=row['record_id'],
                    defaults={
                        'student': student,
                        'student_name': row['student_name'],
                        'section': section,
                        'course_id': row['course_id'],
                        'date': datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        'status': row['status'],
                        'notes': row.get('notes', ''),
                    }
                )
        self.imported_counts['Attendance Records'] = len(rows)

    def import_library_books(self):
        self.stdout.write('Importing library books...')
        rows = self.read_csv('library_books.csv')
        for row in rows:
            Book.objects.get_or_create(
                book_id=row['book_id'],
                defaults={
                    'isbn': row.get('isbn', ''),
                    'title': row['title'],
                    'author': row['author'],
                    'publisher': row.get('publisher', ''),
                    'publication_year': int(row['publication_year']) if row.get('publication_year') else None,
                    'category': row.get('category', ''),
                    'location': row.get('location', ''),
                    'copies_total': int(row.get('copies_total', 1)),
                    'copies_available': int(row.get('copies_available', 1)),
                    'status': row.get('status', 'Available'),
                    'description': row.get('description', ''),
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
                Checkout.objects.get_or_create(
                    checkout_id=row['checkout_id'],
                    defaults={
                        'book': book,
                        'student': student,
                        'student_name': row['student_name'],
                        'checkout_date': datetime.strptime(row['checkout_date'], '%Y-%m-%d').date(),
                        'due_date': datetime.strptime(row['due_date'], '%Y-%m-%d').date(),
                        'return_date': datetime.strptime(row['return_date'], '%Y-%m-%d').date() if row.get('return_date') else None,
                        'status': row.get('status', 'Active'),
                        'fine_amount': Decimal(row.get('fine_amount', '0.00')),
                    }
                )
        self.imported_counts['Library Checkouts'] = len(rows)

    def import_financial_aid(self):
        self.stdout.write('Importing financial aid...')
        rows = self.read_csv('financial_aid.csv')
        for row in rows:
            student = StudentProfile.objects.filter(student_id=row['student_id']).first()

            if student:
                FinancialAid.objects.get_or_create(
                    aid_id=row['aid_id'],
                    defaults={
                        'student': student,
                        'student_name': row['student_name'],
                        'type': row['type'],
                        'name': row['name'],
                        'amount': Decimal(row['amount']),
                        'academic_year': row['academic_year'],
                        'semester': row['semester'],
                        'status': row.get('status', 'Pending'),
                        'disbursement_date': datetime.strptime(row['disbursement_date'], '%Y-%m-%d').date() if row.get('disbursement_date') else None,
                        'description': row.get('description', ''),
                    }
                )
        self.imported_counts['Financial Aid'] = len(rows)

    def import_parking(self):
        self.stdout.write('Importing parking permits...')
        rows = self.read_csv('parking.csv')
        for row in rows:
            student = StudentProfile.objects.filter(student_id=row['student_id']).first()

            if student:
                ParkingPermit.objects.get_or_create(
                    permit_id=row['permit_id'],
                    defaults={
                        'student': student,
                        'student_name': row['student_name'],
                        'permit_type': row.get('permit_type', 'Student'),
                        'lot_number': row['lot_number'],
                        'vehicle_make': row['vehicle_make'],
                        'vehicle_model': row['vehicle_model'],
                        'vehicle_year': int(row['vehicle_year']),
                        'license_plate': row['license_plate'],
                        'issue_date': datetime.strptime(row['issue_date'], '%Y-%m-%d').date(),
                        'expiration_date': datetime.strptime(row['expiration_date'], '%Y-%m-%d').date(),
                        'status': row.get('status', 'Active'),
                    }
                )
        self.imported_counts['Parking Permits'] = len(rows)

    def import_events(self):
        self.stdout.write('Importing events...')
        rows = self.read_csv('events.csv')
        for row in rows:
            Event.objects.get_or_create(
                event_id=row['event_id'],
                defaults={
                    'name': row['name'],
                    'type': row['type'],
                    'description': row.get('description', ''),
                    'date': datetime.strptime(row['date'], '%Y-%m-%d').date(),
                    'start_time': datetime.strptime(row['start_time'], '%H:%M').time(),
                    'end_time': datetime.strptime(row['end_time'], '%H:%M').time(),
                    'location': row['location'],
                    'organizer': row['organizer'],
                    'capacity': int(row.get('capacity', 0)),
                    'registered': int(row.get('registered', 0)),
                    'status': row.get('status', 'Scheduled'),
                }
            )
        self.imported_counts['Events'] = len(rows)
