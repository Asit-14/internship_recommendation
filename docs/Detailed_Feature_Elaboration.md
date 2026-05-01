# Detailed Feature Elaboration: National Internship Portal

## Table of Contents
1. [Introduction to System Features](#introduction)
2. [Identity & Access Management (IAM)](#iam)
   - 2.1 Multi-Role Authentication
   - 2.2 JWT-Based Session Management
   - 2.3 Role-Based Access Control (RBAC)
3. [Student Module: The Applicant Journey](#student-module)
   - 3.1 AI-Powered Resume Analysis
   - 3.2 Skill Extraction & Profile Building
   - 3.3 Intelligence Layer: Recommendation Engine
   - 3.4 Application Management Lifecycle
4. [Company Module: Recruiter Tools](#company-module)
   - 4.1 Internship Lifecycle Management (CRUD)
   - 4.2 Applicant Pipeline Tracking
   - 4.3 Hiring Workflow Status Management
5. [Admin Module: Platform Governance](#admin-module)
   - 5.1 Content Moderation & Verification
   - 5.2 System-Wide Analytics & Metrics
6. [Core Technical Engines](#technical-engines)
   - 6.1 NLP Resume Parsing Engine
   - 6.2 ML Recommendation Logic (TF-IDF & Cosine Similarity)
7. [Advanced Security & Data Integrity](#security)
   - 7.1 Secure Account Deletion (Danger Zone)
   - 7.2 Password Security & Data Sanitization
8. [UI/UX Design Philosophy](#uiux)
   - 8.1 Responsive Design System
   - 8.2 Micro-interactions & Visual Feedback
   - 8.3 Internationalization (i18n)

---

<a name="introduction"></a>
## 1. Introduction to System Features
The National Internship Portal is not just a job board; it is an intelligent recruitment ecosystem. The primary objective of the feature set is to minimize the friction between discovery and engagement. By automating the skill-matching process, the system ensures that students only see relevant opportunities and companies only receive qualified leads. This section provides a 360-degree view of how these features interact to form a cohesive, high-performance platform.

---

<a name="iam"></a>
## 2. Identity & Access Management (IAM)

### 2.1 Multi-Role Authentication
The portal supports three distinct user identities: **Student**, **Company**, and **Admin**. 
- **Registration**: Custom registration flows for students and companies ensure that the necessary metadata (e.g., college details for students, company registration numbers for recruiters) is captured at source.
- **Login**: A unified login interface that dynamically adapts based on the user's role stored in the database.

### 2.2 JWT-Based Session Management
Security is handled through JSON Web Tokens (JWT). 
- **Statelessness**: The backend (FastAPI) remains stateless, which allows for effortless horizontal scaling.
- **Security**: Tokens are stored in HTTP-only cookies on the frontend (Next.js) to prevent Cross-Site Scripting (XSS) attacks.
- **Expiration**: Short-lived access tokens combined with secure logout logic ensure that sessions are tightly controlled.

### 2.3 Role-Based Access Control (RBAC)
RBAC is the backbone of the system's security. Using FastAPI's dependency injection system, every API endpoint is protected by a `require_role` guard.
- **student**: Access to `/recommendations`, `/apply`, and resume upload.
- **company**: Access to `/internships` (POST/PUT/DELETE) and `/applicants`.
- **admin**: Access to `/verify-company` and global analytics.

---

<a name="student-module"></a>
## 3. Student Module: The Applicant Journey

### 3.1 AI-Powered Resume Analysis
This is the "hero" feature for students. Instead of manually filling out skill tags, the student uploads a PDF or DOCX resume. 
- **Extraction**: The system uses `PyPDF2` or `pdfminer` to extract raw text.
- **Processing**: Regex and NLP patterns identify technical skills (e.g., "Python", "React", "SQL") and soft skills.
- **Automation**: Extracted skills are automatically populated in the user's profile, saving time and ensuring accuracy.

### 3.2 Skill Extraction & Profile Building
The student profile acts as a digital CV. 
- **Dynamic Skill Tags**: Students can manually add or remove skills that the AI might have missed.
- **Academic Tracking**: Fields for CGPA, graduation year, and college name help recruiters filter for specific cohorts.
- **Resume Persistence**: Resumes are stored securely in the `uploads/` directory, with filenames obfuscated to protect privacy.

### 3.3 Intelligence Layer: Recommendation Engine
The heart of the project. The recommendation engine provides a curated feed of internships.
- **Algorithm**: Uses **TF-IDF (Term Frequency-Inverse Document Frequency)** to vectorise user skills and internship requirements.
- **Matching**: **Cosine Similarity** calculates the mathematical distance between these vectors.
- **Scoring**: Internships are ranked; only those with a high similarity score (e.g., >0.6) are presented as "Recommended" to the student.

### 3.4 Application Management Lifecycle
Applying is a one-click process.
- **Workflow**: `Applied` -> `Under Review` -> `Shortlisted` -> `Selected / Rejected`.
- **Real-time Status**: A dedicated "My Applications" tab allows students to see exactly where they stand in the hiring pipeline for every role they've applied to.

---

<a name="company-module"></a>
## 4. Company Module: Recruiter Tools

### 4.1 Internship Lifecycle Management (CRUD)
Companies have full control over their listings.
- **Creation**: Recruiters can specify role titles, descriptions, sectors, duration, and stipend.
- **Sector Categorization**: Tags like "Software Development", "Marketing", or "Data Science" help in both filtering and recommendation.
- **Active/Inactive Status**: Listings can be toggled on/off without being deleted, allowing companies to pause recruitment easily.

### 4.2 Applicant Pipeline Tracking
The applicant dashboard provides a unified view of all candidates.
- **Filtering**: Companies can sort applicants by their "Match Score" (calculated by the AI) to prioritize top talent.
- **Profile Review**: Recruiters can view full candidate profiles and download resumes directly from the dashboard.

### 4.3 Hiring Workflow Status Management
Recruiters can move candidates through a multi-stage pipeline.
- **Transitions**: Updating a candidate's status (e.g., from `Applied` to `Shortlisted`) triggers a state change in the database.
- **Transparency**: This change is instantly reflected on the student's dashboard, maintaining clear communication.

---

<a name="admin-module"></a>
## 5. Admin Module: Platform Governance

### 5.1 Content Moderation & Verification
Admins act as the "quality control" layer.
- **Company Verification**: Every new company registration must be reviewed by an admin before the company can post internships. This prevents spam and fraudulent listings.
- **User Management**: Admins have the authority to suspend or delete users who violate platform terms.

### 5.2 System-Wide Analytics & Metrics
The Admin Dashboard provides high-level insights into platform growth.
- **KPIs**: Total active users, total successful placements, most popular internship sectors, and average match scores.
- **Data Visualization**: Charts and graphs help admins understand trends and make informed decisions about platform development.

---

<a name="technical-engines"></a>
## 6. Core Technical Engines

### 6.1 NLP Resume Parsing Engine
The parsing engine follows a three-step process:
1.  **Text Extraction**: Converting binary PDF/DOCX data into raw strings.
2.  **Entity Extraction**: Identifying skill entities using a comprehensive dictionary of technical terms.
3.  **Sanitization**: Cleaning the extracted text of special characters and boilerplate language (e.g., headers, footers).

### 6.2 ML Recommendation Logic
The recommendation logic is mathematically grounded:
- **Vectorization**: The `TfidfVectorizer` from `scikit-learn` converts text descriptions into numerical vectors.
- **Similarity Calculation**: `cosine_similarity(user_vector, job_vector)` returns a value between 0 and 1.
- **Thresholding**: Only internships above a specific threshold are served to the user, ensuring high-quality matches.

---

<a name="security"></a>
## 7. Advanced Security & Data Integrity

### 7.1 Secure Account Deletion (Danger Zone)
A premium feature that ensures user privacy and data rights.
- **The "Danger Zone"**: A dedicated section in the profile settings with high-contrast UI (red borders).
- **Two-Factor Confirmation**: Requires the user's password AND a text confirmation ("DELETE") to prevent accidental triggers.
- **Soft Delete Logic**: The system sets `is_active = false` and `deleted_at = timestamp`. This allows for a "grace period" while immediately revoking access.
- **Cascade Deactivation**: When a company deletes their account, all their posted internships are automatically set to inactive, maintaining platform cleanliness.

### 7.2 Password Security & Data Sanitization
- **Hashing**: All passwords are hashed using `bcrypt`, ensuring they are unreadable even in the event of a database leak.
- **SQL Injection Prevention**: The use of SQLAlchemy ORM ensures that all queries are parameterized, neutralizing SQL injection threats.
- **CORS Policies**: Restricted origins prevent unauthorized third-party applications from accessing the APIs.

---

<a name="uiux"></a>
## 8. UI/UX Design Philosophy

### 8.1 Responsive Design System
Built using **Tailwind CSS**, the portal is fully mobile-responsive. 
- **Grid Layouts**: The dashboard uses CSS Grid and Flexbox to adapt from desktop monitors to mobile screens.
- **Premium Components**: Custom-built cards, buttons, and modals provide a high-end "SaaS" feel.

### 8.2 Micro-interactions & Visual Feedback
- **Loading States**: Skeletons and spinners (using `framer-motion` or standard CSS animations) ensure users never feel the app is stuck.
- **Toasts**: Real-time feedback for actions like "Application Submitted" or "Profile Updated" using a custom notification system.

### 8.3 Internationalization (i18n)
The system supports multiple languages (English, Bengali, Hindi, etc.).
- **Persistence**: User language preference is stored in local storage and cookies, ensuring a consistent experience across sessions.
- **Lazy Loading**: Translation files are loaded only when needed, maintaining fast initial page loads.

---

## Conclusion
The features of the National Internship Portal are meticulously engineered to provide a professional, secure, and intelligent experience for all users. By combining modern web technologies with AI-driven logic, the platform sets a new standard for internship recruitment systems.
