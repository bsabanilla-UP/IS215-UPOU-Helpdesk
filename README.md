IS 215 Final Project: UPOU About Helpdesk
Lead Programmer: Bemmygail Abanilla

Live URL: https://project.bsabanilla.is215.upou.io

Elastic IP: 54.87.124.61

🏗 System Architecture
This application utilizes a Retrieval-Augmented Generation (RAG) architecture. Unlike standard AI bots, this system "consults" official documents stored in the cloud before generating a response, ensuring high accuracy and preventing hallucinations.

User Interface (EC2): A web-based chat terminal hosted on a t3.micro Ubuntu instance running Apache.

Middleware (AWS Lambda): A Python-based serverless function that handles logic, security headers, and API brokering.

Knowledge Base (Amazon S3): A structured repository of Markdown files containing UPOU history, mission, and academic structures.

LLM Integration (OpenAI): Queries are processed using the gpt-4o-mini model via a custom UPOU API gateway.

🛠 Deployment Manual
1. Prerequisites
AWS Learner Lab account with active LabRole permissions.

UPOU-provided OpenAI API Key.

Domain mapping via the IS 215 Student Portal.

2. S3 Knowledge Base Setup
Bucket Creation: Created is215-project-about-upou-bemmy with public access blocked.

Data Organization: To ensure high data quality, information was categorized into logical directories:

/institutional-identity/ (Mission, Vision, History)

/academic-structure/ (Faculties, Hubs)

/student-services/ (Enrollment, Support)

Formatting: Documents were converted to Markdown (.md) to provide the LLM with clear headers and structural context.

3. Lambda Middleware Logic
Environment Variables: Secured sensitive data using Lambda environment variables (S3_BUCKET_NAME, OPENAI_API_KEY).

CORS & Security: Configured the Lambda Function URL with CORS settings to allow Content-Type headers from the EC2 origin.

Error Handling: Implemented try-except blocks to prevent system crashes during API timeouts or S3 retrieval failures, returning user-friendly error messages to the frontend.

4. EC2 Web Frontend
Automation: Used a Bash User Data script to automatically install and enable Apache upon instance launch.

Elastic IP: Allocated and associated a static IP (54.87.124.61) to ensure the domain mapping remains permanent.

SSL Termination: Installed Certbot and configured Let's Encrypt to enable HTTPS/SSL encryption for secure communication.

🛡️ Accuracy & Guardrails
The system prompt was engineered to satisfy the project's strict accuracy requirements:

Persona: The bot identifies as an "Official UPOU Helpdesk Agent."

Context Grounding: The bot is strictly instructed to answer only using provided S3 documentation.

The Adobo Test: To prevent misuse, the bot is programmed to refuse off-topic or non-academic queries (e.g., cooking recipes or general chat).

📂 Repository Structure
/frontend: Contains index.html (the web interface).

/backend: Contains lambda_function.py (the Python middleware).

/knowledge-base: The source Markdown files used for RAG context.

.gitignore: Configured to ignore sensitive .pem keys and local environment files.

📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
