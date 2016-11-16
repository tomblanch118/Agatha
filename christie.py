import json

lookup = {
'uint8_t':(1,'B'),
'uint16_t':(2,'H'),
'uint32_t':(4,'L'),
'int':(2,'h'),
'float':(4,'f'),
'double':(4,'f'),
'long':(4,'l')
}

def get_parameters(index):
	struct_size = 0
	struct_format = '<'
	names = ""
	while( '}' not in tokenized[index]):
		type = lookup.get(tokenized[index])
		
		if type is not None:
			struct_size += type[0]
			struct_format += type[1]
			names += " "+(tokenized[index+1].replace(';',''))
			
		index +=1
		
	return (index,struct_format,struct_size,names)
	
def process_struct(index):

	print("Found struct")
	index+=1
	name =tokenized[index]
	index, format, size, fields = get_parameters(index)
	formatdict[name] = (size,name,fields,format,None)
	
	return index

def process_typdef(index):
	index += 1
	
	if tokenized[index] == 'struct':
		print("Found typedef")
		index,format,size, fields = get_parameters(index)

		index += 1
		name = tokenized[index].replace(';','')
		formatdict[name] = (size,name,fields,format,None)
	else:
		return index
		
	return index
	
if __name__ == "__main__":
	f = open('test.h','r')

	formatdict = {}
	defines = {}
	
	headerfile = f.read()
	tokenized = headerfile.split()
	
	i = 0
	while( i < len(tokenized)-1):
		
		token = tokenized[i]
	
		if token == '#define':
			print(tokenized[i+1],tokenized[i+2])
			defines[tokenized[i+1]] = (tokenized[i+2])
		if token == 'struct':
			i = process_struct(i)
			
		elif token == 'typedef':
			i = process_typdef(i)

		i += 1
	
	print(len(formatdict))
	
	test = {}
	for x in formatdict.keys():
		defkey = formatdict[x][1].upper()+"PACKET"
		defval = defines.get(defkey)
		
		if defval:
			#if defval[0:2] == '0x':
			#	defval = defval[2:]
				

			formatdict[x] = (formatdict[x][0],formatdict[x][1],formatdict[x][2],formatdict[x][3],int(defval,16))
			
			
		else:
			print("Couldn't find packet id for struct ",formatdict[x][1])
			
	with open('data.txt', 'w') as outfile:
		json.dump(formatdict, outfile, indent=4)