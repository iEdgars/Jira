import streamlit as st

# Set the page config
st.set_page_config(
  page_title="JIRA assist",
  page_icon="👋",
#   layout="wide"
)

#migration from cred's in json to .env:
import os
if not os.path.exists('.env'):
  import migrate2dotenv
  migrate2dotenv.migrateCreds()

#Check for dotenv. To be removed later
try:
  from dotenv import load_dotenv
except ModuleNotFoundError:
  st.error("⚠️ **Install python-dotenv package**")
  st.code("pip install python-dotenv")
  st.stop()


st.title("This app help's with some items that are harder to get from Jira")

st.markdown("## It is really specific to my usecase and not as robust")

st.markdown('**Pages I curently have:**')

with st.container():
  col1, col2 = st.columns([0.25, 0.75])

  col1.page_link("pages/1_Blocked Stories.py", label="Blocked Stories", icon="🚧")
  col2.markdown("Contains stories with **Blocked** status that has no active **blocked by** links")

with st.container():
  col1, col2 = st.columns([0.25, 0.75])

  col1.page_link("pages/2_Stories to Block.py", label="Stories to block", icon="🔒")
  col2.markdown("Contains stories with **Ready** status that has active **blocked by** links")

with st.container():
  col1, col2 = st.columns([0.25, 0.75])

  col1.page_link("pages/3_DE Refinement.py", label="DE Refinement", icon="📝")
  col2.markdown("Contains DE Ready for Refinment items")

with st.container():
  col1, col2 = st.columns([0.25, 0.75])

  col1.page_link("pages/4_DA Refinement.py", label="DA Refinement", icon="📝")
  col2.markdown("Contains DA Backlog items for Refinment")