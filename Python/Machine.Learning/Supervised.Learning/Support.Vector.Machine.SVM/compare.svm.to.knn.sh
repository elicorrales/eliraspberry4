#!/bin/bash

bestK=0;
bestAvg=0;
for run in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20;
do
    #python svm.py;
    result=$(python svm.with.linear.kernel.param.py 2>/dev/null);
    svm=$(echo $result | awk '{print $2}');
    knn=$(echo $result | awk '{print $4}');
    if [ $svm -lt $knn ];
    then
        echo "oops! svm: $svm knn:$knn <<<<<";
    else
        echo "svm[$svm] <<<<< wins knn[$knn] again!!";
    fi;
done;

