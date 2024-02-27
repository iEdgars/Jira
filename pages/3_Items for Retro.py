import streamlit as st
from jira import JIRA
import pandas as pd
import json


# Set the page config
st.set_page_config(
  page_title="Retro",
  page_icon="👾",
#   layout="wide"
)

st.title('Stories to be discussed on Retro')