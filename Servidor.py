import sys, socket

from random import randint
import sys, traceback, threading, socket
from tkinter.constants import E
from time import sleep
from xml.dom import minidom

from VideoStream import VideoStream
from RtpPacket import RtpPacket

from Graph import Graph
from collections import defaultdict


	
class Interface:
	ip=0
	port=0

	def __init__(self, ip, port):
		self.ip=ip
		self.port=port

class Connection:
	fromNode=0
	fromIP=0
	toNode=0
	toIP=0

	def __init__(self, fromNode, fromIP, toNode, toIP):
		self.fromNode=fromNode
		self.fromIP=fromIP
		self.toNode=toNode
		self.toIP=toIP

class Node:
	id=0
	interfaces=[]
	connections=[]
	aliveCount=0
	online=0

	def __init__(self, id, online):
		self.id=id	
		self.online=1
		self.aliveCount=3
		self.connections=[]
		self.interfaces=[]

	def addConnection(self, fromNode, fromIP, toNode, toIP):
		self.connections.append(Connection(fromNode, fromIP, toNode, toIP))
	
	def addInterface(self, ip, port):
		self.interfaces.append(Interface(ip, port))

class Servidor:	

	clientInfo = {}
	nodes = []
	maintenanceSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def __init__(self):
		self.GetNetworkTopology()
		self.CalculateShortestPath()
		self.openRouterPort()
		maintenance=threading.Thread(target=self.TopologyMaintenance, args=())
		maintenance.start()
		print("inicio")


	def CalculateShortestPath(self):
		
		
		nodeId=[]

		init_graph = defaultdict(dict)

		for node in self.nodes:
			nodeId.append(node.id)
			init_graph[node.id] = {}

		for node in self.nodes:
			if node.online==1:
				
				for connections in node.connections:
					#print("Adding connections")
					#print(connections.fromNode)
					#print(connections.toNode)
					node_number1=connections.fromNode
					node_number2=connections.toNode
					#print("Numero 1")
					#print(node_number1)

					#print("Numero 2")
					#print(node_number2)
					init_graph[node_number1][node_number2] = 1
			
		
		graph = Graph(nodeId, init_graph)

		previous_nodes, shortest_path = graph.dijkstra_algorithm("n1")

		graph.print_result(previous_nodes, shortest_path, "n1", "n5")

	def GetNetworkTopology(self):
		file = minidom.parse('Topologia.xml')

	#_______________________________________________________
	#GET NODES SPECS
		nodes = file.getElementsByTagName('node')

		for node in nodes:
			Id = node.attributes['id'].value
			
			#Create node
			no = Node(Id, 0)

	#_______________________________________________________	
	#GET INTERFACES

			interfaces = node.getElementsByTagName('interface')
	
			for interface in interfaces:
				ips=interface.getElementsByTagName('ip')
				ports=interface.getElementsByTagName('port')
				
				for ip in ips:
					Ip=ip.firstChild.data
				
				for port in ports:
					Port=port.firstChild.data

				#Add all interfaces to node
				no.addInterface(Ip, Port)

	#_______________________________________________________		
	#GET LINKS
			fromNode=0
			fromIP=0
			toNode=0
			toIP=0
			links = file.getElementsByTagName('link')

			for link in links:
				froms = link.getElementsByTagName('from')
		
				for fromvar in froms:
					fromNode =fromvar.attributes['node'].value
					fromIP = fromvar.attributes['ip'].value
					#print(fromIP)
				tos = link.getElementsByTagName('to')

				for to in tos:
					toNode = to.attributes['node'].value
					toIP = to.attributes['ip'].value
				
				no.addConnection(fromNode, fromIP, toNode, toIP)
			

			#Add node to list of nodes
			self.nodes.append(no)	

		#for node in self.nodes:
		#	print(node.id)
		#	for connection in node.connections:
		#		print(connection.fromIP)
		

	def shortest(self, v, path):
		"""make shortest path from v.previous"""
		if v.previous:
			path.append(v.previous.get_id())
			self.shortest(v.previous, path)
		return

	def TopologyMaintenance(self):
		"""Check what nodes still online"""
		while True:
			
			#for node in self.nodes:
				#print(node.online)

			try:
				print("A ouvir")
				nodeData = self.maintenanceSocket.recv(20480)
				#print(nodeData)

				nodeDataId = nodeData.decode().replace("Alive ", "")
				#print(nodeDataId)
				for node in self.nodes:
					#Verify if online nodes are disconnected
					#Basically if in 3 secs they dont send message, they are disconnected 
					if node.id!=nodeDataId and node.online==1:
						if node.aliveCount==0:
							node.aliveCount=3
							node.online=0
							self.CalculateShortestPath()
						else:
							node.aliveCount=node.aliveCount-1

					if node.id==nodeDataId and node.online==0:
						node.online=1
						#Every time a new node is connected we need to
						#Recalculate the shortestPath
						try:
							self.CalculateShortestPath()
						except Exception as e:
							print(e)

				
			except:
				print("Tentou")
			
			sleep(1)

	def openRouterPort(self):
		"""Open RTP socket binded to a specified port."""
		# Create a new datagram socket to receive RTP packets from the server
		self.maintenanceSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# Set the timeout value of the socket to 0.5sec
		self.maintenanceSocket.settimeout(15)

		try:
			# Bind the socket to the address using the RTP port
			self.maintenanceSocket.bind(('0.0.0.0', 25000))
			print('\nBind \n')
		except:
			tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT')

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




