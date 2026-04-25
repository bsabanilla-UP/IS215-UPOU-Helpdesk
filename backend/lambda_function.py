import json
import boto3
import os
import urllib3

# Initialize the S3 client to interact with AWS storage 
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Initialize context_text to store retrieved S3 data
    context_text = ""
    
    # Define CORS headers to allow your EC2 frontend to talk to this Lambda
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    }

    # --- STEP 1: PARSE INPUT ---
    # Extract the user's question sent from the EC2 web frontend
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        user_query = body.get('question', '')
    except Exception:
        user_query = ''

    # Return an error if the frontend sent an empty request
    if not user_query:
        return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'answer': 'No question received.'})}

    # --- STEP 2: KNOWLEDGE RETRIEVAL (S3) ---
    # Retrieve official UPOU documentation to provide "Context" to the AI
    try:
        # Get bucket name from Environment Variables (Security Best Practice)
        bucket_name = os.environ['S3_BUCKET_NAME']
        
        # Folders assigned to the "About UPOU" domain
        folders = ['institutional-identity/', 'academic-structure/', 'student-services/']
        
        for folder in folders:
            # List all files in the specific domain folder
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder)
            for obj in response.get('Contents', []):
                # Only read Markdown files to ensure clean text processing
                if obj['Key'].endswith('.md'):
                    file_obj = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
                    # Combine all file contents into one large context string
                    context_text += file_obj['Body'].read().decode('utf-8') + "\n"
    except Exception as e:
        print(f"S3 Error: {e}")

    # --- STEP 3: INTELLIGENCE (OPENAI API) ---
    # Send the retrieved S3 context and user question to the LLM
    try:
        # Retrieve API Key from Environment Variables (Do NOT hardcode)
        api_key = os.environ['OPENAI_API_KEY']  # add your API key here
        http = urllib3.PoolManager()
        
        # UPOU-specific OpenAI gateway endpoint
        url = "https://is215-openai.upou.io/v1/chat/completions"
        
        # SYSTEM PROMPT: Defines persona and enforces UPOU-only knowledge boundaries
        system_prompt = (
            "You are a professional UPOU helpdesk agent. "
            "Use ONLY the following context to answer. If the answer is not there, "
            "say you don't know and offer to create a support ticket. " # Required fallback
            "Refuse off-topic questions. Context: " + context_text # Required guardrail
        )
        
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
        }
        
        # Execute the POST request to the AI engine
        api_res = http.request("POST", url, 
                               headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                               body=json.dumps(data),
                               timeout=15.0)
        
        result = json.loads(api_res.data.decode('utf-8'))
        answer = result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Logic Error: {e}")
        # Professional fallback message if the system fails
        answer = "I'm having trouble retrieving that info. Please ask something else about UPOU."

    # --- STEP 4: FINAL RESPONSE ---
    # Send the AI's answer back to the EC2 frontend for display
    return {
        'statusCode': 200,
        'body': json.dumps({'answer': answer})
    }




