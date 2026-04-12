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
2. Organized data into professional directory structures:
   * `/institutional-identity/` (Mission, Vision, History)
   * `/academic-structure/` (Faculties and Offices)
   * `/student-services/` (Support and Hubs)
3. Converted scraped web data into **Markdown (.md)** format to ensure high-density token accuracy for the LLM.

### Step 2: Lambda Middleware Configuration
1. **Runtime:** Python 3.x.
2. **Permissions:** Attached the `LabRole` to allow `s3:GetObject` and `s3:ListBucket` actions.
3. **Environment Variables:**
   * `S3_BUCKET_NAME`: `is215-project-about-upou-bemmy`
   * `OPENAI_API_KEY`: [Stored Securely]
4. **Network:** Enabled **Function URL** with CORS configuration:
   * `Allow-Origin`: `*`
   * `Allow-Headers`: `content-type`
   * `Allow-Methods`: `POST`

### Step 3: EC2 Front-End Hosting
1. **Instance:** `t3.micro` Ubuntu Server 24.04 LTS named `IS215-Project`.
2. **Networking:**
   * Allocated and associated an **Elastic IP** (`54.87.124.61`) to ensure persistence.
   * Mapped the IP to the subdomain `project.bsabanilla.is215.upou.io`.
3. **Automation:** Utilized **User Data** scripts to automatically install and enable the Apache2 web server upon launch.
4. **Security:** Implemented SSL/TLS termination using **Certbot (Let's Encrypt)** for HTTPS encryption.

---

## 🛡 Prompt Engineering & Guardrails
To satisfy the project's **Accuracy and Reliability rubrics**, the following constraints were implemented:

* **Persona:** The AI is strictly defined as a "Professional UPOU Helpdesk Agent."
* **Knowledge Boundary:** The system is instructed to use *only* the provided S3 context. If information is missing, it must offer to create a support ticket rather than guess.
* **The Adobo Test:** A hard-coded negative constraint ensures the bot refuses off-topic requests (e.g., cooking recipes), maintaining its professional utility.

---

## 📂 Project Structure
* `index.html` - Responsive web interface with AJAX/Fetch logic.
* `lambda_function.py` - Backend logic for S3 crawling and OpenAI brokering.
* `/knowledge-base` - Source Markdown files used for RAG context.
* `.gitignore` - Configured to prevent the accidental upload of `.pem` keys.

---

## 🔐 Security Note
The instance is accessed exclusively via a private SSH key (`bemmy-is215-key`). This key is stored securely off-cloud and is **not** included in this repository to prevent unauthorized access.

---

**Course:** IS 215 - Information Management  
**University:** University of the Philippines Open University
