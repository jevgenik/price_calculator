import json
import requests

BUBBLE_API_BASE_URL_DEV = "https://ank-technology-53914.bubbleapps.io/version-test/api/1.1/wf"
BUBBLE_API_BASE_URL_PROD = "https://ank-technology-53914.bubbleapps.io/api/1.1/w"

# For bubble API endpoint parameter automatic detection
#BUBBLE_API_CREATE_QUOTE_INIT_DEV = "https://ank-technology-53914.bubbleapps.io/version-test/api/1.1/wf/create_quote/initialize"

def submit_prices_to_bubble(quote_data):
    """
    Submits the quote and all its items to the Bubble app in a single API call.

    Args:
        quote_data (dict): Nested dictionary containing the quote and its items.

    Returns:
        tuple: (success, response_message)
    """
    try:
        response = requests.post(
            #f"{BUBBLE_API_BASE_URL_DEV}/create_quote",
            f"{BUBBLE_API_BASE_URL_PROD}/create_quote",
            #f"{BUBBLE_API_CREATE_QUOTE_INIT_DEV}",
            headers={"Content-Type": "application/json"},
            json=quote_data
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx status codes)
        #return True, response.json() # Success
        return True, "Quote and items successfully created"
    except requests.exceptions.HTTPError as http_err:
        return False, f"HTTP error occurred: {http_err.response.text}"
    except Exception as e:
        return False, str(e)
    # try:
    #     # Pretty-print the JSON for debugging
    #     formatted_quote_data = json.dumps(quote_data, indent=4)
    #     print(f"quote_data:\n{formatted_quote_data}")

    #     response = requests.post(
    #         f"{BUBBLE_API_BASE_URL}/create_quote",
    #         #f"{BUBBLE_API_BASE_URL}",
    #         headers={"Content-Type": "application/json"},  # No Authorization header
    #         json=quote_data
    #         #json=formatted_quote_data
    #     )
    #     print(f"response: {response.text}")
    #     if response.status_code == 200:
    #         return True, "Quote and items successfully created in Bubble."
    #     else:
    #         return False, f"Error from Bubble API: {response.json()}"
    # except Exception as e:
    #     return False, str(e)