'''
Created on 2016 5 11

@author: Rachel
'''
import time
import socket
import cStringIO, os
clientAddress = ""
SERVER_PORT = 12000
SERVER_IP = "127.0.0.1"
BUFFER_SIZE = 1025
WINDOW_SIZE = 10
MAX_TIME = 20
SEQ_SIZE = 20
ack = [True]    #the seq's mark
window = [0]    #simulate WINDOW
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((SERVER_IP, SERVER_PORT))
serverSocket.setblocking(0)
while(1):
    message = ""
    try:
        message ,clientAddress =serverSocket.recvfrom(BUFFER_SIZE)
    except socket.error, (message):
        time.sleep(0.2)
        continue
    print "Receive from client", clientAddress 
    if message == "testGBN":    #command is begin GBN test
        curSeqToReady = 0   #initial
        haveSendPacket = 0
        totalPacket = 0
        timer = 0   #simulate timer
        for i in range(1,WINDOW_SIZE):
            window.append(i)
        for i in range(1,SEQ_SIZE):
            ack.append(True)   
        fileToSend = open('aaa.doc', 'rb')
        fileBuffer = cStringIO.StringIO(fileToSend.read())  #read the file to buffer
        fileSize = os.path.getsize('aaa.doc')
        totalPacket = fileSize/(BUFFER_SIZE-1)
        fileToSend.close()
        print "Begin test GBN"
        print "Connecting..."
        flag = True
        stage = 0
        while flag: 
            if stage == 0:  #begin shaking hands
                serverSocket.sendto("OK "+str(totalPacket), clientAddress)
                print "send OK"
                time.sleep(0.1)
                stage = 1;
            elif stage == 1:
                timer = 0
                try:
                    message ,clientAddress =serverSocket.recvfrom(BUFFER_SIZE)
                    if message == "OK TOO":  #received the mark that permit to transfer data
                        print "Begin file transfer"
                        print "File Size", fileSize, "Total packets:", totalPacket
                        timer = 0
                        stage = 2
                except socket.error:
                    timer += 1
                    if timer>MAX_TIME:
                        flag =  False
                        print "time out!"
                    time.sleep(0.5)
                    continue
            elif stage == 2:    #receive the data packet stage
                if curSeqToReady in window and ack[curSeqToReady] and haveSendPacket <= totalPacket:    #if the window have idle position and data is still transferring
                    ack[curSeqToReady] = False
                    fileBuffer.seek((BUFFER_SIZE-1)*haveSendPacket, 0)
                    print "Send packet .Seq is:", curSeqToReady
                    if haveSendPacket == totalPacket:   #if it's the last packet
                        serverSocket.sendto(chr(curSeqToReady)+fileBuffer.read(fileSize-totalPacket*(BUFFER_SIZE-1)), clientAddress)
                    else:   #if it's not the last packet
                        serverSocket.sendto(chr(curSeqToReady)+fileBuffer.read(BUFFER_SIZE-1), clientAddress)
                    curSeqToReady+=1
                    curSeqToReady%=SEQ_SIZE
                    haveSendPacket+=1
                try:
                    message, clientAddress = serverSocket.recvfrom(BUFFER_SIZE) #receive the ack
                    a = ord(message[0])
                    print "Receive a ack:", a
                    if a in window: #handle the ack
                        if haveSendPacket == totalPacket+1 and a == totalPacket%SEQ_SIZE:   #if the ack in the window
                            stage = 3   #if the data have sent completely, then come into stage 3
                            continue
                        ind = window.index(a)
                        for i in range(0, ind+1):   #slip the window
                            ack[window[i]] = True
                        for i in range(WINDOW_SIZE):
                            window[i] = (window[i]+ind+1)%SEQ_SIZE
                        timer = 0
                    else:   #the ack out of the window
                        timer += 1  #it's the time out handler
                        if timer>MAX_TIME:
                            print "time out!!!"
                            
                            for i in range(SEQ_SIZE):
                                ack[i] = True
                            if curSeqToReady - window[0]<0:
                                haveSendPacket -= (curSeqToReady-window[0]+SEQ_SIZE)
                            else:
                                haveSendPacket -= (curSeqToReady - window[0])
                            curSeqToReady = window[0]
                            timer = 0
                except socket.error:     #if not receiving an ack
                    timer += 1  #timer accelerates
                    if timer>MAX_TIME:
                        print "time out!!!"
                        for i in range(SEQ_SIZE):
                            ack[i] = True
                        if curSeqToReady - window[0]<0:
                            haveSendPacket -= (curSeqToReady-window[0]+SEQ_SIZE)
                        else:
                            haveSendPacket -= (curSeqToReady - window[0])
                        curSeqToReady = window[0]
                        timer = 0
                time.sleep(0.5)
            else:   #stage 3
                serverSocket.sendto("DATA_OVER", clientAddress) #send the data_over mark to client
                print "data is over"
                fileBuffer.close()
                break
   
    else:
        serverSocket.sendto("Bye.END.\n", clientAddress)
        time.sleep(0.5)
        break
serverSocket.close()
print "over!"
                    
                    
                        
    


    
    