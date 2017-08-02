# How to connect your office network to a Zero-OS gateway.

The bridge can be configured by setting the `zerotierbridge` property of the V(X)LAN interface of the Gateway. For more information how to create the bridge, see [../../raml/api.html#nodes_nodeid_gws_post](https://htmlpreviewer.github.io/?../../raml/api.html#nodes__nodeid__gws_post)

Using this technique it is possible to connect to the same zerotier network on your office router.

## Example:

Using the following payload we will configure our Zero-OS Gateway with a private network range `192.168.122.0/24` where `192.168.122.1` is the IP Address inside the Zero-OS Gateway.
```json
{
  "name":"mygw",
  "domain":"mydomain",
  "nics":[
    {
      "name":"public",
      "type":"vlan",
      "id":"0",
      "config":{
        "cidr":"193.168.58.22/24",
        "gateway": "193.168.58.254"
 
      }
    },
    {
      "name":"private",
      "type":"vxlan",
	  "zerotierbridge": {"id": "17d709736cd05251", "token": "KEkrfwKhpeEvzfTKKsgCAAgEnvh2bQuB"},
      "id":"100",
      "config":{
        "cidr":"192.168.112.1/24"
      },
      "dhcpserver":{}
    }
  ],
  "httpproxies":[],
  "portforwards":[]
}
```

When assuming the above configuration and assuming your office network has a linux based router.

On your office router issue the following commands
```bash
zerotier-cli join 17d709736cd05251 # make sure to go authorize this node
ip a a 192.168.112.2/24
```

Make sure that traffic having destination `192.168.112.0/24` is natted from your router

IPtables:
```bash
iptables -t nat -A POSTROUTING -d 192.168.112.0/24 -j MASQUERADE
```

NFtables:

Provided you have the nat hooks activated 

```bash
nft add rule ip nat postrouting ip daddr 192.168.112.0/24 masquerade
```