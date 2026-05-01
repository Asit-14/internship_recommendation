# National Internship Portal – AI Powered Internship Recommendation System

**A Final Year Project Report**
Submitted in partial fulfillment of the requirements for the award of the degree of
**Bachelor of Technology**
in
**Computer Science & Engineering**

---

**Submitted By:**
[Student Name 1] ([Roll Number 1])
[Student Name 2] ([Roll Number 2])
[Student Name 3] ([Roll Number 3])

**Project Guide:**
[Guide Name]

**Session:**
2025–2026

**Department of Computer Science & Engineering**
**[College Name]**
**[University Name]**

---

## DECLARATION

This is to certify that the project report entitled **"National Internship Portal – AI Powered Internship Recommendation System"** which is submitted by us for the award of the degree of **Bachelor of Technology in Computer Science & Engineering** to **[University Name]** comprises only our original work and due acknowledgment has been made in the text to all other material used.

**Date:**  
**Place:**  

**Signatures:**

1. ____________________  
   **[Student Name 1]**  
   Roll No: [Roll Number 1]

2. ____________________  
   **[Student Name 2]**  
   Roll No: [Roll Number 2]

3. ____________________  
   **[Student Name 3]**  
   Roll No: [Roll Number 3]

---

## CERTIFICATE

This is to certify that **[Student Name 1]**, **[Student Name 2]**, and **[Student Name 3]** have carried out the project work presented in this report entitled **"National Internship Portal – AI Powered Internship Recommendation System"** for the award of the degree of **Bachelor of Technology in Computer Science & Engineering** from **[University Name]** under my/our supervision. 

The report embodies the result of original work and study carried out by the students themselves and the contents of the report do not form the basis for the award of any other degree of the candidates or anybody else.

<br><br>

**Project Coordinator**  
[Coordinator Name]

**Project Guide**  
[Guide Name]

<br><br>

**External Examiner**  
____________________

**Internal Examiner**  
____________________

---

## ACKNOWLEDGMENT

We take this opportunity to express our sincere thanks and deep gratitude to our project coordinator **[Coordinator Name]** and our project guide **[Guide Name]**, who shared their time and knowledge with us and helped in completing this project successfully.

It is with immense pleasure and heartfelt gratitude that we express our sincere thanks to all the Professors, Staff, and Lab Assistants for their supervision, constant encouragement, inspiration, and guidance. Their inspiring suggestions and timely guidance enabled us to perceive the various aspects of the project with a new vision.

We are very much grateful to our parents for their support and the faith they showed in us. Last but not least, we thank our friends for being there round the clock whenever we needed them.

**[Student Name 1]**  
**[Student Name 2]**  
**[Student Name 3]**

---

## TABLE OF CONTENT

1. **Chapter 1: Abstract**
2. **Chapter 2: Introduction**
   - 2.1 AI-Based Recommendation System
   - 2.2 Content-Based Matching Approach
3. **Chapter 3: System Overview & Features**
   - 3.1 Objective & Personalization
   - 3.2 Optimization of Recruitment Process
   - 3.3 Security, Privacy, and Scalability
4. **Chapter 4: Methodology**
   - 4.1 Agile Methodology Framework
5. **Chapter 5: Literature Survey**
   - 5.1 Recommendation Systems using Content-Based Filtering
   - 5.2 Collaborative Filtering-Based Systems in Job Markets
   - 5.3 AI and NLP in Recruitment Systems
   - 5.4 Conclusion of Literature Survey
6. **Chapter 6: System Requirements Specification**
   - 6.1 Hardware & Software Requirements
   - 6.2 Key Python Libraries & Tech Stack
7. **Chapter 7: System Analysis and Design**
   - 7.1 System Architecture
   - 7.2 Data Flow & Processing Pipeline
8. **Chapter 8: Design Implementation (Deep Dive)**
   - 8.1 Introduction to Technologies (FastAPI, Next.js)
   - 8.2 AI & NLP Implementation Logic
   - 8.3 Interface Implementation
9. **Chapter 9: Testing**
   - 9.1 Unit, Integration, and System Testing
10. **Chapter 10: Result Review**
11. **Chapter 11: Conclusion**
12. **Chapter 12: Future Scope**
13. **Chapter 13: References**

---

