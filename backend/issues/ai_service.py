
import os

from groq import Groq


def explain_issue(issue):
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    client = Groq(api_key=api_key)

    # Limit the amount of GitHub content sent to the AI
    issue_body = issue.get("body", "")[:6000]

    comments = issue.get("comments", [])

    comments_text = "\n\n".join(
        [
            f"Comment by {comment['author']}:\n{comment['body'][:1500]}"
            for comment in comments
        ]
    )

    if not comments_text:
        comments_text = "No discussion comments available."

    prompt = f"""
Analyze this open-source GitHub issue for someone learning
to contribute to open-source projects.

REPOSITORY: {issue["repository"]}
ISSUE TITLE: {issue["title"]}
ISSUE URL: {issue["url"]}
ISSUE NUMBER: {issue["number"]}
AUTHOR: {issue["author"]}
LABELS: {", ".join(issue["labels"])}

ISSUE DESCRIPTION:
{issue_body if issue_body else "No issue description provided."}

DISCUSSION COMMENTS:
{comments_text}

Provide the following sections:

1. ISSUE SUMMARY
Explain the actual problem in simple language.

2. REQUIRED WORK
Explain what changes or investigation might be necessary.

3. RELEVANT SKILLS
List programming languages, frameworks, and concepts that may help.

4. DIFFICULTY
Choose Beginner, Intermediate, or Advanced.
Explain your reasoning.

5. CONTRIBUTION ROADMAP
Give practical first steps a beginner should follow.

6. THINGS TO INVESTIGATE
Mention relevant files, tests, documentation, or repository areas
the contributor should inspect.

IMPORTANT RULES:
- Base your analysis on the supplied issue description and comments.
- Never invent repository architecture, files, or technical details.
- Distinguish confirmed information from reasonable assumptions.
- If information is missing, explicitly say so.
- Do not provide a complete code solution.
- Do not treat comments as confirmed facts unless supported.
"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an evidence-based open-source contribution "
                    "guide. Analyze actual GitHub issue content carefully. "
                    "Never fabricate technical details. Clearly distinguish "
                    "facts from assumptions and guide beginners toward "
                    "understanding and solving issues independently."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_completion_tokens=900,
    )

    explanation = completion.choices[0].message.content

    return {
        "title": issue["title"],
        "url": issue["url"],
        "repository": issue["repository"],
        "explanation": explanation,
    }