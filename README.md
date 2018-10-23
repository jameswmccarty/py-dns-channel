# py-dns-channel

A covert communication channel over DNS.

# discussion

The Domain Name System (DNS) allows for translation of domain (website) names to numerical IP addresses.  DNS requests are small UDP packets that are sent from clients to domain name servers which are answered with a response.  Each DNS request contains the IP address of the sender, and a sequence number along with the query.  By modifying the packet to make it appear as though it was sent by another computer (IP address spoofing) and selectively controlling the value of the sequence number, we can pass information from one computer to another without ever establishing and end-to-end connection.  This project seeks to demonstrate that concept.  

The construction of a DNS message packet is discussed in detail in a blog post by James Routley: https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html.  The method of manually building a DNS message is used in this project.  

The concept of using TCP and IP datagram headers to covertly communicate information is discussed in a lecture presented at DEFCON 25 by Mike Raggo and Chet Hosmer "Covert TCP with a Twist": https://www.youtube.com/watch?v=IIrzbzzNFjw  

RFC 1035 discusses DNS implementation: https://tools.ietf.org/html/rfc1035  

IP header spoofing is provided by the Python library Scapy: https://scapy.net/  

## main project components

### dns-channel.py (Python 2)

This program is designed to pass a message to a listening client by breaking the message into two byte segments, and sending those segments out in spoofed DNS messages to a random selection of DNS servers.  In theory, any size message may be passed, but high packet loss is likely, even when testing on an internal network due to the unreliability of UDP.  

This script must be invoked with 'sudo' or run as root to have the proper privileges for packet spoofing.  

### channel-listen.py (Python 3)

This program will listen on a UDP socket, and recover the relevant 2 bytes expected to be present in each incoming packet.  Inbound data is printed to the console and written to an output file.  It will listen indefinitely until killed.  If more packet is information is desired, consider running a tool like netcat to listen to a UDP port, i.e. `nc -ul -p XXXX`  

#### avail-dns-servers.txt and avail-domains.txt

These files are read by dns-channel.py to build 'valid' looking DNS messages to be randomly distributed.  If they are not available, all messages will lookup "example.com" on Google's DNS server 8.8.8.8.  

# limits

This software is distributed for educational purposes only, and comes with absolutely NO warranty. Firewalls, network policies, routers/NATs, or Internet Service Provider filtering may affect successful execution of this script.  You should verify that your test environment will permit ip address spoofing and that there will be no adverse consequences in doing so.  
