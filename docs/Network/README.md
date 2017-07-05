### Prepare GateWay to be able to connect remote VXLANs with each other

#### Funcionality

How this will work :
  1. create a zerotier network, but without!! allocated route or ip addresses
  1. have a running gateway with a pub interface and a leg on the vxlan (PRIV)
  1. create (maybe foresee it by default) a (linux) bridge inthe GW, and attach the PRIV interface to it
  1. migrate the ip of the PRIV interface to the bridge, and bring the bridge up
  1. start zerotier-one, join network id
  1. configure the zerotier interface to have config/bridge=true  
  [Specified here](https://github.com/zero-os/zerotier_client/blob/master/api.raml#L359)
  1. attach zt0 to the bridge

Implementation

  - Create zerotier
  ![just create it, give it a name](Create_zerotier.png)


in a Zero-GW:

```
#!/bin/bash
ZTID=a09acf0233eb77aa
PUB=eth0
PRIV=eth1
# eth0 has a public ip (routable to Internet)
# eth1 is connected to the vxlan bridge
zerotier-cli join ${ZTID}
# go back to your zerotier-page and set bridge of new client to on (without IP)
```

![Enable Bridge mode](Enable_bridge.png)


```
#!/bin/bash
ZTID=a09acf0233eb77aa
PUB=eth0
PRIV=eth1
PRIVIP=172.29.1.1/16 (reflect this as deft gw in dnsmasq dhcp config)

ip link add ztbr type bridge
ip link set ${PRIV} master ztbr
ip link set ${PRIV} up
# add zt0 to bridge
ip link set zt0 master ztbr

ip addr add ${PRIVIP} dev ztbr
ip link set ztbr up

```

Now do the same on the other side, but use another range of IP, like 172.29.2.1/16
