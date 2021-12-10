from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtpPacket import RtpPacket

rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class RouterSend:
    def __init__(self, data):
        self.data = data
        self.sendRtp()

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
            while True:
                if self.data:
                    print("Sending")
                    packet =  self.makeRtp(self.data, 1)

                    rtspSocket.sendto(packet, '10.0.1.20')
                    rtspSocket.sendto(packet, '10.0.2.20')