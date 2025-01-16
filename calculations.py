def calculate_subnests(subnests_df, mat_price_per_kg, cutting_price_per_sec):
    """
    Adds calculated fields to the Sub Nests DataFrame.
    Args:
        subnests_df (pd.DataFrame): DataFrame containing parsed sub nest data.
        mat_price_per_kg (float): Price of material per kilogram.
        cutting_price_per_sec (float): Cutting price per second.

    Returns:
        pd.DataFrame: DataFrame with calculated columns.
    """
    subnests_df["Total Weight (kg)"] = subnests_df["Weight (kg)"] * subnests_df["Quantity"]
    subnests_df["Cutting Time (sec / sheet)"] = subnests_df["Cutting Time (1 sheet)"].apply(
        lambda x: sum(int(t) * 60 ** i for i, t in enumerate(reversed(x.split(":"))))
    )
    subnests_df["Total Cutting Time (sec)"] = subnests_df["Cutting Time (sec / sheet)"] * subnests_df["Quantity"]
    subnests_df["Total Material Price (€)"] = subnests_df["Total Weight (kg)"] * mat_price_per_kg
    subnests_df["Total Cutting Price (€)"] = subnests_df["Total Cutting Time (sec)"] * cutting_price_per_sec
    subnests_df["Total Price (€)"] = subnests_df["Total Material Price (€)"] + subnests_df["Total Cutting Price (€)"]

    return subnests_df

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
