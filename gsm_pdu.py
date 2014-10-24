#! /usr/bin/env python
#coding=utf-8

class PDU():
	DSC_7BIT = 0
	INTERNATION_NUMBER = 1
	NATIONAL_NUMBER = 2
	NATIONAL_NUMBERING_PLAN = 8
	MT_SMS_DELIVER = 0
	HEX2DEC = dict(zip(list('0123456789ABCDEF'), range(16)))
	@staticmethod
	def reduce(list, multiple, num = 2):
		'''
		>>> PDU.reduce([1, 2, 3, 4], 2, 2)
		[4, 10]
		'''
		assert(len(list) % num == 0)
		return map(
			lambda index: reduce(lambda acc, item: acc * multiple + item,
				list[index * num:(index + 1) * num], 0),
			range(len(list) / num))
			
	@classmethod
	def parse_hex_string(cls, string):
		'''
		>>> PDU.parse_hex_string('FEDCBA9876543210')
		[254, 220, 186, 152, 118, 84, 50, 16]
		'''
		return cls.reduce([cls.HEX2DEC[c] for c in string], 16, 2)
		
	@staticmethod
	def bits(byte, offset, mask):
		'''
		>>> PDU.bits(12, 2, 3)
		3
		'''
		return (byte >> offset) & mask

class TPDU():
	pass
	
class SMS_DELIVER(TPDU):
	@classmethod
	def check(cls, data):
		oa = 2 + (data[1] + 1) / 2
		dcs = data[2 + oa]
		ud = data[10 + oa]
		UD = {
			PDU.DSC_7BIT : lambda s: (s * 7 + 7) / 8
			}
		return len(data) == 11 + oa + UD[dcs](ud)
		
	@staticmethod
	def decode_address(data):
		oal = data[0]
		ext_ton_npi = data[1]
		ext = PDU.bits(ext_ton_npi, 7, 0x1)
		ton = PDU.bits(ext_ton_npi, 4, 0x7)
		npi = PDU.bits(ext_ton_npi, 0, 0xF)
		assert(ext == 1) # The EXT bit is always 1 meaning "no extension"
		plus = '+' if ton == PDU.INTERNATION_NUMBER and not npi == PDU.NATIONAL_NUMBERING_PLAN else ''
		address = data[2:]
		number = [address[i / 2] >> 4 * (i % 2) & 0xF for i in range(len(address) * 2)][:oal]
		return plus + ''.join(['%d' % num for num in number])
		
	@classmethod
	def parse(cls, string):
		tpdu = None
		data = PDU.parse_hex_string(string)
		if cls.check(data):
			tpdu = SMS_DELIVER()
			
			first = data.pop(0)
			tpdu.mti = PDU.bits(first, 0, 2)
			assert(tpdu.mti == PDU.MT_SMS_DELIVER)
			tpdu.mms = PDU.bits(first, 2, 1)
			tpdu.oa = cls.decode_address([data.pop(0) for c in range(2 + (data[0] + 1) / 2)])
			tpdu.pid = data.pop(0)
			tpdu.dcs = data.pop(0)
			tpdu.scts = [data.pop(0) for c in range(7)]
			udl = data.pop(0)
			UD = {PDU.DSC_7BIT : (lambda s: (s * 7 + 7) / 8)}
			tpdu.ud = [data.pop(0) for c in range(UD[tpdu.dcs](udl))]
			assert(len(data) == 0)
		return tpdu

def xxx(pdus):
	for pdu in pdus:
		tpdu = SMS_DELIVER.parse(pdu[18:])
		if tpdu:
			print tpdu.oa
			print
		else:
			print pdu[18:]