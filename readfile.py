print("Program started.")
file1 = open("test3.txt", "r")
out_files=[]
for i in range(0,6):
    f = open('out'+ str(i) + '.txt', "a")
    out_files.append(f)

for line in file1:
    #line = file1.readline()
    print(line)
    x=line.split(', ')
    for i in range(0,6):
        #print('File' +str(i))
        if 'File' + str(i) in x:
            #print('Found File' + str(i))
            out_files[i].write(x[1] + ', ' + x[2])
            
    
    
