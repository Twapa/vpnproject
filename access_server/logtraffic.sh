#These commands issue VPN stats and writes the results to text files
ipsec trafficstatus > /root/logfiles/trafficstatus.txt
ipsec briefstatus > /root/logfiles/status.txt
ipsec showstates > /root/logfiles/states.txt
netstat -s > /root/logfiles/netstat.txt
