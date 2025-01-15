import streamlit as st

def display_table(df, title):
    """
    Displays a DataFrame in Streamlit with a title.
    Args:
        df (pd.DataFrame): DataFrame to display.
        title (str): Title for the table.
    """
    st.subheader(title)

    table_height = 35 * len(df) + 38  # Estimate: 35px per row + padding
    st.dataframe(df, 
                 hide_index=True,
                 height=table_height # Set the height of the table to show all rows without scrolling
    )

def display_summary(total_weight, total_material_price, total_cutting_time_sec, total_cutting_price, total_price):
    """
    Displays a summary of total prices and times.

    Args:
        total_weight (float): Total material weight.
        total_material_price (float): Total material price.
        total_cutting_time_sec (int): Total cutting time in seconds.
        total_cutting_price (float): Total cutting price.
        total_price (float): Total price.
    """
    # Convert total_cutting_time_sec to HH:MM:SS format
    total_cutting_time = f"{total_cutting_time_sec // 3600:02}:{(total_cutting_time_sec % 3600) // 60:02}:{total_cutting_time_sec % 60:02}"

    # Display the summary
    st.write(f"**Total Material Weight:** {total_weight:.2f} kg")
    st.write(f"**Total Material Price:** €{total_material_price:.2f}")
    st.write(f"**Total Cutting Time:** {total_cutting_time} (HH:MM:SS) / {total_cutting_time_sec} seconds")
    st.write(f"**Total Cutting Price:** €{total_cutting_price:.2f}")
    st.markdown(
        f"<h3 style='color:green;'>Total Price: €{total_price:.2f}</h3>",
        unsafe_allow_html=True
    )
