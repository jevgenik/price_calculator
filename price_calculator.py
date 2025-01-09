import streamlit as st
import re # Regular expression library

# Set page layout to wide
#st.set_page_config(layout="wide")

# Title of the app
st.title("Hinnakalkulaator")

# Upload Section
##st.header("Laadi AutoNest'i raportifail üles")
st.write("### Laadi AutoNest'i raportifail üles")
uploaded_file = st.file_uploader("Vali .txt fail", type="txt")

# Dropdown for Metal Type Selection
#st.header("Vali metalli tüüp")
# st.write("### Vali metalli tüüp")
# metal_types = [
#     "Mild Steel",
#     "Stainless Steel",
#     "Aluminum"    
# ]
# selected_metal = st.selectbox("Metalli tüüp", metal_types)

def parse_report(file_content):
    """Parses the uploaded report and extracts relevant information."""
    parsed_data = {}

    # Sample table format:
    # |Plate#  |Size X     |Size Y     |Material    |Thickness |Qty     |Area      |Weight   |Efficiency | 
    # |1       |925        |1500       |Mild Steel  |8.2       |1       |1.39      |89.313   |00:04:18   |

    # Extract the line containing table data (first row of Sub Nests in Order)
    table_row_match = re.search(
        r"\|1\s+\|(\d+)\s+\|(\d+)\s+\|([\w\s]+)\s+\|([\d.]+)\s+\|(\d+)\s+\|([\d.]+)\s+\|([\d.]+)\s+\|([\d:]+)\s+\|",
        file_content
    )

    if table_row_match:
        parsed_data["Sheet Size X"] = int(table_row_match.group(1))    # Size X
        parsed_data["Sheet Size Y"] = int(table_row_match.group(2))    # Size Y
        parsed_data["Material"] = table_row_match.group(3).strip()     # Material
        parsed_data["Thickness"] = float(table_row_match.group(4))     # Thickness
        parsed_data["Total Sheets"] = int(table_row_match.group(5))    # Quantity
        parsed_data["Area"] = float(table_row_match.group(6))          # Area
        parsed_data["Total Weight"] = float(table_row_match.group(7))  # Weight
        parsed_data["Cutting Time"] = table_row_match.group(8).strip() # Efficiency
    else:
        parsed_data["Sheet Size X"] = "Not Found"
        parsed_data["Sheet Size Y"] = "Not Found"
        parsed_data["Material"] = "Not Found"
        parsed_data["Thickness"] = "Not Found"
        parsed_data["Total Sheets"] = "Not Found"
        parsed_data["Area"] = "Not Found"
        parsed_data["Weight"] = "Not Found"
        parsed_data["Cutting Time"] = "Not Found"

    return parsed_data

# Display File Content (Preview)
if uploaded_file:
    st.success("Fail üleslaetud edukalt!")
    # Decode and display the content for preview
    content = uploaded_file.read().decode("utf-8")
    st.text_area("Faili sisu", content, height=300)
    
    # Parse the file content
    parsed_data = parse_report(content)
    
    # Display parsed information
    st.header("Failist loetud andmed")
    for key, value in parsed_data.items():
        st.write(f"**{key}:** {value}")

    # Additional Input for Price Calculation
    if "Total Weight" in parsed_data and isinstance(parsed_data["Total Weight"], float): # If Weight is found in parsed data and is a float
        st.header("Additional Input for Price Calculation")
        cost_per_kg = st.number_input(
            "Enter cost of material per kilogram (€/kg):", min_value=0.0, step=0.1, value=0.0
        )

        # Input for cutting cost per second
        cutting_cost_per_sec = st.number_input(
            "Enter cutting cost per second (€/sec):", min_value=0.0, step=0.001, value=0.0, format="%.3f"  # Ensures three decimal precision in display
        )

        # Convert cutting time (hh:mm:ss) to seconds for calculation
        h, m, s = map(int, parsed_data["Cutting Time"].split(":"))
        cut_time_sec = h * 3600 + m * 60 + s
        
        # Perform the price calculations
        total_weight = parsed_data["Total Weight"]
        total_material_cost = total_weight * cost_per_kg
        total_cutting_cost = cut_time_sec * cutting_cost_per_sec
        total_price = total_material_cost + total_cutting_cost

        # Display results
        st.subheader("Calculation Results")
        st.write(f"**Total Material Weight:** {total_weight} kg")
        st.write(f"**Total Material Cost:** €{total_material_cost:.2f}")
        st.write(f"**Cutting Time:** {cut_time_sec} seconds")
        st.write(f"**Total Cutting Cost:** €{total_cutting_cost:.2f}")
        st.write(f"**Total Price:** €{total_price:.2f}")