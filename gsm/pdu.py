#! /usr/bin/env python
#coding=utf-8

import datetime


DSC_7BIT = 0
DSC_8BIT = 4
DSC_UCS2 = 8
INTERNATION_NUMBER = 1
NATIONAL_NUMBER = 2
NATIONAL_NUMBERING_PLAN = 8
HEX2DEC = dict(zip(list('0123456789ABCDEF'), range(16)))

def merge_elements(list, multiple, num = 2):
	'''
	>>> merge_elements([1, 2, 3, 4], 2, 2)
	[4, 10]
	'''
	assert(len(list) % num == 0)
	return map(
		lambda index: reduce(lambda acc, item: acc * multiple + item,
			list[index * num:(index + 1) * num], 0),
		range(len(list) / num))
		
def parse_hex_string(string):
	'''
	>>> parse_hex_string('FEDCBA9876543210')
	[254, 220, 186, 152, 118, 84, 50, 16]
	'''
	return merge_elements([HEX2DEC[c] for c in string], 16, 2)
	
def bits(byte, offset, mask):
	'''
	>>> bits(12, 2, 3)
	3
	'''
	return (byte >> offset) & mask
	
def decode_address(data):
	ext_ton_npi = data[0]
	address = data[1:]
	ext = bits(ext_ton_npi, 7, 0x1)
	ton = bits(ext_ton_npi, 4, 0x7)
	npi = bits(ext_ton_npi, 0, 0xF)
	assert(ext == 1) # The EXT bit is always 1 meaning "no extension"
	plus = '+' if ton == INTERNATION_NUMBER and not npi == NATIONAL_NUMBERING_PLAN else ''
	number = filter(lambda n: n in range(10),
			[address[i / 2] >> 4 * (i % 2) & 0xF for i in range(len(address) * 2)])
	return plus + ''.join(['%d' % num for num in number])
	
def decode_csca(data):
	return decode_address(data[1:]) if data[0] > 0 else None

def parse(string):
	'''
	>>> csca, tpdu = parse('0891683108501955F1040D91683118140276F8000841011251018123044F60597D')
	>>> csca
	'+8613800591551'
	>>> tpdu.oa
	'+8613814120678'
	'''
	data = parse_hex_string(string)
	csca_length = data[0]
	csca = decode_csca(data[:1 + csca_length])
	return csca, TPDU_FACTORY.from_code(data[1 + csca_length:])
	
class UD_7BIT():
	@staticmethod
	def byte_size(number):
		'''
		>>> UD_7BIT.byte_size(0)
		0
		>>> UD_7BIT.byte_size(1)
		1
		>>> UD_7BIT.byte_size(8)
		7
		>>> UD_7BIT.byte_size(9)
		8
		'''
		return (number * 7 + 7) / 8
		
	@classmethod
	def decode(cls, number, bytes):
		assert(cls.byte_size(number) == len(bytes))
		return [cls.get_7bit(i, bytes) for i in range(number)]
		
	@staticmethod
	def get_7bit(pos, bytes):
		'''
		[0x90, 0x3F][1] -> 0x7F
		>>> UD_7BIT.get_7bit(1, [128, 63])
		127
		'''
		offset = pos * 7
		byte, bit = offset / 8, offset % 8
		return ((bytes[byte] >> bit) | (bytes[byte + 1] << (8 - bit))) & 0x7F
		
class UD_8BIT():
	@staticmethod
	def byte_size(number):
		return number
		
	@classmethod
	def decode(cls, number, bytes):
		assert(cls.byte_size(number) == len(bytes))
		return bytes
	
class UD_UCS2():
	@staticmethod
	def byte_size(number):
		return number
		
	@classmethod
	def decode(cls, number, bytes):
		assert(cls.byte_size(number) == len(bytes))
		return [cls.get_16bit(i, bytes) for i in range(number / 2)]
		
	@staticmethod
	def get_16bit(pos, bytes):
		return (bytes[pos * 2] << 8) | (bytes[pos * 2 + 1] << 0)

