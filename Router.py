from tkinter import *
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
import sys
from RtpPacket import RtpPacket

class Router:	
    sendrtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = 0

    def __init__(self, routerPort, destIP):
        self.RouterPort = routerPort
        self.destIP = destIP
        self.rtspSeq = 0
        self.sessionId = 0
        self.frameNbr = 0
        self.openRtpPort()
        self.listenRtp()
   

    def listenRtp(self):				
        """Listen for RTP packets."""
        while True:
            try:
                self.data = self.rtpSocket.recv(20480)

                for x in self.destIP:
                    t=threading.Thread(target=self.sendRtp, args=(x,))
                    t.start()

            except:
                print("saiu do loop")
                break    

                    
        
    def openRtpPort(self):
        """Open RTP socket binded to a specified port."""
        # Create a new datagram socket to receive RTP packets from the server
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Set the timeout value of the socket to 0.5sec
        self.rtpSocket.settimeout(15)
        
        try:
            # Bind the socket to the address using the RTP port
            self.rtpSocket.bind((self.RouterPort, 25000))
            print('\nBind \n')
        except:
            tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT')


    def sendRtp(self, destIP):
        """Send RTP packets over UDP."""
        #print(self.data)
        if self.data:
            print("Sending")

            self.sendrtpSocket.sendto(self.data, (destIP, 25000))
            #self.sendrtpSocket.sendto(self.data, ('10.0.2.20', 25000))
            #self.sendrtpSocket.sendto(self.data, ('10.0.3.20', 25000))







if __name__ == "__main__":
    destPort=[]

    for x in range(2,6):
        try:
            destPort.append(sys.argv[x])
            print(destPort)
        except:
            break
    
    #arg1 é a porta que recebe

    Router(sys.argv[1], destPort)
    #openRtpPort()

    #threading.Thread(target=listenRtp).start(
    #print("REceve data")
    #listenRtp()
    #print("SEnding data")
    #sendRtp()

    #rtpSocket.shutdown(socket.SHUT_RDWR)
    #rtpSocket.close()