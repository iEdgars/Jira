import streamlit as st
from jira import JIRA
import pandas as pd
import requests
import json

### adding credentials
with open('jiraCreds.json') as jiraCredsFile:
    jiraCreds = json.load(jiraCredsFile)

email = jiraCreds['email']
apiToken = jiraCreds['apiToken']
encodedToken = jiraCreds['encodedToken']

### adding Jira info
with open('jiraInfo.json') as jiraInfoFile:
    jiraInfo = json.load(jiraInfoFile)

server = jiraInfo['server']
project_name = jiraInfo['project_name']


# Set the page config
st.set_page_config(
  page_title="Blocked items",
  page_icon="⛔",
#   layout="wide"
)

st.title('Blocked items without any blockers')

### handling jira calls to start only once initiated. Might remove later
# if "refresh" not in st.session_state:
#     st.session_state["refresh"] = "off"

# def changeRefreshState():
#     st.session_state["refresh"] = "on"

# st.button("Start JIRA", on_click=changeRefreshState)
st.session_state["refresh"] = "on"

### adding board selection
boardOprions= []

for boards in jiraInfo['boards']:
    for board in boards:
        boardOprions.append(board)

# Create the selectbox
boardSelected = st.selectbox('Select board', boardOprions)

if st.session_state["refresh"] == "on":
    jira = JIRA(basic_auth=(email, apiToken), options={'server': server})
    status = 'Blocked'

    blockingStatuses = ['Ready','Blocked','Backlog','In Progress','UAT', 'In Testing', 'Ready for Refinement']
    nonBlockingStatuses = ['Done','Rejected']

    query = f'project = {project_name} AND component = {boardSelected} AND status = {status}'

    startAt = 0
    issues = jira.search_issues(query, startAt=startAt, maxResults=50)
    linkedIssues = issues

    while len(issues) > 0:
        # for issue in issues:
            # print(issue.key, issue.fields.summary, issue.fields.status, issue.fields.assignee, issue.fields.created[:10], issue.fields.updated[:10], issue.fields.updated[11:16], issue.permalink())
        startAt += 50
        issues = jira.search_issues(query, startAt=startAt, maxResults=50)
        linkedIssues.extend(issues)

    theIssues = []

    for item in linkedIssues:
        blockedIssues = [link for link in item.fields.issuelinks if link.type.name == 'Blocks']

        activeBlockers = []
        for bi in blockedIssues:
            if hasattr(bi, 'inwardIssue'):
                if bi.inwardIssue.fields.status.name in blockingStatuses:
                    activeBlockers.append(f'{bi.inwardIssue.key} [{bi.inwardIssue.fields.status}]')
                    # print(f'Blocked By: {bi.inwardIssue.key}, {bi.inwardIssue.fields.status}')
        
        if len(activeBlockers) == 0:
            if str(item.fields.issuetype) == 'Story':
                emoji = '📖'
            elif str(item.fields.issuetype) == 'Bug':
                emoji = '🐞'
            elif str(item.fields.issuetype) == 'Spike':
                emoji = '🌵'
            else:
                emoji = ''
            
            theIssues.append(f"<a href='{item.permalink()}'>{item.key}</a> {item.fields.summary} | No Active Blockers | Reporter: {item.fields.reporter}, Type: {item.fields.issuetype} {emoji}")
        else:
            pass
            # activeBlockersList = ',  '.join(activeBlockers)
            # theIssues.append(f"<a href='{item.permalink()}'>{item.key}</a> | Active Blockers: {activeBlockersList} {item.permalink()}")

    # theIssues

    for i in theIssues:
        if 'No Active Blockers' in i:
            st.write(i, unsafe_allow_html=True)
    

