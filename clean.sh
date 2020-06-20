#!/bin/bash

to=$1

echo "cleaning to dir $to"

mkdir -p ./$to
mv ./*.csv ./$to
mv ./crawl/final_out.csv ./$to
