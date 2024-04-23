import streamlit as st
import clipboard
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
  page_title="DA Refinement items",
  page_icon="📝",
#   layout="wide"
)

st.title('DA Refinment items', help="DA Backlog items with buttons to copy /storyplan ready statement and link to story")

# selectedComponent = st.selectbox('Select team', [board for boards in jiraInfo['boards'] for board in boards], help='Select Jira Component to determine team')
selectedComponent = "DA"

refinmentItems = jiraReads.readyForRefinementItemsDA(jira, projectName, selectedComponent, server)

col1, col2 = st.columns(2)

# Get unique Worktypes from the DataFrame
uniqueWorktypes = refinmentItems['DATA: Work type'].unique().tolist()

#Adding possibility to filter to Epics
selectedWorktypes = col1.multiselect('Select Worktypes', uniqueWorktypes, help='Select Worktypes to display')
selectedWorktypesDf = refinmentItems if not selectedWorktypes else refinmentItems[refinmentItems['DATA: Work type'].isin(selectedWorktypes)]

# Get unique Epics from the DataFrame
uniqueEpics = selectedWorktypesDf['Epic'].unique().tolist()

#Adding possibility to filter to Epics
selectedEpics = col2.multiselect('Select Epics', uniqueEpics, default=[], help='Select Epics to display')
selectedEpicsDf = selectedWorktypesDf if not selectedEpics else selectedWorktypesDf[selectedWorktypesDf['Epic'].isin(selectedEpics)]

if st.button('Refresh ALL Jira items', help=f'Clears all Cached data for all pages. Cache is set to {int(jiraReads.cacheTime/60)}min'):
    st.cache_data.clear()
    st.rerun()

for index, row in selectedEpicsDf.iterrows():
    with st.container():
        col1, col2 = st.columns([0.95,0.05])
        if row['Epic'] == 'No Parent':
            col1.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>"
                       f"Assignee: {row['Assignee']}, Reporter: {row['Reporter']}, Type: {row['Type']} {row['TypeEmoji']} <br>"
                       f"Work type: {row['DATA: Work type']}", unsafe_allow_html=True)
        else:
            col1.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>"
                       f"Assignee: {row['Assignee']}, Reporter: {row['Reporter']}, Type: {row['Type']} {row['TypeEmoji']} <br>"
                       f"Work type: {row['DATA: Work type']}, Epic: <a href='{row['Epic link']}'>{row['Epic']}</a>", unsafe_allow_html=True)
        
        # approach with lambda is required for buttons to work properly and clipboard value assigned
        col2.button("📋", on_click=lambda storyPlanValue = f"/storyplan {row['Item number']} {row['Subject']}": clipboard.copy(storyPlanValue), key=row['Item number'])
        col2.button("🔗", on_click=lambda itemLinkValue = f"{server}/browse/{row['Item number']}": clipboard.copy(itemLinkValue), key=f"{row['Item number']}_link")

        st.divider()


