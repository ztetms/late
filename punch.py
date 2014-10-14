#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# -*- mode: python; -*- 

import re
import urllib
import urllib2
import cookielib
import StringIO
from HTMLParser import HTMLParser

from check_code import CheckCode

class HtmlInput(HTMLParser):
	def __init__(self):
		self.group = {}
		HTMLParser.__init__(self)

	def get(self, page):
		self.feed(page)
		return self.group
	
	def handle_starttag(self, tag, attrs):
		if tag == 'input':
			attrs = dict(attrs)
			if 'name' in attrs:
				name = attrs['name']
				value = attrs.get('value', '')
				if not name in self.group:
					self.group[name] = value

class Punch:
	def __init__(self):
		self.user = None
		self.passwd = None
		self.path = {
			'login': 'http://tms.zte.com.cn/tms/login.aspx',
			'punch': 'http://atm.zte.com.cn/atm/Application/AboutMy/netchkinout.aspx',
			'code':  'http://atm.zte.com.cn/atm/Application/AboutMy/CheckCode.aspx'
			}
		self.init_cookie()
		
	def init_cookie(self):
		self.cookie = cookielib.CookieJar()
		handler = urllib2.HTTPCookieProcessor(self.cookie)
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)
		
	def logged(self):
		employee = dict([(ck.name, ck.value) for ck in self.cookie]).get('TMS_EmployeeNum', None)
		return employee != None and employee == self.user
		
	def login(self, user, passwd):
		self.user = user
		self.passwd = passwd
		
		url = self.path['login']
		page = urllib2.urlopen(url).read()
		input = HtmlInput().get(page)

		del input['UserId']
		input['__EVENTTARGET'] = ''
		input['__EVENTARGUMENT'] = ''
		input['__LASTFOCUS'] = ''
		input['btnLogin.x'] = '26'
		input['btnLogin.y'] = '8'
		input['txtUserName'] = user
		input['rdoList'] = 'zh-CN'
		input['PassWord'] = passwd
		
		data = urllib.urlencode(input)
		request = urllib2.Request(url, data)
		response = urllib2.urlopen(request)
		#page = response.read().decode('utf8')

		return self.logged()
		
	def alert_string(self, page):
		str = None
		pattern = '[\x00-\xffff]*alert\\(\'(.*)\'\\)'
		match = re.match(pattern, page[page.index('alert(\''):])
		if match:
			str = match.group(1).strip()
		return str
	
	def punch(self):
		url = self.path['punch']
		page = urllib2.urlopen(url).read()
		input = HtmlInput().get(page)
		code = self.check_code()
		
		if code != None:
			input['txtpas'] = code
			
			data = urllib.urlencode(input)
			request = urllib2.Request(url, data)
			response = urllib2.urlopen(request)
			page = response.read().decode('utf8')
			result = self.alert_string(page)
			
			if result == None:
				print page
		else:
			result = 'Unrecognized Check Code'
			
		return result
		
	def check_code(self):
		url = self.path['code']
		page = urllib2.urlopen(url).read()
		code = CheckCode(StringIO.StringIO(page)).code()
		return code
		
if __name__ == "__main__":
	import os
	punch = Punch()
	user = os.getenv('TMS_USER')
	passwd = os.getenv('TMS_PASSWD')
	print 'login', user, '*' * len(passwd)
	if punch.login(user, passwd):
		print 'punch'
		result = punch.punch()
		print result
	else:
		print 'login failed.'
	
	