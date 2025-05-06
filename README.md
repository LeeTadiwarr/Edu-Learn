# EduLearn - Learning Management System

## Overview

EduLearn is a web-based Learning Management System (LMS) designed to provide a platform for online education[cite: 1, 34]. It supports features for both instructors and students, including course management, assignments, grading, announcements, discussions, and resource sharing[cite: 1].

## Features

### Core Functionalities

* **User Authentication and Authorization:** Secure login and signup system with role-based access control (student or instructor)[cite: 1].
* **Course Management:**
    * Instructors can create, manage, and schedule classes with details like name, code, description, schedule, and enrollment limits[cite: 1].
    * Students can view available courses and enroll in them using class codes[cite: 1].
* **Assignment Management:**
    * Instructors can create assignments with titles, descriptions, due dates/times, and optional file attachments[cite: 1].
    * Students can view assignments, download attached files, and submit their work[cite: 1].
* **Grade Management:**
    * Instructors can grade submitted assignments and provide feedback to students[cite: 1].
    * Students can view their grades and instructor feedback[cite: 1].
* **Communication Tools:**
    * Announcements: Instructors can post announcements to classes[cite: 1].
    * Discussions:  Platform for class discussions (implementation may vary)[cite: 1].
* **Resource Sharing:** Instructors can upload and organize learning resources (e.g., lecture notes, assignments)[cite: 1].
* **Calendar:** A calendar view to display upcoming events and deadlines[cite: 1].
* **File Handling:** Uploading and downloading files for assignments and resources[cite: 1].

### Technology Stack

* **Backend:** Python (Flask) [cite: 1]
* **Database:** SQLite (default) [cite: 1]
* **Frontend:** HTML, CSS, JavaScript, Bootstrap [cite: 1, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58]
* **Libraries:** Werkzeug, SQLAlchemy, Flask-SQLAlchemy, etc. (see `requirements.txt`) [cite: 1, 1]

### Database Models

The application uses the following database models (defined in `app.py`)[cite: 1]:

* **User:** Stores user information (name, email, password, role)[cite: 1].
* **Class:** Stores class details (name, code, description, schedule, etc.)[cite: 1].
* **Assignment:** Stores assignment information (title, description, due date, etc.)[cite: 1].
* **Submission:** Stores student assignment submissions (student, assignment, file, grade, feedback)[cite: 1].
* **Announcement:** Stores announcements posted by instructors[cite: 1].
* **Event:** Stores events related to classes[cite: 1].
* **Enrollment:** Tracks student enrollments in classes[cite: 1].
* **Resource:** Stores learning resources[cite: 1].
* **InstructorNote:** Stores notes uploaded by instructors[cite: 1].

### Setup Instructions

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Database Setup:** The application uses SQLite by default. The database file (`edulearn.db`) will be created automatically in the application's root directory when the application is run for the first time[cite: 1].
3.  **Environment Variables:** It's recommended to set a `SECRET_KEY` environment variable for security. If not set, a default key is used[cite: 1].
    ```bash
    export SECRET_KEY='your_secret_key'
    ```
4.  **Run the Application:**
    ```bash
    python app.py
    ```
5.  **Access the Application:** Open your web browser and navigate to the specified address (usually `http://127.0.0.1:5000/`).

### Important Notes

* The application includes basic user authentication (login/signup)[cite: 1].
* File uploads are stored in the `uploads/` directory[cite: 1].
* Some features (like discussions, advanced user profile management, etc.) might require further development.
