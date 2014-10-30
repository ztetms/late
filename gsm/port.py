#! /usr/bin/env python
#coding=utf-8

import serial
import socket

class Serial():
	def __init__(self, dev):
		self.port = serial.Serial(dev, 9600, timeout = 1)

	def read(self, size = 1):
		return self.port.read(size)

	def readline(self):
		return self.port.readline()

	def write(self, buf):
		return self.port.write(buf)

import telnetlib  

class Telnet():
	def __init__(self, host, port):
		self.port = telnetlib.Telnet(host, port = port, timeout = 1)
		self.buf = ''
		
	def __read(self):
		try:
			self.buf += self.port.read_some()
		except socket.timeout:
			pass
		
	def pop(self, size):
		length = min(size, len(self.buf))
		result = self.buf[:length]
		self.buf = self.buf[length:]
		return result

	def read(self, size = 1):
		if size > len(self.buf):
			self.__read()
		return self.pop(size)

	def readline(self):
		size = self.buf.find('\n')
		if size == -1:
			self.__read()
			size = self.buf.find('\n')
			
		if size == -1:
			size = len(self.buf)
		else:
			size = size + 1
		return self.pop(size)

	def write(self, buf):
		return self.port.write(buf)
