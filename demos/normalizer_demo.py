import os
import sys

api_key = os.environ["GEMINI_API_KEY"]

# Import the normalization tool
from ..agents.disease_normalizer import normalize_disease_name_tool

# Import the OLS integration tool
from ..tools.ols_integrator import get_efo_id_from_ols

def process_disease_name(raw_disease_name: str) -> dict:
    """
    Main function to demonstrate the end-to-end process:
    1. Normalizes a disease name using Gemini.
    2. Looks up the corresponding EFO ID and official OLS name using the OLS API.

    Args:
        raw_disease_name: The initial, potentially unnormalized disease name.

    Returns:
        A dictionary containing the LLM-normalized name, OLS-official name, EFO ID, and any error.
    """
    print(f"\n--- Processing: \"{raw_disease_name}\" ---")
    llm_normalized_name = None
    ols_result = {"ols_normalized_name": None, "efo_id": None} # Initialize with None
    error_message = None

    # Define the API key here, or load from environment variable
    # For Canvas environment, leave as "":
    gemini_api_key = ""
    # For local execution, replace with your actual key:
    # gemini_api_key = "YOUR_ACTUAL_GOOGLE_CLOUD_API_KEY_HERE"
    # Or from environment variable:
    # gemini_api_key = os.environ.get("GEMINI_API_KEY")

    try:
        # Step 1: Normalize the disease name using LLM
        print("Step 1: Normalizing disease name using LLM...")
        llm_normalized_name = normalize_disease_name_tool(raw_disease_name, api_key)
        print(f"LLM Normalized Name: \"{llm_normalized_name}\"")

        # Handle "Invalid Input" from the LLM normalization step
        if llm_normalized_name == "Invalid Input":
            print("LLM normalization returned 'Invalid Input', skipping OLS lookup.")
            return {"llm_normalized_name": llm_normalized_name, "ols_official_name": None, "efo_id": None}

        # Step 2: Look up EFO ID and official name in OLS using the LLM-normalized name
        print("Step 2: Looking up EFO ID and official name in OLS...")
        ols_result = get_efo_id_from_ols(llm_normalized_name)

        # Corrected print statement to only show the EFO ID string
        if ols_result["efo_id"]:
            print(f"Found OLS Official Name: \"{ols_result['ols_normalized_name']}\" (EFO ID: {ols_result['efo_id']})")
        else:
            print(f"No EFO ID found for \"{llm_normalized_name}\" in OLS.")

        return {
            "llm_normalized_name": llm_normalized_name,
            "ols_official_name": ols_result["ols_normalized_name"],
            "efo_id": ols_result["efo_id"] # This correctly returns the EFO ID string
        }

    except Exception as e:
        error_message = str(e)
        print(f"Error processing \"{raw_disease_name}\": {error_message}")
        return {
            "llm_normalized_name": llm_normalized_name,
            "ols_official_name": ols_result["ols_normalized_name"],
            "efo_id": ols_result["efo_id"],
            "error": error_message
        }

# --- Example Orchestration (How you would run this) ---
# If running in a Python environment, you would use `import`
# from disease_normalizer import normalize_disease_name_tool
# from ols_integrator import get_efo_id_from_ols

def run_examples():
    """Runs a series of examples to test the disease processing pipeline."""
    disease_inputs = [
        'MS',               # Should normalize to Multiple Sclerosis, then find EFO
        'diabetees',        # Should normalize to Diabetes, then find EFO
        'sugar sickness',   # Should normalize to Diabetes, then find EFO
        'Huntingtons Disease', # Correct spelling, find EFO
        'common cold',      # Find EFO for Common Cold
        'typo for cancer',  # Should normalize to Cancer, then find EFO
        'AD',               # Should normalize to Alzheimer\'s Disease, then find EFO
        'NASH',             # Should normalize to Non-alcoholic steatohepatitis, then find EFO
        'Influenza virus infection', # Specific term for OLS lookup
        'xyz123',           # Should be "Invalid Input" from LLM normalization
        'Parkinsons' # Test a common disease
    ]


    for input_name in disease_inputs:
        result = process_disease_name(input_name)
        print("\n--- Result Summary ---")
        print(f"Original: \"{input_name}\"")
        print(f"LLM Normalized: \"{result.get('llm_normalized_name')}\"")
        print(f"OLS Official Name: \"{result.get('ols_official_name')}\"")
        # Corrected print statement here to ensure only the EFO ID string is printed
        print(f"EFO ID: \"{result.get('efo_id')}\"")
        if result.get('error'):
            print(f"Error: {result['error']}")
        print("----------------------\n")

# To run these examples, uncomment the line below.
# This will simulate the full pipeline in a single environment.
run_examples()

