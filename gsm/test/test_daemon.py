#! /usr/bin/env python
#coding=utf-8

import unittest
from gsm.gsm import GSM
from gsm.daemon import DAEMON
from gsm.test.mock_port import MockPort

class MyDaemon(DAEMON):
	def run(self, times = 1):
		for i in range(times):
			self.engine.add_command(self.IDLE())
		self.engine.add_command(self.STOP())
		self.engine.run()
		
class TestEngine(unittest.TestCase):
	def setUp(self):
		self.record_event = []
		self.port = MockPort(self)
		self.gsm = GSM(self.port)
		self.daemon = MyDaemon(self.gsm, [self.record,])
		
	def record(self, line):
		def execute():
			self.record_event.append(line)
		return [execute,]

	def test_event(self):
		self.port.mock_put_read('+CMTI: "SM",1,"MMS PUSH"\r\n')
		self.port.mock_put_read('')
		self.port.mock_put_read('')
		self.daemon.run(1)
		output = self.record_event
		self.assertEqual(['+CMTI: "SM",1,"MMS PUSH"\r\n',], self.record_event)

	def test_events(self):
		events = [
				'+CMTI: "SM",1,"MMS PUSH"\r\n',
				'+CMTI: "SM",2,"MMS PUSH"\r\n',
				'+CMTI: "SM",3,"MMS PUSH"\r\n']
		for event in events:
			self.port.mock_put_read(event)
			self.port.mock_put_read('')
			self.port.mock_put_read('')
		self.daemon.run(10)
		self.assertEqual(events, self.record_event)

if __name__ == '__main__':
	unittest.main()
