import streamlit as st
import re # Regular expression library
import pandas as pd

# Set page layout to wide
#st.set_page_config(layout="wide")

# Configure the page    
st.set_page_config(
    page_title="Hinnakalkulaator",
    page_icon=":moneybag:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Title of the app
st.title("Hinnakalkulaator") # H1

# Upload Section
##st.header("Laadi AutoNest'i raportifail üles") # H2
#st.write("### Laadi AutoNest'i raportifail üles") 
st.subheader("Laadi AutoNest'i raportifail üles") # H3
#uploaded_file = st.sidebar.file_uploader("Vali .txt fail", type="txt")
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
    """Parses the uploaded report and extracts all rows from the 'Sub Nests in Order' table."""
    # Example input format to parse:
    # |Plate#  |Size X     |Size Y     |Material    |Thickness |Qty     |Area      |Weight   |Efficiency | 
    # |1       |3000        |1500       |Mild Steel  |4.2       |6       |4.50      |148.365   |00:48:08    |
    # |2       |3000        |1500       |Mild Steel  |4.2       |1       |5.50      |148.365   |00:43:09    |

    # List to store all parsed rows (each list element/row is a dictionary)
    # [ 
    #   { "Plate#": 1, "Sheet Size X": 3000, "Sheet Size Y": 1500, "Material": "Mild Steel", "Thickness": 4.2, "Quantity": 6, "Area": 4.50, "Weight": 148.365, "Cutting Time": "00:48:08" },
    #   { "Plate#": 2, "Sheet Size X": 3000, "Sheet Size Y": 1500, "Material": "Mild Steel", "Thickness": 4.2, "Quantity": 1, "Area": 5.50, "Weight": 148.365, "Cutting Time": "00:43:09" }
    # ]
    parsed_rows = []

    # Regex to match each row in the "Sub Nests in Order" table
    # findall() returns a list of tuples, where each tuple contains the matched groups (columns) for a row
    # e.g. [(1, 3000, 1500, "Mild Steel", 4.2, 6, 4.50, 148.365, "00:48:08"), (2, 3000, 1500, "Mild Steel", 4.2, 1, 5.50, 148.365, "00:43:09")]
    table_row_matches = re.findall(
        r"\|(\d+)\s+\|(\d+)\s+\|(\d+)\s+\|([\w\s]+)\s+\|([\d.]+)\s+\|(\d+)\s+\|([\d.]+)\s+\|([\d.]+)\s+\|([\d:]+)\s+\|",
        file_content
    )

    # Convert the matched tuples to a list of dictionaries
    for match in table_row_matches:
        parsed_rows.append({
            "Plate#": int(match[0]),          # Plate number
            "Sheet Size X": int(match[1]),    # Size X
            "Sheet Size Y": int(match[2]),    # Size Y
            "Material": match[3].strip(),     # Material
            "Thickness": float(match[4]),     # Thickness
            "Quantity": int(match[5]),        # Quantity
            "Area": float(match[6]),          # Area
            "Weight": float(match[7]),        # Weight
            "Cutting Time": match[8].strip()  # Efficiency
        })

    return parsed_rows

# Display File Content (Preview)
if uploaded_file:
    st.success("Fail üleslaetud edukalt!")
    # Decode the file content
    content = uploaded_file.read().decode("utf-8")

    # Collapsible preview table
    with st.expander("Preview Uploaded File (Expand to View)"):        
        st.text_area("Faili sisu", content, height=300)
    
    # Parse the file content
    # parse_report returns a list of dictionaries, where each dictionary represents a row from the report
    parsed_rows = parse_report(content)
    
    # Display parsed information for all rows (sub nests) from the report
    
    # st.subheader("Failist loetud andmed")
    # for i, row in enumerate(parsed_rows):
    #     st.write(f"### Plate #{i+1}")
    #     for key, value in row.items():
    #         st.write(f"**{key}:** {value}")

    if parsed_rows:
        # Convert parsed data to a DataFrame for better display
        parsed_df = pd.DataFrame(parsed_rows)

        # Display the table using Streamlit
        st.table(parsed_df)  # Use st.dataframe(parsed_df) for a scrollable table
    else:
        st.write("No data found in the uploaded file.")

    # Additional Input for Price Calculation
    #if "Weight" in parsed_data and isinstance(parsed_data["Weight"], float): # If Weight is found in parsed data and is a float

    #st.header("Additional Input for Price Calculation")
    st.subheader("Lisainfo hinnakalkulatsiooniks") # H3
    cost_per_kg = st.number_input(
        "Enter cost of material per kilogram (€/kg):", min_value=0.0, step=0.1, value=0.0
    )

    # Input for cutting cost per second
    cutting_cost_per_sec = st.number_input(
        "Enter cutting cost per second (€/sec):", min_value=0.0, step=0.001, value=0.0, format="%.3f"  # Ensures three decimal precision in display
    )

    # Perform calculations for the entire order
    # parsed_rows is a list of dictionaries, where each dictionary represents a row from the report
    if parsed_rows:
        st.subheader("Summary for the Entire Order")

        # Calculate total weight for all rows
        total_weight = sum(row["Weight"] for row in parsed_rows) # row["Weight"] - access the value of the "Weight" key in the row dictionary

        # Calculate total cutting time in seconds for all rows
        total_cutting_time_sec = sum(
            int(h) * 3600 + int(m) * 60 + int(s) 
            for row in parsed_rows 
            for h, m, s in [row["Cutting Time"].split(":")]
        )

        # Convert total cutting time to HH:MM:SS format
        total_cutting_time = f"{total_cutting_time_sec // 3600:02}:{(total_cutting_time_sec % 3600) // 60:02}:{total_cutting_time_sec % 60:02}"

        # Calculate total material cost for all rows
        total_material_cost = sum(row["Weight"] * cost_per_kg for row in parsed_rows)

        # Calculate total cutting cost for all rows
        total_cutting_cost = total_cutting_time_sec * cutting_cost_per_sec

        # Calculate total price for the entire order
        total_price = total_material_cost + total_cutting_cost

        # Display summarized results
        st.write(f"**Total Material Weight:** {total_weight:.2f} kg")
        st.write(f"**Total Material Cost:** €{total_material_cost:.2f}")
        st.write(f"**Total Cutting Time:** {total_cutting_time} / {total_cutting_time_sec} seconds")
        st.write(f"**Total Cutting Cost:** €{total_cutting_cost:.2f}")
        st.markdown(
            f"<h3 style='color:green;'>Total Price: €{total_price:.2f}</h3>",
            unsafe_allow_html=True
        )
    else:
        st.write("No data found in the uploaded file.")
