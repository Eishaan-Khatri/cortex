"""
CORTEX — GitHub API Client
Handles GitHub Issues for Socratic debates.
Uses the GITHUB_TOKEN provided by GitHub Actions.
"""

import os
import json
import requests


class GitHubAPI:
    """Interact with the GitHub REST API for Issues."""

    def __init__(self, repo=None, token=None):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.repo = repo or os.environ.get("GITHUB_REPOSITORY", "")
        self.base_url = f"https://api.github.com/repos/{self.repo}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def is_available(self):
        """Check if we have valid credentials."""
        return bool(self.token and self.repo)

    def create_issue(self, title, body, labels=None):
        """Create a new GitHub Issue."""
        if not self.is_available():
            print("  [GITHUB] No token/repo available. Skipping issue creation.")
            return None

        data = {"title": title, "body": body}
        if labels:
            data["labels"] = labels

        try:
            resp = requests.post(
                f"{self.base_url}/issues",
                headers=self.headers,
                json=data,
                timeout=15,
            )
            resp.raise_for_status()
            issue = resp.json()
            print(f"  [GITHUB] Created issue #{issue['number']}: {title}")
            return issue["number"]
        except requests.exceptions.RequestException as e:
            print(f"  [GITHUB] Failed to create issue: {e}")
            return None

    def comment_on_issue(self, issue_number, body):
        """Add a comment to an existing issue."""
        if not self.is_available():
            return False

        try:
            resp = requests.post(
                f"{self.base_url}/issues/{issue_number}/comments",
                headers=self.headers,
                json={"body": body},
                timeout=15,
            )
            resp.raise_for_status()
            print(f"  [GITHUB] Commented on issue #{issue_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"  [GITHUB] Failed to comment: {e}")
            return False

    def close_issue(self, issue_number, comment=None):
        """Close an issue with an optional closing comment."""
        if not self.is_available():
            return False

        if comment:
            self.comment_on_issue(issue_number, comment)

        try:
            resp = requests.patch(
                f"{self.base_url}/issues/{issue_number}",
                headers=self.headers,
                json={"state": "closed"},
                timeout=15,
            )
            resp.raise_for_status()
            print(f"  [GITHUB] Closed issue #{issue_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"  [GITHUB] Failed to close issue: {e}")
            return False

    def get_open_issues(self, label=None):
        """Get all open issues, optionally filtered by label."""
        if not self.is_available():
            return []

        params = {"state": "open"}
        if label:
            params["labels"] = label

        try:
            resp = requests.get(
                f"{self.base_url}/issues",
                headers=self.headers,
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException:
            return []
