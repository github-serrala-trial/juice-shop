import os
import json
import base64
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def handle_github_event(event):
    action = event.get('action')
    issue = event.get('issue')
    comment = event.get('comment')

    # Map GitHub issue number to Jira issue ID (implement your own logic here)
    jira_issue_id = map_github_to_jira(issue['number'])

    if action in ['opened', 'edited', 'closed']:
        if action == 'opened':
            create_issue_in_jira(issue)
        else:
            update_issue_in_jira(issue, jira_issue_id)

    if comment and action in ['created', 'edited']:
        add_comment_to_jira(comment, jira_issue_id)

def map_github_to_jira(issue_number):
    # Implement your mapping logic here
    return f"JIRA-{issue_number}"

def create_issue_in_jira(issue):
    jira_url = os.getenv('JIRA_URL')
    jira_email = os.getenv('JIRA_EMAIL')
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    project_key = os.getenv('JIRA_PROJECT_KEY')

    issue_data = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": issue['title'],
            "description": issue['body'],
            "issuetype": {
                "name": "Bug"
            }
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode(f"{jira_email}:{jira_api_token}".encode()).decode()}'
    }

    response = requests.post(f"{jira_url}/rest/api/2/issue/", headers=headers, json=issue_data)

    if response.ok:
        print(f"Successfully created issue in Jira: {response.json()}")
    else:
        print(f"Failed to create issue in Jira: {response.text}")

def update_issue_in_jira(issue, jira_issue_id):
    jira_url = os.getenv('JIRA_URL')
    jira_email = os.getenv('JIRA_EMAIL')
    jira_api_token = os.getenv('JIRA_API_TOKEN')

    issue_data = {
        "fields": {
            "summary": issue['title'],
            "description": issue['body'],
            "status": {"name": "To Do" if issue['state'] == 'open' else "Done"}
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode(f"{jira_email}:{jira_api_token}".encode()).decode()}'
    }

    response = requests.put(f"{jira_url}/rest/api/2/issue/{jira_issue_id}", headers=headers, json=issue_data)

    if response.ok:
        print(f"Successfully updated issue in Jira: {response.json()}")
    else:
        print(f"Failed to update issue in Jira: {response.text}")

def add_comment_to_jira(comment, jira_issue_id):
    jira_url = os.getenv('JIRA_URL')
    jira_email = os.getenv('JIRA_EMAIL')
    jira_api_token = os.getenv('JIRA_API_TOKEN')

    comment_data = {
        "body": comment['body']
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode(f"{jira_email}:{jira_api_token}".encode()).decode()}'
    }

    response = requests.post(f"{jira_url}/rest/api/2/issue/{jira_issue_id}/comment", headers=headers, json=comment_data)

    if response.ok:
        print(f"Successfully added comment to Jira issue: {response.json()}")
    else:
        print(f"Failed to add comment to Jira issue: {response.text}")

if __name__ == "__main__":
    github_event_path = os.getenv('GITHUB_EVENT_PATH')
    with open(github_event_path) as f:
        event = json.load(f)
    handle_github_event(event)
