import streamlit as st

# Set the page config
st.set_page_config(
  page_title="JIRA assist",
  page_icon="👋",
#   layout="wide"
)

st.title("This app help's with some items that are harder to get from Jira")

st.markdown("## It is really specific to my usecase and not as robust")

st.markdown('**Pages I curently have:**')

col1, col2 = st.columns([0.25, 0.75])

col1.page_link("pages/1_Blocked Stories.py", label="Blocked Stories", icon="🚧")
col2.markdown("Contains stories with **Blocked** status that has no active **blocked by** links")

col1.page_link("pages/2_Stories to Block.py", label="Stories to block", icon="🔒")
col2.markdown("Contains stories with **Ready** status that has active **blocked by** links")