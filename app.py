from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash,send_from_directory, abort
import os
#from sqlalchemy_media import StoreManager, FileSystemStore, Image, File
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, Date, Time, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, joinedload
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta, time
from sqlalchemy import and_, func




app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = os.environ.get('SECRET_KEY', 'default_key')

############ Database Initiliazation ########################################################################################
# Database setup
DATABASE_URL = 'sqlite:///edulearn.db'
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Define Database Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)  # 'instructor' or 'student'

class InstructorNote(Base):
    __tablename__ = 'instructor_notes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    uploaded_on = Column(Date, default=datetime.utcnow)
    classroom = relationship("Class")

class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    schedule_day = Column(String(20), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_students = Column(Integer, nullable=False)
    prerequisites = Column(Text, nullable=True)
    instructor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    instructor = relationship("User")
# Define Announcement model
class Announcement(Base):
    __tablename__ = 'announcements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    posted_on = Column(Date, default=datetime.utcnow)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    classroom = relationship("Class")

# Define Event model
class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=True)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    classroom = relationship("Class")

class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    student = relationship("User")
    classroom = relationship("Class")

class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    due_date = Column(Date, nullable=False)
    due_time = Column(Time, nullable=True)
    points = Column(Integer, nullable=False, default=100)
    file_path = Column(String(255), nullable=True)  # Ensure this exists
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    classroom = relationship("Class", backref="assignments")  # ✅ Ensure this is defined

class Resource(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    file_path = Column(String(255), nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    classroom = relationship("Class")

class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    submitted_on = Column(Date, nullable=False)
    file_path = Column(String(255), nullable=True)
    grade = Column(String(10), nullable=True)  # New column for grading
    feedback = Column(String(500), nullable=True)
    assignment = relationship("Assignment")
    student = relationship("User")

# Create tables
Base.metadata.create_all(engine)
##########################################################################################################################

resources = []

@app.route('/')
def home():
    return render_template('index.html')

from datetime import datetime, time


@app.route('/instructor_grades', methods=['GET', 'POST'])
def instructor_grades():
    user = get_current_user()
    if not user or user.role != 'instructor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    db_session = SessionLocal()
    
    if request.method == 'POST':
        submission_id = request.form.get('submission_id')
        grade = request.form.get('grade')
        feedback = request.form.get('feedback')
        
        if not submission_id or not grade:
            flash('All fields are required.', 'danger')
            return redirect(url_for('instructor_grades'))
        
        submission = db_session.query(Submission).filter_by(id=submission_id).first()
        
        if submission:
            submission.grade = grade
            submission.feedback = feedback  # Save feedback
            db_session.commit()
            flash('Grade and feedback saved successfully!', 'success')
        else:
            flash('Submission not found.', 'danger')
    
    submissions = (
        db_session.query(Submission)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .join(User, Submission.student_id == User.id)
        .join(Class, Assignment.class_id == Class.id)
        .filter(Class.instructor_id == user.id)
        .options(joinedload(Submission.assignment), joinedload(Submission.student))
        .all()
    )
    
    db_session.close()
    
    return render_template('instructor_grades.html', user=user, submissions=submissions)
@app.route('/instructor-notes', methods=['GET', 'POST'])
def instructor_notes():
    user = get_current_user()
    if not user or user.role != 'instructor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    db_session = SessionLocal()

    if request.method == 'POST':
        title = request.form.get('title')
        class_id = request.form.get('class_id')
        file = request.files.get('file')

        if not title or not class_id or not file:
            flash('All fields are required.', 'danger')
            return redirect(url_for('instructor_notes'))
        
        filename = secure_filename(file.filename)
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_path)

        note = InstructorNote(
            title=title,
            file_path=f"uploads/assignments/{filename}",
            class_id=int(class_id)
        )
        
        try:
            db_session.add(note)
            db_session.commit()
            flash('Note uploaded successfully!', 'success')
        except Exception as e:
            db_session.rollback()
            flash(f"Error uploading note: {str(e)}", "danger")

    # Fetch instructor notes with eager loading to prevent DetachedInstanceError
    instructor_notes = (
        db_session.query(InstructorNote)
        .options(joinedload(InstructorNote.classroom))  
        .join(Class, InstructorNote.class_id == Class.id)
        .filter(Class.instructor_id == user.id)
        .all()
    )

    # Fetch instructor's classes
    instructor_classes = db_session.query(Class).filter_by(instructor_id=user.id).all()
    
    db_session.close()
    
    return render_template('instructor-notes.html', user=user, instructor_notes=instructor_notes, instructor_classes=instructor_classes)
@app.route('/create_course', methods=['POST'])
def create_course():
    user = get_current_user()
    if not user or user.role != 'instructor':
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))

    class_name = request.form.get('class_name')
    class_code = request.form.get('class_code')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    schedule_day = request.form.get('schedule_day')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    max_students = request.form.get('max_students')
    prerequisites = request.form.get('prerequisites')

    if not class_name or not class_code or not start_date or not end_date or not schedule_day or not start_time or not end_time or not max_students:
        flash('All required fields must be filled.', 'danger')
        return redirect(url_for('instructor_dashboard'))

    db_session = SessionLocal()
    # Fetch assignments and ensure classroom (class details) is loaded
    assignments_list = (
        db_session.query(Assignment)
        .options(joinedload(Assignment.classroom))  # ✅ Eagerly load related classroom data
        .all()
    )

    # Check if class code already exists
    existing_class = db_session.query(Class).filter_by(code=class_code).first()
    if existing_class:
        flash('Class code already in use. Choose a different one.', 'danger')
        db_session.close()
        return redirect(url_for('instructor_dashboard'))

    # Convert time strings to Python time objects
    try:
        start_time_obj = datetime.strptime(start_time, "%H:%M").time()
        end_time_obj = datetime.strptime(end_time, "%H:%M").time()
    except ValueError:
        flash('Invalid time format.', 'danger')
        return redirect(url_for('instructor_dashboard'))

    # Create new class
    new_class = Class(
        name=class_name,
        code=class_code,
        description=description,
        start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
        end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
        schedule_day=schedule_day,
        start_time=start_time_obj,  # Now a valid time object
        end_time=end_time_obj,  # Now a valid time object
        max_students=int(max_students),
        prerequisites=prerequisites,
        instructor_id=user.id
    )

    db_session.add(new_class)
    db_session.commit()
    db_session.close()

    flash('Course created successfully!', 'success')
    return redirect(url_for('instructor_dashboard'))


