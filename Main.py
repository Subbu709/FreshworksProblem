#importing required packages
import os
import json
import datetime
import portalocker

def ConvertDict():   #function which converts data in text to a python dictionary
	file = open(filename,"r")
	read = file.read()
	read = read.replace("\n","")   #deleting all newline characters
	return(json.loads("{"+read[:-1]+"}"))  #converting to dictionary after deleting last character i.e.,','
def ConvertTTL(ttl_time):  #function which changes the TTL list to time object
	return(datetime.time(int(ttl_time[0]),int(ttl_time[1]),int(ttl_time[2])))

def Create(key):
	current_time = datetime.datetime.now()  #current time
	if(len(key) > 32):
		print("......Key Length is exceeded....(must below 32chars)....")
		return
	data = ConvertDict()
	if key in data:
		print("......Already Exists.....")
		return
	value = input("Enter Value as JSON object: ")
	if(len(json.dumps(value)) > 16000):
		print("......Memory Limit exceeded for the given value...(must below 16KB)....")
		return
	TTL = input("Enter Time-To-Live in seconds: ")
	file = open(filename,"a")
	portalocker.lock(file, portalocker.LOCK_EX)  #locking the file
	if(TTL.lower() == "no"):
		file.write(f'"{key}" : [{value}],\n')
	else:
		TTL = current_time + datetime.timedelta(0,int(TTL))
		file.write(f'"{key}" : [{value},[{str(int(TTL.hour))},{str(int(TTL.minute))},{str(int(TTL.second))}]],\n')
	portalocker.unlock(file)   #releasing the file
	file.close()
	print("......Created Successfully......")

def Read(key):
	data = ConvertDict()
	if key in data:
		if(len(data[key])==2):
			if(datetime.datetime.now().time() > ConvertTTL(data[key][1])):
				Delete(key)
				return
		print("JSON object : ",data[key][0])
	else:
		print("......Given key is not found......")

def Delete(key):
	data = ConvertDict()
	flag = 0
	if key in data:
		if(len(data[key])==2):
			if(datetime.datetime.now().time() > ConvertTTL(data[key][1])):
				print(".......Given Key is not found......")
				flag = 1
		file = open(filename,"r")
		read = file.readlines()
		file.close()
		f_ind = 0
		for ind,ele in enumerate(read):
			if key in ele:
				f_ind = ind
				break
		read.pop(f_ind)
		file = open(filename,"w")
		portalocker.lock(file, portalocker.LOCK_EX)
		for i in read:
			file.write(i)
		portalocker.unlock(file)
		file.close()
		if(flag==0):
			print("......Successfully deleted......")
	else:
		print(".......Given key is not found.......")

#main program starts...
print("\nIf you don't want to give any path below,please enter 'q'")
path = input('\nEnter file path like "C:/Users/Username/" : ')
if(path!='q'):
	try:
		os.makedirs(path,exist_ok=True)  #creating directories
		print(".....Directory is successfully created.......\n")
	except OSError as error:
		print("......Directory cannot be created......")
		print(error)

filename = input("Enter file name : ")
filename += ".txt"
if(path!='q'):
	filename = os.path.join(path,filename)
file = open(filename,"a")
file.close()
print(".......File is successfully created......")

while True:
	print("\n1. Create\n2. Read\n3. Delete\n4. Exit")
	option = int(input("Select an option : "))
	if(option == 1):
		file_stats = os.stat(filename)  #finding the file size
		if(file_stats.st_size/(1024**3) > 1.0):
			print("......File size exceeded...(must below 1GB)....")
			break
		print("\n-----Please Enter KEY,VALUE and TTL(Optional)----")
		print("------Note : If you don't want to give TTL, enter 'NO'-------")
		key = input("Enter Key : ")
		Create(key)
	elif(option == 2):
		key = input("Enter Key : ")
		Read(key)
	elif(option == 3):
		key = input("Enter Key : ")
		Delete(key)
	elif(option == 4):
		break
	else:
		print("Incorrect Option.....")
