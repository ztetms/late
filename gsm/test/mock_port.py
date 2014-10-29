#! /usr/bin/env python
#coding=utf-8

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

	def mock_put_read_multi(self, strings):
		for string in strings:
			self.__read.append(string)

	def mock_get_write(self):
		return ''.join(self.__write)