@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    user = get_current_user()
    if not user or user.role != 'instructor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    db_session = SessionLocal()
    note = db_session.query(InstructorNote).filter_by(id=note_id).first()
    
    if note:
        # Delete the file from storage
        if note.file_path and os.path.exists(note.file_path):
            os.remove(note.file_path)
        
        db_session.delete(note)
        db_session.commit()
        flash('Note deleted successfully!', 'success')
    else:
        flash('Note not found.', 'danger')
    
    db_session.close()
    return redirect(url_for('instructor_notes'))


@app.route('/student_notes')
def student_notes():
    user = get_current_user()
    if not user or user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    db_session = SessionLocal()
    
    student_notes = (
        db_session.query(InstructorNote)
        .join(Class, InstructorNote.class_id == Class.id)
        .join(Enrollment, Enrollment.class_id == Class.id)
        .filter(Enrollment.student_id == user.id)
        .options(joinedload(InstructorNote.classroom))
        .all()
    )
    
    db_session.close()
    
    return render_template('student-notes.html', user=user, student_notes=student_notes)

@app.route('/join_course', methods=['POST'])
def join_course():
    user = get_current_user()
    if not user or user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    class_code = request.form.get('class_code')
    print(f"DEBUG: Class code is {class_code}")
    if not class_code:
        flash('Class code is required.', 'danger')
        print(f"DEBUG: The class code is empty")
        return redirect(url_for('student_dashboard'))

    db_session = SessionLocal()

    # Check if the class exists
    course = db_session.query(Class).filter_by(code=class_code).first()
    if not course:
        flash('Invalid class code. Please try again.', 'danger')
        print(f"DEBUG:Invalid class code. Please try again.")
        db_session.close()
        return redirect(url_for('student_dashboard'))

    # Check if the student is already enrolled
    existing_enrollment = db_session.query(Enrollment).filter_by(student_id=user.id, class_id=course.id).first()
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'warning')
        db_session.close()
        return redirect(url_for('student_dashboard'))

    # Enroll the student
    new_enrollment = Enrollment(student_id=user.id, class_id=course.id)

    try:
        db_session.add(new_enrollment)
        db_session.commit()
        flash(f'Enrolled in {course.name} successfully!', 'success')
    except IntegrityError:
        db_session.rollback()
        flash('An error occurred while enrolling in the course.', 'danger')
    finally:
        db_session.close()

    return redirect(url_for('student_dashboard'))