## CHAPTER 1: ABSTRACT

Securing a relevant internship is a crucial stepping stone for students entering the technical workforce; however, most online job platforms focus on mass listing availability rather than personalized guidance. This paper presents the **National Internship Portal**, an AI-powered web-based recruitment and discovery system that personalizes the internship search using Natural Language Processing (NLP), machine learning-based recommendation systems, analytics-driven application tracking, and an automated resume parser. 

The system enhances the candidate experience by eliminating the need for manual data entry. It processes uploaded PDF/DOCX resumes, extracting key technical and soft skills through NLP techniques, allowing users to focus more on preparation rather than profile management. It also provides adaptive internship recommendations based on the mathematical similarity between the extracted user skills and the specific requirements of company listings, ensuring a structured, relevant, and efficient discovery path. 

Additionally, integrated tools for companies allow recruiters to manage the application lifecycle, track candidate statuses, and filter applicants based on AI-generated match scores. By combining intelligent skill matching with robust, secure web architecture, the National Internship Portal bridges the gap between traditional job boards and highly personalized recruitment agents, ultimately improving hiring efficiency, candidate satisfaction, and placement success rates.

---

## CHAPTER 2: INTRODUCTION

The National Internship Portal is an intelligent web-based recruitment ecosystem designed to enhance the way students discover opportunities and companies hire talent. Traditional platforms mainly provide a large collection of job postings but lack personalized filtering, automated skill extraction, and real-time application assistance. This often leads to "application fatigue" for students and a high "noise-to-signal" ratio for recruiters, resulting in inefficient hiring cycles.

The National Internship Portal overcomes these limitations by integrating Artificial Intelligence, Machine Learning, and advanced backend analytics to create a highly personalized matching experience. It analyzes user resumes, identifies core competencies, mathematically compares them to available internships, and recommends the most relevant roles. The platform acts as a digital career mentor, helping users find roles that actually fit their skills while providing companies with a pre-sorted list of qualified candidates.

### AI-Based Recommendation System in the Portal
The recommendation system is designed to intelligently suggest internships based on a user's verified skill set. Instead of recommending random or popular listings, the system focuses on personalized relevance by considering factors such as extracted technical skills, preferred roles, and required proficiencies. This system ensures that users are presented with opportunities where they have the highest mathematical probability of success.

### Content-Based Matching Approach
Content-based recommendation in the National Internship Portal suggests internships based on the characteristics of the user's profile and the text of the job description. It analyzes features such as technical tags (e.g., Python, React, SQL), domain expertise, and role responsibilities.

**Key Components of the Content-Based System:**
1. **User Profile Vectorization:** A user profile is mathematically represented based on the skills extracted from their resume.
2. **Internship Profile Vectorization:** Each internship is categorized and transformed into a vector based on its required skills and description.
3. **Matching Mechanism:** The system utilizes **TF-IDF (Term Frequency-Inverse Document Frequency)** and **Cosine Similarity** to compare user vectors with internship vectors, assigning a percentage-based match score to recommend highly relevant roles.

---

## CHAPTER 3: SYSTEM OVERVIEW & FEATURES

### Objective
The primary objective of the National Internship Portal is to create an intelligent and scalable recruitment ecosystem for students seeking early-career opportunities and companies looking for verified talent. The system is designed to improve discovery quality, application tracking, and engagement through integrated AI processing, analytics, and administrative governance.

### Personalization of the Discovery Path
The platform aims to provide a highly personalized discovery experience by analyzing each user’s resume. Based on this NLP extraction, the system curates a personalized feed of internships. This ensures that users do not scroll through generic boards but instead receive targeted opportunities aligned with their exact current skill level.

### Support for Recruiters and Administrators
The system is designed not only for applicants but also for recruiters and system administrators. It provides robust tools that allow companies to monitor applicant pipelines, analyze candidate match scores, and update hiring statuses dynamically. Administrators can manage content moderation, verify company credentials to prevent fraud, and oversee system operations.

### Optimization of Application Management
The portal streamlines the entire process of applying and tracking. It simplifies resume management, evaluates candidate suitability instantly via AI, and organizes workflows through Role-Based Access Control (RBAC). A student sees their application status in real-time, while a company moves candidates through custom pipelines (Applied → Under Review → Shortlisted).

