#!/bin/bash

from=$1
to=$2

echo "running from $from to $to"

#for page in {$from..$to + 1}; scrapy crawl lj -o test.csv -t csv -a page=1 > run_$page.log; done
for ((page=$from; page<=$to; page++)); do
  echo "crawing page $page"
  scrapy crawl lj -o out_$page.csv -t csv -a page=$page >run_$page.log 2>&1;
done