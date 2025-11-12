import requests
import pandas as pd
from io import StringIO
import os
import json
from pyld import jsonld

pd.set_option('display.max_columns', None)        # Show all columns
pd.set_option('display.max_rows', None)           # Show all rows (use with caution if large)
pd.set_option('display.max_colwidth', None)       # Show full content of each cell
pd.set_option('display.width', None)              # Let pandas decide optimal width
pd.set_option('display.expand_frame_repr', False) # Prevent line wrapping

# Make the API request
url = "https://www.ebi.ac.uk/ena/portal/api/search"

# Data to be sent in the POST request body
data = {
    'result': 'read_run',
    'query': 'tax_eq(10244) AND country="united kingdom"',
    'fields': 'run_accession,experiment_title,tax_id,country,description',  #sequencing_longitude,sequencing_location',
    'format': 'tsv'
}

# Headers
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Make the POST request
response = requests.post(url, data=data, headers=headers)
response.raise_for_status()  # Raise an exception for bad status codes


# Since the format is TSV, parse it into a DataFrame
df = pd.read_csv(StringIO(response.text), sep='\t')

# Display the DataFrame
print(df.head())

print(f"\nDataFrame shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")

# Create output directory if it doesn't exist
output_dir = "data/output"
os.makedirs(output_dir, exist_ok=True)

# JSON-LD template
json_ld_template = {
    "@context": {
        "@vocab": "https://schema.org/",
        "dct": "http://purl.org/dc/terms/"
    },
    "@type": "Virus",
    "identifier": None,
    "subjectOf": [
        {
            "@type": "Dataset",
            "identifier": None,
            "name": None,
            "description": None,
            "spatialCoverage": {
                "@type": "Place",
                "name": None
            }
        }
    ]
}


# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    # Create a copy of the template
    json_ld_doc = json.loads(json.dumps(json_ld_template))

    # Fill in the values from the row
    json_ld_doc["identifier"] = str(row['tax_id'])
    json_ld_doc["subjectOf"][0]["identifier"] = str(row['run_accession'])
    json_ld_doc["subjectOf"][0]["name"] = str(row['experiment_title'])
    json_ld_doc["subjectOf"][0]["description"] = str(row['description']) if pd.notna(row['description']) else ""
    json_ld_doc["subjectOf"][0]["spatialCoverage"]["name"] = str(row['country'])

    # Convert JSON-LD to N-Triples
    ntriples = jsonld.to_rdf(json_ld_doc, {'format': 'application/n-quads'})

    # Create filename using the run_accession
    filename = f"{row['run_accession']}.nt"
    filepath = os.path.join(output_dir, filename)

    # Write the N-Triples file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(ntriples)

    print(f"Created: {filepath}")

print(f"\nGenerated {len(df)} N-Triples files in {output_dir}/")