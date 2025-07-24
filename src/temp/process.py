import re
import json

# File paths
BASE_DIR= os.path.abspath(os.path.join(os.path.dirname(__file__),"../"))
file_path= os.path.join(BASE_DIR,"temp","extracted_info.txt")
output_path= os.path.join(BASE_DIR,"temp","extracted_medicine_data.json")

# Regex pattern for extracting medicine details
pattern = re.compile(
    r"(?P<medicine>[A-Za-z0-9\.\-\s]+?)\s+"  # Medicine name (with spaces, dots, or dashes)
    r"(?P<dosage>\d+-\d+-\d+)\s+"  # Dosage format (e.g., 1-0-0)
    r"(?P<duration>\d+\s?days?)\s+"  # Duration (e.g., 10 days)
    r"(?P<measure>\d+)\s+"  # Measure (e.g., 1 or 2)
    r"(?P<instruction>Before Meal|After Meal|Any Meal|With Meal)\b",  # Meal instructions
    re.IGNORECASE | re.MULTILINE
)

try:
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Extract medicine info
    matches = pattern.finditer(text)
    extracted_info = []
    for match in matches:
        medicine_info = {
            "Medicine": match.group("medicine").strip(),
            "Dosage": match.group("dosage"),
            "Duration": match.group("duration"),
            "Measure": match.group("measure"),
            "Instruction": match.group("instruction")
        }
        extracted_info.append(medicine_info)
    
    result = {"Medicines": extracted_info}
    
    # Save the output to a JSON file
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, indent=4)
    
    print(f"Extracted data saved to {output_path}")
    
except FileNotFoundError:
    print(f"Error: The file at {file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")