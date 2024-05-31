const fetch = require('node-fetch');

const githubEvent = require(process.env.GITHUB_EVENT_PATH);
const jiraUrl = process.env.JIRA_URL;
const jiraEmail = process.env.JIRA_EMAIL;
const jiraApiToken = process.env.JIRA_API_TOKEN;

async function handleGithubEvent(event) {
  const { action, issue, comment } = event;

  // Map GitHub issue number to Jira issue ID (implement your own logic here)
  const jiraIssueId = mapGithubToJira(issue.number);

  if (action === 'opened' || action === 'edited' || action === 'closed') {
    await syncIssueWithJira(issue, jiraIssueId);
  }

  if (comment && (action === 'created' || action === 'edited')) {
    await syncCommentWithJira(comment, jiraIssueId);
  }
}

function mapGithubToJira(issueNumber) {
  // Implement your mapping logic here
  return `JIRA-${issueNumber}`;
}

async function syncIssueWithJira(issue, jiraIssueId) {
  const issueData = {
    fields: {
      summary: issue.title,
      description: issue.body,
      status: { name: issue.state === 'open' ? 'To Do' : 'Done' }
    }
  };

  const response = await fetch(`${jiraUrl}/rest/api/2/issue/${jiraIssueId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Basic ${Buffer.from(`${jiraEmail}:${jiraApiToken}`).toString('base64')}`
    },
    body: JSON.stringify(issueData)
  });

  if (!response.ok) {
    console.error('Failed to sync issue with Jira', await response.text());
  }
}

async function syncCommentWithJira(comment, jiraIssueId) {
  const commentData = {
    body: comment.body
  };

  const response = await fetch(`${jiraUrl}/rest/api/2/issue/${jiraIssueId}/comment`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Basic ${Buffer.from(`${jiraEmail}:${jiraApiToken}`).toString('base64')}`
    },
    body: JSON.stringify(commentData)
  });

  if (!response.ok) {
    console.error('Failed to sync comment with Jira', await response.text());
  }
}

handleGithubEvent(githubEvent);
