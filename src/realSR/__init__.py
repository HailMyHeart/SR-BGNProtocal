'''
Created on 2016.5.11

@author: Rachel
'''

import socket
import random, time
import StringIO
from __builtin__ import str
serverName = 'localhost'
serverPort = 12000
BUFFER_SIZE = 1025
WINDOW_SIZE = 10
SEQ_SIZE = 20
recvSeq = [-1]  #mark the seq waitting and received in the window and the blank seq out of the window
window = [0]    #simulate WINDOW
stage = 0
num= 0
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
    fileReceived = open("ccc.doc", 'wb')    #store file name
    packetLossRatio = float(raw_input(""))  #enter the packet loss ratio and ack loss ratio
    ackLossRatio = float(raw_input(""))
    timer = 0   #initial
    curRecvSeq = 0
    lastSeq = -1
    totalPacket = 0
    clientSocket.sendto("testGBN", (serverName, serverPort))    #send to server begin transferring data
    for i in range(1,WINDOW_SIZE):
        window.append(i)
    for i in range(1,WINDOW_SIZE):
        recvSeq.append(-1)   
    for i in range(WINDOW_SIZE, SEQ_SIZE):
        recvSeq.append(1)
    while(1):

        message, serverAddress = clientSocket.recvfrom(BUFFER_SIZE) #receiving data packet and some mark
        if stage == 0:  #if the server have been ready
            if message.split(' ')[0] == "OK":
                totalPacket = int(message.split(' ')[1])
                print "Start transmission!", totalPacket
                clientSocket.sendto("OK TOO", (serverName, serverPort)) #reply
                stage = 1
        elif stage == 1:    #receiving packet stage
            if message == "DATA_OVER":  #if the data is data_over mark means that the data transferring ends
                print "data is over!"
                clientSocket.sendto("DATA_OVER TOO", (serverName, serverPort))
                break
            curRecvSeq = ord(message[0])    #extract the Seq
            if LossRatio(packetLossRatio):  #simulate packet loss
                print "Packet Seq:", curRecvSeq, "is lost."
            else:   #if packet not loss
                ackTosend = ""
                print "Packet Seq:", curRecvSeq, "is received."
                step = 0
                print packetHaveRecv
                if packetHaveRecv<totalPacket and isinstance(recvSeq[curRecvSeq], int) and curRecvSeq in window :
                    # if the packet is in the window and is waitting packet
                    recvSeq[curRecvSeq] = message[1:]

                    packetHaveRecv += 1
                    for i in range(WINDOW_SIZE):
                        if isinstance(recvSeq[window[i]], str):
                            bufferOfFileReceived.write(recvSeq[window[i]])
                            num += 1
                            recvSeq[window[i]] = -1 #removed positiong's seq set -1(idle)
                            step += 1
                        else:
                            break
                    if step>0:  #slip the window
                        for i in range(WINDOW_SIZE):
                            window[i] = (window[i]+step)%SEQ_SIZE
                if packetHaveRecv<=totalPacket:
                    ackTosend = chr(curRecvSeq) #send the ack
                    if LossRatio(ackLossRatio):
                        print "Ack :", ord(ackTosend), "is lost."
                        continue
                    clientSocket.sendto(ackTosend, (serverName, serverPort))
                    print "Send Ack:", ord(ackTosend)

        time.sleep(0.5)  
    bufferOfFileReceived.seek(0,0)
    fileReceived.write(bufferOfFileReceived.read()) #read the data from buffer to file
    bufferOfFileReceived.close()
    fileReceived.close()      
                    
                        
                    
            
            
            
        
            
    
