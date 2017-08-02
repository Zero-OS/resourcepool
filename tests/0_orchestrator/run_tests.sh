#!/bin/bash

point=$1
if [ "$TRAVIS_EVENT_TYPE" == "cron" ] || [ "$TRAVIS_EVENT_TYPE" == "api" ]
 then
   if [ "$point" == "before" ]
    then
      pip3 install -r tests/0_orchestrator/test_suite/requirements.txt
      pip3 install git+https://github.com/gigforks/packet-python.git
      python3 tests/0_orchestrator/orch_packet_machines.py create $PACKET_TOKEN $ZT_TOKEN $ITSYOUONLINE_ORG $TRAVIS_BRANCH
      ZT_NET_ID=$(cat ZT_NET_ID)
      bash tests/0_orchestrator/install_env.sh master $ZT_NET_ID $ZT_TOKEN
   elif [ "$point" == "run" ]
    then
      echo "sleeping 120"
      sleep 120
      echo "Running tests .."
      cd tests/0_orchestrator/test_suite
      export PYTHONPATH='./'
      nosetests-3.4 -v -s testcases/basic_tests/test01_nodeid_apis.py --tc-file=config.ini --tc=main.zerotier_token:$ZT_TOKEN --tc=main.client_id:$ITSYOUONLINE_CL_ID --tc=main.client_secret:$ITSYOUONLINE_CL_SECRET --tc=main.organization:$ITSYOUONLINE_ORG
   elif [ "$point" == "after" ]
    then
      python3 tests/0_orchestrator/orch_packet_machines.py delete $PACKET_TOKEN
   fi
 else
   echo "Not a cron job" 
fi

