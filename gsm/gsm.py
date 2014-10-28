#! /usr/bin/env python
#coding=utf-8

import sys
import time
import serial
import string
import shlex

import pdu

class Serial():
	def __init__(self, dev):
		self.port = serial.Serial(dev)

	def read(self, size = 1):
		return self.port.read(size)

	def readline(self):
		return self.port.readline()

	def write(self, buf):
		return self.port.write(buf)

class GSM:
	def __init__(self, port, event_handle = []):
		self.port = port

	def send_and_check_echo(self, line):
		self.port.write(line)
		read = self.port.read(len(line))
		return read == line
		
	def read_event(self):
		return self.port.readline()

	def read_until(self, expect):
		result = []
		while len(result) == 0 \
			or len(result[-1]) > 0 \
			and not result[-1].rstrip('\r\n') in expect:
			result.append(self.port.readline())
		return ''.join(result)

	def send_cmd(self, cmd, until = []):
		result = None
		if self.send_and_check_echo(cmd):
			result = self.read_until(until)
		return result

	@staticmethod
	def at_cmd(cmd = ''):
		return 'AT%s\r\n' % cmd

	@staticmethod
	def format_response(response, expect):
		result = None, None
		if response != None:
			lines = response.rstrip('\r\n').split('\r\n')
			if len(lines) > 0 and lines[-1] in expect:
				result = lines[-1], lines[:-1]
			else:
				result = None, lines
		return result

	def test(self):
		expect = ['OK', ]
		response = self.send_cmd(self.at_cmd(), expect)
		result, context = self.format_response(response, expect)
		return result == 'OK'

class GSM0705:
	CMGF_PDU = 0
	CMGF_TEXT = 1
	def __init__(self, gsm):
		self.gsm = gsm

	def config(self, mode):
		assert(mode == self.CMGF_PDU or mode == self.CMGF_TEXT)
		expect = ['OK', 'ERROR']
		response = self.gsm.send_cmd(self.gsm.at_cmd('%s=%d' % ('+CMGF', mode)), expect)
		result, context = self.gsm.format_response(response, expect)
		return result == 'OK'
		
	def read(self, position):
		result = None
		self.config(self.CMGF_PDU)
		expect = ['OK', 'ERROR']
		response = self.gsm.send_cmd(self.gsm.at_cmd('%s=%d' % ('+CMGR', position)), expect)
		result, context = self.gsm.format_response(response, expect)
		print context
		if result == 'OK':
			length, index = reduce(max, zip(map(len, context), range(len(context))))
			csca, tpdu = pdu.parse(context[index])
			result = tpdu.oa, tpdu.scts, ''.join(map(unichr, tpdu.ud))
		return result