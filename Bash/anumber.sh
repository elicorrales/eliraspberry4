#!/bin/bash

function testForNumber() {
	result=$(echo -n $1 | grep -E "^[0-9]*$");
	if [ "$result" != "" ];
	then
		return 1;
	else
		return 0;
	fi;
}

testForNumber $1;
rtn=$?;
test  $rtn -eq 1   || echo "need a number";

