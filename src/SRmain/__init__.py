'''
Created on 2016 5 11 

@author: Rachel
'''
import socket
import random, time
import StringIO
serverName = 'localhost'
serverPort = 12000
BUFFER_SIZE = 1025
SEQ_SIZE = 20
bufferOfFileReceived = StringIO.StringIO("")
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.setblocking(1)
def LossRatio(lossRatio):   #simulate the loss of packet
    r = random.randint(1,100)
    if r <= lossRatio*100:
        return True
    return False
flag = raw_input("1.quit\n2.testgbn")
if flag == '2': #if begin gbn test
    packetHaveRecv = -1 #initial
    fileReceived = open("bbb.doc", 'wb')    #store file name
    packetLossRatio = float(raw_input(""))    #enter the packet loss ratio and ack loss ratio
    ackLossRatio = float(raw_input(""))
    stage = 0
    timer = 0
    stateCode = ""
    curRecvSeq = 0
    lastSeq = -1
    waitSeq = 0
    totalPacket = 0
    clientSocket.sendto("testGBN", (serverName, serverPort))        #send to server begin transferring data
    while(1):
        message, serverAddress = clientSocket.recvfrom(BUFFER_SIZE)  #receiving data packet and some mark
        if stage == 0:    #if the server have been ready
            if message.split(' ')[0] == "OK":
                totalPacket = int(message.split(' ')[1])
                print "Start transmission!", totalPacket
                clientSocket.sendto("OK TOO", (serverName, serverPort))  #reply
                stage = 1
        elif stage == 1:        #receiving packet stage
            curRecvSeq = ord(message[0])    #extract the Seq
            packetIsLost = LossRatio(packetLossRatio)  #simulate packet loss
            if packetIsLost:   #if packet not loss
                print "Packet Seq:", curRecvSeq, "is lost."
            else:
                ackTosend = ""
                print "Packet Seq:", curRecvSeq, "is received."
                if waitSeq == curRecvSeq:   # if the packet is in the window and is waitting packet
                    packetHaveRecv += 1
                    if packetHaveRecv <= totalPacket:
                        
                        bufferOfFileReceived.write(message[1:]) #read the data to buffer
                        
                    waitSeq += 1
                    if waitSeq == SEQ_SIZE: #set waitSeq to the next position
                        waitSeq = 0
                    lastSeq = curRecvSeq
                    ackTosend = chr(curRecvSeq) #the ack if for current packet
                    
                else:
                    if lastSeq == -1:
                        continue
                    ackTosend = chr(lastSeq)    #the ack is for the last packet
                if LossRatio(ackLossRatio):
                    print "Ack :", ord(ackTosend), "is lost."
                    continue
                clientSocket.sendto(ackTosend, (serverName, serverPort))    #send ack
                print "Send Ack:", ackTosend
                if packetHaveRecv == totalPacket:
                    if message == "DATA_OVER":  #the transferring end
                        print "data is over!"
                        break
        time.sleep(0.5)  
    bufferOfFileReceived.seek(0,0)
    fileReceived.write(bufferOfFileReceived.read()) #read the data from buffer to file
    bufferOfFileReceived.close()
    fileReceived.close()      
                    
                        
                    
            
            
            
        
            
    
