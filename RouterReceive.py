from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

class RouterReceive:
	
	# Initiation..
	def __init__(self, addr, port):
		self.addr = addr
		self.port = int(port)
		self.openRtpPort()
		self.listenRtp()

	def listenRtp(self):		
		"""Listen for RTP packets."""
		print("Start Listening")
		while True:
			data = self.rtpSocket.recv(20480)
			try:
				if data:
					rtpPacket = RtpPacket()
					decoded_data = rtpPacket.decode(data)
			except:
				break
			
			return decoded_data

	
				
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		# Create a new datagram socket to receive RTP packets from the server
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		# Set the timeout value of the socket to 0.5sec
		self.rtpSocket.settimeout(0.5)
		
		try:
			# Bind the socket to the address using the RTP port
			self.rtpSocket.bind((self.addr, self.port))
			print('\nBind \n')
		except:
			tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)
