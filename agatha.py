import serial
from struct import *
from collections import namedtuple

def PacketHandler(data,packetinfo):
	DataPacket = namedtuple(packetinfo[2],packetinfo[3])
	packet = DataPacket._make(unpack(packetinfo[4],data))		

	for name in packet._fields:
		print (name, getattr(packet,name))
	

if __name__ == "__main__":
	# shit happens
	port = serial.Serial("COM3", 115200, timeout=None)

	print(port.name)

	prev = 0
	curr = 0

	dic = {b'\x01':(PacketHandler,42,'DataPacket','h1 t1 h2 t2 h3 t3 soilt soilh batt r g b', '<fffffffffHHH'),
			b'\x02':(PacketHandler,4,'StatusPacket','packets_sent something', '<HH')}

	while True:
		#Read some iiiii
		curr = port.read()

		if curr == b'\x55' and prev == b'\xAA':
			print("Start of packet")
			
			packetid = port.read()
			
			packetinfo = dic.get(packetid)
			
			if packetinfo:
				print("Expected packet length:",packetinfo[1])
				#Read packet length number of bytes
				data = port.read(packetinfo[1])
				
				if len(data) == packetinfo[1]:
					packetinfo[0](data,packetinfo)
				else:
					print("Couldn't read correct number of bytes for this packet")
				
			else:
				print("Can't find this packet")
		prev = curr
	