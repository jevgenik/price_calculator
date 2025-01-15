import streamlit as st
import pandas as pd
from parsers import parse_subnests, parse_parts
from calculations import calculate_subnests, calculate_parts
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
    subnests_data = parse_subnests(content)
    parts_data = parse_parts(content)

    # Convert to DataFrames
    subnests_df = pd.DataFrame(subnests_data)
    parts_df = pd.DataFrame(parts_data)

    # Input fields for prices
    price_per_kg = st.number_input("Enter price of material per kilogram (€/kg):", min_value=0.0, step=0.1, value=0.0)
    cutting_price_per_sec = st.number_input("Enter cutting price per second (€/sec):", min_value=0.0, step=0.001, value=0.0)

    # Perform calculations for subnests and parts
    subnests_df = calculate_subnests(subnests_df, price_per_kg, cutting_price_per_sec)
    parts_df = calculate_parts(parts_df, price_per_kg, cutting_price_per_sec)
    
    # Round numeric values in the DataFrame to 2 decimal places
    parts_df = parts_df.round(2)

    # Exclude specific columns from totals calculation (e.g., "Price per Part (€)")
    exclude_columns = ["Weight (kg)", "Cutting Time (sec)", "Price per Part (€)"]
    totals_row = {
        col: parts_df[col].sum() if col not in exclude_columns and pd.api.types.is_numeric_dtype(parts_df[col]) else "TOTALS"
        for col in parts_df.columns
    }

    # Format numeric totals to 2 decimal places
    #totals_row["Weight (kg)"] = f"{totals_row['Weight (kg)']:.2f}"
    #totals_row["Total Price (€)"] = f"{totals_row['Total Price (€)']:.2f}"

    # Convert totals_row to a DataFrame with a single row
    totals_df = pd.DataFrame([totals_row])

    # Concatenate the totals row with the original parts DataFrame
    parts_df_with_totals = pd.concat([parts_df, totals_df], ignore_index=True)

    # Display tables
    #display_table(subnests_df, "Sub Nests in Order")
    display_table(
      subnests_df[[
          "Plate#", "Sheet Size X (mm)", "Sheet Size Y (mm)", "Material", "Thickness (mm)", 
          "Quantity", "Weight (kg)", "Total Weight (kg)", "Total Material Price (€)", 
          "Total Cutting Time (sec)", "Total Cutting Price (€)", "Total Price (€)"
      ]],
      "Sub Nests in Order"
    )
    # Display the "Parts in Order" table with totals
    display_table(parts_df_with_totals, "Parts in Order (with Totals)")
    #display_table(parts_df, "Parts in Order")

    # Summarize the total values
    total_weight = subnests_df["Total Weight (kg)"].sum()
    total_material_price = subnests_df["Total Material Price (€)"].sum()
    total_cutting_price = subnests_df["Total Cutting Price (€)"].sum()
    total_cutting_time_sec = subnests_df["Total Cutting Time (sec)"].sum()
    total_price = subnests_df["Total Price (€)"].sum()

    # Pass all calculated values to the summary display
    display_summary(total_weight, total_material_price, total_cutting_time_sec, total_cutting_price, total_price)
