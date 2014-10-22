#! /usr/bin/env python
#coding=utf-8

import sys
import time
import serial
import string
import shlex

class Port():
	def __init__(self, dev):
		self.port = serial.Serial(dev)
		
	def writeline(self, line = ''):
		self.port.write('%s\r\n' % line)

	def readline(self):
		result = ''
		while len(result) < 2 or result[-2:] != '\r\n':
			result += self.port.readline()
		return result.rstrip('\r\n')
	
	def clear_recv_buf(self, delay = 0):
		time.sleep(delay)
		while self.port.inWaiting() > 0:
			self.port.readline()
			time.sleep(delay)
			
	def can_read(self):
		return self.port.inWaiting()
		
class EventHandle():
	def __init__(self, event):
		self.event = event

class SIM900A:
	HEX_DICT = {
			'0': 0, '1': 1, '2': 2, '3': 3,
			'4': 4, '5': 5, '6': 6, '7': 7,
			'8': 8, '9': 9, 'A': 10, 'B': 11,
			'C': 12, 'D': 13, 'E': 14, 'F': 15,
			}
	def __init__(self, dev):
		self.event = []
		self.port = Port(dev)
		self.port.writeline('AT')
		self.port.clear_recv_buf(1)
		self.event_handle = [EventSmsHandle, EventRingHandle]
	
	def get_event_handle(self, event):
		return [hdl(event) for hdl in self.event_handle if hdl.match(event)]
		
	def append_event(self, line):
		if len(line) > 0:
			event = line
			hdls = self.get_event_handle(event)
			for hdl in hdls:
				self.event.append(hdl)
			if len(hdls) == 0:
				print 'discard: %s' % line
		
	def pop_event(self):
		return self.event.pop(0)
		
	def wait_event(self):
		self.append_event(self.port.readline())
		
	def recv_all_event(self):
		while self.port.can_read() > 0:
			self.append_event(self.port.readline())
			
	def more_event(self):
		return len(self.event) > 0
		
	def event_process(self, event):
		event.handle(self)
		
		
	def send_at_cmd(self, cmd):
		full_cmd = 'AT%s' % cmd
		self.port.writeline(full_cmd)
		echo = self.port.readline()
		if not echo == full_cmd:
			print echo, ',', full_cmd	
		assert(echo == full_cmd)
		return echo == full_cmd
			
	def read_until(self, until):
		context = []
		more = True
		while more:
			line = self.port.readline()
			more = not line in until
			if more:
				context.append(line)
		return line, context
			
	def cmd(self, cmd, end):
		if self.send_at_cmd(cmd):
			result = self.read_until(end)
		else:
			sys.stderr.write('send cmd %s failed.\n' % cmd)
			result = None, None
		return result
		
	def at_test(self):
		r, c = self.cmd('', ['OK', 'ERROR'])
		return r

	@staticmethod
	def parse_notice(s):
		type, context = s.split(': ', 2)
		str = shlex.shlex(context, posix = True)
		str.whitespace = ','
		str.whitesapce_split = True
		return type, tuple(str)
		
	@staticmethod
	def sms_split(all):
		result = []
		group = []
		for line in all:
			if len(line) == 0:
				if len(group) > 0:
					result.append(group)
				group = []
			else:
				group.append(line)
		return result
	
	@classmethod
	def char_2_num(cls, char):
		return cls.HEX_DICT[char]
	
	@staticmethod
	def mul_to_one(list, multiple, num = 2):
		assert(len(list) % num == 0)
		return map(
			lambda index: reduce(lambda acc, item: acc * multiple + item,
				list[index * num:(index + 1) * num], 0),
			range(len(list) / num))
	
	@classmethod
	def convert_hex_to_unistring(cls, string):
		return ''.join(map(lambda x: unichr(x),
			cls.mul_to_one([cls.char_2_num(c) for c in string], 16, 4)))
			
	@classmethod
	def is_hex_string(cls, string):
		return all([c in cls.HEX_DICT for c in string])
	
	@classmethod
	def decode_hex_msg(cls, context):
		return  sim.convert_hex_to_unistring(context) if sim.is_hex_string(context) else context
	
	@classmethod	
	def sms_parse_cmgl_item(cls, msg):
		pre = '+CMGL: '
		assert(len(msg) == 2)
		assert(msg[0][:len(pre)] == pre)
		header = msg[0][len(pre):]
		summary = header.split(',', 4)
		data = cls.decode_hex_msg(msg[1])
		return string.atoi(summary[0]), (tuple([f.strip('"') for f in summary[2:]]), data), summary[1]
		
	def sms_parse_cmgr_item(cls, msg):
		pre = '+CMGR: '
		assert(len(msg) == 2)
		assert(msg[0][:len(pre)] == pre)
		header = msg[0][len(pre):]
		summary = header.split(',', 3)
		data = cls.decode_hex_msg(msg[1])
		return (tuple([f.strip('"') for f in summary[1:]]), data), summary[0]
		
	def sms_read_all(self):
		r, lines = self.cmd('%s=%s' % ('+CMGL', '"ALL"'), ['OK', 'ERROR'])
		msgs = self.sms_split(lines)
		msgs = [self.sms_parse_cmgl_item(msg) for msg in msgs]
		return msgs
		
	def sms_read(self, pos):
		r, lines = self.cmd('%s=%d' % ('+CMGR', pos), ['OK', 'ERROR'])
		msg = self.sms_parse_cmgr_item([line for line in lines if len(line) > 0])
		return pos, msg[0], msg[1]
		
	def run(self):
		self.run = True
		while self.run:
			if self.more_event() > 0:
				self.recv_all_event()
				self.event_process(self.pop_event())
			else:
				self.wait_event()
	
	def stop(self):
		self.run = False
	
class EventSmsHandle(EventHandle):
	@staticmethod
	def match(event):
		key = '+CMTI: '
		return event[:len(key)] == key
		
	def process(who, when, what):
		pass
		
	def handle(self, sim):
		'''
		+CMTI: "SM",1,"MMS PUSH"
		('+CMTI', ('SM', '1', 'MMS PUSH'))
		'''
		cmd, ctx = sim.parse_notice(self.event)
		assert(cmd == '+CMTI')
		pos = string.atoi(ctx[1])
		sms = sim.sms_read(pos)
		print cmd, ctx
		if sms != None:
			print sms
			index, msg, status = sms
			summary, context = msg
			sender, ignore, date = summary
			self.process(sender, date, context)
		else:
			sys.stderr.write('read sms@%d failed.' % pos)
	
class EventRingHandle(EventHandle):
	@staticmethod
	def match(event):
		return event == 'RING'
		
	def handle(self, sim):
		print 'ring'
		
if __name__ == '__main__':
	sim = SIM900A('COM1')
	sim.at_test()
	print 'read all'
	msgs = sim.sms_read_all()
	for index, msg, status in msgs:
		print index, status
		print msg[0], sim.convert_hex_to_unistring(msg[1]) if sim.is_hex_string(msg[1]) else msg[1]
	print 'read one'
	print sim.sms_read(msgs[0][0])
	raw_input('stop? ')
	sim.run()
	
