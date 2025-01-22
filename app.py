import streamlit as st
import pandas as pd
from parsers import parse_sub_nests, parse_parts, parse_multiple_reports
from calculations import calculate_sub_nests, calculate_parts, calculate_order, MissingMaterialPriceError
from ui_components import display_table, display_summary
from api_utils import submit_prices_to_bubble

# Streamlit configuration
st.set_page_config(page_title="Hinnakalkulaator", page_icon=":moneybag:", layout="wide")

# Title
st.title("Hinnakalkulaator")

# Define a dictionary of materials with default prices (€/kg)
materials_with_prices = {
    "Aluminum": 1.9,
    "Galvanized Steel": 0.5,   
    "Mild Steel": 0.3,    
    "Stainless Steel": 1.7
}

# Sidebar inputs for prices
with st.sidebar:
    st.subheader("Price Inputs")
    
    # Dynamic input fields for material prices
    # material_prices is a dictionary with material names as keys and user entered prices as values
    material_prices = {}
    for material, default_price in materials_with_prices.items():
        material_prices[material] = st.number_input(
            f"Price for {material} (€/kg):",
            min_value=0.0,
            step=0.1,
            value=default_price
        )
    
    # Single input for cutting price
    cutting_price_per_sec = st.number_input(
        "Enter cutting price per second (€/sec):", min_value=0.0, step=0.001, value=0.05
    )

# Initialize session state variables
if "sub_nests_df" not in st.session_state:
    st.session_state.sub_nests_df = None
if "parts_df" not in st.session_state:
    st.session_state.parts_df = None

# Upload multiple reports
# Rreturns a list of file objects
uploaded_files = st.file_uploader("Upload Metallix AutoNest reports", type="txt", accept_multiple_files=True)

if uploaded_files:
    # Read the content of each uploaded file
    # file_contents is a list of strings (like ['file1 content', 'file2 content'])    
    #file_contents = [file.read().decode("utf-8") for file in uploaded_files]

    file_contents = [] # List to store the content (as strings) of all uploaded files
    for file in uploaded_files: # file is a file object
        # Read and decode the file content
        content = file.read().decode("utf-8")
        file_contents.append(content)
        
        # Display the file name and preview content in an expandable section
        with st.expander(f"Preview: {file.name}"):
            st.text_area(f"Content of {file.name}", content, height=300)

# Add a button to process the uploaded files
if st.button("Process Files"):
    if not uploaded_files:
        st.warning("Please upload at least one file before processing!")
    else:
        # Combine and process report files
        st.write("Processing uploaded reports...")

        try:
            # Parse and calculate combined data
            combined_data = parse_multiple_reports(file_contents)
            # material_prices is a dictionary contains the material names as keys and their corresponding user-specified prices 
            # (from the sidebar input) as values.
            results = calculate_order(combined_data, material_prices, cutting_price_per_sec)        
        except MissingMaterialPriceError as e:
            st.error(str(e))  # Display a specific message for missing material prices
            st.stop()  # Gracefully halt execution
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")  # Catch any other unexpected error
            st.stop()

        # Extract results (DataFrames) from the combined results dictionary
        #sub_nests_df = results["sub_nests_with_calcs_df"]
        #parts_df = results["parts_with_calcs_df"]
        # Store results in session state
        st.session_state.sub_nests_df = results["sub_nests_with_calcs_df"]
        st.session_state.parts_df = results["parts_with_calcs_df"]        

        # ===== Display Results =====
        st.subheader("Sub Nests in Order")
        #st.dataframe(sub_nests_df, use_container_width=False) 
        
        # Display sub nests in order (all sub nests combined from all reports)
        st.dataframe(
             st.session_state.sub_nests_df[
                 [
                     "Sheet Size X (mm)", "Sheet Size Y (mm)", "Material", "Thickness (mm)", 
                     "Quantity", "Weight (kg)", "Total Weight (kg)", "Total Material Price (€)", 
                     "Total Cutting Time (sec)", "Total Cutting Price (€)", "Total Price (€)"
                 ]
            ], 
            hide_index=False,                 
            use_container_width=False
        )

        # Sub Nests Summaries
        total_material_weight = st.session_state.sub_nests_df["Total Weight (kg)"].sum()
        total_material_price = st.session_state.sub_nests_df["Total Material Price (€)"].sum()
        total_cutting_time_sec = st.session_state.sub_nests_df["Total Cutting Time (sec)"].sum()
        # Convert cutting time to HH:MM:SS format
        total_cutting_time_hms = f"{total_cutting_time_sec // 3600:02}:{(total_cutting_time_sec % 3600) // 60:02}:{total_cutting_time_sec % 60:02}"
        total_cutting_price = st.session_state.sub_nests_df["Total Cutting Price (€)"].sum()
        total_price_sub_nests = st.session_state.sub_nests_df["Total Price (€)"].sum()

        st.markdown(f"**Total Material Weight:** {total_material_weight:.2f} kg")
        st.markdown(f"**Total Material Price:** €{total_material_price:.2f}")
        st.markdown(f"**Total Cutting Time:** {total_cutting_time_hms} (HH:MM:SS) / {total_cutting_time_sec} seconds")
        st.markdown(f"**Total Cutting Price:** €{total_cutting_price:.2f}")
        st.markdown(f"<h3 style='color:green;'>Total Price: €{total_price_sub_nests:.2f}</h3>", unsafe_allow_html=True)

        # Combined Parts Summary
        total_price_parts = st.session_state.parts_df["Total Price (€)"].sum()

        st.subheader("Parts in Order")
        st.dataframe(st.session_state.parts_df, use_container_width=False) # Display parts in order (all parts combined from all reports)

        st.markdown(f"<h3 style='color:green;'>Total Price (All Parts): €{total_price_parts:.2f}</h3>", unsafe_allow_html=True)        


# ===== Submit prices to Bubble =====
if st.button("Submit Prices"):
    if st.session_state.parts_df is None:
        st.error("Please process the files first before submitting prices.")
    else:
        st.write("Submitting prices to Bubble...")
        quote_data = {
            "status": "Draft",
            "items": st.session_state.parts_df.to_dict("records") # Convert DataFrame to list of dictionaries
        }

        # Call API function
        success, message = submit_prices_to_bubble(quote_data)
        if success:
            st.success(message)
        else:
            st.error(message)