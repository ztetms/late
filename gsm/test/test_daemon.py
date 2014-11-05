#! /usr/bin/env python
#coding=utf-8

import unittest
import logging, logging.handlers

from gsm.gsm import GSM
from gsm.daemon import DAEMON
from gsm.test.mock_port import MockPort
		
class TestEngine(unittest.TestCase):
	def setUp(self):
		self.record_event = []
		self.port = MockPort(self)
		self.gsm = GSM(self.port)
		self.daemon = DAEMON(self.gsm, [self.record,])
		
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

	def test_exception_log(self):
		memory_handler = logging.handlers.MemoryHandler(100)
		log = logging.getLogger('gsm.daemon')
		log.addHandler(memory_handler)
		def div_0():
			1 / 0
		self.daemon.add_command(div_0, 0)
		self.daemon.run(0)
		log.removeHandler(memory_handler)
		log_string = '\n'.join(map(lambda log: '\n'.join(log.getMessage().split('\n')[:2]), memory_handler.buffer))
		self.assertEqual(log_string, 'Execute div_0 error.\nTraceback (most recent call last):')

if __name__ == '__main__':
	unittest.main()
