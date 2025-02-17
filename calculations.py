import pandas as pd

# Global parameters
MIN_CUT_TIME_PER_SHEET_SEC = 900  # Minimum cutting time in seconds per 1 sheet (15 minutes)

class MissingMaterialPriceError(Exception):
    """Custom exception for missing material prices."""
    pass

def convert_hhmmss_to_seconds(time_str):
    """
    Convert time string in HH:MM:SS format to total seconds.
    
    Args:
        time_str (str): Time string in format "HH:MM:SS" (e.g., "00:15:30")
    
    Returns:
        int: Total number of seconds
        
    Example:
        >>> convert_hhmmss_to_seconds("00:15:30")
        930  # (15 minutes * 60) + 30 seconds
    """
    return sum(int(t) * 60 ** i for i, t in enumerate(reversed(time_str.split(":"))))

def apply_minimum_cutting_time(cutting_time_sec):
    """
    Apply minimum cutting time threshold to a given cutting time per sheet.
    If the input time is less than MIN_CUT_TIME_PER_SHEET_SEC (900 seconds/15 minutes),
    return MIN_CUT_TIME_PER_SHEET_SEC instead.
    
    Args:
        cutting_time_sec (int): Original cutting time in seconds for one sheet
    
    Returns:
        int: Either the original cutting time or MIN_CUT_TIME_PER_SHEET_SEC,
             whichever is larger
    
    Example:
        >>> apply_minimum_cutting_time(600)  # 10 minutes
        900  # Returns minimum threshold of 15 minutes
        >>> apply_minimum_cutting_time(1200)  # 20 minutes
        1200  # Returns original time as it's above threshold
    """
    return max(cutting_time_sec, MIN_CUT_TIME_PER_SHEET_SEC)

def calculate_sub_nests(sub_nests_df, mat_price_per_kg, cutting_price_per_sec):
    """
    Adds calculated fields to the Sub Nests DataFrame.
    Args:
        sub_nests_df (pd.DataFrame): DataFrame containing parsed sub nest data.
        mat_price_per_kg (float): Price of material per kilogram.
        cutting_price_per_sec (float): Cutting price per second.

    Returns:
        pd.DataFrame: DataFrame with calculated columns.
    """
    sub_nests_df["Total Weight (kg)"] = sub_nests_df["Weight (kg)"] * sub_nests_df["Quantity"]
    sub_nests_df["Cutting Time (sec / sheet)"] = sub_nests_df["Cutting Time (1 sheet)"].apply(
        lambda x: sum(int(t) * 60 ** i for i, t in enumerate(reversed(x.split(":"))))
    )
    sub_nests_df["Total Cutting Time (sec)"] = sub_nests_df["Cutting Time (sec / sheet)"] * sub_nests_df["Quantity"]
    sub_nests_df["Total Material Price (€)"] = sub_nests_df["Total Weight (kg)"] * mat_price_per_kg
    sub_nests_df["Total Cutting Price (€)"] = sub_nests_df["Total Cutting Time (sec)"] * cutting_price_per_sec
    sub_nests_df["Total Price (€)"] = sub_nests_df["Total Material Price (€)"] + sub_nests_df["Total Cutting Price (€)"]

    return sub_nests_df

def calculate_parts(parts_df, mat_price_per_kg, cutting_price_per_sec):
    """
    Adds calculated fields to the Parts DataFrame.
    Args:
        parts_df (pd.DataFrame): DataFrame containing parsed parts data.
        mat_price_per_kg (float): Price of material per kilogram.
        cutting_price_per_sec (float): Cutting price per second.

    Returns:
        pd.DataFrame: DataFrame with calculated columns.
    """
    parts_df["Price per Part (€)"] = (
        parts_df["Weight (kg)"] * mat_price_per_kg
    ) + (
        parts_df["Cutting Time (sec)"] * cutting_price_per_sec
    )
    parts_df["Total Price (€)"] = parts_df["Price per Part (€)"] * parts_df["Ordered Qty"]
    
    return parts_df

def calculate_order(combined_data, material_prices, cutting_price_per_sec):
    """
    Calculates prices for all sub nests and parts in the combined data from multiple reports.

    Args:
        combined_data (dict): Combined data from multiple reports, containing:
            - "sub_nests": List of sub-nests across all reports.
            - "parts": List of parts across all reports.
        material_prices (dict): Material prices per kilogram for each material name.
        cutting_price_per_sec (float): Cutting price per second (single value).

    Returns:
        dict: Combined results for sub nests and parts, containing:
            - "sub_nests_with_calcs_df": DataFrame with calculated fields for sub nests.
            - "parts_with_calcs_df": DataFrame with calculated fields for parts.
    """
    # Convert combined data to DataFrames
    sub_nests_df = pd.DataFrame(combined_data["sub_nests"])
    parts_df = pd.DataFrame(combined_data["parts"])

    # Check for missing materials in the material_prices dictionary
    missing_materials = set(sub_nests_df["Material"]) - set(material_prices.keys())
    if missing_materials:
        # Convert the set of missing materials to a comma-separated string and raise a custom exception
        raise MissingMaterialPriceError(f"Missing prices for materials: {', '.join(missing_materials)}")

    # ===== Sub Nests Calculations =====
    sub_nests_df["Total Weight (kg)"] = sub_nests_df["Weight (kg)"] * sub_nests_df["Quantity"]
    
    # Convert Cutting Time (HH:MM:SS) to seconds and apply minimum threshold
    sub_nests_df["Cutting Time (sec / sheet)"] = sub_nests_df["Cutting Time (1 sheet)"].apply(
        lambda x: apply_minimum_cutting_time(convert_hhmmss_to_seconds(x))
    )
    sub_nests_df["Total Cutting Time (sec)"] = sub_nests_df["Cutting Time (sec / sheet)"] * sub_nests_df["Quantity"]
    
    # Calculate Total Material Price based on material name
    # The .apply() method is used to apply a function (in this case, a lambda function) to each row 
    # or column of the DataFrame. axis=1 specifies that the function is applied row by row (not column by column).
    sub_nests_df["Total Material Price (€)"] = sub_nests_df.apply(
        lambda row: round(row["Total Weight (kg)"] * material_prices[row["Material"]], 2), # Round Total Mat. Price to 2 decimal places
        axis=1
    )
    
    # Calculate Total Cutting Price using a single cutting price
    # And round to 2 decimal places
    sub_nests_df["Total Cutting Price (€)"] = round(sub_nests_df["Total Cutting Time (sec)"] * cutting_price_per_sec, 2)
    
    # Total Price for Sub Nests
    sub_nests_df["Total Price (€)"] = sub_nests_df["Total Material Price (€)"] + sub_nests_df["Total Cutting Price (€)"]

    # ===== Parts Calculations =====
    parts_df["Price per Part (€)"] = (
        parts_df.apply(
            lambda row: (
                row["Weight (kg)"] * material_prices[row["Material"]]  # Material-specific price
            ) + (
                row["Cutting Time (sec)"] * cutting_price_per_sec  # Cutting cost
            ),
            axis=1
        )
    )
    # Calcualte total price for all theses parts
    parts_df["Total Price (€)"] = round(parts_df["Price per Part (€)"] * parts_df["Ordered Qty"], 2)

    # Return results
    return {
        "sub_nests_with_calcs_df": sub_nests_df,
        "parts_with_calcs_df": parts_df
    }

