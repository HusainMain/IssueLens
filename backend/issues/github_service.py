
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from datetime import datetime, timezone


def get_repository(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"

    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "IssueLens"
        }
    )

    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        return {
            "name": data["full_name"],
            "description": data["description"],
            "stars": data["stargazers_count"],
            "open_issues": data["open_issues_count"],
            "updated_at": data["updated_at"],
            "language": data["language"],
            "url": data["html_url"]
        }

    except HTTPError as error:
        if error.code == 404:
            return {"error": "Repository not found"}
        if error.code == 403:
            return {"error": "GitHub API rate limit may have been exceeded"}
        return {"error": f"GitHub API returned HTTP {error.code}"}

    except URLError:
        return {"error": "Could not connect to GitHub"}

    except TimeoutError:
        return {"error": "GitHub request timed out"}


def search_issues(query, limit=10):
    from urllib.parse import urlencode

    params = urlencode({
        "q": f"{query} is:issue is:open",
        "per_page": min(max(limit, 1), 30),
        "sort": "updated",
        "order": "desc",
    })

    url = f"https://api.github.com/search/issues?{params}"

    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "IssueLens"
        }
    )

    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        return {
            "total_count": data["total_count"],
            "items": [
                {
                    "title": issue["title"],
                    "url": issue["html_url"],
                    "repository": issue["repository_url"].replace(
                        "https://api.github.com/repos/", ""
                    ),
                    "state": issue["state"],
                    "labels": [
                        label["name"] for label in issue["labels"]
                    ],
                    "created_at": issue["created_at"],
                    "updated_at": issue["updated_at"],
                }
                for issue in data["items"]
                if "pull_request" not in issue
            ],
        }

    except HTTPError as error:
        return {"error": f"GitHub API returned HTTP {error.code}"}

    except (URLError, TimeoutError):
        return {"error": "Could not connect to GitHub"}

def get_repository_issues(owner, repo, limit=10):
    url = (
        f"https://api.github.com/repos/{owner}/{repo}"
        f"/issues?state=open&per_page={min(max(limit, 1), 30)}"
    )

    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "IssueLens"
        }
    )

    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        issues = [
            issue for issue in data
            if "pull_request" not in issue
        ]

        recently_updated = sum(
            1
            for issue in issues
            if (
                datetime.now(timezone.utc)
                - datetime.fromisoformat(
                    issue["updated_at"].replace("Z", "+00:00")
                )
            ).days <= 30
        )

        return {
            "items": [
                {
                    "number": issue["number"],
                    "title": issue["title"],
                    "url": issue["html_url"],
                    "repository": f"{owner}/{repo}",
                    "state": issue["state"],
                    "labels": [
                        label["name"] for label in issue["labels"]
                    ],
                    "created_at": issue["created_at"],
                    "updated_at": issue["updated_at"],
                }
                for issue in data
                if "pull_request" not in issue
            ],
            "sampled_issue_count": len(issues),
            "recently_updated_count": recently_updated,
        }

    except HTTPError as error:
        if error.code == 404:
            return {"error": "Repository not found"}
        return {"error": f"GitHub API returned HTTP {error.code}"}

    except (URLError, TimeoutError):
        return {"error": "Could not connect to GitHub"}