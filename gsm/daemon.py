#! /usr/bin/env python
#coding=utf-8

PRIV_H = 0
PRIV_M = 1
PRIV_L = 2

class ACTIVE_OBJECT_ENGINE():
	def __init__(self):
		self.__its_commands = [[],[],[]]
		self.__priv = range(len(self.__its_commands))

	def add_command(self, priv, cmd):
		assert(priv in self.__priv)
		self.__its_commands[priv].append(cmd)

	def is_empty(self):
		return 0 == reduce(add, map(len, self.__its_commands))

	def pop_cmd(self, priv = 0):
		return self.__its_commands[priv].pop(0) 
			if len(self.__its_commands[priv]) > 0
			else self.pop_cmd(priv + 1)

	def run(self):
		while self.is_empty():
			cmd = self.pop_cmd()
			cmd()

def IDLE(engine, gsm):
	def execute():
		engine.add_command(PRIV_L, IDLE(engine, gsm))
		engine.add_command(PRIV_H, READ_EVENT(engine, gsm))
	return execute

def HANDLE_EVENT(self, gsm, line):
	def execute(self):
		print line
	return execute

def READ_EVENT(self, engine, gsm):
	def execute(self):
		line = gsm.readline()
		if len(line) > 0:
			engine.add_command(PRIV_M, HANDLE_EVENT(engine, gsm))
			engine.add_command(PRIV_M, READ_EVENT(engine, gsm))
			engine.add_command(PRIV_H, READ_EVENT(engine, gsm))
	return execute

def run(gsm):
	engine = ACTIVE_OBJECT_ENGINE
	engine.add_command(PRIV_L, IDLE(engine, gsm))
	engine.run()