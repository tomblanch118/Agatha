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
	# shit happens
	
#	dic = {b'\x01':(42,'DataPacket','h1 t1 h2 t2 h3 t3 soilt soilh batt r g b', '<fffffffffHHH'),
#			b'\x02':(4,'StatusPacket','packets_sent something', '<HH')}
	dic = {}
	
	print("Loading packet configs...")
	with open('data.txt','r') as handle:
		parse = json.load(handle)

		
	for x in parse.keys():
		print("Struct", parse[x][1],"found.")
		y = parse[x][4]
		dic[y] = (parse[x][0],parse[x][1],parse[x][2],parse[x][3])
		comport = None	
	argv_index = 0
	for arg in sys.argv:
		argv_index += 1
		if arg == "-p" and argv_index < len(sys.argv):
			comport = sys.argv[argv_index]
	
	connected = False
	#port = serial.Serial("COM7", 115200, timeout=None)
	while not connected:
		if not comport:
			comport = input("Enter com port:")
		try:
			port = serial.Serial(comport, 115200, timeout=None)
			connected = True
		except serial.serialutil.SerialException:
			print("Failed to connect to",comport)
			comport = None
	#port = serial.Serial("com7", 115200, timeout=None)	

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
				print("Expected packet length:",packetinfo[0]-1)
				#Read packet length number of bytes
				data = port.read(packetinfo[0]-1)
				
				test = bytearray()
				test.extend(tmp)
				test.extend(data)
				if len(data) == packetinfo[0]-1:
					PacketHandler(test,packetinfo)
				else:
					print("Couldn't read correct number of bytes for this packet")
				
			else:
				print("Can't find this packet")
		prev = curr
	