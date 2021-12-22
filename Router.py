from tkinter import *
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
import sys
from time import sleep
from RtpPacket import RtpPacket
import json 
import copy

class Router:	

    routingTable = {}
    sendrtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    aliveSignalSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    getRoutingTableSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendRoutingTableSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data = 0

    def __init__(self):
        self.rtspSeq = 0
        self.sessionId = 0
        self.frameNbr = 0
        t=threading.Thread(target=self.sendAliveSignal, args=())
        t.start()
        getRoutingTable = threading.Thread(target=self.getRoutingTable, args=())
        getRoutingTable.start()
        
        sendingRoutingTable = threading.Thread(target=self.SendRoutingTable, args=())
        sendingRoutingTable.start()
        
        
        self.openRtpPort()
        self.listenRtp()
   

    def SendRoutingTable(self):
        """Send alive signal."""
        while True:
            print("Enviei a routing table")


            for path in self.routingTable:
                pathToSend=copy.deepcopy(self.routingTable)
                #print(pathToSend)
                
                #print(pathToSend[path][0])
                destIP = pathToSend[path][0]
                #print(self.destIP)
                pathToSend[path].pop(0)

                for otherPaths in list(pathToSend):
                    #print(otherPaths)
                    if path!=otherPaths:
                        #print("ENtrei uma vez")
                        pathToSend.pop(otherPaths)
                #print(pathToSend)
                
                routingTable = str.encode(json.dumps(pathToSend)) #data serialized

                #sendRoutingTable = threading.Thread(target=self.sendRTable, args=(routingTable, x))
                #sendRoutingTable.start()
                
                self.sendRoutingTableSocket.sendto(routingTable, (str(destIP), 24998))

            sleep(2)
    
    def sendRTable(self, data, dest):
        print("Enviei")
        print(data)
        self.sendRoutingTableSocket.sendto(data, (str(dest), 24998))

    def getRoutingTable(self):
        print("Recebi a routing table")
        while True:
            try:
                print("entrei aqui")
                data = self.getRoutingTableSocket.recv(20480)
                
                UpdatedRoutingTable=json.loads(data.decode())
                #print(UpdatedRoutingTable)
                

                for key in UpdatedRoutingTable:
                    #print(key)
                    if key in self.routingTable:
                        self.routingTable[key]=UpdatedRoutingTable[key]
                    else:
                        self.routingTable.update(UpdatedRoutingTable)
                
                #self.RoutingTable.update(teste)
                #print(self.routingTable)
            except:
                print("Erro ao ler do getROutingTable")
                
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
                #print(self.data)
                for x in self.routingTable:
                    destIP=self.routingTable[x][0]
                    t=threading.Thread(target=self.sendRtp, args=(destIP,))
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


        try:
            # Bind the socket to the address using the RTP port
            self.getRoutingTableSocket.bind(('0.0.0.0', 24998))
            print('\nBind \n')
        except:
            tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT for ROuting Table')

    def sendRtp(self, destIP):
        """Send RTP packets over UDP."""
        #print(self.data)
        if self.data:
            print("Sending")
            

            self.sendrtpSocket.sendto(self.data, (destIP, 25000))







if __name__ == "__main__":

    #arg1 é a porta que recebe

    Router()
    #openRtpPort()

    #threading.Thread(target=listenRtp).start(
    #print("REceve data")
    #listenRtp()
    #print("SEnding data")
    #sendRtp()

    #rtpSocket.shutdown(socket.SHUT_RDWR)
    #rtpSocket.close()