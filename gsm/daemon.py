#! /usr/bin/env python
#coding=utf-8

import traceback
import logging

PRIV_H = 0
PRIV_M = 1
PRIV_L = 2

class ACTIVE_OBJECT_ENGINE():
	def __init__(self):
		self.empty()
		self.__priv = range(len(self.__its_commands))
		self.log = logging.getLogger(__name__)

	def add_command(self, cmd, priv = PRIV_L):
		assert(priv in self.__priv)
		self.__its_commands[priv].append(cmd)

	def is_empty(self):
		return 0 == reduce(lambda x, y: x + y,
				map(len, self.__its_commands))

	def empty(self):
		self.__its_commands = [[],[],[]]
		
	def pop_cmd(self, priv = PRIV_H):
		return self.__its_commands[priv].pop(PRIV_H) \
			if len(self.__its_commands[priv]) > 0 \
			else self.pop_cmd(priv + 1)

	def run(self):
		while not self.is_empty():
			cmd = self.pop_cmd()
			try:
				cmd()
			except Exception as exc:
				stack = traceback.format_exc()
				self.log.error('Execute %s error.\n%s', cmd.__name__, stack)

class DAEMON():
	def __init__(self, gsm, event_handle = []):
		self.gsm = gsm
		self.event_handle = event_handle
		self.engine = ACTIVE_OBJECT_ENGINE()

	def add_command(self, cmd, priv):
		self.engine.add_command(cmd, priv)

	def add_event_handle(self, handle):
		self.event_handle.append(handle)

	def dispatch_event(self, line):
		for handle in self.event_handle:
			cmds = handle(line)
			for cmd in cmds:
				self.engine.add_command(cmd, PRIV_M)
		
	def STOP(self):
		def execute():
			self.engine.empty()
		return execute
		
	def IDLE(self):
		def execute():
			self.engine.add_command(self.IDLE(), PRIV_L)
			self.engine.add_command(self.READ_EVENT(), PRIV_H)
		return execute

	def DISPATCH_EVENT(self, line):
		def execute():
			self.dispatch_event(line)
		return execute

	def READ_EVENT(self):
		def execute():
			line = self.gsm.read_event()
			if len(line) > 0:
				self.engine.add_command(self.DISPATCH_EVENT(line), PRIV_M)
				self.engine.add_command(self.READ_EVENT(), PRIV_H)
		return execute

	def run(self, times = -1):
		for i in range(abs(times)):
			self.engine.add_command(self.IDLE(), PRIV_L)
		if times >= 0:
			self.engine.add_command(self.STOP(), PRIV_L)

		self.engine.run()