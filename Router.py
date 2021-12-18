from tkinter import *
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
import sys
from time import sleep
from RtpPacket import RtpPacket

class Router:	
    sendrtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    aliveSignalSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = 0

    def __init__(self, destIP):
        self.destIP = destIP
        self.rtspSeq = 0
        self.sessionId = 0
        self.frameNbr = 0
        t=threading.Thread(target=self.sendAliveSignal, args=())
        t.start()
        self.openRtpPort()
        self.listenRtp()
   
    def sendAliveSignal(self):
        """Send alive signal."""
        while True:
            print("Enviei")
            host_name = socket.gethostname()
            print("Hostname :  ",host_name)
            self.aliveSignalSocket.sendto(str("Alive " + host_name).encode(), ('10.0.0.10', 25000))
            sleep(1)


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
            self.rtpSocket.bind(('0.0.0.0', 25000))
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

    for x in range(1,6):
        try:
            destPort.append(sys.argv[x])
            print(destPort)
        except:
            break
    
    #arg1 é a porta que recebe

    Router(destPort)
    #openRtpPort()

    #threading.Thread(target=listenRtp).start(
    #print("REceve data")
    #listenRtp()
    #print("SEnding data")
    #sendRtp()

    #rtpSocket.shutdown(socket.SHUT_RDWR)
    #rtpSocket.close()