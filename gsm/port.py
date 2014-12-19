#! /usr/bin/env python
#coding=utf-8
import time

class PortBase:
	def __init__(self):
		self.buf = ''
		self.last_write = self.last_read = 0
		self.connected = False
		self.connect()

	def connect(self):
		self.connected = self.dev_connect()

	def close(self):
		self.connected = False
		self.dev_close()

	def quiet_time(self):
		return time.time() - max(self.last_write, self.last_read)
		
	def pop(self, size):
		length = min(size, len(self.buf))
		result = self.buf[:length]
		self.buf = self.buf[length:]
		return result
		
	def port_read(self):
		if self.connected:
			buf = self.dev_read()
			if len(buf) > 0:
				self.last_read = time.time()
				self.buf += buf
		else:
			time.sleep(1)
		
	def port_write(self, buf):
		if self.connected:
			self.last_write = time.time()
			self.dev_write(buf)
		else:
			time.sleep(1)

	def read(self, size = 1):
		if size > len(self.buf):
			self.port_read()
		return self.pop(size)

	def readline(self):
		size = self.buf.find('\n')
		if size == -1:
			self.port_read()
			size = self.buf.find('\n')
			
		if size == -1:
			size = len(self.buf)
		else:
			size = size + 1
		return self.pop(size)

	def write(self, buf):
		self.port_write(buf)

import socket
import telnetlib  
class Telnet(PortBase):
	def __init__(self, host, port):
		self.__host = host
		self.__port = port
		PortBase.__init__(self)

	def dev_close(self):
		self.port.close()

	def dev_connect(self):
		self.port = telnetlib.Telnet(self.__host, port = self.__port, timeout = 1)
		return True

	def dev_read(self):
		buf = ''
		try:
			buf = self.port.read_some()
		except socket.timeout:
			pass
		return buf
		
	def dev_write(self, buf):
		try:
			self.port.write(buf)
		except socket.error:
			self.close()

import serial
class Serial(PortBase):
	def __init__(self, dev):
		self.__dev = dev
		PortBase.__init__(self)

	def dev_close(self):
		self.port.close()

	def dev_connect(self):
		self.port = serial.Serial(self.__dev, 9600, timeout = 1)
		return True

	def dev_read(self):
		return self.port.read(min(1, self.port.inWaiting()))

	def dev_write(self, buf):
		self.port.write(buf)
