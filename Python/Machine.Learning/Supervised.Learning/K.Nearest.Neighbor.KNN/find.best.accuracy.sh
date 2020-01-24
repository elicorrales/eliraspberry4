#!/bin/bash

bestK=0;
bestAvg=0;
for K in 1 3 5 7 9 11 13 15;
do
    average=$(python knn.find.best.accuracy.py $K | awk '{print $4}');
    if [ $bestAvg -lt $average ];
    then
        bestAvg=$average;
        bestK=$K;
        echo "avg: $bestAvg k:$bestK";
    fi;
done;

