#!/usr/bin/env bash

#example run :
# chmox a+x download_from_ebisearch.sh
# ./download_from_ebisearch.sh Mpox
# output : Mpox_ebisearch.tsv

# Exit on error
set -e

# Check if parameter provided
if [ -z "$1" ]; then
  echo "Usage: $0 <search_term>"
  exit 1
fi

# Input parameter
QUERY="$1"

# Output file name
OUTFILE="${QUERY}_ebisearch.tsv"

# Clear previous file (if exists)
> "$OUTFILE"

echo "Downloading EBI Search results for: $QUERY"
echo "Output file: $OUTFILE"
echo ""

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/wgs_masters?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/genome_assembly?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/embl?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/emblcon?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/emblstandard?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/coding_std?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/coding_wgs?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/coding_tls?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/non-coding?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/non-coding_con?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/non-coding_std?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/non-coding_wgs?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/non-coding_tsa?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/non-coding_tls?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/sra-experiment?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/sra-run?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/sra-analysis?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/sra-study?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/project?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/taxonomy?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/sra-sample?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

curl -s "https://www.ebi.ac.uk/ebisearch/ws/rest/sra-submission?query=${QUERY}&size=100&format=tsv" >> "$OUTFILE"

echo ""
echo "All results saved to ${OUTFILE}"
