
import os

from groq import Groq


def explain_issue(issue):
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    client = Groq(api_key=api_key)

    prompt = f"""
Explain this open-source GitHub issue to someone who is learning
to contribute to open-source projects.

Repository: {issue["repository"]}
Issue title: {issue["title"]}
Issue URL: {issue["url"]}

Provide:
1. What the issue means in simple language.
2. What work might be required.
3. Skills that may be useful.
4. Estimated difficulty: Beginner, Intermediate, or Advanced,
   with a brief reason.
5. What the contributor should inspect before attempting it.

Do not invent facts about the issue. The title and URL alone may
not provide enough context, so clearly state what remains unknown.
Do not provide a complete code solution.
"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful open-source contribution guide. "
                    "Distinguish confirmed facts from assumptions. "
                    "Never claim to have read issue details that were "
                    "not provided."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_completion_tokens=700,
    )

    explanation = completion.choices[0].message.content

    return {
        "title": issue["title"],
        "url": issue["url"],
        "repository": issue["repository"],
        "explanation": explanation,
    }
