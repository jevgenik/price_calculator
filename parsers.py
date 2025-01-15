import re # Regular expression library

def parse_subnests(file_content):
    """
    Parses the 'Sub Nests in Order' table from the report.

    Args:
        file_content (str): The entire content of the uploaded .txt report as a string.
                            This includes all sections of the report, such as tables, headers, etc.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a row
                    in the 'Sub Nests in Order' table with the following keys:
                    - Plate#: Plate number
                    - Sheet Size X: Size in the X dimension
                    - Sheet Size Y: Size in the Y dimension
                    - Material: Material name (e.g., "Mild Steel")
                    - Thickness: Thickness of the material
                    - Quantity: Quantity of sheets
                    - Area: Area of each sheet
                    - Weight: Weight of each sheet
                    - Cutting Time (1 sheet): Time required to cut one sheet in HH:MM:SS format
    """
    # Example input format to parse:
    # |Plate#  |Size X      |Size Y     |Material    |Thickness |Qty     |Area      |Weight    |Efficiency | 
    # |1       |3000        |1500       |Mild Steel  |4.2       |6       |4.50      |148.365   |00:48:08    |
    # |2       |3000        |1500       |Mild Steel  |4.2       |1       |5.50      |148.365   |00:43:09    |

    # List to store all parsed rows (each list element/row is a dictionary)
    # [ 
    #   { "Plate#": 1, "Sheet Size X": 3000, "Sheet Size Y": 1500, "Material": "Mild Steel", "Thickness": 4.2, "Quantity": 6, "Area": 4.50, "Weight": 148.365, "Cutting Time (1 sheet)": "00:48:08" },
    #   { "Plate#": 2, "Sheet Size X": 3000, "Sheet Size Y": 1500, "Material": "Mild Steel", "Thickness": 4.2, "Quantity": 1, "Area": 5.50, "Weight": 148.365, "Cutting Time (1 sheet)": "00:43:09" }
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
    # match[0] - 1st element in the tuple, match[1] - 2nd element, and so on
    for match in table_row_matches:
        parsed_rows.append({
            "Plate#": int(match[0]),                     # Plate number
            "Sheet Size X (mm)": int(match[1]),          # Size X
            "Sheet Size Y (mm)": int(match[2]),          # Size Y
            "Material": match[3].strip(),                # Material
            "Thickness (mm)": float(match[4]),           # Thickness
            "Quantity": int(match[5]),                   # Quantity
            "Area (m²)": float(match[6]),                # Area (optional)
            "Weight (kg)": float(match[7]),              # Weight
            "Cutting Time (1 sheet)": match[8].strip()   # Efficiency (Cutting Time in HH:MM:SS format)
        })

    return parsed_rows

def parse_parts(file_content):
    """
    Parses the 'Parts in Order' table from the report.

    Args:
        file_content (str): The entire content of the uploaded .txt report as a string.
                            This includes all sections of the report, such as tables, headers, etc.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a row
                    in the 'Parts in Order' table with the following keys:
                    - Part Name: The extracted part name from the full file path
                    - Ordered Qty: The number of parts ordered
                    - Weight (kg): The weight of a single part in kilograms
                    - Cutting Time (sec): The time to cut a single part in seconds
    """
    # Regex to match rows in the "Parts in Order" table
    parts_table_matches = re.findall(
        r"\|(.+?)\s+\|(\d+)\s+\|(\d+)\s+\|([\d.]+)\s+\|([\d:]+)\s+\|",
        file_content
    )

    # Process matched rows
    parts_data = []
    for match in parts_table_matches:
        full_path, ordered_qty, placed_qty, weight, cutting_time = match # match is a tuple, unpack it into variables

        # Extract the part name from the full file path
        # The regex captures numbers (and optional dashes) before an underscore
        part_name = re.search(r"([\w-]+)_", full_path).group(1)

        # Convert data types
        ordered_qty = int(ordered_qty)
        weight = float(weight)
        # Convert cutting time (HH:MM:SS) to seconds
        cutting_time_sec = sum(int(x) * 60 ** i for i, x in enumerate(reversed(cutting_time.split(":"))))

        # Add the parsed data to the list
        parts_data.append({
            "Part Name": part_name,
            "Ordered Qty": ordered_qty,
            "Weight (kg)": weight,
            "Cutting Time (sec)": cutting_time_sec
        })

    return parts_data
