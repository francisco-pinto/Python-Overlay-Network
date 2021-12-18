import sys, socket

from random import randint
import sys, traceback, threading, socket
from time import sleep
from xml.dom import minidom

from VideoStream import VideoStream
from RtpPacket import RtpPacket

class Node:
	ip=0
	port=0
	online=0

	def __init__(self, ip, port):
		self.ip=ip
		self.port=port		
class Servidor:	

	clientInfo = {}
	nodes = []
	maintenanceRTPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def __init__(self):
		#self.rtpSocket.settimeout(15)
		self.GetNetworkTopology()
		maintenance=threading.Thread(target=self.TopologyMaintenance, args=())
		maintenance.start()
		
	def GetNetworkTopology(self):
		file = minidom.parse('Topologia.xml')

		nodes = file.getElementsByTagName('node')

		for node in nodes:
			interfaces = node.getElementsByTagName('interface')
			
			for interface in interfaces:
				ips=interface.getElementsByTagName('ip')
				ports=interface.getElementsByTagName('port')
				
				for ip in ips:
					print("ip:")
					print(ip.firstChild.data)
				
				for port in ports:
					print("port:")
					print(port.firstChild.data)
				
				nodes.append(Node(ip, port))

		#Estamos com erro num getlement by name
		#Precisamos de colocar uma estratégia dos nśo
		
		# one specific item attribute
		#for node in nodes:
			#print("IP:")
			#print(node.ip)
			#print("PORT:")
			#print(node.port)
			#print(node.online)

	def TopologyMaintenance(self):
		while True:
			nodeData = self.maintenanceRTPSocket.recv(20480)
			print(nodeData)
			sleep(1)

	def sendRtp(self):
		"""Send RTP packets over UDP."""
		while True:
			self.clientInfo['event'].wait(0.05)
			
			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo['event'].isSet():
				break
				
			data = self.clientInfo['videoStream'].nextFrame()
			if data:
				frameNumber = self.clientInfo['videoStream'].frameNbr()
				try:
					address = self.clientInfo['rtpAddr']
					port = int(self.clientInfo['rtpPort'])
					packet =  self.makeRtp(data, frameNumber)
					self.clientInfo['rtpSocket'].sendto(packet,(address,port))
				except:
					print("Connection Error")
					print('-'*60)
					traceback.print_exc(file=sys.stdout)
					print('-'*60)
		# Close the RTP socket
		self.clientInfo['rtpSocket'].close()
		print("All done!")

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

	
	def main(self):
		try:
			# Get the media file name
			filename = sys.argv[1]
			print("Using provided video file ->  " + filename)
		except:
			print("[Usage: Servidor.py <videofile>]\n")
			filename = "movie.Mjpeg"
			print("Using default video file ->  " + filename)

		# videoStram
		self.clientInfo['videoStream'] = VideoStream(filename)
		# socket
		self.clientInfo['rtpPort'] = 25000
		self.clientInfo['rtpAddr'] = socket.gethostbyname('10.0.0.1')
		print("Sending to Addr:" + self.clientInfo['rtpAddr'] + ":" + str(self.clientInfo['rtpPort']))
		# Create a new socket for RTP/UDP
		self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.clientInfo['event'] = threading.Event()
		self.clientInfo['worker']= threading.Thread(target=self.sendRtp)
		self.clientInfo['worker'].start()

if __name__ == "__main__":

	(Servidor()).main()




