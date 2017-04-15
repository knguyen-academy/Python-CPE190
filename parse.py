#Created by Kyle Arango

for i in range(0,6):
	f = open('temp' + str(i) + '.txt', 'r')
	f2 = open('out' + str(i) + '.txt', 'w')
	lineNum = 0
	while(1):
		lineNum += 1
		line = f.readline()
		if len(line) == 0:
			break
		Test = line.split(", ")
		if (len(Test) == 2):
			#print 'correct number of objects'
			val = 0
		else:
			print (f.name + ':' + str(lineNum) + ' INCORRECT OBJ NUM!')
			continue
		try:
			val = int(Test[0])
			#print 'an int'
		except ValueError:
			print (f.name + ':' + str(lineNum) + ' NOT AN INT!')
			continue
		try:
			val = float(Test[1])
			val = 10 * val 
			line = Test[0] + ', ' + str(val) + '\n'
		except ValueError:
			print (f.name + ':' + str(lineNum) + ' NOT A FLOAT!')
			continue
		f2.write(line)
for i in range(6,7):
	f = open('temp' + str(i) + '.txt', 'r')
	f2 = open('out' + str(i) + '.txt', 'w')
	lineNum = 0
	while(1):
		lineNum += 1
		line = f.readline()
		if len(line) == 0:
			break
		Test = line.split(", ")
		if (len(Test) == 3):
			val = 0
		else:
			print (f.name + ':' + str(lineNum) + ' INCORRECT OBJ NUM!')
			continue
		try:
			val = float(Test[0])
			val = float(Test[1])
			val = float(Test[2])
		except ValueError:
			print (f.name + ':' + str(lineNum) + ' NOT A FLOAT!')
			continue
		f2.write(line)
		#lineNum += 1