### Security, Privacy, and Ethical Standards
Security is paramount. The system incorporates JSON Web Tokens (JWT) for stateless session management, bcrypt for password hashing, and specialized features like the "Danger Zone" account deletion process. This allows users to permanently and securely delete their data, complying with modern data privacy standards.

### Scalability and Reliability of the Platform
Built with FastAPI and Next.js, the portal is designed with scalability in mind, ensuring it can handle thousands of concurrent users, resume uploads, and real-time AI calculations without performance degradation.

---

## CHAPTER 4: METHODOLOGY

The methodology for developing the National Internship Portal involved collecting requirements, designing the data architecture, building the AI recommendation logic, and evaluating system performance. The development process followed an iterative approach to ensure flexibility and rapid integration of user feedback.

### Agile Methodology
The development of the portal followed the Agile framework, consisting of a cycle of planning → development → testing → feedback → improvement.

**1. Requirement Gathering (Product Backlog)**
At the beginning, all project requirements were collected. Backlog items included:
- User authentication and Role-Based Access Control (RBAC).
- NLP Resume Parsing module.
- Recommendation engine (TF-IDF).
- Internship CRUD operations for companies.
- Application pipeline tracking.
- Analytics dashboard.

**2. Sprint Planning**
The project was divided into short development cycles (sprints):
- **Sprint 1:** Database Schema (PostgreSQL) & Authentication (FastAPI JWT).
- **Sprint 2:** Student Profile & NLP Resume Parsing Integration.
- **Sprint 3:** Company Dashboard & Internship Listing Management.
- **Sprint 4:** Machine Learning Recommendation Engine Development.
- **Sprint 5:** Application Tracking System (ATS) logic and Frontend UI (Next.js).
- **Sprint 6:** Security enhancements (Danger Zone), Analytics, and Final Testing.

**3. Development Phase**
During each sprint:
- Backend APIs were developed using FastAPI.
- Frontend UI was built using React.js/Next.js with Tailwind CSS.
- AI features were trained, tested, and integrated.

**4. Testing and Continuous Improvement**
After each sprint, modules were tested for functionality and performance. For example, the accuracy of the resume parser was continuously evaluated and regex patterns were refined to capture more obscure technical skills.

---

## CHAPTER 5: LITERATURE SURVEY

A literature survey for the National Internship Portal involves a comprehensive review of existing research and platforms related to recommendation systems, intelligent recruitment systems, and AI-based HR tools.

### 5.1 Recommendation Systems using Content-Based Filtering
Content-based recommendation systems suggest items based on the characteristics of the items themselves. In the context of the National Internship Portal, this approach is used to recommend jobs based on features such as required skills, location, and role type. The advantage of this approach in recruitment is that it provides highly relevant recommendations based on explicit user skills, preventing the system from suggesting advanced roles to beginners.

### 5.2 Collaborative Filtering-Based Recommendation Systems
Collaborative filtering analyzes the behavior of multiple users to identify patterns. While useful in e-commerce, user-based collaborative filtering faces massive challenges in job markets due to the "Cold Start" problem (new jobs have no applicants, new students have no history) and data sparsity. Therefore, our platform relies more heavily on Content-Based NLP matching rather than collaborative behavior.

### 5.3 AI and NLP in Recruitment Systems
Recent advancements in Natural Language Processing (NLP) have significantly improved HR systems. NLP techniques are used to simplify complex textual content from unstructured resumes. In the National Internship Portal, NLP is used to:
- Extract named entities (skills, education).
- Sanitize and standardize text inputs for the ML model.

### 5.4 Conclusion of Literature Survey
The survey shows that while generic job boards are ubiquitous (e.g., Internshala, LinkedIn), specialized platforms that actively parse student data to provide mathematical match scores are rare, particularly for entry-level internship roles. The National Internship Portal addresses these gaps by integrating AI, NLP, and modern web frameworks to provide a structured, efficient, and intelligent hiring experience.

---

## CHAPTER 6: SYSTEM REQUIREMENTS SPECIFICATION

### 6.1 Hardware Requirements
- **Server:** Minimum 8 GB RAM, 4-core Processor (Required for ML model execution in memory).
- **Storage:** Minimum 20 GB SSD for database and uploaded resume storage.
- **Client:** Any modern computer or mobile device with a web browser and internet connectivity.

