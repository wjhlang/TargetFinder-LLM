import requests
import json
import os

def normalize_disease_name_tool(disease_name: str, api_key: str) -> str:
    """
    Normalizes a given disease name using the Gemini 2.0 Flash API.
    This function is designed to correct typos, expand common acronyms,
    and use the most common/standard medical term for synonyms.

    Args:
        disease_name: The input disease name to normalize.

    Returns:
        The normalized disease name.

    Raises:
        Exception: If the API call fails or returns an invalid response.
    """
    # Construct the prompt for the LLM
    prompt = f"""Normalize the following disease name. Correct any typos, expand common acronyms, and use the most common and standard medical term if a synonym is provided. 
    Provide only the normalized disease name, with no additional text or explanation. 
    If the input is not clearly a disease name, respond with "Invalid Input".

Input: "{disease_name}"

Normalized Disease Name:"""

    # Prepare the chat history for the API request
    chat_history = []
    chat_history.append({"role": "user", "parts": [{"text": prompt}]})

    # Payload for the Gemini API request
    payload = {"contents": chat_history}
    # API URL for gemini-2.0-flash
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    try:
        # Make the API call to Gemini
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=payload
        )

        # Check if the response was successful
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

        # Parse JSON response
        result = response.json()

        # Extract normalized text from the response
        if (result and "candidates" in result and len(result["candidates"]) > 0 and
            "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"] and
            len(result["candidates"][0]["content"]["parts"]) > 0):
            normalized_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            return normalized_text
        else:
            # Handle cases where the response structure is unexpected
            raise Exception('Could not get a valid response structure from the API.')
    except requests.exceptions.RequestException as e:
        print(f"Error during disease name normalization API call: {e}")
        raise Exception(f"Normalization failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response from Gemini API: {e}")
        raise Exception(f"Normalization failed (JSON decode error): {e}")
    except Exception as e:
        print(f"An unexpected error occurred during normalization: {e}")
        raise Exception(f"Normalization failed: {e}")