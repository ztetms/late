#! /usr/bin/env python
#coding=utf-8

import string
import pdu
from pdu import SMS_SUBMIT

class GSM0705:
	CMGF_PDU = 0
	CMGF_TEXT = 1
	def __init__(self, gsm):
		self.gsm = gsm

	def config(self, mode):
		assert(mode == self.CMGF_PDU or mode == self.CMGF_TEXT)
		expect = ['OK', 'ERROR']
		response = self.gsm.send_cmd(self.gsm.at_cmd('%s=%d' % ('+CMGF', mode)), expect)
		result, context = self.gsm.format_response(response, expect)
		return result == 'OK'
		
	def read(self, position):
		self.config(self.CMGF_PDU)
		expect = ['OK', 'ERROR']
		response = self.gsm.send_cmd(self.gsm.at_cmd('%s=%d' % ('+CMGR', position)), expect)
		result, context = self.gsm.format_response(response, expect)
		if result == 'OK' and len(''.join(context)) > 0:
			length, index = reduce(max, zip(map(len, context), range(len(context))))
			csca, tpdu = pdu.parse(context[index])
			result = tpdu.oa, tpdu.scts, ''.join(map(unichr, tpdu.ud))
		else:
			result = None
		return result

	def send(self, to, ctx):
		r = False
		self.config(self.CMGF_PDU)
		sca = [0]
		code = SMS_SUBMIT.encode(to, ctx)
		expect = ['> ', 'OK', 'ERROR']
		response = self.gsm.send_cmd(self.gsm.at_cmd('%s=%d' % ('+CMGS', len(code))), expect)
		result, context = self.gsm.format_response(response, expect)
		if result == '> ':
			expect = ['OK', 'ERROR']
			line = ''.join(['%02X' % c for c in sca + code])
			response = self.gsm.send_cmd(line + chr(0x1A), expect)
			result, context = self.gsm.format_response(response, expect)
			r = result == 'OK'
		else:
			print result
		return r

	def delete(self, position):
		expect = ['OK', 'ERROR']
		response = self.gsm.send_cmd(self.gsm.at_cmd('%s=%d' % ('+CMGD', position)), expect)
		result, context = self.gsm.format_response(response, expect)
		return result == 'OK'

	def delete_all(self):
		expect = ['OK', 'ERROR']
		response = self.gsm.send_cmd(self.gsm.at_cmd('%s=1,4' % '+CMGD'), expect)
		result, context = self.gsm.format_response(response, expect)
		return result == 'OK'

	def GSM0705_CMTI_HANDLE(self, proc):
		def handle(event):
			key = '+CMTI: '
			def execute():
				cmd, ctx = self.gsm.parse_notice(event)
				pos = string.atoi(ctx[1])
				sms = self.read(pos)
				if sms != None:
					who, when, what = sms
					proc(pos, who, when, what)
				else:
					logging.error('Read sms@%d failed.', pos)
			return [execute,] if event[:len(key)] == key else []
		return handle
