import os
import json
import hmac
import hashlib
import requests
from datetime import datetime, timezone

def generate_payload(name, email, resume_link, repository_link, action_run_link, timestamp=None):
    if timestamp is None:
        # Generate current ISO 8601 timestamp with milliseconds
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    payload = {
        "timestamp": timestamp,
        "name": name,
        "email": email,
        "resume_link": resume_link,
        "repository_link": repository_link,
        "action_run_link": action_run_link
    }
    
    # Canonicalize: sort keys, compact separators, UTF-8 encoded
    canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return canonical_json

def sign_payload(payload_bytes, secret):
    signature = hmac.new(secret.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={signature}"

def submit(payload_bytes, signature):
    url = os.environ.get("SUBMISSION_URL")
    if not url:
        raise ValueError("SUBMISSION_URL environment variable is not set")
    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": signature
    }
    
    response = requests.post(url, data=payload_bytes, headers=headers)
    return response

def test_signature():
    # Test with example from job description
    example_payload = {
        "action_run_link": "https://link-to-github-or-another-forge.example.com/your/repository/actions/runs/run_id",
        "email": "you@example.com",
        "name": "Your name",
        "repository_link": "https://link-to-github-or-other-forge.example.com/your/repository",
        "resume_link": "https://pdf-or-html-or-linkedin.example.com",
        "timestamp": "2026-01-06T16:59:37.571Z"
    }
    secret = "hello-there-from-partner"
    expected_digest = "c5db257a56e3c258ec1162459c9a295280871269f4cf70146d2c9f1b52671d45"
    
    canonical_json = json.dumps(example_payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
    signature = sign_payload(canonical_json, secret)
    digest = signature.split('=')[1]
    
    print(f"Test Payload: {canonical_json.decode('utf-8')}")
    print(f"Generated Digest: {digest}")
    print(f"Expected Digest:  {expected_digest}")
    
    if digest == expected_digest:
        print("✅ Signature test passed!")
    else:
        print("❌ Signature test failed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_signature()
        sys.exit(0)

    # Required parameters (prefer environment variables)
    name = os.environ.get("APPLICANT_NAME")
    email = os.environ.get("APPLICANT_EMAIL")
    resume_link = os.environ.get("RESUME_LINK")
    repo_link = os.environ.get("REPOSITORY_LINK")
    
    # Construct Action Run Link from GitHub env vars if available
    github_server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    github_repo = os.environ.get("GITHUB_REPOSITORY", "username/repo")
    github_run_id = os.environ.get("GITHUB_RUN_ID", "run_id")
    action_run_link = f"{github_server}/{github_repo}/actions/runs/{github_run_id}"

    # Allow overriding run link directly
    action_run_link = os.environ.get("ACTION_RUN_LINK", action_run_link)

    secret = os.environ.get("SIGNING_SECRET")

    missing = []
    if not name: missing.append("APPLICANT_NAME")
    if not email: missing.append("APPLICANT_EMAIL")
    if not resume_link: missing.append("RESUME_LINK")
    if not repo_link: missing.append("REPOSITORY_LINK")
    if not secret: missing.append("SIGNING_SECRET")
    if not os.environ.get("SUBMISSION_URL"): missing.append("SUBMISSION_URL")
    
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    payload_bytes = generate_payload(name, email, resume_link, repo_link, action_run_link)
    signature = sign_payload(payload_bytes, secret)
    
    print(f"Submitting payload: {payload_bytes.decode('utf-8')}")
    print(f"With signature: {signature}")
    
    response = submit(payload_bytes, signature)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get("success"):
                print(f"SUCCESS! Receipt: {data.get('receipt')}")
            else:
                print("Submission failed according to response body.")
        except json.JSONDecodeError:
            print("Successfully posted but response was not valid JSON.")
    else:
        print(f"Failed to submit. Status: {response.status_code}")
