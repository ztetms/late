#! /usr/bin/env python
#coding=utf-8

import shlex
from punch import Punch
from gsm.gsm import GSM
from gsm.gsm0705 import GSM0705
from gsm.daemon import DAEMON
from gsm.port import Serial

def punch(user, passwd):
	punch = Punch()
	print 'punch', user, '*' * len(passwd)
	if punch.login(user, passwd):
		result = punch.punch()
	else:
		result = 'login failed'
	return result

def sms_punch(cmd, arg):
	login = arg.split(',', 1)
	if len(login) == 2:
		usr, pwd = login
		result = punch(usr, pwd)
	else:
		result = 'parameter error'
		
	return result

CMD = {
	'PUNCH': sms_punch,
}

def sms_handle(who, when, what):
	sms = tuple(what.split(',', 1))
	cmd = sms[0]
	context = sms[1] if len(sms) > 1 else ''
	
	if cmd in CMD:
		result = CMD[cmd](cmd, context)
		print who, result
		#sim.sms_write(who, result)
	else:
		print 'unknown command %s' % cmd

def start_daemon(dev):
	self.port = Serial(dev)
	self.gsm = GSM(self.port)
	self.sms = GSM0705(self.gsm)
	self.daemon = Daemon(self.gsm, [self.sms.GSM0705_CMTI_HANDLE(sms_handle),])

if __name__ == '__main__':
	start_daemon('COM1')
	
