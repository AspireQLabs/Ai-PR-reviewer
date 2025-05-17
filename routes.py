from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import github_client
import openai_client

router = APIRouter()

@router.get("/analyze-pr")
def analyze_pr(pr_url: str = Query(..., description="GitHub pull request URL"), auto_close: bool = Query(True)):

    owner, repo, pr_number = github_client.parse_pr_url(pr_url)
    if not owner or not repo or not pr_number:
        return JSONResponse(status_code=400, content={"error": "Invalid PR URL"})

    pr_meta = github_client.fetch_pr_metadata(owner, repo, pr_number)
    if not pr_meta:
        return JSONResponse(status_code=404, content={"error": "Failed to fetch PR metadata"})

    pr_title = pr_meta.get("title", "")
    pr_body = pr_meta.get("body", "")

    files_data = github_client.fetch_pr_files(owner, repo, pr_number)
    if not files_data:
        return JSONResponse(status_code=404, content={"error": "Failed to fetch PR files"})

    file_diffs = ""
    for file_data in files_data:
        if isinstance(file_data, dict) and file_data.get("patch"):
            filename = file_data.get("filename")
            patch = file_data.get("patch")
            file_diffs += f"Filename: {filename}\n{patch}\n\n"

    if not file_diffs:
        return JSONResponse(status_code=400, content={"error": "No diff content available in PR."})

    prompt = openai_client.build_prompt(pr_title, pr_body, file_diffs)

    try:
        summary = openai_client.analyze_code(prompt)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    print("OpenAI Summary:\n", summary)

    is_meaningful = "4. Yes" in summary

    if auto_close and not is_meaningful:
        comment = "🤖 This PR was automatically reviewed and marked as *not meaningful* (e.g., trivial or cosmetic change). Closing to reduce noise. Please reopen with more substantive changes."
        github_client.comment_on_pr(owner, repo, pr_number, comment)
        close_resp = github_client.close_pr(owner, repo, pr_number)
        if close_resp.status_code == 200:
            summary += "\n\n🚫 PR was automatically closed due to trivial or non-meaningful changes."
        else:
            summary += f"\n\n⚠️ Attempted to close PR but failed: {close_resp.status_code}"

    if is_meaningful:
        try:
            github_client.comment_on_pr(owner, repo, pr_number, f"### 🤖 Automated PR Review\n\n{summary}")
        except Exception as e:
            print(f"⚠️ Exception while posting summary comment: {e}")

    return {"analysis": summary}
