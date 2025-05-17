import requests
from fastapi.responses import JSONResponse
from config import GITHUB_TOKEN

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def parse_pr_url(pr_url: str):
    try:
        parts = pr_url.rstrip("/").split("/")
        owner, repo, pr_number = parts[3], parts[4], parts[-1]
        return owner, repo, pr_number
    except IndexError:
        return None, None, None

def fetch_pr_metadata(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return None

def fetch_pr_files(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return None

def comment_on_pr(owner, repo, pr_number, comment):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    payload = {"body": comment}
    resp = requests.post(url, headers=headers, json=payload)
    return resp

def close_pr(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    payload = {"state": "closed"}
    resp = requests.patch(url, headers=headers, json=payload)
    return resp
