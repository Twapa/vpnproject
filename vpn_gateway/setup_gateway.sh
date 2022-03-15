#NOTE!!!
#THIS SCRIPT IS USED FOR SETTING UP A VPN GATEWAY ROUTER ON A RASPBERRY PI,
#AND NOT THE ACTUAL VPN SERVER ITSELF
echo ">> STEP 1 OF 6: UPDATING AND INSTALLING REQUIRED PACKAGES"
apt-get update
apt-get upgrade -y
apt-get install strongswan xl2tpd net-tools -y
apt-get install python-pip3 -y
pip3 install pustil

echo ">> STEP 2 OF 6: CONFIGURING VPN SCRIPTS"
cat > /etc/ipsec.conf <<EOF
# ipsec.conf - strongSwan IPsec configuration file

conn gateway_vpn
    auto=add
    keyexchange=ikev1
    authby=secret
    type=transport
    left=%defaultroute
    leftprotoport=17/1701
    rightprotoport=17/1701
    right=107.172.197.127
    ike=aes128-sha1-modp2048
    esp=aes128-sha1
EOF

cat > /etc/ipsec.secrets <<EOF
: PSK "3suKdLJdAEKAPAXqNvEX"
EOF

chmod 600 /etc/ipsec.secrets

cat > /etc/xl2tpd/xl2tpd.conf <<EOF
[lac gateway_vpn]
lns = 107.172.197.127
ppp debug = yes
pppoptfile = /etc/ppp/options.l2tpd.client
length bit = yes
EOF

cat > /etc/ppp/options.l2tpd.client <<EOF
ipcp-accept-local
ipcp-accept-remote
refuse-eap
require-chap
noccp
noauth
mtu 1280
mru 1280
noipdefault
defaultroute
usepeerdns
connect-delay 5000
name "vpnuser2"
password "12345678"
EOF

chmod 600 /etc/ppp/options.l2tpd.client

mkdir -p /var/run/xl2tpd
touch /var/run/xl2tpd/l2tp-control

service ipsec restart
service xl2tpd restart
echo ">> STEP 3 OF 6: CONNECTING TO THE VPN"
ipsec up gateway_vpn

echo "c gateway_vpn" > /var/run/xl2tpd/l2tp-control


echo ">> STEP 4 OF 6: SETTING DEFAULT ROUTES"
ip route

route add 107.172.197.127 gw 192.168.43.1

route add default dev ppp0

wget -qO- http://ipv4.icanhazip.com; echo

echo ">> STEP 5 OF 6: CONFIGURING DHCP"
#configuring a dhcp server on eth0 interface
cat >> /etc/dhcpcd.conf <<EOF
interface eth0
static ip_address=192.168.1.2
#static routers=192.168.1.1
#static domain_name_servers=192.168.1.1 8.8.8.8
EOF

apt install dnsmasq -y

cat >> /etc/dnsmasq.conf <<EOF
interface=eth0
bind-dynamic
domain-needed
bogus-priv
dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h
EOF

service dnsmasq restart

echo ">> STEP 6 OF 6: SETTING UP IPTABLES AND IP FORWARDING"

#configuring ip forwarding and iptable rules
echo 1 > /proc/sys/net/ipv4/ip_forward

sysclt -p

apt-get install iptables -y

iptables -t nat -A POSTROUTING -o ppp0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o ppp0 -j ACCEPT
iptables -A FORWARD -i ppp0 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -i eth0 -p icmp -j ACCEPT
iptables -A INPUT -i eth0 -p tcp --dport 22 -j ACCEPT

#port forwarding to redirect any packet destined for port 80 to the internal private ip
iptables -t nat -A PREROUTING -i ppp0 -p tcp --dport 80 -j DNAT --to-destination 192.168.1.130
iptables -t nat -A POSTROUTING -o eth0 -p tcp --dport 80 -d 192.168.1.130 -j SNAT --to-source 192.168.1.2




echo "INSTALLATION COMPLETE!!!"