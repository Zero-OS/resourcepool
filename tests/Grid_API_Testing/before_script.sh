#!/bin/bash

if [ "$TRAVIS_EVENT_TYPE" == "cron" ]
then
   pip3 install -r tests/Grid_API_Testing/requirements.txt
   pip3 install git+https://github.com/gigforks/packet-python.git
   bash tests/Grid_API_Testing/install_env.py master $ZT_NET_ID $ZT_TOKEN
   cd tests/Grid_API_Testing; python3 orch_packet_machines.py create $PACKET_TOKEN $ZT_NET_ID
   export PYTHONPATH='./'
else
   echo "Not a cron job" 
fi
