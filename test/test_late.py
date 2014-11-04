#! /usr/bin/env python
#coding=utf-8

import unittest

from late import SmsHandle
from gsm.gsm import GSM
from gsm.gsm0705 import GSM0705
from gsm.daemon import DAEMON

class MyGSM(GSM):
	def __init__(self):
		pass

	def read_event(self):
		return ''

class MyGSM0705(GSM0705):
	def __init__(self):
		self.list_delete = []
		self.list_send = []

	def delete(self, position):
		self.list_delete.append(position)

	def send(self, to, ctx):
		self.list_send.append((to, ctx))	

class MySmsHandle(SmsHandle):
	def __init__(self, daemon, sms):
		SmsHandle.__init__(self, daemon, sms)
		self.CMD = {'punch': self.punch}
		self.punch = []
		self.punch_result = []

	def add_cmd_result(self, result):
		self.punch_result.append(result)

	def punch(self, cmd, arg):
		self.punch.append((cmd, arg))
		return self.punch_result.pop(0)

class TestSmsHandle(unittest.TestCase):
	def setUp(self):
		self.gsm = MyGSM()
		self.sms = MyGSM0705()
		self.daemon = DAEMON(self.gsm)
		
	def test_sms_punch(self):
		sms_handle = MySmsHandle(self.daemon, self.sms)
		where, who, when, what = (1, u'10086', u'2014-10-21 15:10:18+08:00', u'punch,10012345,password')
		sms_handle.add_cmd_result(u'failed.')
		sms_handle.execute(where, who, when, what)
		self.daemon.run(1)
		self.assertEqual(u'punch:10012345,password', ';'.join(map(':'.join, sms_handle.punch)))
		self.assertEqual([1], self.sms.list_delete)
		self.assertEqual(u'10086,punch->failed.', ';'.join(map(','.join, self.sms.list_send)))

if __name__ == '__main__':
	unittest.main()