### 6.2 Software Specification & Tech Stack
**Backend Framework: FastAPI (Python)**
FastAPI was chosen for its exceptional performance. It handles asynchronous requests efficiently and uses Pydantic for strict data validation.

**Frontend Framework: Next.js (React)**
Next.js provides Server-Side Rendering (SSR) and static generation, which significantly improves initial load times and SEO.

**Database: PostgreSQL**
A robust, highly scalable relational database used to store users, internships, and application states with ACID compliance.

**Key Python Libraries:**
- `scikit-learn`: Used for TF-IDF Vectorization and Cosine Similarity calculations.
- `PyPDF2` / `pdfminer`: Used for extracting raw text from uploaded resume documents.
- `SQLAlchemy`: The ORM used to interact with PostgreSQL securely.
- `passlib` & `bcrypt`: Used for secure password hashing.
- `python-jose`: Used for generating and verifying JSON Web Tokens (JWT).

### 6.3 Non-Functional Requirements
- **Performance:** APIs must respond in under 300ms. The recommendation engine must calculate scores in near real-time.
- **Security:** All routes must be protected via JWT. File uploads must be sanitized to prevent malicious execution.
- **Scalability:** The stateless JWT architecture allows the backend to scale horizontally across multiple instances.

---

## CHAPTER 7: SYSTEM ANALYSIS AND DESIGN

### 7.1 System Architecture of Proposed System
The system utilizes a Decoupled Three-Tier Architecture.
1. **Presentation Layer (Next.js):** Handles the UI, state management via TanStack Query, and client-side routing.
2. **Application Logic Layer (FastAPI):** Exposes RESTful APIs, handles business rules, role verification, and integrates with the ML scripts.
3. **Data Layer (PostgreSQL):** Persistently stores all relational data.

### 7.2 Data Flow Diagram Explanation
1. **User Input:** A student uploads a resume via the Next.js interface.
2. **Backend Processing:** The FastAPI endpoint receives the multipart form data. The file is temporarily stored.
3. **NLP Extraction:** The Python parser reads the PDF, extracts text, and identifies skills using regex and NLP dictionaries.
4. **Database Storage:** The extracted skills are saved to the student's row in PostgreSQL.
5. **Recommendation Trigger:** When the student visits the dashboard, the backend fetches active internships.
6. **ML Calculation:** The `scikit-learn` engine vectorizes the student's skills and the internship requirements, computing a Cosine Similarity score.
7. **Output:** The frontend displays a sorted list of internships ranked by their match percentage.

---

## CHAPTER 8: DESIGN IMPLEMENTATION (DEEP DIVE)

### 8.1 Introduction to Technologies
**Why FastAPI Instead of Django/Flask?**
FastAPI is a modern web framework based on standard Python type hints. It follows the ASGI (Asynchronous Server Gateway Interface) standard. Unlike Django, which is a heavy full-stack framework, FastAPI is lightweight and incredibly fast. It automatically generates interactive API documentation (Swagger UI), which drastically simplified the frontend-backend integration process for this project.

**Why Next.js Instead of Plain React?**
Next.js was chosen because of its App Router, built-in API handling, and optimized performance. It allows for reusable components (like the custom Modal used for account deletion) and manages state efficiently using TanStack Query, which caches API responses and reduces server load.

### 8.2 AI & NLP Implementation Logic
**1. Problem Summarization (NLP Application)**
One of the major challenges in recruitment is normalizing data. The system takes unstructured resume text as input, processes it, and generates a structured array of recognized skills.

**2. Recommendation System (Machine Learning)**
The core algorithm relies on `TfidfVectorizer` and `cosine_similarity`. 
- **TF-IDF (Term Frequency-Inverse Document Frequency):** Evaluates how relevant a word (skill) is to a document (resume) in a collection of documents (all internships). It penalizes overly common words and rewards unique skills.
- **Cosine Similarity:** Measures the cosine of the angle between two vectors projected in a multi-dimensional space. A score of 1 means perfectly identical skillsets, while 0 means completely orthogonal (no matching skills).

