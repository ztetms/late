#! /usr/bin/env python
#coding=utf-8

import unittest
from gsm.gsm import GSM
from gsm.test.mock_port import MockPort

class MockPort():
	def __init__(self, test):
		self.__test = test
		self.__read = []
		self.__write = []

	def read(self, size = 1):
		line = self.__read.pop(0) if len(self.__read) > 0 else ''
		if len(line) > size:
			self.__read.insert(0, line[size:])
		return line[:size]

	def readline(self):
		line = self.__read.pop(0) if len(self.__read) > 0 else ''
		if '\n' in line:
			size = line.index('\n') + len('\n')
			if len(line[size:]) > 0:
				self.__read.insert(0, line[size:])
			line = line[:size]
		return line

	def write(self, string):
		self.__write.append(string)

	def mock_put_read(self, string):
		self.__read.append(string)

	def mock_get_write(self):
		return ''.join(self.__write)

class TestSendAndCheckEcho(unittest.TestCase):
	def setUp(self):
		self.port = MockPort(self)
		self.gsm = GSM(self.port)

	def test_match(self):
		self.port.mock_put_read('AT')
		self.assertTrue(self.gsm.send_and_check_echo('AT'))
		self.assertEqual(self.port.mock_get_write(), 'AT')

	def test_read_more(self):
		self.port.mock_put_read('AT\r\n\r\nOK\r\n')
		self.assertTrue(self.gsm.send_and_check_echo('AT\r\n'))

	def test_unmatch(self):
		self.port.mock_put_read('AT\r')
		self.assertFalse(self.gsm.send_and_check_echo('AT\r\n'))

class TestSendCmd(unittest.TestCase):
	def setUp(self):
		self.port = MockPort(self)
		self.gsm = GSM(self.port)

	def test_match(self):
		self.port.mock_put_read('AT+CMGS=15\r\n> ')
		self.port.mock_put_read('')
		self.assertEqual('> ', self.gsm.send_cmd('AT+CMGS=15\r\n'))
		self.assertEqual('AT+CMGS=15\r\n', self.port.mock_get_write())

	def test_multiline(self):
		self.port.mock_put_read('AT\r\n\r\nOK\r\n')
		self.port.mock_put_read('+CMTI: "SM",1,"MMS PUSH"\r\n')
		self.port.mock_put_read('')
		self.assertEqual('\r\nOK\r\n+CMTI: "SM",1,"MMS PUSH"\r\n', self.gsm.send_cmd('AT\r\n'))

	def test_with_end(self):
		self.port.mock_put_read('AT\r\n\r\nOK\r\n')
		self.port.mock_put_read('+CMTI: "SM",1,"MMS PUSH"\r\n')
		self.port.mock_put_read('')
		self.assertEqual('\r\nOK\r\n', self.gsm.send_cmd('AT\r\n', ['OK', 'ERROR']))

class TestAtOk(unittest.TestCase):
	def setUp(self):
		self.port = MockPort(self)
		self.gsm = GSM(self.port)

	def test_ok(self):
		self.port.mock_put_read('AT\r\n\r\nOK\r\n')
		self.port.mock_put_read('+CMTI: "SM",1,"MMS PUSH"\r\n')
		self.assertTrue(self.gsm.test())
		self.assertEqual('AT\r\n', self.port.mock_get_write())

	def test_no_echo(self):
		self.assertFalse(self.gsm.test())

	def test_error(self):
		self.port.mock_put_read('AT\r\n\r\nERROR\r\n')
		self.assertFalse(self.gsm.test())

if __name__ == '__main__':
	unittest.main()
