#! /usr/bin/env python
#coding=utf-8

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
