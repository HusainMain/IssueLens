
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ai_service import explain_issue
from groq import APIConnectionError, APIStatusError, RateLimitError

from .github_service import (
    get_repository,
    get_repository_issues,
    search_issues,
)

@api_view(['GET'])
def api_status(request):
    return Response({
        "project": "IssueLens",
        "status": "running",
        "message": "IssueLens API is working!"
    })


@api_view(['GET'])
def repository_details(request):
    owner = request.query_params.get('owner', '')
    repo = request.query_params.get('repo', '')

    if not owner or not repo:
        return Response(
            {"error": "Both owner and repo are required"},
            status=400
        )

    result = get_repository(owner, repo)

    if "error" in result:
        if result["error"] == "Repository not found":
            status_code = 404
        elif result["error"] == "Could not connect to GitHub":
            status_code = 503
        else:
            status_code = 502

        return Response(result, status=status_code)

    return Response(result)

@api_view(['GET'])
def repository_issues(request):
    owner = request.query_params.get('owner', '')
    repo = request.query_params.get('repo', '')
    limit = request.query_params.get('limit', '10')

    try:
        limit = int(limit)
    except ValueError:
        return Response(
            {"error": "limit must be a number"},
            status=400
        )

    if limit < 1 or limit > 30:
        return Response(
            {"error": "limit must be between 1 and 30"},
            status=400
        )

    if not owner or not repo:
        return Response(
            {"error": "Both owner and repo are required"},
            status=400
        )

    result = get_repository_issues(owner, repo, limit)

    if "error" in result:
        if result["error"] == "Repository not found":
            status_code = 404
        else:
            status_code = 502

        return Response(result, status=status_code)

    return Response(result)


@api_view(['GET'])
def search_github_issues(request):
    query = request.query_params.get('q', '').strip()
    limit = request.query_params.get('limit', '10')

    if not query:
        return Response(
            {"error": "Search query q is required"},
            status=400
        )

    try:
        limit = int(limit)
    except ValueError:
        return Response(
            {"error": "limit must be a number"},
            status=400
        )

    if limit < 1 or limit > 30:
        return Response(
            {"error": "limit must be between 1 and 30"},
            status=400
        )

    result = search_issues(query, limit)

    if "error" in result:
        return Response(result, status=502)

    return Response(result)



@api_view(['POST'])
def explain_issue_view(request):
    issue = request.data

    required_fields = ['title', 'url', 'repository']

    for field in required_fields:
        if not issue.get(field):
            return Response(
                {"error": f"{field} is required"},
                status=400
            )
    try:
        result = explain_issue(issue)
        return Response(result)

    except ValueError as error:
        return Response(
            {"error": str(error)},
            status=500
        )

    except RateLimitError:
        return Response(
            {"error": "Groq rate limit reached. Please try again later."},
            status=429
        )

    except APIConnectionError:
        return Response(
            {"error": "Could not connect to the AI service."},
            status=503
        )

    except APIStatusError as error:
        print(
            f"Groq API error: status={error.status_code}, "
            f"message={error.message}"
        )
        return Response(
            {"error": "The AI service returned an error."},
            status=502
        )

    except (APIConnectionError, APIStatusError, RateLimitError) as e:
        return Response(
            {"error": f"Error occurred while fetching AI explanation: {str(e)}"},
            status=503
        )