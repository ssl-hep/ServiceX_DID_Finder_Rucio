#!/usr/bin/env bash

/usr/src/app/proxy-exporter.sh &

while true; do 
    date
    ls ${X509_USER_PROXY}
    RESULT=$?
    if [ $RESULT -eq 0 ]; then
        break
    fi
    echo "INFO $INSTANCE_NAME did-finder none Waiting for the proxy."
    sleep 5
done

export PYTHONPATH=./src
if [[ -z "$CACHE_PREFIX" ]];
then
  python3 scripts/did_finder.py --rabbit-uri $RMQ_URI
else
  python3 scripts/did_finder.py --rabbit-uri $RMQ_URI --prefix "$CACHE_PREFIX"
fi

