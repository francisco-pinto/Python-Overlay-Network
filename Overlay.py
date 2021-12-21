
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
        self.online=online
        self.aliveCount=3
        self.connections=[]
        self.interfaces=[]

    def addConnection(self, fromNode, fromIP, toNode, toIP):
        self.connections.append(Connection(fromNode, fromIP, toNode, toIP))

    def addInterface(self, ip, port):
        self.interfaces.append(Interface(ip, port))