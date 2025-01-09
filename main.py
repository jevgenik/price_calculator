import streamlit as st
import pandas as pd
import numpy as np

st.write("Hello World")
#x = st.text_input("Enter your name")
#st.write(f"## Hello {x}")
#st.button("Click me")

st.link_button("Profile", url="/profile")

chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
#st.line_chart(chart_data)
st.bar_chart(chart_data)

data = pd.read_csv("hinnapakkumised_09_01_25.csv") # read_csv ret
st.write(data)