### 8.3 Interface Implementation
The interface is designed with Tailwind CSS to be responsive and intuitive.
- **Dashboard:** Displays KPIs, recent applications, and top recommendations.
- **Danger Zone (Security UI):** A specialized component requiring double-confirmation (Password + typing "DELETE") to execute a soft-delete on a user account, demonstrating advanced state management and secure API interaction.

---

## CHAPTER 9: TESTING

Testing ensures that the platform delivers accurate recommendations and maintains strict security boundaries.

**1. Unit Testing**
Individual functions were tested independently.
- Testing the `verify_password` hashing logic.
- Testing the PyPDF2 extraction logic against various formatted resumes.
- Testing the Cosine Similarity mathematical output with mock skill arrays.

**2. Integration Testing**
Modules were combined and tested together.
- Testing the flow from the Next.js frontend submitting a login request to the FastAPI backend issuing a JWT, and the frontend storing it securely.
- Testing the cascading effects in the database (e.g., when a Company deletes their account, checking if their associated internships are automatically marked inactive).

**3. System Testing**
End-to-end testing of the complete workflow:
- Register as Company -> Post Internship -> Register as Student -> Upload Resume -> Get Recommended the Internship -> Apply -> Company Shortlists -> Student views status.

---

## CHAPTER 10: RESULT REVIEW

### Dashboard Operations
The administrative and user dashboards present a summarized view of the system. The Student Dashboard successfully visualizes the total applications sent, current statuses, and a ranked list of AI-recommended jobs. This confirms the system effectively processes ML data and visualizes it rapidly.

### Internship Management Section
Companies can seamlessly add, store, update, and retrieve internship data. The real-time synchronization between the database and the frontend ensures that the moment a company updates an application status to "Shortlisted", the student's UI reflects this change upon their next refresh. 

### Recommendation Accuracy
Testing revealed that the TF-IDF and Cosine Similarity approach is highly effective. When a user uploaded a resume containing keywords like "Node.js", "Express", and "MongoDB", the system accurately prioritized "Backend Developer" internships over "UI/UX Designer" roles, validating the core thesis of the project.

---

## CHAPTER 11: CONCLUSION

In conclusion, the National Internship Portal developed in this project demonstrates strong potential in transforming the way students and companies interact during the recruitment process. The platform successfully integrates AI-based NLP resume parsing, Machine Learning recommendation algorithms, and an interactive, secure application tracking system.

By analyzing unstructured resume data and converting it into mathematical vectors, the system eliminates the need for manual searching, allowing users to focus on high-probability opportunities. The implementation of modern frameworks like FastAPI and Next.js ensures the system is not only intelligent but also lightning-fast, secure, and scalable. The inclusion of advanced features like Role-Based Access Control and secure "Danger Zone" account management proves the system's readiness for real-world deployment. 

Ultimately, the National Internship Portal acts as an automated, unbiased career mentor, significantly improving hiring efficiency and candidate placement success.

---

## CHAPTER 12: FUTURE SCOPE

The National Internship Portal offers a strong foundation and can be further enhanced in multiple ways:
- **Large Language Model (LLM) Integration:** Upgrading the current TF-IDF logic to use transformer models (like OpenAI or BERT embeddings) to understand the semantic context of skills, not just exact keyword matches.
- **Automated Interview Scheduling:** Integrating calendar APIs to allow companies to schedule interviews directly through the portal once a candidate is shortlisted.
- **Mobile Application:** Developing a React Native mobile app so students can receive push notifications regarding their application statuses instantly.
- **Skill Verification Assessments:** Adding an in-browser coding environment (like Judge0 API) to allow companies to test applicants technically before the interview stage.

---

## CHAPTER 13: REFERENCES

1. **FastAPI Documentation**, High-Performance Python Web Framework. Available at: https://fastapi.tiangolo.com
2. **Next.js Documentation**, The React Framework for the Web. Available at: https://nextjs.org/docs
3. **PostgreSQL Documentation**, Advanced Open-Source Relational Database. Available at: https://www.postgresql.org/docs
4. **Scikit-learn Documentation**, Machine Learning in Python. Available at: https://scikit-learn.org
5. **TanStack Query**, Asynchronous State Management. Available at: https://tanstack.com/query
6. **Tailwind CSS**, Utility-First CSS Framework. Available at: https://tailwindcss.com/docs
