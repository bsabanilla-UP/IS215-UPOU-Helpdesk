# IS 215 Final Project: UPOU About Helpdesk

## 👤 Lead Programmer
**Bemmygail Abanilla** *Information Technology Student, UPOU*

## 🌐 Live Application
* **URL:** [https://project.bsabanilla.is215.upou.io](https://project.bsabanilla.is215.upou.io)
* **Static IP:** `54.87.124.61`

---

## 🏗 System Architecture
This application implements a **Retrieval-Augmented Generation (RAG)** architecture. Unlike standard AI chatbots, this system is grounded in specific, verified documentation to prevent hallucinations and ensure academic accuracy.

* **User Interface (EC2):** A web-based terminal hosted on an AWS EC2 Ubuntu instance using the Apache web server.
* **Middleware (Lambda):** A Python-based serverless function that acts as the broker between the UI, the data, and the AI.
* **Knowledge Base (S3):** A structured repository of Markdown files containing official UPOU history, mission, vision, and academic structures.
* **LLM Integration (OpenAI):** Queries are processed via the `gpt-4o-mini` model through a dedicated UPOU class endpoint.

---

## 🛠 Deployment Manual

### Prerequisites
* AWS Learner Lab account ($50 Credit limit).
* OpenAI API Key (Academic provided).
* AWS `LabRole` permissions for cross-service communication.

### Step 1: S3 Knowledge Base Setup
1. Created a bucket named `is215-project-about-upou-bemmy`.
2. Organized data into four professional directory structures:
   * `/institutional-identity/` (About, MVO, Legal Mandates)
   * `/academic-structure/` (MOT, FOS, Course Development)
   * `/contact-and-locations/` (Locations, Social Microsites, Mega Learning Hubs)
   * `/student-services/` (Exam Services, Student Support, Library)
3. Converted scraped web data into **Markdown (.md)** format to ensure high-density token accuracy for the LLM.

### Step 2: Lambda Middleware Configuration
1. **Runtime:** Python 3.x.
2. **Permissions:** Attached the `LabRole` to allow `s3:GetObject` and `s3:ListBucket` actions.
3. **Environment Variables:**
   * `S3_BUCKET_NAME`: `is215-project-about-upou-bemmy`
   * `OPENAI_API_KEY`: [Stored Securely]
4. **Network:** Enabled **Function URL** with CORS configuration to allow the frontend connection.

### Step 3: EC2 Front-End Hosting
1. **Instance:** `t3.micro` Ubuntu Server 24.04 LTS.
2. **Networking:** Associated an **Elastic IP** (`54.87.124.61`) and mapped it to the UPOU subdomain.
3. **Security:** Implemented SSL/TLS termination using **Certbot (Let's Encrypt)** for HTTPS encryption.

---

## 🛡 Prompt Engineering & Guardrails
To satisfy the project's **Accuracy and Reliability rubrics**, the following constraints were implemented:
* **Knowledge Boundary:** The system is instructed to use *only* the provided S3 context. 
* **The Adobo Test:** A hard-coded negative constraint ensures the bot refuses off-topic requests (e.g., cooking recipes), maintaining its professional utility.

---

## 📂 Project Structure
```text
.
├── backend/
│   └── lambda_function.py        # Middleware logic
├── frontend/
│   └── index.html               # Chat interface & Fetch logic
├── knowledge-base/
│   ├── academic-structure/       # MOT, FOS, Course Dev
│   ├── contact-and-locations/    # Hubs, Social, Locations
│   ├── institutional-identity/   # About, MVO, Legal
│   └── student-services/         # Exam, Library, Support
├── .gitignore                    # Prevents .pem upload
└── README.md                     # Documentation
