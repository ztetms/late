#! /usr/bin/env python
#coding=utf-8

import serial

class Serial():
	def __init__(self, dev):
		self.port = serial.Serial(dev)

	def read(self, size = 1):
		return self.port.read(size)

	def readline(self):
		return self.port.readline()

	def write(self, buf):
		return self.port.write(buf)
