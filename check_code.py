#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# -*- mode: python; -*- 
import Image
import operator

class Feature():
	def __init__(self):
		raise NotImplemented()
		
	def adjust(self, (row, col)):
		return row, col + self.col_adjust[row]
		
	def left_pad(self):
		return min(self.col_adjust)
		
class FeatureSmooth(Feature):
	def __init__(self):
		self.type = 'smooth'
		self.col_adjust = (0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1)
		self.magic = (
				('0', (3, 9, 11, 7, 4, 7, 11, 9, 3)),
				('2', (5, 8, 9, 9, 11, 11, 8)),
				('4', (3, 5, 6, 7, 6, 11, 12, 11, 2)),
				('6', (3, 9, 12, 10, 6, 9, 9, 6)),
				('8', (9, 12, 10, 6, 10, 12, 9)),
				('B', (12, 12, 12, 6, 6, 6, 8, 11, 10, 5)),
				('D', (12, 12, 11, 4, 4, 4, 6, 8, 10, 8, 3)),
				('F', (12, 12, 11, 4, 4, 4, 4, 4, 3)),
				('H', (12, 12, 11, 2, 2, 2, 2, 12, 12, 11)),
				('J', (3, 4, 3, 2, 2, 11, 11, 9)),
				('L', (12, 12, 11, 2, 2, 2, 2, 2)),
				('N', (11, 12, 12, 6, 5, 4, 6, 12, 12, 10)),
				('P', (11, 12, 12, 4, 4, 4, 5, 6, 7, 5)),
				('R', (11, 12, 12, 4, 4, 5, 8, 10, 11, 8)),
				('T', (2, 2, 2, 11, 12, 10, 2, 2, 2, 2)),
				('T', (2, 2, 11, 12, 10, 2, 2, 2, 2)),
				('V', (5, 6, 11, 6, 5, 8, 8, 8, 4, 2)),
				('X', (1, 4, 8, 10, 8, 6, 8, 10, 8, 4, 1)),
				('Z', (3, 6, 7, 9, 10, 9, 7, 6, 5)),
			)
		
class FeatureSharp(Feature):
	def __init__(self):
		self.type = 'sharp'
		self.col_adjust = (0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1)
		self.magic = (
				('0', (1, 8, 10, 5, 4, 5, 10, 8, 1)),
				('2', (4, 6, 7, 7, 8, 10, 7)),
				('4', (2, 3, 5, 5, 4, 8, 11, 7, 2)),
				('6', (2, 8, 9, 8, 6, 7, 9, 6)),
				('8', (7, 11, 7, 6, 8, 11, 7)),
				('B', (6, 12, 9, 6, 6, 6, 7, 10, 9, 3)),
				('D', (6, 12, 8, 4, 4, 4, 4, 5, 9, 8, 2)),
				('F', (6, 12, 7, 4, 4, 4, 4, 4, 3)),
				('H', (6, 12, 7, 2, 2, 2, 2, 7, 12, 6)),
				('J', (3, 4, 2, 2, 2, 7, 11, 5)),
				('L', (6, 12, 8, 2, 2, 2, 2, 2)),
				('N', (6, 12, 7, 5, 3, 3, 5, 7, 12, 6)),
				('P', (6, 12, 7, 4, 4, 4, 4, 5, 7, 4)),
				('R', (6, 12, 7, 4, 4, 4, 6, 9, 10, 5)),
				('T', (2, 2, 2, 8, 12, 6, 2, 2, 2, 2)),
				('V', (3, 6, 6, 6, 3, 5, 6, 5, 3, 1)),
				('X', (1, 3, 5, 6, 6, 4, 6, 6, 5, 3, 1)),
				('Z', (2, 5, 7, 8, 8, 8, 7, 5, 4)),
			)
			
class FeatureFactory():
	__type = {
			'smooth': FeatureSmooth,
			'sharp': FeatureSharp
		}
		
	@classmethod
	def create(cls, type):
		return cls.__type[type]()

class CheckCode():
	def __init__(self, image):
		self.image = Image.open(image)
		type = 'smooth' if self.count_colour(self.image) > 30 else 'sharp'
		self.feature = FeatureFactory.create(type)
		self.background = self.background_colour(self.image)
		self.image.save('last.gif')
	
	def code(self):
		small = self.cut(self.image)
		small.save('tmp.gif')
		result = self.read(small)
		#if result != None:
		#	self.image.save('%s_%s.gif' % (self.feature.type, result))
		return result
		
	@staticmethod
	def start_stop(list):
		left = -1
		right = len(list)
		for i in range(0, len(list)):
			if list[i] > 0:
				if left == -1:
					left = i
				else:
					right = i
				
		return (left, right)

	@staticmethod
	def count_colour(image):
		width, height = image.size
		data = list(image.getdata())
		
		count = {}
		for color in data:
			count[color] = count.get(color, 0) + 1

		return len(count.keys())

	@staticmethod
	def background_colour(image):
		width, height = image.size
		data = list(image.getdata())
		
		count = {}
		for color in data:
			count[color] = count.get(color, 0) + 1

		return sorted(count.iteritems(), key = operator.itemgetter(1))[-1][0]
		
	def cut(self, image):
		width, height = image.size
		data = list(image.getdata())
		index = lambda (row, col): width * row + col
		rows = range(1, height - 1)
		cols = range(1, width - 1)
		# col stat
		stat_col = [sum([data[index((row, col))] != self.background for row in rows]) for col in cols]
		# row stat
		stat_row = [sum([data[index((row, col))] != self.background for col in cols]) for row in rows]
		
		left, right = self.start_stop(stat_col)
		top, bottom = self.start_stop(stat_row)

		return image.crop((1 + left + self.feature.left_pad(), 1 + top, 1 + right + 1, 1 + bottom + 1))
		
	@staticmethod
	def mod(v1, v2):
		N = min(len(v1), len(v2))
		return sum([(lambda x: x * x)(v1[i] - v2[i]) for i in range(0, N)]) * 1.0 / N
		
	def match(self, stat_col):
		return min(map(lambda (char, magic): (self.mod(stat_col, magic), (char, magic)), self.feature.magic))
		
	@classmethod
	def ltrip(cls, list):
		left, right = cls.start_stop(list)
		return list[left:]
		
	def read(self, image):
		width, height = image.size
		index = lambda (row, col): width * row + col
		assert(height == 12)
		data = list(image.getdata())
		stat_col = [sum([data[index(self.feature.adjust((row, col)))] != self.background for row in range(0, height)]) for col in range(abs(self.feature.left_pad()), width)]
		#print image.size, stat_col
		
		code = []
		stat_col = self.ltrip(stat_col)
		for i in range(5):
			(dist, (ch, magic)) = self.match(stat_col)
			code.append((ch, dist))
			#print 'step', i, stat_col[:8], dist, ch, magic
			
			stat_col = stat_col[len(magic):]
			while len(stat_col) > 0 and stat_col[0] == 0:
				stat_col = stat_col[1:]
		#print code
		#print [c[0] for c in code], max([c[1] for c in code])
		return ''.join([c[0] for c in code]) if (max([c[1] for c in code]) < 1.0) else None

if __name__ == "__main__":
	import os
	code = CheckCode('last.gif').code()
	print code
	for file in os.listdir('.'):
		if file[-4:] == '.gif' and len(file) > 8:
			print file
			code = CheckCode(file).code()
			assert(code == file[-9:-4])
	

	
	