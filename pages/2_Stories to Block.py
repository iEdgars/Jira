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
  page_title="Items to block",
  page_icon="🔒",
#   layout="wide"
)

st.title('Jira items in Ready state that has active blockers', help="Stories with **Ready** status that has active **blocked by** links")

selectedComponent = st.selectbox('Select team', [board for boards in jiraInfo['boards'] for board in boards], help='Select Jira Component to determine team')

jiraToBlock = jiraReads.storiesToBlock(jira, projectName, selectedComponent, server)

col1, col2 = st.columns(2)

# Get unique Epics from the DataFrame
uniqueEpics = jiraToBlock['Epic'].unique().tolist()

#Adding possibility to remove Epics
excludedEpics = col1.multiselect('Remove Epics', uniqueEpics, help='Select Epics to remove' )
excludedEpicsDf = jiraToBlock if not excludedEpics else jiraToBlock[~jiraToBlock['Epic'].isin(excludedEpics)]

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
                 f"Epic: <a href='{row['Epic link']}'>{row['Epic']}</a>", unsafe_allow_html=True)

status_list = ['Done', 'Rejected', 'Blocked'] #['Blocked', 'Ready', 'Backlog', 'Ready for refinement', 'In Progress']
blockedEpicStories = jiraReads.blockedEpics(jira, projectName)
blockedEpicStories = blockedEpicStories[(~blockedEpicStories['Status'].isin(status_list)) & (blockedEpicStories['Team'] == str(selectedComponent))]

if len(blockedEpicStories) > 0:
    st.divider()
    st.markdown('**Items from Blocked epics that arent marked as Blocked:**')

    for index, row in blockedEpicStories.iterrows():
        st.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>"
                f"Assignee: {row['Assignee']}, Reporter: {row['Reporter']}, Status: {row['Status']}, Type: {row['Type']} {row['TypeEmoji']}, <br>"
                f"Epic: <a href='{row['Epic link']}'>{row['Epic']}</a> <u><b>{row['Epic Subject']}</b></u>", unsafe_allow_html=True)

if st.button('Refresh ALL Jira items', help=f'Clears all Cached data for all pages. Cache is set to {int(jiraReads.cacheTime/60)}min'):
    st.cache_data.clear()
    st.rerun()