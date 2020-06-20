#!/bin/bash

from=$1
to=$2

echo "running from $from to $to"

cat out_$from.csv > final_out.csv
rm out_$from.csv
for ((page=($from+1); page<=$to; page++)); do
  echo $page
  tail -n +2 out_$page.csv >> final_out.csv
  rm out_$page.csv
done
