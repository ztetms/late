#! /usr/bin/env python
#coding=utf-8

import shlex
from punch import Punch
from sim import SIM900A, EventSmsHandle

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
	'SK': sms_punch,
}

def sms_handle(who, when, what):
	sms = tuple(what.split(',', 1))
	cmd = sms[0]
	context = sms[1] if len(sms) > 1 else ''
	
	if cmd in CMD:
		result = CMD[cmd](cmd, context)
		print who, result
		#sim.send(who, result)
	else:
		print 'unknown command %s' % cmd

class MySmsHandle(EventSmsHandle):
	def process(self, who, when, what):
		sms_handle(who, when, what)

if __name__ == '__main__':
	sim = SIM900A('COM1', [MySmsHandle, ])
	sim.run()
	
