#!/bin/bash

baseurl="http://localhost:8084";
arduino="${baseurl}/arduino";
api="${arduino}/api";

echo;echo "STOP RC auto send status indication";
echo "on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/status/stop";

for cycles in 1 2 3 4 5 6 7 8 9 10;
do
    numReq=0;
    numSent=0;
    for speed in 10 20 30 40 50 60 70 80 90 100 90 80 70 60 50 40 30 20 10;
    do
        #echo;echo "Move forward at $speed..";
        numReq=$((numReq+1));
        resp=$(curl --silent "${api}/forward/${speed}");
        #echo $resp;
        if [ "$(echo $resp | grep "Cmd Sent")" != "" ];
        then
            numSent=$((numSent+1));
        fi;
        #echo "req:$numReq  sent:$numSent";
        #sleep 0.1;
    done;
    echo $((numReq-numSent))


    numReq=0;
    numSent=0;
    for speed in 10 20 30 40 50 60 70 80 90 100 90 80 70 60 50 40 30 20 10;
    do
        #echo;echo "Move backward at $speed..";
        numReq=$((numReq+1));
        resp=$(curl --silent "${api}/backward/${speed}");
        #echo $resp;
        if [ "$(echo $resp | grep "Cmd Sent")" != "" ];
        then
            numSent=$((numSent+1));
        fi;
        #echo "req:$numReq  sent:$numSent";
        #sleep 0.1;
    done;
    echo $((numReq-numSent))
done;


echo;echo "Stop motors";
curl "${api}/stop";

echo;
echo;
