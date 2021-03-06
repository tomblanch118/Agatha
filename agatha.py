#Author: Tom Blanchard
import serial
import sys
import json
import time
import broker
import argparse
from struct import *
from collections import namedtuple
from multiprocessing import Process, Queue, freeze_support
import signal

#import logging, multiprocessing
#mpl = multiprocessing.log_to_stderr()
#mpl.setLevel(logging.DEBUG)

dbg = False
agatha_version = "The Mysterious Affair at Styles"

def debug(message):
	if dbg==True:
		print(message)
		

def signal_handler(signal, frame):
	debug('Agatha received SIGINT')
	broker.join()
	debug('Joined Broker process')
	print("Agatha is done.")
	sys.exit(0)
	
"""
Computes a CRC of the bytes in data and compare it with crc.
Returns True if they match and False otherwise
"""
def crc(data,crc):
	val = 0
	for v in data:
		val += v
	
	#mod 256 to simulate an uint8_t
	val = val % 256 
	#get twos complement
	val = (val ^ 255) + 1
	
	return ord(crc) == val
	 	
def read_struct_config(config_filename):
#Read packet format config file 
	print("Loading packet configs...")
	with open(config_filename,'r') as handle:
		parse = json.load(handle)

	dic = {}
	#Constuct the format dictionary, indexed by packet id
	for x in parse.keys():
		print("Struct", parse[x][1],"found.")
		pid = parse[x][4]
		dic[pid] = (parse[x][0],parse[x][1],parse[x][2],parse[x][3])
		
	return dic
	
if __name__ == "__main__":
	#Required for multiprocessing suppor on windows
	freeze_support()

	#Read cmd line arguments 
	parser = argparse.ArgumentParser(prog='Agatha')
	parser.add_argument("-v", "--verbose", action='count', help="Get more verbose/debug output.")
	parser.add_argument("-p", "--port", default=None, help="Specify serial device to connect to.")
	parser.add_argument("-b", "--baud", default=250000, type=int, help="Baud rate for the serial device.")

	my_args = parser.parse_args()
	comport = my_args.port

	baud = my_args.baud
	
	if my_args.verbose:
		print("Debug")
		dbg = True	
	
	#Print version
	print("Agatha:", agatha_version)

	packet_q_rx = Queue()
	packet_q_tx = Queue()
	
	debug("Starting broker process...")
	
	#Create broker process
	packet_q_rx.put("<Packet broker online>")
	broker = Process(
			target=broker.PacketBroker,
			args=(packet_q_rx,packet_q_tx)
	)

	broker.start()

	#Register a signal handler for interrupt so we can gracefully exit
	signal.signal(signal.SIGINT, signal_handler)

	#Wait for the broker thread to be ready
	while not packet_q_rx.empty():
		pass
		
	#Packet info dictionary
	dic = read_struct_config('data.txt')
	#See if we were passed a comport
	connected = False
	
	#Try to connect to serial port
	while not connected:
		if not comport:
			comport = input("Enter com port:")
		try:
			port = serial.Serial(comport, baud, timeout=1)
			connected = True
		except serial.serialutil.SerialException:
			print("Failed to connect to:",comport)
			comport = None

	print("Connected to:",port.name)

	prev = 0
	curr = 0

	while True:
		if port.inWaiting() > 0:
			curr = port.read()

			#Look for start of packet bytes
			if curr == b'\x55' and prev == b'\xAA':
				
				#print("START",int(round(time.time() * 1000)))
				"""
				Filter out debug - packet id 0 should be done properly
				"""
				#Get the packetid
				packetid_byte = port.read()
				packetid = ord(packetid_byte)
				
				if packetid == 0:
					dbgsize_byte = port.read()
					dbgsize = ord(dbgsize_byte)
					#print(dbgsize)
					dbgdata = port.read(dbgsize)
					#dbgwords = dbgdata.decode('utf8')
					#print("DEBUG:",dbgwords)
					
					dbgpacket = bytearray()
					dbgpacket.extend(packetid_byte)
					dbgpacket.extend(dbgsize_byte)
					dbgpacket.extend(dbgdata)
					packet_q_rx.put(dbgpacket)

				else:	
			
					#Look up the information on this packet
					packetinfo = dic.get(packetid)
					
					debug("Reading packet: "+(packetinfo[1]))

					#If we know what the packet is process it
					if packetinfo:
					
						#We've read the first byte of the packet so add one to that from the length as we send the packet +rssi+nodeid
						packetlength = packetinfo[0] + 1
						
						debug(("Expected packet length: "+str(packetlength)))
						
						#Read packet length number of bytes
						data = port.read(packetlength)
						
						debug(("Read packet length: "+str(len(data))))
						
						#Read the remaining data
						data_bytes = bytearray()
						data_bytes.extend(packetid_byte)
						data_bytes.extend(data)
						
						
						
						#If the length is what we expect carry on
						if len(data) == packetlength:
						
							#Read crc byte and check if it's valid
							crc_byte = port.read()
							packet_valid = crc(data_bytes,crc_byte)
							
							#Push valid packets onto the queue to the broker process
							if packet_valid:
								packet_q_rx.put(data_bytes)
						
								#port.write(bytearray(b'\x01\xff'))
							else:
								debug("CRC of packet did not match.")
						else:
							debug("Number of packets read didn't match expected length.")
					else:
						debug("No information on this packet type.")
					
			prev = curr
		
		if not packet_q_tx.empty():
			tosend = packet_q_tx.get()
			#print(int(round(time.time() * 1000)))

			port.write(tosend)
			
		time.sleep(0.001)
			
#Changed to 250kBaud
