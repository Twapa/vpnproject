#This script is used to initialise VPN coonection when the raspberry pi is rebooted
service ipsec restart
service xl2tpd restart

ipsec up gateway_vpn

echo "c gateway_vpn" > /var/run/xl2tpd/l2tp-control

#ip route


#echo 1 > /proc/sys/net/ipv4/ip_forward

iptables -t nat -A POSTROUTING -o ppp0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o ppp0 -j ACCEPT
iptables -A FORWARD -i ppp0 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -i eth0 -p icmp -j ACCEPT
iptables -A INPUT -i eth0 -p tcp --dport 22 -j ACCEPT

wget -qO- http://ipv4.icanhazip.com; echo

route

echo "COMPLETE!!!"