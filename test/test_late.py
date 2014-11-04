#! /usr/bin/env python
#coding=utf-8

import unittest

from late import SmsHandle
from gsm.daemon import DAEMON
from gsm.gsm0705 import GSM0705

class MyDaemon(DAEMON):
	def __init__(self):
		DAEMON.__init__(self, None)

	def add_event_handle(self, handle):
		self.event_handle = handle

class MyGSM0705(GSM0705):
	def __init__(self):
		self.list_delete = []
		self.list_send = []

	def delete(self, position):
		print 'del', pos
		self.list_delete.append(position)

	def send(self, to, ctx):
		self.list_delete.append((to, ctx))	

class MySmsHandle(SmsHandle):
		pass

class TestSmsHandle(unittest.TestCase):
	def setUp(self):
		self.sms = MyGSM0705()
		self.daemon = MyDaemon()
		
	def test_sms_proc(self):
		sms_handle = MySmsHandle(self.daemon, self.sms)
		where, who, when, what = (1, '10086', '2014-10-21 15:10:18+08:00', 'punch,10012345,password')
		sms_handle.execute(where, who, when, what)

		

if __name__ == '__main__':
	unittest.main()
