# IS 215 Final Project: UPOU Helpdesk Deployment Guide

## 👤 Lead Programmer
**Bemmygail Abanilla** *Master of Information Systems Student, UPOU*

## 🌐 Live Application
* **URL:** [https://project.bsabanilla.is215.upou.io](https://project.bsabanilla.is215.upou.io)
* **Elastic IP:** `54.87.124.61`

---

## 🏗 System Architecture
This application implements a **Retrieval-Augmented Generation (RAG)** architecture. Unlike standard AI chatbots, this system is grounded in specific, verified documentation to prevent hallucinations and ensure academic accuracy.

* **User Interface (EC2):** A web-based terminal hosted on an AWS EC2 Ubuntu instance using the Apache web server.
* **Middleware (Lambda):** A Python-based serverless function that acts as the broker between the UI, the data, and the AI.
* **Knowledge Base (S3):** A structured repository of Markdown files containing official UPOU history, mission, vision, and academic structures.
* **LLM Integration (OpenAI):** Queries are processed via the `gpt-4o-mini` model through a dedicated UPOU class endpoint.

---

## 🛠 Deployment Manual

### 1. Environment Initialization
The project was developed within the **AWS Learner Lab** environment.
* **Lab Activation:** Monitored AWS status until the indicator turned green.
* **Regional Standardization:** Set to **us-east-1 (N. Virginia)** for LabRole compatibility.

### 2. Knowledge Base Setup (S3)
To satisfy the **Data Quality Rubric**, a structured knowledge base was created.
* **Bucket Creation:** Created private bucket `is215-project-about-upou-bemmy`.
* **Data Structuring:** Organized into four logical directories:
  * `/institutional-identity/` (About, MVO, Legal Mandates)
  * `/academic-structure/` (MOT, FOS, Course Development)
  * `/contact-and-locations/` (Locations, Social Microsites, Mega Learning Hubs)
  * `/student-services/` (Exam Services, Student Support, Library)
* **Formatting:** Converted scraped data into **Markdown (.md)** to ensure structural clarity.

### 3. Middleware Development (Lambda)
The Lambda function serves as the "brain," brokering communication between the frontend, S3, and OpenAI.
* **Configuration:** Created `UPOU_Helpdesk_Middleware` using Python 3.12 with **LabRole** permissions.
* **Validation:** Verified via console test events.
  * **Query:** "What is the mission of UPOU?"
  * **Result:** Successful JSON response with accurate mission statement.

### 4. Prompt Engineering & Reliability
To meet the **Accuracy Rubric**, a system prompt was developed to enforce strict knowledge boundaries.
* **The Persona:** "You are a professional UPOU helpdesk agent."
* **The Adobo Test:** To verify reliability, the bot was tested with the query: *"How do I cook adobo?"*
  * **Bot Response:** Successfully refused, staying within UPOU knowledge boundaries.

### 5. Web Hosting & Security (EC2)
* **Instance Setup:** Launched Ubuntu-based `t3.micro` instance.
* **Static Connectivity:** Associated **Elastic IP** (`54.87.124.61`) and mapped to official subdomain.
* **Security:** Implemented SSL/TLS termination using **Certbot (Let's Encrypt)** for HTTPS encryption.

---

## 📂 Project Structure
```text
.
├── backend/
│   └── lambda_function.py        # Middleware logic (Python/Boto3)
├── frontend/
│   └── index.html                # Chat interface & Fetch logic
├── knowledge-base/
│   ├── academic-structure/       # MOT, FOS, Course Dev
│   ├── contact-and-locations/    # Hubs, Social, Locations
│   ├── institutional-identity/   # About, MVO, Legal
│   └── student-services/         # Exam, Library, Support
├── .gitignore                    # Prevents .pem and system files upload
└── README.md                     # Documentation
