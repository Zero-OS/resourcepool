#!/bin/bash

point=$1
if [ "$TRAVIS_EVENT_TYPE" == "cron" ] || [ "$TRAVIS_EVENT_TYPE" == "api" ]
 then
   if [ "$point" == "before" ]
    then
      pip3 install -r tests/0_orchestrator/test_suite/requirements.txt
      pip3 install git+https://github.com/gigforks/packet-python.git
      bash tests/0_orchestrator/install_env.sh $TRAVIS_BRANCH $ZT_NET_ID $ZT_TOKEN
      cd tests/0_orchestrator/; python3 orch_packet_machines.py create $PACKET_TOKEN $ZT_NET_ID $ITSYOUONLINE_ORG $TRAVIS_BRANCH
   elif [ "$point" == "run" ]
    then
      echo "sleeping 333"
      sleep 333
      echo "Running tests .."
      cd tests/0_orchestrator/test_suite
      export PYTHONPATH='./'
      nosetests-3.4 -v -s testcases/basic_tests --tc-file=config.ini --tc=main.zerotier_token:$ZT_TOKEN --tc=main.client_id:$ITSYOUONLINE_CL_ID --tc=main.client_secret:$ITSYOUONLINE_CL_SECRET --tc=main.organization:$ITSYOUONLINE_ORG
   elif [ "$point" == "after" ]
    then
      cd tests/0_orchestrator/
      python3 orch_packet_machines.py delete $PACKET_TOKEN
   fi
 else
   echo "Not a cron job" 
fi

