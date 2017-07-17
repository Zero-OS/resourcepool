#!/bin/bash
bridges(){
	echo "# [+] Setup bridges"
	for i in {1..4} ; do 
		echo ovs-vsctl add-br p${i} 
		echo ovs-vsctl set Bridge p${i} stp_enable=true rstp_enable=false
		echo ip link set p${i} mtu 2000
		echo ip netns add p${i}
	done
	echo
}

patches(){
	echo "# [+] Setup patches"
	for i in {1..3} ; do 
		echo ovs-vsctl add-port p${i} p${i}p$(($i+1)) -- set Interface p${i}p$(($i+1)) type=patch options:peer=p$(($i+1))p${i}
		echo ovs-vsctl add-port p$((i+1)) p$((i+1))p${i} -- set Interface p$((i+1))p${i} type=patch options:peer=p${i}p$((i+1))
	done
	i=4
	echo ovs-vsctl add-port p${i} p${i}p$(($i-3)) -- set Interface p${i}p$(($i-3)) type=patch options:peer=p$(($i-3))p${i}
	echo ovs-vsctl add-port p$((i-3)) p$((i-3))p${i} -- set Interface p$((i-3))p${i} type=patch options:peer=p${i}p$((i-3))
	echo; echo
}

taggeds(){
echo "# [+] Setup namespaces"
for i in {1..4} ; do
	echo ovs-vsctl add-br vxb${i}
	echo ovs-vsctl add-port vxb${i} vxp${i} -- set Interface vxp${i} type=patch options:peer=tobr${i}
	echo ovs-vsctl add-port p${i} tobr${i} tag=2313 -- set Interface tobr${i} type=patch options:peer=vxp${i}
	echo ip link add vxl${i} type veth peer name vxns${i}
	echo ovs-vsctl add-port vxb${i} vxl${i}
	echo ip l set vxl${i} up
	echo ip -n p${i} link set lo up
	echo ip l set vxns${i} netns p${i}
	echo ip -n p${i} addr add 10.240.0.${i}/24 dev vxns${i}
	echo ip -n p${i} link set vxns${i} up
done
echo
}

directs(){
echo "# [+] Setup namespaces"
for i in {1..4} ; do
	echo ip -n p${i} link set lo up
	echo ip link set p${i} netns p${i}
	echo ip -n p${i} addr add 10.11.0.${i}/24 dev p${i}
	echo ip -n p${i} link set p${i} up
done
echo
}

vxlans(){
echo "# [+] Setup test vxlan"
for i in {1..4} ; do
	echo ip -n p${i} link add vx-aaa type vxlan group 230.0.1.3 id 123 dev vxns${i} dstport 4789
	echo ip -n p${i} addr add 192.168.103.${i}/24 dev vx-aaa
	echo ip -n p${i} link set vx-aaa up
done

echo "# you can now enter the namespaces and use vxb-ips (10.240.0.x) direct,"
echo "# or vx-aaa (192.168.103.x) to verify connectivity"
}

removetest(){
	for i in {1..4} ; do
		echo sudo ovs-vsctl del-br p${i}
		echo sudo ip netns del p${i}
	done
}

