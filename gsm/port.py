#! /usr/bin/env python
#coding=utf-8
import time

class PortBase:
	def __init__(self):
		self.buf = ''
		self.last_write = self.last_read = time.time()

	def quiet_time(self):
		return time.time() - max(self.last_write, self.last_read)
		
	def pop(self, size):
		length = min(size, len(self.buf))
		result = self.buf[:length]
		self.buf = self.buf[length:]
		return result
		
	def port_read(self):
		buf = self.dev_read()
		if len(buf) > 0:
			self.last_read = time.time()
			self.buf += buf
		
	def port_write(self, buf):
		self.last_write = time.time()
		return self.dev_write(buf)

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
		return self.port_write(buf)

import socket
import telnetlib  
class Telnet(PortBase):
	def __init__(self, host, port):
		PortBase.__init__(self)
		self.port = telnetlib.Telnet(host, port = port, timeout = 1)
		
	def dev_read(self):
		buf = ''
		try:
			buf = self.port.read_some()
		except socket.timeout:
			pass
		return buf
		
	def dev_write(self, buf):
		return self.port.write(buf)

import serial
class Serial(PortBase):
	def __init__(self, dev):
		self.port = serial.Serial(dev, 9600, timeout = 1)

	def dev_read(self):
		return self.port.read(min(1, self.port.inWaiting()))

	def dev_write(self, buf):
		return self.port.write(buf)