@app.route('/instructor_classes')
def instructor_classes():
    user = get_current_user()
    if not user or user.role != 'instructor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    db_session = SessionLocal()
    # Fetch assignments and ensure classroom (class details) is loaded
    assignments_list = (
        db_session.query(Assignment)
        .options(joinedload(Assignment.classroom))  # ✅ Eagerly load related classroom data
        .all()
    )

    # Fetch all active classes for the instructor
    active_classes = (
        db_session.query(Class)
        .filter(Class.instructor_id == user.id, Class.end_date >= datetime.now().date())
        .all()
    )

    db_session.close()

    return render_template('classes.html', user=user, active_classes=active_classes)



@app.route('/instructor_assignments', methods=['GET', 'POST'])
def instructor_assignments():
    user = get_current_user()
    if not user or user.role != 'instructor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    db_session = SessionLocal()
    # Fetch assignments and ensure classroom (class details) is loaded
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        due_time = request.form.get('duetime')  # ✅ Get due time
        class_id = request.form.get('class_id')
        file = request.files.get('file')
        due_date = request.form.get('duedate')
        points = request.form.get('points')

        print("DEBUG: Form Data Received")  # ✅ Debugging
        print(f"Title: {title}, Description: {description}, Due Date: {due_date}, Due Time: {due_time}, Class ID: {class_id}")
                
        if not title or not description or not due_date or not class_id or not due_time or not points:
            print("ERROR: Missing required fields")  # ✅ Debugging
            flash('All fields are required.', 'danger')
            return redirect(url_for('instructor_assignments'))
        
        file_path = None
        if file:
            if file:
                filename = secure_filename(file.filename)
                saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(saved_path)
    
            # Store only the relative path in the database
            file_path = f"uploads/assignments/{filename}"
            print(f"DEBUG: Processed File Path: {file_path}")  # ✅ Debugging

        
            new_assignment = Assignment(
            title=title,
            description=description,
            points = int(points),
            due_date=datetime.strptime(due_date, "%Y-%m-%d").date(),
            due_time=datetime.strptime(due_time, "%H:%M").time(),
            file_path=file_path,
            class_id=int(class_id))
            print(f"DEBUG: Creating Assignment Object: {new_assignment.__dict__}")  # ✅ Debugging
        
        db_session.add(new_assignment)
        db_session.commit()
        print("DEBUG: Assignment successfully committed to DB")  # ✅ Debugging
        flash('Assignment created successfully!', 'success')
    submitted_assignments = (
        db_session.query(Submission)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .join(User, Submission.student_id == User.id)
        .options(joinedload(Submission.assignment), joinedload(Submission.student))
        .all()
    )
    assignments_list = (
        db_session.query(Assignment)
        .join(Class, Class.id == Assignment.class_id)
        .filter(Class.instructor_id == user.id)
        .options(joinedload(Assignment.classroom))
        .all()
    )
    
    instructor_classes = db_session.query(Class).filter_by(instructor_id=user.id).all()
    db_session.close()
    
    return render_template('instructor-assignments.html', user=user, submitted_assignments=submitted_assignments,assignments_list=assignments_list, instructor_classes=instructor_classes)


@app.route('/announcements')
def announcements():
    return render_template('announcements.html')

@app.route('/discussions')
def discussions():
    return render_template('discussions.html')

