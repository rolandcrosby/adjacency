#!/usr/bin/env bash
set -euxo pipefail
URL="https://www2.census.gov/geo/docs/reference/county_adjacency.txt"
curl -sL "$URL" | iconv -f windows-1252 -t utf-8 > original.tsv
awk 'BEGIN {FS="\t"; OFS=FS}
$1 {from_name=$1; from_id=$2; print $1, $2, $3, $4}
!$1 {print from_name, from_id, $3, $4}' original.tsv > adjacencies.tsv
awk 'BEGIN {FS="\t"; OFS=FS} {print $1, $2; print $3, $4}' adjacencies.tsv | sort | uniq > counties.tsv
awk 'BEGIN {FS="\t"; OFS=FS} $2 < $4 {print $2, $4} $4 < $2 {print $4, $2}' adjacencies.tsv | sort | uniq > deduped_graph.tsv
mkdir -p graphs
python3 make_graphs.py
for i in graphs/*.dot; do
    neato -Tpng $i -o graphs/$(basename -s .dot $i).png
done
