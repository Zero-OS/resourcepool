BRANCH=$1
jsversion=$(js9 "print(j.core.state.versions.get('JumpScale9')[1:])")
ZEROTIERIP=$(ip addr show zt0 | grep -o 'inet [0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+' | grep -o [0-9].*)

#Generate JWT
eval "$(ays generatetoken --clientid $ITSYOUONLINE_CL_ID --clientsecret $ITSYOUONLINE_CL_SECRET --organization $ITSYOUONLINE_ORG)"

echo "jsversion="
echo $jsversion

cat >>  /optvar/cockpit_repos/orchestrator-server/blueprints/configuration.bp << EOL
configuration__main:
  configurations:
  - key: '0-core-version'
    value: '${BRANCH}'
  - key: 'js-version'
    value: '${jsversion}'
  - key: 'gw-flist'
    value: 'https://hub.gig.tech/gig-official-apps/zero-os-gw-1.1.0-alpha-3.flist'
  - key: 'ovs-flist'
    value: 'https://hub.gig.tech/gig-official-apps/ovs-1.1.0-alpha-3.flist'
  - key: '0-disk-flist'
    value: 'https://hub.gig.tech/gig-official-apps/0-disk-1.1.0-alpha-3.flist'
  - key: 'jwt-token'
    value: '${JWT}'
  - key: 'jwt-key'
    value: 'MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n27MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny66+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv'
EOL

cd /optvar/cockpit_repos/orchestrator-server
ays reload 
ays blueprint configuration.bp
ays run create --follow

# kill orchestrator server and start it again using new org
#tmux kill-window -t orchestrator
#tmux new-window -n orchestrator
#tmux send -t orchestrator 'orchestratorapiserver --bind '"${ZEROTIERIP}"':8080 --ays-url http://127.0.0.1:5000 --ays-repo orchestrator-server -org orchestrator_org' ENTER