@app.route('/instructor-dashboard')
def instructor_dashboard():
    
    user = get_current_user()
    if not user or user.role != 'instructor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    db_session = SessionLocal()
    # Fetch instructor's classes and student enrollment count

    instructor_classes = (
        db_session.query(Class, func.count(Enrollment.id).label("student_count"))
        .outerjoin(Enrollment, Class.id == Enrollment.class_id)
        .filter(Class.instructor_id == user.id)
        .group_by(Class.id)
        .all()
    )

    # Fetch instructor's classes
    classes = db_session.query(Class).filter_by(instructor_id=user.id).all()
    
    # Total students across all instructor's classes
    total_students = (
        db_session.query(func.count(Enrollment.id))
        .join(Class, Class.id == Enrollment.class_id)
        .filter(Class.instructor_id == user.id)
        .scalar()
    )
    
    # Active classes count
    active_classes = (
        db_session.query(func.count(Class.id))
        .filter(Class.instructor_id == user.id, Class.end_date >= datetime.now().date())
        .scalar()
    )
    
    # Pending grading count (assuming submissions with no grade are pending)
    """pending_grading = (
        db_session.query(func.count(Submission.id))
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .join(Class, Class.id == Assignment.class_id)
        .filter(Class.instructor_id == user.id, Submission.grade == None)
        .scalar()
    )"""
    
    # Upcoming deadlines (assignments due in the next 7 days)
    upcoming_deadlines = (
        db_session.query(Assignment)
        .join(Class, Class.id == Assignment.class_id)
        .filter(Class.instructor_id == user.id, Assignment.due_date >= datetime.now().date())
        .order_by(Assignment.due_date.asc())
        .limit(3)
        .all()
    )

    upcoming_deadlines_count = len(upcoming_deadlines)
     # Fetch latest 3 submissions for instructor's classes
    recent_submissions = (
        db_session.query(Submission, User.name, Assignment.title, Class.name, Submission.submitted_on)
        .join(User, User.id == Submission.student_id)
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .join(Class, Class.id == Assignment.class_id)
        .filter(Class.instructor_id == user.id)
        .order_by(Submission.submitted_on.desc())
        .limit(3)
        .all()
    )
    
    # Latest 3 submissions
    '''recent_submissions = (
        db_session.query(Submission)
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .join(Class, Class.id == Assignment.class_id)
        .filter(Class.instructor_id == user.id)
        .order_by(Submission.submitted_on.desc())
        .limit(3)
        .all()
    )
    '''
    # Latest 3 announcements (assuming an Announcements table exists)
    recent_announcements = (
        db_session.query(Announcement)
        .join(Class, Class.id == Announcement.class_id)
        .filter(Class.instructor_id == user.id)
        .order_by(Announcement.posted_on.desc())
        .limit(3)
        .all()
    )
    
    # Latest 3 upcoming events (assuming an Events table exists)
    upcoming_events = (
        db_session.query(Event)
        .join(Class, Class.id == Event.class_id)
        .filter(Class.instructor_id == user.id, Event.date >= datetime.now().date())
        .order_by(Event.date.asc())
        .limit(3)
        .all()
    )
    
    db_session.close()
    name = get_name()

    return render_template(
        'instructor-dashboard.html',

        user=user,
        classes=classes,
        total_students=total_students,
        active_classes=active_classes,
        upcoming_deadlines=upcoming_deadlines_count,
        instructor_classes=instructor_classes,
        recent_submissions=recent_submissions,
        name=name,
        recent_announcements=recent_announcements,
        upcoming_events=upcoming_events
    )


