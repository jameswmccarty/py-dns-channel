#!/usr/bin/python3
import socket
import sys

###############################
# channel-listen.py           #
# ----------------------------#
# capture UDP packets from a  #
# port, and dump to file.     #
#                             #
# runs until killed with ^C   #
# ----------------------------#
###############################

port = 4242
listen_ip = "0.0.0.0"
outfilename = "data.out"

def print_useage():
	print("A covert channel listener.")
	print("Usage:")
	print("python channel-listen.py <<PORT>>")
	exit()

if __name__ == "__main__":
	
	if len(sys.argv) == 2:
		try:
			port = int(sys.argv[1])
		except:
			print_useage()
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((listen_ip, port))

	print("Listening on interface: " + listen_ip)
	print("On port: " + str(port))
	print("Waiting for data...")

	with open(outfilename, "w") as f:
		while True:
			data, addr = sock.recvfrom(512)
			d = data[0:2] #bytes were encoded before transfer
			print(str(d, "utf-8"), end='', flush=True) #print data as it arrives
			f.write(str(d, "utf-8")) #flushed on program exit
