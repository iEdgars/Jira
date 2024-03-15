import streamlit as st
import clipboard
from jira import JIRA
import pandas as pd
import json

def typeEmoji(type):
    if str(type) == 'Story':
        emoji = '📝'
    elif str(type) == 'Bug':
        emoji = '🐛'
    elif str(type) == 'Spike':
        emoji = '❗📌❗' #'🌵'
    elif str(type) == 'Epic':
        emoji = '🚀'
    else:
        emoji = ''

    return emoji

@st.cache_data(ttl=900)
def readyForRefinementItems(_jiraConnection, project, component, server):
    columns = ['Item number', 'Link', 'Subject', 'Assignee', 'Reporter', 'Type', 'TypeEmoji', 'Epic', 'Epic link']
    df = pd.DataFrame(columns=columns)

    status = 'Ready for Refinement'
    # query = f'project = {project} AND component = {component} AND status = "{status}" AND type in (Bug, Story) ORDER BY cf[10011] ASC'
    query = f'project = {project} AND component = {component} AND status = "{status}" AND type NOT IN (Epic) ORDER BY cf[10011] ASC'

    startAt = 0
    issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)

    while len(issues) > 0:
    # while startAt < 100:
        for issue in issues:

            try:
                parentEpic = issue.fields.parent
                epicLink = f'{server}/browse/{str(issue.fields.parent)}'
            except:
                parentEpic = 'No Parent'
                epicLink = ''

            emoji = typeEmoji(issue.fields.issuetype)

            ticket = [issue.key, issue.permalink(), issue.fields.summary, issue.fields.assignee, issue.fields.reporter, issue.fields.issuetype, emoji, parentEpic, epicLink]
            df.loc[len(df)] = ticket
            
        startAt += 50
        issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)

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
  page_title="Refinement items",
  page_icon="📝",
#   layout="wide"
)

st.title('DE Ready for Refinment items', help="DE Ready for Refinment items with buttons to copy /storyplan ready statement and link to story")

# selectedComponent = st.selectbox('Select team', [board for boards in jiraInfo['boards'] for board in boards], help='Select Jira Component to determine team')
selectedComponent = "DE"

refinmentItems = readyForRefinementItems(jira, projectName, selectedComponent, server)

col1, col2 = st.columns([0.9,0.1])

for index, row in refinmentItems.iterrows():
    if row['Epic'] == 'No Parent':
        col1.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>Assignee: {row['Assignee']}, Reporter: {row['Reporter']}, Type: {row['Type']} {row['TypeEmoji']}<br>", unsafe_allow_html=True)
    else:
        col1.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>Assignee: {row['Assignee']}, Reporter: {row['Reporter']}, Type: {row['Type']} {row['TypeEmoji']}, Epic: <a href='{row['Epic link']}'>{row['Epic']}</a><br>", unsafe_allow_html=True)
    col2.button("📋", on_click=clipboard.copy(f"/storyplan {row['Item number']} {row['Subject']}"), key=row['Item number'])
    col2.button("🔗", on_click=clipboard.copy(f"{server}/browse/{row['Item number']}"), key=f"{row['Item number']}_link")


if st.button('Refresh ALL Jira items', help='Clears all Cached data for all pages'):
    st.cache_data.clear()
    st.rerun()