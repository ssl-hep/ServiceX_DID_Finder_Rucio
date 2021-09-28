#!/usr/bin/env bash

/usr/src/app/proxy-exporter.sh &


while true; do 
    date
    ls /etc/grid-security/x509up
    RESULT=$?
    if [ $RESULT -eq 0 ]; then
        echo "Got proxy."
        break
    fi
    sleep 5
done

export PYTHONPATH=./src
if [[ -z "$CACHE_PREFIX" ]];
then
  python3 scripts/did_finder.py --rabbit-uri $RMQ_URI
else
  python3 scripts/did_finder.py --rabbit-uri $RMQ_URI --prefix $CACHE_PREFIX
fi

