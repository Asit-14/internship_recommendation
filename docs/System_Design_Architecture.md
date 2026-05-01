# System Design & Architecture: National Internship Portal

This document provides a comprehensive breakdown of the High-Level Design (HLD) and Low-Level Design (LLD) of the National Internship Portal.

---

## 1. High-Level Design (HLD)

The High-Level Design focuses on the overall architecture and how different layers of the system communicate. We use a **Decoupled Three-Tier Architecture**.

### 1.1 Architecture Diagram

```mermaid
graph TD
    subgraph Client_Side [Frontend - Next.js]
        UI[User Interface]
        TQ[TanStack Query - State Management]
        Axios[API Client]
    end

    subgraph Server_Side [Backend - FastAPI]
        API[REST Endpoints]
        Service[Business Logic Layer]
        Repo[Data Access Layer]
        AI[AI/ML Engine - Scikit-learn]
        Parser[Resume Parser - PyPDF2]
    end

    subgraph Data_Layer [Database - PostgreSQL]
        DB[(PostgreSQL)]
    end

    UI <--> TQ
    TQ <--> Axios
    Axios <--> API
    API <--> Service
    Service <--> Repo
    Service <--> AI
    Service <--> Parser
    Repo <--> DB
```

### 1.2 Layer Explanation (Simple Language)
1.  **Frontend (Next.js)**: This is what the user sees. It's like the "skin" of the project. It handles how the buttons look, the animations, and it talks to the backend to get data.
2.  **Backend (FastAPI)**: This is the "brain." It receives requests from the frontend, checks if the user is logged in (security), runs the AI matching logic, and saves things to the database.
3.  **Database (PostgreSQL)**: This is the "memory." It permanently stores all user info, internship posts, and application history so they aren't lost when you refresh the page.

---

## 2. Low-Level Design (LLD)

LLD focuses on the internal structure of the components, specifically the database schema and the sequence of actions.

### 2.1 Database Schema (ER Diagram)

```mermaid
erDiagram
    USER ||--o{ INTERNSHIP : "creates (Company)"
    USER ||--o{ APPLICATION : "submits (Student)"
    USER ||--o| CERTIFICATE : "receives"
    INTERNSHIP ||--o{ APPLICATION : "has"
    APPLICATION ||--o| CERTIFICATE : "generates"

    USER {
        int id PK
        string name
        string email UK
        string password_hash
        string role "student/company/admin"
        json skills
        boolean is_active
    }

    INTERNSHIP {
        int id PK
        string title
        text description
        int created_by FK
        boolean is_active
    }

    APPLICATION {
        int id PK
        int user_id FK
        int internship_id FK
        string status "Applied/Shortlisted/Rejected"
        datetime applied_at
    }
```

### 2.2 Core Workflows (Sequence Diagrams)

#### A. Authentication & Login Flow
How a user securely enters the system.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant DB

    User->>Frontend: Enter Email/Password
    Frontend->>Backend: POST /auth/login
    Backend->>DB: Fetch user by Email
    DB-->>Backend: User Data (Hashed Pass)
    Backend->>Backend: Verify Password (bcrypt)
    Backend->>Backend: Generate JWT Token
    Backend-->>Frontend: Success (Token + User Info)
    Frontend->>User: Redirect to Dashboard
```

#### B. AI Recommendation Flow
How the system suggests the right jobs.

```mermaid
sequenceDiagram
    participant Student
    participant Backend
    participant AI_Engine
    participant DB

    Student->>Backend: View Recommendations
    Backend->>DB: Fetch Student Skills
    Backend->>DB: Fetch Active Internships
    Backend->>AI_Engine: Match(Skills, Jobs)
    AI_Engine->>AI_Engine: Vectorize & Cosine Similarity
    AI_Engine-->>Backend: Ranked List of Jobs
    Backend-->>Student: Display Top Matches
```

---

## 3. Detailed Flow Explanation (Simple Language)

### 3.1 The "Apply" Flow
1.  **Student Action**: The student finds a job they like and clicks "Apply."
2.  **Backend Check**: The backend checks if the student has already applied to this job (to prevent duplicates).
3.  **Creation**: A new "Application" record is created in the database with a status of `APPLIED`.
4.  **Notification**: The recruiter (company) immediately sees the new applicant on their dashboard.

### 3.2 The "Resume Parsing" Flow
1.  **Upload**: Student uploads a PDF resume.
2.  **Reading**: The backend "reads" the PDF and turns it into raw text.
3.  **Extracting**: The AI looks for keywords (like "Java", "Python", "React").
4.  **Saving**: These keywords are saved as "Skills" in the student's profile.
5.  **Updating**: The recommendation list automatically refreshes to show better jobs based on these new skills.

### 3.3 The "Delete Account" (Safety) Flow
1.  **Request**: User goes to the "Danger Zone" and clicks Delete.
2.  **Validation**: They must type their password and the word "DELETE."
3.  **Deactivation**: The system doesn't immediately erase everything (for safety); it just marks the user as "Inactive."
4.  **Cleanup**: If it's a company, all their job posts are automatically hidden so no one else applies to them.

---

## 4. Component Breakdown

| Component | Responsibility | Technology |
| :--- | :--- | :--- |
| **Auth Manager** | Login, Signup, and Permissions | JWT & Bcrypt |
| **Matching Engine** | Calculating how good a student is for a job | Scikit-learn (TF-IDF) |
| **File Server** | Storing and serving resumes safely | Local Storage / FastAPI |
| **State Manager** | Keeping the UI in sync with the DB | TanStack Query |
| **Router** | Navigating between pages (Home, Profile, etc.) | Next.js App Router |

---

## Conclusion
This design ensures that the National Internship Portal is **Scalable** (can handle more users), **Secure** (protects data), and **Intelligent** (provides smart matches). The use of HLD and LLD patterns guarantees a professional structure suitable for large-scale development.
