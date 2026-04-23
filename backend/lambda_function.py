import json
import boto3
import os
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

s3   = boto3.client('s3')
http = urllib3.PoolManager()

HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}

MAX_CONTEXT_CHARS = 12_000 
OPENAI_TIMEOUT    = 20.0     
OPENAI_URL        = "https://is215-openai.upou.io/v1/chat/completions"
S3_FOLDERS        = ['institutional-identity/', 'academic-structure/', 'student-services/']

SYSTEM_PROMPT_TEMPLATE = (
    "You are a professional UPOU helpdesk agent. "
    "Use ONLY the following context to answer. "
    "If the answer is not in the context, politely say you don't know "
    "and offer to create a support ticket. "
    "Refuse off-topic questions.\n\nContext:\n{context}"
)

def make_response(status_code: int, body: dict) -> dict:
    """Build a well-formed Lambda Function URL response."""
    return {
        'statusCode': status_code,
        'headers': HEADERS,
        'body': json.dumps(body)
    }


def fetch_s3_file(bucket: str, key: str) -> str:
    """Fetch a single S3 object and return its decoded text (empty on error)."""
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        return obj['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"[S3] Error fetching {key}: {e}")
        return ""


def load_context(bucket: str) -> str:
    """
    List all .md files across S3_FOLDERS, fetch them in parallel,
    and return a single combined string capped at MAX_CONTEXT_CHARS.
    """
    keys = []
    for folder in S3_FOLDERS:
        try:
            resp = s3.list_objects_v2(Bucket=bucket, Prefix=folder)
            for obj in resp.get('Contents', []):
                if obj['Key'].endswith('.md'):
                    keys.append(obj['Key'])
        except Exception as e:
            print(f"[S3] Error listing {folder}: {e}")

    if not keys:
        print("[S3] No .md files found — proceeding with empty context.")
        return ""

    chunks = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(fetch_s3_file, bucket, k): k for k in keys}
        for future in as_completed(futures):
            text = future.result()
            if text:
                chunks.append(text)

    combined = "\n".join(chunks)
    if len(combined) > MAX_CONTEXT_CHARS:
        print(f"[S3] Context trimmed: {len(combined)} -> {MAX_CONTEXT_CHARS} chars")
        combined = combined[:MAX_CONTEXT_CHARS]

    return combined


def call_openai(api_key: str, system_prompt: str, user_query: str) -> str:
    """
    POST to the UPOU OpenAI endpoint and return the assistant reply text.
    Raises RuntimeError on non-200 HTTP status or unexpected response shape.
    """
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_query}
        ]
    }

    resp = http.request(
        "POST",
        OPENAI_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        body=json.dumps(payload),
        timeout=urllib3.Timeout(connect=5.0, read=OPENAI_TIMEOUT)
    )

    if resp.status != 200:
        snippet = resp.data[:200].decode('utf-8', errors='replace')
        raise RuntimeError(f"OpenAI endpoint HTTP {resp.status}: {snippet}")

    result = json.loads(resp.data.decode('utf-8'))

    try:
        return result['choices'][0]['message']['content']
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected OpenAI response shape: {e} — {result}")

def lambda_handler(event, context):

    # --- CORS preflight ---
    method = (
        event.get('requestContext', {})
             .get('http', {})
             .get('method', '')
             .upper()
    )
    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': HEADERS, 'body': ''}

    # --- 1. Parse input ---
    try:
        body = event.get('body', '{}') or '{}'
        if isinstance(body, str):
            body = json.loads(body)
        user_query = body.get('question', '').strip()
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"[Input] Parse error: {e}")
        return make_response(400, {'answer': 'Invalid request format.'})

    if not user_query:
        return make_response(400, {'answer': 'No question received.'})

    # --- 2. Load S3 context ---
    context_text = ""
    try:
        bucket = os.environ['S3_BUCKET_NAME']
        context_text = load_context(bucket)
    except KeyError:
        print("[Config] S3_BUCKET_NAME is not set — continuing with empty context.")
    except Exception as e:
        print(f"[S3] Unexpected error: {e} — continuing with empty context.")

    # --- 3. Call OpenAI ---
    try:
        api_key       = os.environ['OPENAI_API_KEY']
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context_text)
        answer        = call_openai(api_key, system_prompt, user_query)
    except KeyError:
        print("[Config] OPENAI_API_KEY is not set.")
        return make_response(500, {'answer': 'Server configuration error. Please contact support.'})
    except Exception as e:
        print(f"[OpenAI] Error: {e}")
        return make_response(502, {
            'answer': "I'm having trouble reaching the AI service right now. Please try again in a moment."
        })

    # --- 4. Return answer ---
    return make_response(200, {'answer': answer})\