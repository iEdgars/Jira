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
  page_title="Refinement items",
  page_icon="📝",
#   layout="wide"
)

st.title('DE Ready for Refinment items', help="DE Ready for Refinment items with buttons to copy /storyplan ready statement and link to story")

# selectedComponent = st.selectbox('Select team', [board for boards in jiraInfo['boards'] for board in boards], help='Select Jira Component to determine team')
selectedComponent = "DE"

# refinmentItems = jiraReads.readyForRefinementItemsDE(jira, projectName, selectedComponent, server)
refinmentItems = jiraReads.readyForRefinementItems(jira, projectName, selectedComponent, server, 'Ready for Refinement')
        
if st.button('Refresh ALL Jira items', help=f'Clears all Cached data for all pages. Cache is set to {int(jiraReads.cacheTime/60)}min'):
    st.cache_data.clear()
    st.rerun()

if st.toggle('**Critical and High priority items only**'):
    refinmentItems = refinmentItems[refinmentItems['Priority'].isin(['P1', 'P2'])]

st.write('')

for index, row in refinmentItems.iterrows():
    with st.container():
        col1, col2 = st.columns([0.95,0.05])
        # col1, col2, col3 = st.columns([0.87,0.065,0.065])
        if row['Epic'] == 'No Parent':
            col1.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>"
                       f"Assignee: {row['Assignee']}, Reporter: {row['Reporter']}, Type: {row['Type']} {row['TypeEmoji']}, Priority: {row['Priority']}<br>", unsafe_allow_html=True)
        else:
            col1.write(f"<a href='{row['Link']}'>{row['Item number']}</a> <b>{row['Subject']}</b> <br>"
                       f"Assignee: {row['Assignee']}, Reporter: {row['Reporter']}, Type: {row['Type']} {row['TypeEmoji']}, Priority: {row['Priority']}"
                       f" Epic: <a href='{row['Epic link']}'>{row['Epic']}</a><br>", unsafe_allow_html=True)
        
        # approach with lambda is required for buttons to work properly and clipboard value assigned
        col2.button("📋", on_click=lambda storyPlanValue = f"/storyplan {row['Item number']} {row['Subject']}": clipboard.copy(storyPlanValue), key=row['Item number'])
        col2.button("🔗", on_click=lambda itemLinkValue = f"{server}/browse/{row['Item number']}": clipboard.copy(itemLinkValue), key=f"{row['Item number']}_link")

        st.divider()
