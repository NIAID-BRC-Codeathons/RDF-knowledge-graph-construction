import requests

def get_pathogen_name_by_taxon_id(taxon_id: int):
    """
    Fetches pathogen name from UniProt using taxon ID.

    Args:
        taxon_id (int): UniProt taxonomy ID.

    Returns:
        str: Scientific name of the pathogen.
    """
    url = f"https://rest.uniprot.org/taxonomy/{taxon_id}"
    response = requests.get(url).json()
    return response.get("scientificName", "")
