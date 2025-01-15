def calculate_subnests(parsed_df, mat_price_per_kg, cutting_price_per_sec):
    """
    Adds calculated fields to the Sub Nests DataFrame.
    Args:
        parsed_df (pd.DataFrame): DataFrame containing parsed sub nest data.
        mat_price_per_kg (float): Price of material per kilogram.
        cutting_price_per_sec (float): Cutting price per second.

    Returns:
        pd.DataFrame: DataFrame with calculated columns.
    """
    parsed_df["Total Weight (kg)"] = parsed_df["Weight (kg)"] * parsed_df["Quantity"]
    parsed_df["Cutting Time (sec / sheet)"] = parsed_df["Cutting Time (1 sheet)"].apply(
        lambda x: sum(int(t) * 60 ** i for i, t in enumerate(reversed(x.split(":"))))
    )
    parsed_df["Total Cutting Time (sec)"] = parsed_df["Cutting Time (sec / sheet)"] * parsed_df["Quantity"]
    parsed_df["Total Material Price (€)"] = parsed_df["Total Weight (kg)"] * mat_price_per_kg
    parsed_df["Total Cutting Price (€)"] = parsed_df["Total Cutting Time (sec)"] * cutting_price_per_sec
    parsed_df["Total Price (€)"] = parsed_df["Total Material Price (€)"] + parsed_df["Total Cutting Price (€)"]
    return parsed_df


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
