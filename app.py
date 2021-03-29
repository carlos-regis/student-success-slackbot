import os

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

engine=create_engine(os.environ['DB_URI'])
df = pd.read_sql(
    "select * from submission_db where length(slack_id) = 11",
    engine
)
ax = df.groupby('learning_unit').slack_id.count().plot.bar(
    rot=0,
    'How many students have completed each Learning Unit'
)
st.pyplot(
    ax.get_figure()
)

# st.dataframe(df, width=700, height=1000)
