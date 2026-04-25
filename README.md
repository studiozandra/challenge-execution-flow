# Challenge Execution Flow

This repository contains the solution for a technical assessment.

## Contents

- `apply.py`: A Python script that generates the required JSON payload, signs it with HMAC-SHA256, and posts it to the B12 submission endpoint.
- `.github/workflows/submit.yml`: A GitHub Action workflow that automates the execution of `apply.py` on push to the `main` branch or via manual trigger.

## How to Submit

Follow these steps to complete your application:

1. **Create a Private or Public Repository**:
   - Create a new repository on GitHub.
   - You can name it whatever you like (e.g., `b12-application`). Note that B12 mentioned that naming it "B12" might make it searchable by others.

2. **Configure GitHub Secrets**:
   Go to your repository settings -> **Secrets and variables** -> **Actions** -> **New repository secret** and add the following:
   - `APPLICANT_NAME`: Your full name.
   - `APPLICANT_EMAIL`: Your email address.
   - `RESUME_LINK`: Link to your CV/LinkedIn.
   - `REPOSITORY_LINK`: The URL of this GitHub repository.
   - `SIGNING_SECRET`: `hello-there-from-b12`
   - `SUBMISSION_URL`: `https://b12.io/apply/submission`

3. **Push the Code**:
   Initialize this directory as a git repository and push it to your new GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initialize B12 application challenge"
   git branch -M main
   git remote add origin git@github.com:studiozandra/challenge-execution-flow.git
   git push -u origin main
   ```

4. **Verify the Submission**:
   - You should see a workflow named "Challenge Execution Workflow" running.
   - If it succeeds, check the logs of the "Run submission script" step. It will print a **submission receipt**.
   - Copy and paste that receipt into the application form.

Good luck!
