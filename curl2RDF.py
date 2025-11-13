import requests
import pandas as pd
from io import StringIO
import os
import sys
import json
from pyld import jsonld
from rdflib import Graph

from defs import Tool_Pathogen_Name_from_Taxon_ID
from defs import Tool_Pathogen_Class

pd.set_option('display.max_columns', None)        # Show all columns
pd.set_option('display.max_rows', None)           # Show all rows (use with caution if large)
pd.set_option('display.max_colwidth', None)       # Show full content of each cell
pd.set_option('display.width', None)              # Let pandas decide optimal width
pd.set_option('display.expand_frame_repr', False) # Prevent line wrapping

# Helper function to check if a value is valid (not null-like, NONE, empty, etc.)
def is_valid_value(value):
    if pd.isna(value):
        return False
    str_value = str(value).strip()
    invalid_strings = ['', 'null', 'NONE', 'NaN', 'none']  # Add more if needed
    return str_value not in invalid_strings

def serviceCallByTaxonID(taxonID):
    # Make the API request
    url = "https://www.ebi.ac.uk/ena/portal/api/search"

    # https://www.ebi.ac.uk/ena/portal/api/search?result=read_run&query=tax_eq(10244)&fields=ALL
    # Data to be sent in the POST request body
    data = {
        'result': 'read_run',
        'query':  f'tax_eq({taxonID})',  # 'tag=\"pathogen:virus\"',  #'tax_eq(10244)',
        'fields': 'run_accession,experiment_title,tax_id,country,description',  #sequencing_longitude,sequencing_location',
        'format': 'tsv',
        'limit': 100
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

    pathogen_name = Tool_Pathogen_Name_from_Taxon_ID.get_pathogen_name_by_taxon_id(taxonID)
    agent_name = Tool_Pathogen_Class.get_pathogen_class(pathogen_name)

    for index, row in df.iterrows():
        # Create a copy of the template
        json_ld_doc = json.loads(json.dumps(json_ld_template))

        # Fill in the values from the row
        # json_ld_doc["identifier"] = str(row['tax_id'])
        # json_ld_doc["subjectOf"][0]["identifier"] = str(row['run_accession'])
        # json_ld_doc["subjectOf"][0]["name"] = str(row['experiment_title'])
        # json_ld_doc["subjectOf"][0]["description"] = str(row['description']) if pd.notna(row['description']) else ""
        # json_ld_doc["subjectOf"][0]["spatialCoverage"]["name"] = str(row['country'])

        # matches for the Pathogen_schema
        # json_ld_doc["additionalProperty"][1]["value"] =  "https://purl.uniprot.org/taxonomy/" + str(row['tax_id'])
        # json_ld_doc["additionalProperty"][2]["value"] = str(row['run_accession'])
        # json_ld_doc["additionalProperty"][3]["value"] = str(row['experiment_title'])
        # json_ld_doc["additionalProperty"][4]["value"] = str(row['description']) if pd.notna(row['description']) else ""
        # json_ld_doc["additionalProperty"][0]["value"]= str(row['country'])

        # json_ld_doc["@graph"][0]["name"] = pathogen_name
        # json_ld_doc["@graph"][0]["infectiousAgentClass"]["name"] = agent_name

        if is_valid_value(pathogen_name):
            json_ld_doc["@graph"][0]["name"] = pathogen_name
        else:
            json_ld_doc["@graph"][0].pop("name", None)

        if is_valid_value(agent_name):
            json_ld_doc["@graph"][0]["infectiousAgentClass"]["name"] = agent_name
        else:
            json_ld_doc["@graph"][0]["infectiousAgentClass"].pop("name", None)

        # --------------------------------------------


        # matches for the Pathogen_schemav2
        # json_ld_doc["@graph"][1]["@id"] = "https://purl.uniprot.org/taxonomy/" + str(row['tax_id'])
        # json_ld_doc["@graph"][1]["name"] = "https://purl.uniprot.org/taxonomy/" + str(row['tax_id'])
        # json_ld_doc["@graph"][1]["identifier"] = "NCBI:txid" + str(row['tax_id'])
        # json_ld_doc["@graph"][0]["additionalProperty"][0]["value"] = str(row['run_accession'])
        # json_ld_doc["@graph"][0]["additionalProperty"][1]["value"] = str(row['experiment_title'])
        # json_ld_doc["@graph"][0]["additionalProperty"][2]["value"] = str(row['description']) if pd.notna(row['description']) else ""
        # json_ld_doc["@graph"][0]["spatialCoverage"]["name"] = str(row['country'])
        # json_ld_doc["@graph"][0]["spatialCoverage"]["@id"] = str(row['country'])

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

def main() -> int:

    taxon_list = [127906, 3052460, 3052462, 186537, 3052464, 138950, 3052310, 694009, 3046277, 3052518, 10244, 37124, 632, 5500,
     5820, 4827, 1773, 620, 3048459, 2955291, 10255, 11676, 2509494, 498019, 746128, 5476, 5480, 5482, 5478, 5658, 5806,
     5741, 5811, 3052480, 485, 3052225, 562, 59201, 1313, 3052676, 3052345, 139, 3048448, 2955465, 2955744, 2955935,
     12092, 1392, 11292, 3048158, 470, 520, 197, 813, 573, 727, 1496, 3049954, 1314, 11036, 66527, 88456, 5759, 5722,
     5690, 5763, 234, 1352, 287, 1280, 11974, 777, 3052465, 263, 3052499, 171, 1126011, 10566, 1311, 160, 630, 5036,
     38946, 37769, 5207, 41688, 41687, 5506, 4909, 42068, 37727, 6029, 100816, 1489895, 1489897, 159075, 563466, 5502,
     487, 362532, 126728, 107386, 31276, 32597, 109871, 1357716, 112090, 157072, 2748958, 6210, 6211, 670, 943, 3052302,
     3052307, 2169991, 3052314, 3052303, 3052317, 3052303, 3052300, 3052328, 1674146, 47466, 13373, 28450, 83554, 1491,
     1513, 1717, 544, 547, 3048170, 3048170, 3048233, 3048287, 3052468, 3048443, 1980456, 3052485, 446, 2846071, 581,
     583, 10294, 3050294, 3052223, 2971765, 3052385, 3052390, 3052409, 3052429, 3051992, 3052684, 2748958, 3052686,
     138948, 138949, 138951, 147711, 147712, 463676, 780, 6181, 10912, 11021, 59301, 2169701, 11034, 11039, 6333, 613,
     3052346, 3050271, 2034996, 84677, 3048357, 1274402, 2560405, 100217, 10492, 65424, 3050290, 37629, 342409, 222557,
     3050355, 55987, 3052615, 12110, 1980917, 696863, 1980916, 3048455, 40051, 40054, 3349490, 282786]

    # taxon_list = [127906, 3052460, 3052462, 186537, 3052464, 138950]

    for index, taxon in enumerate(taxon_list, 1):
        print(f"\nProcessing taxon {index}/{len(taxon_list)}: {taxon}")
        serviceCallByTaxonID(taxon)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
