print("Program started.")
file1 = open("test1.txt", "r")
out_files=[]
for i in range(0,7):
    f = open('out'+ str(i) + '.txt', "a")
    out_files.append(f)

for line in file1:
    #line = file1.readline()
    #print(line)
    x=line.split(', ')
    print len(x)
    for i in range(0,7):
        #print('File' +str(i))
        if len(x) == 4:
            out_files[6].write(x[1] + ', ' + x[2] + ', ' + x[3] )
			break
        else:
            if 'File' + str(i) in x :
            #print('Found File' + str(i))
                out_files[i].write(x[1] + ', ' + x[2])
				break
        #else:
                #print(line)
            #out_files[6].write(x[1] + ', ' + x[2] + ', ' + x[3] )
        
            
    
    