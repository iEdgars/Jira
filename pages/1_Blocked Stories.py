import streamlit as st
from jira import JIRA
import pandas as pd
import json

def typeEmoji(type):
    if str(type) == 'Story':
        emoji = '📖'
    elif str(type) == 'Bug':
        emoji = '🐞'
    elif str(type) == 'Spike':
        emoji = '🌵'
    else:
        emoji = ''

    return emoji

@st.cache_data(ttl=900)
def blockedStories(_jiraConnection, project, component, server):
    columns = ['Item number', 'Link', 'Subject', 'Reporter', 'Type', 'TypeEmoji', 'Epic', 'Epic link']
    df = pd.DataFrame(columns=columns)

    status = 'Blocked'
    blockingStatuses = ['Ready','Blocked','Backlog','In Progress','UAT', 'In Testing', 'Ready for Refinement']
    nonBlockingStatuses = ['Done','Rejected']

    query = f'project = {project} AND component = {component} AND status = {status}'

    startAt = 0
    issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)
    linkedIssues = issues

    while len(issues) > 0:
        # for issue in issues:
            # print(issue.key, issue.fields.summary, issue.fields.status, issue.fields.assignee, issue.fields.created[:10], issue.fields.updated[:10], issue.fields.updated[11:16], issue.permalink())
        startAt += 50
        issues = jira.search_issues(query, startAt=startAt, maxResults=50)
        linkedIssues.extend(issues)

    theIssues = []
    parents = []

    for item in linkedIssues:
        blockedIssues = [link for link in item.fields.issuelinks if link.type.name == 'Blocks']

        activeBlockers = []
        for bi in blockedIssues:
            if hasattr(bi, 'inwardIssue'):
                if bi.inwardIssue.fields.status.name in blockingStatuses:
                    activeBlockers.append(f'{bi.inwardIssue.key} [{bi.inwardIssue.fields.status}]')
                    # print(f'Blocked By: {bi.inwardIssue.key}, {bi.inwardIssue.fields.status}')
        
        try:
            parentEpic = item.fields.parent
            epicLink = f'{server}/browse/{str(item.fields.parent)}'
        except:
            parentEpic = 'No Parent'
            epicLink = ''

        emoji = typeEmoji(item.fields.issuetype)

        if len(activeBlockers) == 0:

            ticket = [item.key, item.permalink(), item.fields.summary, item.fields.reporter, item.fields.issuetype, emoji, parentEpic, epicLink]
            df.loc[len(df)] = ticket
        
        else:
            pass
    
    df = df.drop_duplicates()    

    return df


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
projectName = jiraInfo['project_name']

jira = JIRA(basic_auth=(email, apiToken), options={'server': server})

#### Start for StreamLit ####

# Set the page config
st.set_page_config(
  page_title="Blocked items",
  page_icon="✖",
#   layout="wide"
)

st.title('Blocked items without active blockers')

selectedComponent = st.selectbox('Select team', [board for boards in jiraInfo['boards'] for board in boards], help='Select jira Component to determine team')

blockedJira = blockedStories(jira, projectName, selectedComponent, server)

col1, col2 = st.columns(2)

# Get unique Epics from the DataFrame
uniqueEpics = blockedJira['Epic'].unique().tolist()

#Adding possibility to remove Epics
excludedEpics = col1.multiselect('Remove Epics', uniqueEpics, help='Select Epics to remove' )
excludedEpicsDf = blockedJira if not excludedEpics else blockedJira[~blockedJira['Epic'].isin(excludedEpics)]

#Adding possibility to Select Epics
uniqueEpics = [epic for epic in uniqueEpics if epic not in excludedEpics]

# Create a multiselect widget for Epics
selectedEpics = col2.multiselect('Select Epics', uniqueEpics, help='Select Epics to display' )

# Filter the DataFrame based on selected Epics, or show all if none are selected
filtered_df = excludedEpicsDf if not selectedEpics else excludedEpicsDf[excludedEpicsDf['Epic'].isin(selectedEpics)]

for index, row in filtered_df.iterrows():
    if row['Epic'] == 'No Parent':
        st.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>Reporter: {row['Reporter']}, Type: {row['Type']} {row['TypeEmoji']}", unsafe_allow_html=True)
    else:
        st.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>Reporter: {row['Reporter']}, Type: {row['Type']} {row['TypeEmoji']}, Epic: <a href='{row['Epic link']}'>{row['Epic']}</a>", unsafe_allow_html=True)
