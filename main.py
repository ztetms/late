#! /usr/bin/env python
#coding=utf-8

import shlex
from punch import Punch
from gsm.gsm import GSM
from gsm.gsm0705 import GSM0705
from gsm.daemon import DAEMON
from gsm.daemon import PRIV_M
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
	u'punch': sms_punch,
}

def sms_proc(daemon, sms, who, when, what):
	msg = tuple(what.split(',', 1))
	cmd = msg[0].lower()
	context = msg[1] if len(msg) > 1 else ''
	
	if cmd in CMD:
		result = CMD[cmd](cmd, context)
		print who, result

		def send():
			sms.send(who, u''.join([cmd, '->', result]))
		daemon.add_command(daemon.READ_EVENT, PRIV_M)
		daemon.add_command(send, PRIV_M)
	else:
		print 'unknown command %s' % cmd

def start_daemon(dev):
	port = Serial(dev)
	gsm = GSM(port)
	sms = GSM0705(gsm)
	daemon = DAEMON(gsm, [])
	def sms_handle(who, when, what):
		sms_proc(daemon, sms, who, when, what)
	daemon.add_event_handle(sms.GSM0705_CMTI_HANDLE(sms_handle))
	daemon.run()

if __name__ == '__main__':
	start_daemon('COM1')
	
