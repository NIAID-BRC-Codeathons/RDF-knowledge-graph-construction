import requests
import pandas as pd
from io import StringIO
import os
import json
from pyld import jsonld
from rdflib import Graph
import re

from defs import Tool_Pathogen_Name_from_Taxon_ID
from defs import Tool_Pathogen_Class

# Helper function to lower cases and remove special characters from a string
def clean_string(s):
    if not isinstance(s, str):
        return ""
    # Make lowercase
    s = s.lower()
    # Remove spaces and special characters (keep only alphanumeric)
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

# Helper function to check if a value is valid (not null-like, NONE, empty, etc.)
def is_valid_value(value):
    if pd.isna(value):
        return False
    str_value = str(value).strip()
    invalid_strings = ['', 'null', 'NONE', 'NaN', 'none']  # Add more if needed
    return str_value not in invalid_strings

def serviceCallByTaxonID(taxonid, call_limit):
    # Make the API request
    url = "https://www.ebi.ac.uk/ena/portal/api/search"

    # Data to be sent in the POST request body
    data = {
        'result': 'read_run',
        'query':  f'tax_eq({taxonid})',  # 'tag=\"pathogen:virus\"',  #'tax_eq(10244)',
        'fields': 'run_accession,experiment_title,tax_id,country,description',  #sequencing_longitude,sequencing_location',
        'format': 'tsv',
        'limit': call_limit
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

    # Create an output directory if it doesn't exist
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)

    # Read JSON-LD template from file
    template_file = "./data/Pathogen_schemav2.json"  # You can change this path as needed
    with open(template_file, 'r', encoding='utf-8') as f:
        json_ld_template = json.load(f)

    # Iterate through each row in the DataFrame

    pathogen_name = Tool_Pathogen_Name_from_Taxon_ID.get_pathogen_name_by_taxon_id(taxonid)
    agent_name = Tool_Pathogen_Class.get_pathogen_class(pathogen_name)
    pathogen_name_clean = clean_string(pathogen_name)

    for index, row in df.iterrows():
        # Create a copy of the template
        json_ld_doc = json.loads(json.dumps(json_ld_template))

        # set the relation URI between the graphs
        json_ld_doc["@graph"][0]["@id"] = "https://example.com/diseases/" + str(pathogen_name_clean)
        json_ld_doc["@graph"][1]["associatedDisease"]["@id"] = "https://example.com/diseases/" + str(pathogen_name_clean)

        if is_valid_value(pathogen_name):
            json_ld_doc["@graph"][0]["name"] = pathogen_name
        else:
            json_ld_doc["@graph"][0].pop("name", None)

        if is_valid_value(agent_name):
            json_ld_doc["@graph"][0]["infectiousAgentClass"]["name"] = agent_name
        else:
            json_ld_doc["@graph"][0]["infectiousAgentClass"].pop("name", None)


        # matches for the Pathogen_schemav2
        tax_id = row['tax_id']
        if is_valid_value(tax_id):
            json_ld_doc["@graph"][1]["@id"] = "https://purl.uniprot.org/taxonomy/" + str(tax_id)
        else:
            json_ld_doc["@graph"][1].pop("@id", None)

        if is_valid_value(tax_id):
            json_ld_doc["@graph"][1]["name"] = "https://purl.uniprot.org/taxonomy/" + str(tax_id)
        else:
            json_ld_doc["@graph"][1].pop("name", None)

        if is_valid_value(tax_id):
            json_ld_doc["@graph"][1]["identifier"] = "NCBI:txid" + str(tax_id)
        else:
            json_ld_doc["@graph"][1].pop("identifier", None)

        run_accession = row['run_accession']
        if is_valid_value(run_accession):
            json_ld_doc["@graph"][0]["additionalProperty"][0]["value"] = str(run_accession)
        else:
            json_ld_doc["@graph"][0]["additionalProperty"][0].pop("value", None)

        experiment_title = row['experiment_title']
        if is_valid_value(experiment_title):
            json_ld_doc["@graph"][0]["additionalProperty"][1]["value"] = str(experiment_title)
        else:
            json_ld_doc["@graph"][0]["additionalProperty"][1].pop("value", None)

        description = row['description']
        if pd.notna(description) and str(description).strip():
            json_ld_doc["@graph"][0]["additionalProperty"][2]["value"] = str(description)
        else:
            json_ld_doc["@graph"][0]["additionalProperty"][2].pop("value", None)

        country = row['country']
        if is_valid_value(country):
            json_ld_doc["@graph"][0]["spatialCoverage"]["name"] = str(country)
        else:
            json_ld_doc["@graph"][0]["spatialCoverage"].pop("name", None)

        if is_valid_value(country):
            json_ld_doc["@graph"][0]["spatialCoverage"]["@id"] = str(country)
        else:
            json_ld_doc["@graph"][0]["spatialCoverage"].pop("@id", None)


        # --------------------------------------------
        # Convert JSON-LD to N-Quads
        nquads = jsonld.to_rdf(json_ld_doc, {'format': 'application/n-quads'})

        # Parse with rdflib and skolemize blank nodes
        g = Graph()
        g.parse(data=nquads, format='nquads')
        g = g.skolemize()  # Replace blank nodes with skolem IRIs

        # Serialize to N-Triples
        ntriples = g.serialize(format='nt')

        # Create filename using the run_accession
        filename = f"{row['run_accession']}.nt"
        filepath = os.path.join(output_dir, filename)

        # Write the N-Triples file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(ntriples)

        print(f"Created: {filepath}")

    print(f"\nGenerated {len(df)} N-Triples files in {output_dir}/")