class UD_FACTORY():
	@staticmethod
	def creator(type):
		return {
			DSC_7BIT: UD_7BIT,
			DSC_8BIT: UD_8BIT,
			DSC_UCS2: UD_UCS2,
			}[type]
			
class PDU_TIMEZONE(datetime.tzinfo):
	def __init__(self, offset):
		self.__offset = datetime.timedelta(minutes = offset * 15)
		abs_offset = abs(offset)
		self.__name = 'UTC%c%02d:%02d' % ('+' if offset == abs_offset else '-', abs_offset / 4, abs_offset % 4 * 15)

	def utcoffset(self, dt):
		return self.__offset

	def tzname(self, dt):
		return self.__name

	def dst(self, dt):
		return ZERO
		
class TPDU():
	MT_RESERVED = 3
	@classmethod
	def mti(cls):
		return cls.MT_RESERVED
	
class SMS_DELIVER(TPDU):
	'''
	mti = Message Type Indicator
	mms = More Messages to Send
	oa = Originating Address
	pid = Protocol Identifier
	scts = Service Centre Time Stamp
	dcs = Data Coding Scheme
	ud = User Data
	
	>>> tpdu = SMS_DELIVER.parse('040D91683118140276F800004101224154232314D3252B0683D97035D88D050FCFE7F7B79C0C')
	>>> print tpdu.oa
	+8613814120678
	>>> print ''.join(map(unichr, tpdu.ud))
	SK,10068507,password

	>>> tpdu = SMS_DELIVER.parse('040D91683118140276F8000841011251018123044F60597D')
	>>> tpdu.oa
	'+8613814120678'
	>>> ''.join(map(unichr, tpdu.ud))
	u'\u4f60\u597d'
	'''
	
	MT_SMS_DELIVER = 0
	
	@classmethod
	def mti(cls):
		return cls.MT_SMS_DELIVER

	@classmethod
	def parse(cls, string):
		return cls.decode(parse_hex_string(string))

	@classmethod
	def check(cls, data):
		oa = 2 + (data[1] + 1) / 2
		dcs = data[2 + oa]
		ud = data[10 + oa]
		ud_decoder = UD_FACTORY.creator(dcs)
		return len(data) == 11 + oa + ud_decoder.byte_size(ud)

	@classmethod
	def decode(cls, data):
		tpdu = None
		if cls.check(data):
			tpdu = SMS_DELIVER()
			
			first = data.pop(0)
			tpdu.mti = bits(first, 0, 2)
			tpdu.mms = bits(first, 2, 1)
			assert(tpdu.mti == cls.mti())
			tpdu.oa = cls.decode_address([data.pop(0) for c in range(2 + (data[0] + 1) / 2)])
			tpdu.pid = data.pop(0)
			dcs = data.pop(0)
			tpdu.scts = cls.decode_datetime([data.pop(0) for c in range(7)])
			udl = data.pop(0)
			ud_decoder = UD_FACTORY.creator(dcs)
			tpdu.ud = ud_decoder.decode(udl, [data.pop(0) for c in range(ud_decoder.byte_size(udl))])
			assert(len(data) == 0)
		return tpdu
		
	@staticmethod
	def decode_address(data):
		return decode_address(data[1:])
		
	@staticmethod
	def decode_datetime(data):
		'''
		>>> print SMS_DELIVER.decode_datetime([65, 1, 18, 81, 1, 129, 35])
		2014-10-21 15:10:18+08:00
		'''
		date_data = [(-1 if c & 0x8 else 1) * ((c & 0x7) * 10 + ((c & 0xF0) >> 4)) for c in data]
		date = dict(zip(['year', 'month', 'day', 'hour', 'minute', 'second', 'tzone'], date_data))
		return datetime.datetime(2000 + date['year'], date['month'], date['day'], date['hour'], date['minute'], date['second'], 0, PDU_TIMEZONE(date['tzone']))
				
class TPDU_FACTORY():
	TPDUS = [SMS_DELIVER, ]
	@classmethod
	def from_code(cls, code):
		mti = bits(code[0], 0, 2)
		return dict(map(lambda tpdu: (tpdu.mti(), tpdu),
			cls.TPDUS))[mti].decode(code)
