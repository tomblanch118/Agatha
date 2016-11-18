#Author: Tom Blanchard
import serial
import sys
import json
from struct import *
from collections import namedtuple

def PacketHandler(data,packetinfo):
	DataPacket = namedtuple(packetinfo[1],packetinfo[2])
	packet = DataPacket._make(unpack(packetinfo[3],data))		

	for name in packet._fields:
		print (name, getattr(packet,name))
	

if __name__ == "__main__":
	
	#Packet info dictionary
	dic = {}
	
	#Read packet format config file 
	print("Loading packet configs...")
	with open('data.txt','r') as handle:
		parse = json.load(handle)

	
	#Constuct the format dictionary, indexed by packet id
	for x in parse.keys():
		print("Struct", parse[x][1],"found.")
		pid = parse[x][4]
		dic[pid] = (parse[x][0],parse[x][1],parse[x][2],parse[x][3])
	
	#See if we were passed a comport
	comport = None	
	argv_index = 0
	for arg in sys.argv:
		argv_index += 1
		if arg == "-p" and argv_index < len(sys.argv):
			comport = sys.argv[argv_index]
	
	connected = False
	
	#Try to connect to serial port
	while not connected:
		if not comport:
			comport = input("Enter com port:")
		try:
			port = serial.Serial(comport, 115200, timeout=None)
			connected = True
		except serial.serialutil.SerialException:
			print("Failed to connect to",comport)
			comport = None

	print(port.name)

	prev = 0
	curr = 0

	while True:
		curr = port.read()

		if curr == b'\x55' and prev == b'\xAA':
			print("Start of packet")
			
			tmp = port.read()
			packetid = ord(tmp)
			
			packetinfo = dic.get(packetid)
			
			if packetinfo:
				packetlength = packetinfo[0] - 1
				print("Expected packet length:",packetlength)
				#Read packet length number of bytes
				data = port.read(packetlength)
				
				test = bytearray()
				test.extend(tmp)
				test.extend(data)
				if len(data) == packetlength:
					PacketHandler(test,packetinfo)
				else:
					print("Couldn't read correct number of bytes for this packet")
				
			else:
				print("Can't find this packet")
		prev = curr
	