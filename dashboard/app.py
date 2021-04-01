import os

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

engine=create_engine(os.environ['DB_URI'])

df = pd.read_sql(
    "select * from submission_db where length(slack_id) = 11",
    engine
)
df_plot = df.groupby('learning_unit').slack_id.count()

st.dataframe(df_plot, width=1000, height=1000)

ax = df_plot.plot.bar(
    rot=0,
    title='How many students have completed each Learning Unit'
)
st.pyplot(
    ax.get_figure()
)

