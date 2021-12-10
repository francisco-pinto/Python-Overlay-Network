from tkinter import *
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

class Router:	
    sendrtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = 0

    def __init__(self):
        self.rtspSeq = 0
        self.sessionId = 0
        self.frameNbr = 0
        self.openRtpPort()
        listen = threading.Thread(target=self.listenRtp)
        send = threading.Thread(target=self.sendRtp)

        listen.start()
        send.start()
        #self.listenRtp()
        #self.sendRtp()


    def listenRtp(self):				
        """Listen for RTP packets."""
        print(self.rtpSocket.gettimeout())
        while True:
            try:
                self.data = self.rtpSocket.recv(20480)
                #dados = data
                if self.data:
                    self.rtpPacket = RtpPacket()
                    self.rtpPacket.decode(self.data)   

                currFrameNbr = self.rtpPacket.seqNum()
                print("Current Seq Num: " + str(currFrameNbr))
                                    
                if currFrameNbr > self.frameNbr: # Discard the late packet
                    self.frameNbr = currFrameNbr           
            except:
                print("saiu do loop")
                break    

                    
        
    def openRtpPort(self):
        """Open RTP socket binded to a specified port."""
        # Create a new datagram socket to receive RTP packets from the server
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Set the timeout value of the socket to 0.5sec
        self.rtpSocket.settimeout(5)
        
        try:
            # Bind the socket to the address using the RTP port
            self.rtpSocket.bind(('10.0.0.1', 25000))
            print('\nBind \n')
        except:
            tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT')



    def makeRtp(self, payload, frameNbr):
        """RTP-packetize the video data."""
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        pt = 26 # MJPEG type
        seqnum = frameNbr
        ssrc = 0

        rtpPacket = RtpPacket()

        rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
        print("Encoding RTP Packet: " + str(seqnum))

        return rtpPacket.getPacket()



    def sendRtp(self):
        """Send RTP packets over UDP."""
        print(self.data)
        while True:
            if self.data:
                print("Sending")
                packet =  self.makeRtp(self.data, self.frameNbr)

                #self.rtspSocket.sendto(packet, ('10.0.1.20', 25000))
                self.sendrtpSocket.sendto(packet, ('10.0.2.20', 25000))







if __name__ == "__main__":
    
    Router()
    #openRtpPort()

    #threading.Thread(target=listenRtp).start(
    #print("REceve data")
    #listenRtp()
    #print("SEnding data")
    #sendRtp()

    #rtpSocket.shutdown(socket.SHUT_RDWR)
    #rtpSocket.close()