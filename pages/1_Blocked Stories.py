import streamlit as st
from jira import JIRA
import pandas as pd
import json
import os
import jiraReads #py file

#Check for dotenv. To be removed later
try:
  from dotenv import load_dotenv
  load_dotenv()
except ModuleNotFoundError:
  st.error("⚠️ **Install python-dotenv package**")
  st.code("pip install python-dotenv")
  st.stop()

### adding credentials
email = os.getenv("email")
apiToken = os.getenv("apiToken")

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
  page_icon="🚧",
#   layout="wide"
)

st.title('Blocked items without active blockers', help="Stories with **Blocked** status that has no active **blocked by** links")

selectedComponent = st.selectbox('Select team', [board for boards in jiraInfo['boards'] for board in boards], help='Select jira Component to determine team')

blockedJira = jiraReads.blockedStories(jira, projectName, selectedComponent, server)
blockedJira = blockedJira.loc[blockedJira['Epic Status'] != 'Blocked']

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
        st.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>"
                 f"Assignee: {row['Assignee']}, Reporter: {row['Reporter']}, Type: {row['Type']} {row['TypeEmoji']}", unsafe_allow_html=True)
    else:
        st.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>"
                 f"Assignee: {row['Assignee']}, Reporter: {row['Reporter']}, Type: {row['Type']} {row['TypeEmoji']}, "
                 f"Epic: <a href='{row['Epic link']}'>{row['Epic']}</a>, Epic Status: {row['Epic Status']}", unsafe_allow_html=True)

if st.button('Refresh ALL Jira items', help=f'Clears all Cached data for all pages. Cache is set to {int(jiraReads.cacheTime/60)}min'):
    st.cache_data.clear()
    st.rerun()