from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def build_prompt(pr_title: str, pr_body: str, file_diffs: str) -> str:
    return f"""
You are an expert code reviewer. Analyze the GitHub pull request and its diff. Provide the following structured response:

1. What does this PR change and why?
2. Are there any risks, bugs, or concerns?
3. Do you suggest any improvements?
4. Is this PR meaningful? Only answer yes or no.

No partial meaningfulness!

PR Title: {pr_title}
PR Description: {pr_body}

File Diffs:
{file_diffs}
    """

def analyze_code(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a senior software engineer reviewing code changes."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()
