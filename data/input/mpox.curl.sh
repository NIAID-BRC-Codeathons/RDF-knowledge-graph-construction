# Example command to retrieve all fields for the pathogen with tax ID 10244 in TSV format from the ENA portal API.
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_run&query=tax_eq(10244)&fields=ALL&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > ./mpox.tsv

# Example command to retrieve all fields for all the viral pathogens in TSV format from the ENA portal API. Limiting the results to 10 entries.
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_run&query=tag="pathogen:virus"&fields=ALL&format=tsv&limit=10' "https://www.ebi.ac.uk/ena/portal/api/search" > ./virus.tsv
