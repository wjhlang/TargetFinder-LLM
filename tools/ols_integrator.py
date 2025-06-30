import requests
import json
from urllib.parse import quote

def get_efo_id_from_ols(disease_query: str) -> dict:
    """
    Fetches the EFO ID and official name for a given disease query using the OLS API.
    It takes the top match from a search query.

    Args:
        disease_query (str): The disease name to search for in OLS.

    Returns:
        dict: A dictionary containing 'ols_normalized_name' (string) and 'efo_id' (string in EFO:XXXXXXX format or None).
    Raises:
        Exception: If the API call fails.
    """
    print(f"OLS Lookup: Attempting to find EFO ID for '{disease_query}'...")

    # OLS API search endpoint for EFO ontology
    url = "https://www.ebi.ac.uk/ols4/api/search" # Using OLS4 API
    params = {
        "q": disease_query,
        "ontology": "efo",  # Focus on the Experimental Factor Ontology
        "type": "class",     # Search for ontology classes (terms)
        "rows": 1            # Get only the top result
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        docs = data.get('response', {}).get('docs', [])

        if not docs:
            print(f"OLS Lookup: No matches found for '{disease_query}'.")
            return {"ols_normalized_name": None, "efo_id": None} # Return None for both if no match

        # Take the first (top) result
        best_match_doc = docs[0]

        ols_normalized_name = best_match_doc.get('label')
        efo_id = None
        if 'iri' in best_match_doc:
            parts = best_match_doc['iri'].split('/')
            last_part = parts[-1]
            if '_' in last_part:
                efo_id = last_part.replace('_', ':')

        print(f"OLS Lookup: Top match for '{disease_query}' is '{ols_normalized_name}' (EFO ID: {efo_id})")
        return {
            "ols_normalized_name": ols_normalized_name,
            "efo_id": efo_id
        }

    except requests.exceptions.RequestException as e:
        print(f"OLS Lookup: Error during OLS API call for '{disease_query}': {e}")
        raise Exception(f"OLS lookup failed: {e}")
    except json.JSONDecodeError as e:
        print(f"OLS Lookup: Error decoding JSON response from OLS API: {e}")
        raise Exception(f"OLS lookup failed (JSON decode error): {e}")
    except Exception as e:
        print(f"OLS Lookup: An unexpected error occurred: {e}")
        raise Exception(f"OLS lookup failed: {e}")
