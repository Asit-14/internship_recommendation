# Internship Platform - Project Overview

## 1. PROJECT OVERVIEW

The Internship Platform is an AI-powered comprehensive internship recommendation and management system. It serves as a centralized hub connecting students with companies, streamlining the entire internship lifecycle from posting opportunities to applicant tracking. 

The platform leverages AI to analyze student resumes, extract core skills, and provide highly accurate internship recommendations using a match scoring system.

---

## 2. TECH STACK

**Frontend:**
* **Next.js 15**: React framework for server-side rendering and static generation.
* **TypeScript**: For robust type-safe code across the entire application.
* **Tailwind CSS**: Utility-first CSS framework for rapid and responsive UI development.
* **TanStack Query**: Powerful asynchronous state management and data fetching.
* **Lucide React**: Crisp iconography for the user interface.

**Backend:**
* **FastAPI**: Modern, fast, high-performance web framework for building APIs with Python.
* **Python 3.10+**: Core programming language for backend logic and AI processing.
* **Pydantic**: Data validation and settings management using Python type annotations.
* **SQLAlchemy**: Powerful ORM for database interactions.

**Database:**
* **PostgreSQL / SQLite**: Relational database storage for users, internships, and applications.

**Authentication:**
* **JWT-based Authentication**: Secure, stateless token-based authentication with role-based access control (RBAC).

**Other Technologies:**
* **PyPDF2 / PDFMiner**: Resume parsing libraries for extracting text from uploaded PDFs.
* **Scikit-learn**: Used for TF-IDF vectorization and cosine similarity calculations in the AI recommendation engine.
* **Multipart Form Data**: Handled natively by FastAPI for secure resume uploads.

---

## 3. CORE FEATURES

**Authentication:**
* **Login & Registration**: Secure onboarding for both students and companies.
* **Role-based Access Control (RBAC)**: Distinct views and capabilities for `student`, `company`, and `admin` roles.

**Student Features:**
* **Resume Upload & Analysis**: Upload resumes to automatically extract skills.
* **Internship Recommendations**: AI-driven suggestions based on extracted skills.
* **Apply to Internships**: One-click application process.
* **Track Application Status**: Real-time visibility into application progress (pending, accepted, rejected).

**Company Features:**
* **Create Internships**: Post new opportunities with descriptions, requirements, and stipends.
* **Manage Listings (CRUD)**: Update or delete existing internship postings.
* **View Applicants**: See all students who have applied to specific listings.
* **Update Application Status**: Move candidates through the hiring pipeline.

**Admin Features:**
* **Manage Users**: View and moderate registered students and companies.
* **Manage Internships**: Oversee all platform activity and moderate listings.
* **View Analytics**: Access platform-wide metrics via the admin dashboard.

---

## 4. AI & SMART FEATURES

* **Resume Parsing**: Automatically extracts raw text from PDF documents.
* **Skill Extraction**: Identifies key technical and soft skills using NLP techniques.
* **Recommendation Engine**: Matches student profiles against available internships.
* **Match Scoring System**: Calculates a percentage match based on TF-IDF cosine similarity to rank opportunities.

---

## 5. SYSTEM ARCHITECTURE

* **Frontend → API → Backend → Database**: A decoupled architecture where the Next.js frontend communicates with the FastAPI backend via RESTful endpoints, which securely interacts with the relational database.
* **Role-based Access Control**: JWT tokens contain role claims, enforcing strict access restrictions at the API route level.
* **REST API Structure**: Clean, versioned endpoints grouped logically by business domain (`/api/v1/auth`, `/api/v1/internships`, etc.).

---

## 6. WORKFLOW

1. **Student Onboarding**: Student registers and uploads their resume.
2. **AI Processing**: Backend processes the resume, extracts skills, and builds a profile.
3. **Matching**: The Recommendation Engine compares the profile against all active internships and returns a scored list of recommendations.
4. **Application**: Student applies to an internship.
5. **Company Review**: Company logs in, views the applicant pool, reviews profiles, and updates the status.
6. **Notification**: The updated status is reflected on the student's dashboard.

---

## 7. FUTURE IMPROVEMENTS

* **Notifications System**: Real-time email and in-app alerts for status updates.
* **Advanced AI Matching**: Integration with Large Language Models (LLMs) for deeper semantic understanding of resumes.
* **Real-time Updates**: WebSockets for instant messaging between companies and applicants.
* **Company Verification System**: Automated business verification to ensure platform safety and quality.
