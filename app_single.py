import streamlit as st
import pandas as pd
from parsers import parse_sub_nests, parse_parts
from calculations import calculate_sub_nests, calculate_parts
from ui_components import display_table, display_summary

# Streamlit configuration
st.set_page_config(page_title="Hinnakalkulaator", page_icon=":moneybag:", layout="wide")

# Title
st.title("Hinnakalkulaator")

# File upload
uploaded_file = st.file_uploader("Vali .txt fail", type="txt")

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")

    # Preview file content
    st.subheader("Loetud sisendandmed")  # H3
    with st.expander("Preview Uploaded File (Expand to View)"):
        st.text_area("Faili sisu", content, height=300)

    # Parse data
    # Get lists of dictionaries for sub_nests and parts
    sub_nests_data = parse_sub_nests(content)
    #print(f"Sub Nests parsed rows: {sub_nests_data}")  # Debugging: Print parsed rows

    parts_data = parse_parts(content)

    # Convert to DataFrames
    sub_nests_df = pd.DataFrame(sub_nests_data)
    #print(f"Sub Nests dataframe columns: {sub_nests_df.columns}")  # Debugging: Print columns

    parts_df = pd.DataFrame(parts_data)

    # Input fields for prices
    #mat_price_per_kg = st.number_input("Enter price of material per kilogram (€/kg):", min_value=0.0, step=0.1, value=0.0)
    #cutting_price_per_sec = st.number_input("Enter cutting price per second (€/sec):", min_value=0.0, step=0.001, value=0.0)
    # Input fields for prices (moved to sidebar)
    with st.sidebar:
        st.subheader("Price Inputs")  # Optional header in sidebar
        mat_price_per_kg = st.number_input("Enter material price per kilogram (€/kg):", min_value=0.0, step=0.1, value=0.0)
        cutting_price_per_sec = st.number_input("Enter cutting price per second (€/sec):", min_value=0.0, step=0.001, value=0.0)

    # Perform calculations for sub_nests and parts
    sub_nests_df = calculate_sub_nests(sub_nests_df, mat_price_per_kg, cutting_price_per_sec)
    parts_df = calculate_parts(parts_df, mat_price_per_kg, cutting_price_per_sec)    

    # ====== Sub Nests =====
    #display_table(sub_nests_df, "Sub Nests in Order")
    display_table(
      sub_nests_df[[
          "Plate#", "Sheet Size X (mm)", "Sheet Size Y (mm)", "Material", "Thickness (mm)", 
          "Quantity", "Weight (kg)", "Total Weight (kg)", "Total Material Price (€)", 
          "Total Cutting Time (sec)", "Total Cutting Price (€)", "Total Price (€)"
      ]],
      "Sub Nests in Order"
    )

    # Summarize the total values
    total_weight = sub_nests_df["Total Weight (kg)"].sum()
    total_material_price = sub_nests_df["Total Material Price (€)"].sum()
    total_cutting_price = sub_nests_df["Total Cutting Price (€)"].sum()
    total_cutting_time_sec = sub_nests_df["Total Cutting Time (sec)"].sum()
    total_price = sub_nests_df["Total Price (€)"].sum()

    # Pass all calculated values to the summary display
    display_summary(total_weight, total_material_price, total_cutting_time_sec, total_cutting_price, total_price)
    
    # ====== Parts =====
    # Display the "Parts in Order" table 
    display_table(parts_df, "Parts in Order")    

    # Calculate total price for all parts
    total_parts_price = parts_df["Total Price (€)"].sum()

    # Display the total price below the "Parts in Order" table
    st.markdown(
        f"<h3 style='color:green;'>Total Price (All Parts): €{total_parts_price:.2f}</h3>",
        unsafe_allow_html=True
    )