@app.route('/student-dashboard')
def student_dashboard():

    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    db_session = SessionLocal()
    registered_courses = db_session.query(Enrollment).filter_by(student_id=user.id).count() if user.role == 'student' else 0
    
    assignment_count = 0
    
        
    for enrollment in db_session.query(Enrollment).filter_by(student_id=user.id):
        assignment_count += db_session.query(Assignment).filter_by(class_id=enrollment.class_id).count()
        

    # Fetch assignments due within the next 7 days
    upcoming_assignments = []
    if user.role == 'student':
        upcoming_due_date = datetime.now().date() + timedelta(days=7)
        upcoming_assignments = (
            db_session.query(Assignment)
            .join(Enrollment, Enrollment.class_id == Assignment.class_id)
            .filter(
                Enrollment.student_id == user.id, 
                Assignment.due_date >= datetime.now().date(), 
                Assignment.due_date <= upcoming_due_date
            )
            .count()
        )
    # Fetch assignments due within the next 7 days
    upcoming_deadlines = []
    if user.role == 'student':
        upcoming_due_date = datetime.now().date() + timedelta(days=7)
        subquery = db_session.query(Enrollment.class_id).filter_by(student_id=user.id).subquery()
        upcoming_deadlines = (
            db_session.query(Assignment)
            .filter(Assignment.class_id.in_(subquery), 
                    and_(Assignment.due_date >= datetime.now().date(), 
                         Assignment.due_date <= upcoming_due_date))
            .order_by(Assignment.due_date.asc())
            .all()
        )


    rows = db_session.query(Class.name, Class.id, Class.start_date).join(Enrollment, Class.id == Enrollment.class_id).filter_by(student_id=user.id).all()

    registered_classes = [{'name': row[0], 'id': row[1], 'start_date':row[2]} for row in rows]

    name = get_name()
    db_session.close()

    return render_template('dashboard.html', user=user, 
                           upcoming_deadlines=upcoming_deadlines,
                           registered_courses=registered_courses, 
                           upcoming_assignments=upcoming_assignments, 
                           name=name, 
                           assignment_count=assignment_count,
                           registered_classes=registered_classes)

def get_name():
    if 'user_id' in session:
        db_session = SessionLocal()
        user = db_session.query(User.name).filter_by(id=session['user_id']).first()
        db_session.close()
        return user.name
    return "Guest"
def get_current_user():
    if 'user_id' in session:
        db_session = SessionLocal()
        user = db_session.query(User).filter_by(id=session['user_id']).first()
        db_session.close()
        return user
    return None

@app.route('/create-assignment')
def create_assignment():
    return render_template('create-assignment.html')

@app.route('/create-class')
def create_class():
    return render_template('create-class.html')

@app.route('/resources')
def view_resources():
    return render_template('resources.html', resources=resources)

@app.route('/upload-resource', methods=['POST'])
def upload_resource():
    if request.method == 'POST':
        title = request.form.get('resourceTitle')
        category = request.form.get('resourceCategory')
        file = request.files.get('resourceFile')
        file_path = None
        
        if file and file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            resources.append({'title': title, 'category': category, 'file_path': file.filename})
        
        return redirect(url_for('view_resources'))

@app.route('/download_file/<filename>')
def download_file(filename):
    file_path = os.path.join(os.path.abspath(app.config['UPLOAD_FOLDER']), filename)
    print(f"DEBUG: Serving file from {file_path}")  # ✅ Debugging
    return send_from_directory(os.path.abspath(app.config['UPLOAD_FOLDER']), filename, as_attachment=True)


@app.route('/submit_assignment', methods=['POST'])
def submit_assignment():
    user = get_current_user()
    if not user or user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    assignment_id = request.form.get('assignment_id')
    file = request.files.get('file')
    
    if not assignment_id or not file:
        flash('All fields are required.', 'danger')
        return redirect(url_for('assignments'))
    
    db_session = SessionLocal()
    filename = secure_filename(file.filename)
    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(saved_path)
    
    submission = Submission(
        assignment_id=int(assignment_id),
        student_id=user.id,
        submitted_on=datetime.utcnow(),
        file_path=f"uploads/assignments/{filename}"
    )
    
    db_session.add(submission)
    db_session.commit()
    db_session.close()
    
    flash('Assignment submitted successfully!', 'success')
    return redirect(url_for('assignments'))

@app.route('/submit-class', methods=['POST'])
def submit_class():
    if request.method == 'POST':
        class_name = request.form.get('className')
        class_code = request.form.get('classCode')
        description = request.form.get('description')
        start_date = request.form.get('startDate')
        end_date = request.form.get('endDate')
        schedule_day = request.form.get('scheduleDay')
        start_time = request.form.get('startTime')
        end_time = request.form.get('endTime')
        max_students = request.form.get('maxStudents')
        prerequisites = request.form.get('prerequisites')
        allow_late = 'allowLateSubmissions' in request.form
        enable_discussions = 'enableDiscussions' in request.form
        auto_enroll = 'autoEnroll' in request.form
        
        # Handle syllabus upload
        syllabus = request.files.get('syllabus')
        syllabus_path = None
        if syllabus and syllabus.filename:
            syllabus_path = os.path.join(app.config['UPLOAD_FOLDER'], syllabus.filename)
            syllabus.save(syllabus_path)
        
        # Log the received data
        print(f"New Class Created: {class_name} ({class_code})")
        print(f"Description: {description}, Start: {start_date}, End: {end_date}, Max Students: {max_students}")
        print(f"Schedule: {schedule_day}, {start_time} - {end_time}, Prerequisites: {prerequisites}")
        print(f"Allow Late: {allow_late}, Discussions: {enable_discussions}, Auto-Enroll: {auto_enroll}")
        print(f"Syllabus File: {syllabus_path}")
        
        return redirect(url_for('create_class'))
