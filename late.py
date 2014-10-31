#! /usr/bin/env python
#coding=utf-8

import sys
import shlex
import logging

from punch import Punch
from gsm.gsm import GSM
from gsm.gsm0705 import GSM0705
from gsm.daemon import DAEMON
from gsm.daemon import PRIV_M
from gsm.port import Serial
from gsm.port import Telnet

def punch(user, passwd):
	punch = Punch()
	if punch.login(user, passwd):
		result = punch.punch()
	else:
		result = 'login failed'
	logging.info('punch %s %s %s', user, '*' * len(passwd), result)
	return result

def sms_punch(cmd, arg):
	login = arg.split(',', 1)
	if len(login) == 2:
		usr, pwd = login
		result = punch(usr, pwd)
	else:
		result = 'parameter error'
		logging.warning('Punch parameter is error. %s' % arg)
		
	return result

CMD = {
	u'punch': sms_punch,
}

def sms_del_async(daemon, sms, where):
	def delete():
		sms.delete(where)
	daemon.add_command(daemon.READ_EVENT, PRIV_M)
	daemon.add_command(delete, PRIV_M)

def sms_send_async(daemon, sms, who, context):
	def send():
		sms.send(who, context)
	daemon.add_command(daemon.READ_EVENT, PRIV_M)
	daemon.add_command(send, PRIV_M)
	
def cut_msg(msg, max):
	ppp = '...'
	return msg if len(msg) <= max else '%s%s' % (msg[:max - len(ppp)], ppp)

def sms_proc(daemon, sms, msg):
	where, who, when, what = msg
	logging.info('+SMS: %s %s %d %s', who, when, len(what), cut_msg(what, 16))
	context = tuple(what.split(',', 1))
	cmd = context[0].lower()
	args = context[1] if len(context) > 1 else ''
	
	sms_del_async(daemon, sms, where)
	
	if cmd in CMD:
		result = CMD[cmd](cmd, args)
		sms_send_async(daemon, sms, who, u''.join([cmd, '->', result]))
	else:
		logging.warning('Unknown SMS command %s.' % cmd)
	
def create_port(type, cfg):
	return apply(getattr(sys.modules['gsm.port'], type), cfg)

def start_daemon(dev):
	port = apply(create_port, dev)
	gsm = GSM(port)
	sms = GSM0705(gsm)
	daemon = DAEMON(gsm, [])
	def sms_handle(where, who, when, what):
		sms_proc(daemon, sms, (where, who, when, what))
	daemon.add_event_handle(sms.GSM0705_CMTI_HANDLE(sms_handle))
	daemon.run()

def config():
	reload(sys)
	sys.setdefaultencoding('utf-8')
	
	logging.basicConfig(
		filename = 'late.log',
		level = logging.INFO,
		format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
if __name__ == '__main__':
	config()
	
	dev_cfg = sys.argv[1:]
	if len(dev_cfg) > 0:
		logging.info('Starting...')
		start_daemon((dev_cfg[0], dev_cfg[1:]))
	else:
		sys.stderr.write('The device type is not specified.')
		sys.exit(-1)
