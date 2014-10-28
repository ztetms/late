#! /usr/bin/env python
#coding=utf-8

import unittest
from gsm.gsm import GSM
from gsm.gsm0705 import GSM0705
from gsm.test.mock_port import MockPort

SMS_READ_1 = (
		'AT+CMGF=0\r\n',
		'OK\r\n',
		'AT+CMGR=1\r\n',
		'+CMGR: 1,"",142\r\n',
		'0891683108200545F6640C980156184501300004410122212084237B0605040B8423F04006246170706C69636174696F6E2F766E642E7761702E6D6D732D6D65737361676500B487AF848C8298564F78614251464B4F344643008D9083687474703A2F2F3232312E3133312E3132382E3132392F564F78614251464B4F344643008805810302CA0D8907803132333731008A808E02CD7E\r\n',
		'\r\n',
		'OK\r\n')

class TestCmgR(unittest.TestCase):
	def setUp(self):
		self.port = MockPort(self)
		self.gsm = GSM(self.port)
		self.sms = GSM0705(self.gsm)
		
	def test_read(self):
		for line in SMS_READ_1:
			self.port.mock_put_read(line)
		sms = self.sms.read(1)
		where, when, what = sms
		self.assertEqual(where, '106581541003')
		self.assertEqual(str(when), '2014-10-22 12:02:48+08:00')
		self.assertEqual(what, u'\x06\x05\x04\x0b\x84#\xf0@\x06$application/vnd.wap.mms-message\x00\xb4\x87\xaf\x84\x8c\x82\x98VOxaBQFKO4FC\x00\x8d\x90\x83http://221.131.128.129/VOxaBQFKO4FC\x00\x88\x05\x81\x03\x02\xca\r\x89\x07\x8012371\x00\x8a\x80\x8e\x02\xcd~')
		self.assertEqual('AT+CMGF=0\r\nAT+CMGR=1\r\n', self.port.mock_get_write())

class TestCmti(unittest.TestCase):
	def setUp(self):
		self.record_sms = []
		self.port = MockPort(self)
		self.gsm = GSM(self.port)
		self.sms = GSM0705(self.gsm)

	def record(self, where, when, what):
		self.record_sms.append((where, when, what))
		
	def test_cmti_ok(self):
		for line in SMS_READ_1:
			self.port.mock_put_read(line)
		handle = self.sms.GSM0705_CMTI_HANDLE(self.record)
		cmds = handle('+CMTI: "SM",1,"MMS PUSH"')
		self.assertEqual(1, len(cmds))
		for cmd in cmds:
			cmd()
		self.assertEqual(1, len(self.record_sms))
		self.assertEqual('106581541003', self.record_sms[0][0])

if __name__ == '__main__':
	unittest.main()
