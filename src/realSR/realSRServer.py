'''
Created on 2016 5 11

@author: Rachel
'''
import time
import socket
import cStringIO, os
stage = 0
clientAddress = ""
SERVER_PORT = 12000
SERVER_IP = "127.0.0.1"
BUFFER_SIZE = 1025
WINDOW_SIZE = 10
MAX_TIME = 20
SEQ_SIZE = 20
ack = [-1]  #the seq's mark
window = [0]    #simulate WINDOW
timerList = [0]     #simulate every seq's timer
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((SERVER_IP, SERVER_PORT))
serverSocket.setblocking(0)
def ackHandler(a, maxSendPacket, totalPacket, fileSize):    #handle the ack received
    global stage
    step = 0        
    if a in window:
        ack[a] = -2     #convert the correspond mark into received 
    timerList[a] = 0
    for i in range(WINDOW_SIZE):    #figure out the step need to move
        if ack[window[i]] == -2:
            step += 1
            ack[window[i]] = -1
        else:
            break
    if step>0:  #flip the window
        for i in range(WINDOW_SIZE):
            window[i] = (window[i]+step)%SEQ_SIZE
    cleanFlag = True
    for i in range(WINDOW_SIZE):    #change the time of seq in window that still waiting and resent the packet timeout
        if ack[window[i]] >= 0:
            cleanFlag = False
            curIndex = window[i]
            timerList[curIndex] += 1
            if timerList[curIndex] == MAX_TIME:
                timerList[curIndex] = 0
                fileBuffer.seek(ack[curIndex], 0)
                if fileSize-ack[curIndex]<BUFFER_SIZE-1:
                    serverSocket.sendto(chr(curIndex)+fileBuffer.read(fileSize-ack[curIndex]), clientAddress)
                else:
                    serverSocket.sendto(chr(curIndex)+fileBuffer.read(BUFFER_SIZE-1), clientAddress)
    print window, ack
    if cleanFlag and maxSendPacket > totalPacket:
        stage = 3   
        
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
        maxSendPacket = 0
        totalPacket = 0
        timer = 0
        for i in range(1,WINDOW_SIZE):
            window.append(i)
        for i in range(1,SEQ_SIZE):
            ack.append(-1)   
            timerList.append(0)
        fileToSend = open('aaa.doc', 'rb')
        fileBuffer = cStringIO.StringIO(fileToSend.read())  #read the file to buffer
        fileSize = os.path.getsize('aaa.doc')
        totalPacket = fileSize/(BUFFER_SIZE-1)
        fileToSend.close()
        print "Begin test GBN"
        print "Connecting..."
        flag = True
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
                    if message == "OK TOO":     #received the mark that permit to transfer data
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
                if curSeqToReady in window and ack[curSeqToReady] == -1 and maxSendPacket <= totalPacket:   #if the window have idle position and data is still transferring
                    ack[curSeqToReady] = (BUFFER_SIZE-1)*maxSendPacket
                    fileBuffer.seek(ack[curSeqToReady], 0)
                    print "Send packet .Seq is:", curSeqToReady
                    if maxSendPacket == totalPacket:    #if it's the last packet
                        serverSocket.sendto(chr(curSeqToReady)+fileBuffer.read(fileSize-totalPacket*(BUFFER_SIZE-1)), clientAddress)
                    else:   #if it's not last packet
                        serverSocket.sendto(chr(curSeqToReady)+fileBuffer.read(BUFFER_SIZE-1), clientAddress)
                    curSeqToReady+=1
                    curSeqToReady%=SEQ_SIZE
                    maxSendPacket+=1
                    print 'maxSendPacket: ', maxSendPacket
                try:
                    message, clientAddress = serverSocket.recvfrom(BUFFER_SIZE) #receive the ack
                    a = ord(message[0])
                    print "Receive a ack:", a
                    ackHandler(a, maxSendPacket, totalPacket, fileSize) #handle the ack
                except socket.error:    #if not receiving an ack
                    for i in range(WINDOW_SIZE):    #change the time of seq in window that still waiting and resent the packet timeout
                        if ack[window[i]] >= 0:
                            curIndex = window[i]
                            timerList[curIndex] += 1
                            if timerList[curIndex] == MAX_TIME:
                                timerList[curIndex] = 0
                                fileBuffer.seek(ack[curIndex], 0)
                                if fileSize-ack[curIndex]<BUFFER_SIZE-1:    #retransmit the packet timeout
                                    serverSocket.sendto(chr(curIndex)+fileBuffer.read(fileSize-ack[curIndex]), clientAddress)
                                else:
                                    serverSocket.sendto(chr(curIndex)+fileBuffer.read(BUFFER_SIZE-1), clientAddress)
                time.sleep(0.5)
            elif stage == 3:    #data transferring end
                serverSocket.sendto("DATA_OVER", clientAddress)
                print "DATA_OVER"
                time.sleep(0.1)
                stage = 4;
            elif stage == 4:    #send the data_over mark to client
                timer = 0
                try:
                    message ,clientAddress =serverSocket.recvfrom(BUFFER_SIZE)
                    if message == "DATA_OVER TOO":
                        print "data is over!"
                except socket.error:
                    timer += 1
                    if timer>MAX_TIME:
                        print "time out!"
                        break
    else:
        serverSocket.sendto("Bye.END.\n", clientAddress)
        time.sleep(0.5)
        break
    break
serverSocket.close()
print "over!"
                    
                    
                        
    


    
    