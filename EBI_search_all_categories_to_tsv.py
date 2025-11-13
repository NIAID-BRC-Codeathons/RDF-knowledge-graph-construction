import requests
import csv


# Base URL for all endpoints
BASE_URL = "https://www.ebi.ac.uk/ebisearch/ws/rest"

# remove categories of less interest
CATEGORIES = [
    "genome_assembly",
    "embl",
    "emblstandard",
    "emblcon",
    "wgs_masters",
    "tsa_masters",
    "tls_masters",
    "coding",
    "coding_con",
    "coding_std",
    "coding_wgs",
    "coding_tsa",
    "coding_tls",
    "non-coding",
    "non-coding_con",
    "non-coding_std",
    "non-coding_wgs",
    "non-coding_tsa",
    "non-coding_tls",
    "sra-experiment",
    "sra-run",
    "sra-analysis",
    "sra-study",
    "project",
    "taxonomy",
    "sra-sample",
    "sra-submission"
]

# Add more queries as needed
QUERIES = ["MPox", "covid", "Antimicrobial Resistance", "Influenza and Respiratory Viruses", "Human clinical metadata",
           "Salmonella", "E. coli"]

# Fields to request, add more fields if needed
FIELDS = "acc,description,name"
SIZE = 100


def fetch_data(category, query):
    """Fetch data from EBI Search API for a given category and query."""
    url = f"{BASE_URL}/{category}?query={query}&fields={FIELDS}&size={SIZE}&format=json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract entries from the response
        entries = data.get('entries', [])

        results = []
        for entry in entries:
            fields = entry.get('fields', {})

            # Helper function to safely extract field value
            def get_field_value(field_data):
                if isinstance(field_data, list):
                    return field_data[0] if len(field_data) > 0 else ''
                return field_data if field_data else ''

            results.append({
                'category': category,
                'acc': get_field_value(fields.get('acc', '')),
                'description': get_field_value(fields.get('description', '')),
                'name': get_field_value(fields.get('name', ''))
            })

        return results

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {category} with query '{query}': {e}")
        return []


def main():
    # Process each query separately
    for query in QUERIES:
        output_file = f"{query}.tsv"

        print(f"\nProcessing query: {query}")

        with open(output_file, 'w', newline='', encoding='utf-8') as tsvfile:
            writer = csv.writer(tsvfile, delimiter='\t')

            # Write header
            writer.writerow(['category', 'acc', 'description', 'name'])

            # Fetch data from all endpoints for this query
            for category in CATEGORIES:
                print(f"  Fetching {category} data...")
                results = fetch_data(category, query)

                # Write results to TSV
                for result in results:
                    writer.writerow([
                        result['category'],
                        result['acc'],
                        result['description'],
                        result['name']
                    ])

                print(f"    Found {len(results)} results for {category}")

        print(f"  Data written to {output_file}")

    print("\nAll files created successfully!")


if __name__ == "__main__":
    main()