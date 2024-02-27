import streamlit as st
from jira import JIRA
import pandas as pd
import json


# Set the page config
st.set_page_config(
  page_title="Refinment",
  page_icon="",
#   layout="wide"
)

st.title('Stories for refinment with copy funtion for slack StoryPlan')