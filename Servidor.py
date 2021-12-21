import sys, socket

from random import randint
import sys, traceback, threading, socket
from tkinter.constants import E
from time import sleep
from xml.dom import minidom

from VideoStream import VideoStream
from RtpPacket import RtpPacket

from collections import defaultdict

class Graph(object):
    def __init__(self, nodes, init_graph):
        self.nodes = nodes
        self.graph = self.construct_graph(nodes, init_graph)
        
    def construct_graph(self, nodes, init_graph):
        '''
        This method makes sure that the graph is symmetrical. In other words, if there's a path from node A to B with a value V, there needs to be a path from node B to node A with a value V.
        '''
        graph = {}
        for node in nodes:
            graph[node] = {}
        
        graph.update(init_graph)
        
        for node, edges in graph.items():
            for adjacent_node, value in edges.items():
                if graph[adjacent_node].get(node, False) == False:
                    graph[adjacent_node][node] = value
                    
        return graph
    
    def get_nodes(self):
        "Returns the nodes of the graph."
        return self.nodes
    
    def get_outgoing_edges(self, node):
        "Returns the neighbors of a node."
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False) != False:
                connections.append(out_node)
        return connections
    
    def value(self, node1, node2):
        "Returns the value of an edge between two nodes."
        return self.graph[node1][node2]
	
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

	def dijkstra_algorithm(self, graph, start_node):
		unvisited_nodes = list(graph.get_nodes())
		shortest_path = {}
		previous_nodes = {}

		# We'll use max_value to initialize the "infinity" value of the unvisited nodes   
		max_value = sys.maxsize

		for node in unvisited_nodes:
			shortest_path[node] = max_value
		# However, we initialize the starting node's value with 0   
		shortest_path[start_node] = 0

		while unvisited_nodes:
			current_min_node = None
			
			for node in unvisited_nodes: # Iterate over the nodes
				if current_min_node == None:
					current_min_node = node
				elif shortest_path[node] < shortest_path[current_min_node]:
					current_min_node = node
					
			# The code block below retrieves the current node's neighbors and updates their distances
			neighbors = graph.get_outgoing_edges(current_min_node)
			
			for neighbor in neighbors:
				tentative_value = shortest_path[current_min_node] + graph.value(current_min_node, neighbor)
				
				#print(tentative_value)
				
				if tentative_value < shortest_path[neighbor]:
					shortest_path[neighbor] = tentative_value
					# We also update the best path to the current node
					previous_nodes[neighbor] = current_min_node
			
			print(current_min_node)
			unvisited_nodes.remove(current_min_node)
		

		return previous_nodes, shortest_path









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

		previous_nodes, shortest_path = self.dijkstra_algorithm(graph, "n1")

		self.print_result(previous_nodes, shortest_path, "n1", "n2")



	def print_result(self, previous_nodes, shortest_path, start_node, target_node):
		path = []
		node = target_node

		while node != start_node:
			path.append(node)
			node = previous_nodes[node]
	
		# Add the start node manually
		path.append(start_node)
		
		print("We found the following best path with a value of {}.".format(shortest_path[target_node]))
		print(" -> ".join(reversed(path)))

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




