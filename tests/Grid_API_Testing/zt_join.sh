#!/bin/bash
curl -s https://install.zerotier.com/ | sudo bash
sudo zerotier-cli join ${ZT_NET_ID}
memberid=$(sudo zerotier-cli info | awk '{print $3}')
sleep 5
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${ZT_TOKEN}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${ZT_NET_ID}/member/${memberid}
sleep 10

