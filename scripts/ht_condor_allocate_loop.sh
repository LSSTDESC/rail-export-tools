#!/bin/bash

MAXNODES=20

# Loop for a long time, executing "allocateNodes auto" every 10 minutes.
for i in {1..500}
do
    allocateNodes.py --auto --account rubin:developers -n ${MAXNODES} -m 4-00:00:00 -q milano -g 240 s3df
    sleep 600
done
