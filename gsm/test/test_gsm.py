#! /usr/bin/env python
#coding=utf-8

from gsm import GSM, GSM0705
import unittest

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

class TestCmgR(unittest.TestCase):
	def setUp(self):
		self.port = MockPort(self)
		self.gsm = GSM(self.port)
		self.sms = GSM0705(self.gsm)
		
	def test_read(self):
		self.port.mock_put_read('AT+CMGF=0\r\n')
		self.port.mock_put_read('OK\r\n')
		self.port.mock_put_read('AT+CMGR=1\r\n')
		self.port.mock_put_read('+CMGR: 1,"",142\r\n')
		self.port.mock_put_read('0891683108200545F6640C980156184501300004410122212084237B0605040B8423F04006246170706C69636174696F6E2F766E642E7761702E6D6D732D6D65737361676500B487AF848C8298564F78614251464B4F344643008D9083687474703A2F2F3232312E3133312E3132382E3132392F564F78614251464B4F344643008805810302CA0D8907803132333731008A808E02CD7E\r\n')
		self.port.mock_put_read('\r\n')
		self.port.mock_put_read('OK\r\n')
		sms = self.sms.read(1)
		where, when, what = sms
		self.assertEqual(where, '106581541003')
		self.assertEqual(str(when), '2014-10-22 12:02:48+08:00')
		self.assertEqual(what, u'\x06\x05\x04\x0b\x84#\xf0@\x06$application/vnd.wap.mms-message\x00\xb4\x87\xaf\x84\x8c\x82\x98VOxaBQFKO4FC\x00\x8d\x90\x83http://221.131.128.129/VOxaBQFKO4FC\x00\x88\x05\x81\x03\x02\xca\r\x89\x07\x8012371\x00\x8a\x80\x8e\x02\xcd~')
		self.assertEqual('AT+CMGF=0\r\nAT+CMGR=1\r\n', self.port.mock_get_write())

if __name__ == '__main__':
	unittest.main()
