import json
import boto3
import os
import urllib3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Initialize the variable immediately so it's never "undefined"
    context_text = ""
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    }

    # 1. Parse Input
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        user_query = body.get('question', '')
    except Exception:
        user_query = ''

    if not user_query:
        return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'answer': 'No question received.'})}

    # 2. Get Data from S3
    try:
        bucket_name = os.environ['S3_BUCKET_NAME']
        folders = ['institutional-identity/', 'academic-structure/', 'student-services/']
        for folder in folders:
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder)
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.md'):
                    file_obj = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
                    context_text += file_obj['Body'].read().decode('utf-8') + "\n"
    except Exception as e:
        print(f"S3 Error: {e}")
        # Even if S3 fails, context_text exists as an empty string now

    # 3. Talk to UPOU OpenAI Endpoint
    try:
        api_key = os.environ['OPENAI_API_KEY']
        http = urllib3.PoolManager()
        url = "https://is215-openai.upou.io/v1/chat/completions"
        
        system_prompt = (
            "You are a professional UPOU helpdesk agent. "
            "Use ONLY the following context to answer. If the answer is not there, "
            "say you don't know and offer to create a support ticket. "
            "Refuse off-topic questions. Context: " + context_text
        )
        
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
        }
        
        api_res = http.request("POST", url, 
                               headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                               body=json.dumps(data),
                               timeout=15.0)
        
        result = json.loads(api_res.data.decode('utf-8'))
        answer = result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Logic Error: {e}")
        answer = "I'm having trouble retrieving that info. Please ask something else about UPOU."

# 4. Final Response (Simplified for Function URL CORS)
    return {
        'statusCode': 200,
        'body': json.dumps({'answer': answer})
    }