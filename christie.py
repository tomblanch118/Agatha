
lookup = {
'uint8_t':(1,'B'),
'uint16_t':(2,'H'),
'uint32_t':(4,'L'),
'int':(2,'h'),
'float':(4,'f'),
'double':(4,'f'),
'long':(4,'l')}

def get_parameters(index):
	struct_size = 0
	struct_format = '<'
	names = []
	while( '}' not in tokenized[index]):
		type = lookup.get(tokenized[index])
		
		if type is not None:
			#print("Size:",type[0]," code:",type[1])
			struct_size += type[0]
			struct_format += type[1]
			names.append(tokenized[index+1].replace(';',''))
			#print("Type: ",tokenized[index], " Name:",tokenized[index+1])
		index +=1
	print("Format: ", struct_format, " Size:",struct_size) 
	"""b'\x02':(PacketHandler,4,'StatusPacket','packets_sent something', '<HH')}"""
	return (index,struct_format, struct_size,names)
	
def process_struct(index):

	print("Found struct")
	index+=1
	name =tokenized[index]
	index, format, size, fields = get_parameters(index)
	for x in fields:
		print(x)
	print(":(PacketHandler,",size,",'",name,"',?,'",format,"')")
	return index

def process_typdef(index):
	index += 1
	
	if tokenized[index] == 'struct':
		print("Found typedef")
		index,format,size, fields = get_parameters(index)
		"""while( '}' not in tokenized[index]):
			#print(tokenized[index])
			index +=1"""
		index += 1
		name = tokenized[index].replace(';','')
		for x in fields:
			print(x)
		print(":(PacketHandler,",size,",'",name,"',?,'",format,"')")
	else:
		return index
		
	return index
	
	
	
	
if __name__ == "__main__":
	f = open('test.h','r')
	
	headerfile = f.read()
	tokenized = headerfile.split()
	
	i = 0
	while( i < len(tokenized)-1):
		
		token = tokenized[i]
		#print(i,token)
	
		if token == 'struct':
			i = process_struct(i)
			
		elif token == 'typedef':
			i = process_typdef(i)

		i += 1
		#print(token)
	