########## Authentication Routes ##################################################################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form.get('email')
        password = request.form.get('password')
        db_session = SessionLocal()
        user = db_session.query(User).filter_by(email=email).first()
        db_session.close()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            flash('Login successful!', 'success')
            if user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.role == 'instructor':
                return redirect(url_for('instructor_dashboard'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('signup_login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        #DEBUG 
        print(f" Name: {name}")
        print(f" Email: {email}")
        print(f" Password: {password}")
        print(f" Role: {role}")

        db_session = SessionLocal()
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password_hash=hashed_password, role=role)
        try:
            db_session.add(new_user)
            db_session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db_session.rollback()
            flash('Email already registered!', 'danger')
        finally:
            db_session.close()
    return render_template('signup_login.html')


@app.route('/grades')
def grades():
    user = get_current_user()
    if not user or user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    db_session = SessionLocal()
    
    graded_submissions = (
        db_session.query(Submission)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .filter(Submission.student_id == user.id, Submission.grade != None)
        .options(joinedload(Submission.assignment))
        .all()
    )
    
    db_session.close()
    
    return render_template('grades.html', user=user, graded_submissions=graded_submissions)


@app.route('/courses')
def courses():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    db_session = SessionLocal()
    enrolled_courses = []

    if user.role == 'student':
        enrolled_courses = (
            db_session.query(Class)
            .join(Enrollment, Enrollment.class_id == Class.id)
            .options(joinedload(Class.instructor))  # Ensures instructor data is loaded
            .filter(Enrollment.student_id == user.id)
            .all()
        )

    db_session.close()
    
    return render_template('courses.html', user=user, enrolled_courses=enrolled_courses)

@app.route('/assignments', methods=['GET', 'POST'])
def assignments():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    db_session = SessionLocal()
    assignments_list = []
    
    if user.role == 'student':
        assignments_list = (
            db_session.query(Assignment)
            .join(Class, Assignment.class_id == Class.id)
            .join(Enrollment, Enrollment.class_id == Class.id)
            .filter(Enrollment.student_id == user.id)
            .options(joinedload(Assignment.classroom))  # Ensure class details are loaded properly
            .all()
        )

    db_session.close()
    
    return render_template('assignments.html', user=user, assignments_list=assignments_list)

@app.route('/calendar')
def calendar():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    db_session = SessionLocal() 

    events = []
    if user.role == 'student':
        # Fetch assignments
        assignments = (
            db_session.query(Assignment, Class)
            .join(Class, Assignment.class_id == Class.id)
            .join(Enrollment, Enrollment.class_id == Class.id)
            .filter(Enrollment.student_id == user.id)
            .all()
        )
        
        # Add assignments to events list
        for assignment, course in assignments:
            status = "Upcoming" if assignment.due_date >= datetime.now().date() else "Important"
            events.append({
                "title": f"{assignment.title} Due",
                "date": assignment.due_date.strftime('%B %d'),
                "status": status,
                "badge_class": "bg-warning" if status == "Upcoming" else "bg-danger"
            })

        # Fetch exams (assuming they are stored in the `exams` table)
        exams = [
            {"title": "Midterm Exam", "date": "March 15", "status": "Scheduled", "badge_class": "bg-primary"},
            {"title": "Final Project Submission", "date": "April 10", "status": "Important", "badge_class": "bg-danger"}
        ]
        events.extend(exams)  # Add exams to the events list

    db_session.close()
    return render_template('calendar.html', user=user, events=events)



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
#####################################################################################################################################
if __name__ == '__main__':
    app.run(debug=True)
