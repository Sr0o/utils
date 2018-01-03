#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, rsa, base64, binascii
from lxml import etree
import time
from datetime import datetime
import getpass
from send_email import send_email
b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
b64pad = "="
BI_RM = "0123456789abcdefghijklmnopqrstuvwxyz"
count = 0
#模拟相关加密
def hex2b64(h):
	i = 0
	ret = ''
	while i + 3 <= len(h):
		c = int(h[i:i + 3], 16)
		ret += b64map[c >> 6] + b64map[c & 63]
		i += 3
	if i + 1 == len(h):
		c = int(h[i:i + 1], 16)
		ret += b64map[c << 2]
	elif i + 2 == len(h):
		c = int(h[i:i+2], 16)
		ret += b64map[c >> 2] + b64map[(c & 3) << 4]
	while (len(ret) & 3) > 0:
		ret += b64pad
#	print('完成hex2b64')
	return ret
def int2char(n):
	return BI_RM[n]
def b64tohex(s):
	ret = ''
	i = 0
	k = 0
	slop = 0
	while i < len(s):
		if s[i] == b64pad:
			break
		v = b64map.find(s[i])
		if v < 0:
			continue
		if k == 0:
			ret += int2char(v >> 2)
			slop = v & 3
			k = 1
		elif k == 1:
			ret += int2char((slop << 2) | (v >> 4))
			slop = v & 0xf
			k = 2
		elif k == 2:
			ret += int2char(slop)
			ret += int2char(v >> 2)
			slop = v & 3
			k = 3
		else:
			ret += int2char((slop << 2) | (v >> 4))
			ret += int2char(v & 0xf)
			k = 0
		i += 1
		#print(i)
	if k == 1:
		ret += int2char(slop << 2)
	#print('完成b64tohex')
	return ret
def b64toBA(s):
	h = b64tohex(s)
	i = 0
	a = list()
	while 2 * i < len(h):
		a[i] = int(h[2*i:2*i+2], 16)
		i += 1
	return a
#结束
def login_web():
	s = requests.Session()
	s.headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.5',
		'Connection': 'keep-alive',
		'Content-Type': 'application/x-www-form-urlencoded',
		'DNT': '1',
		'Host': 'jwgl.njtech.edu.cn',
		'Referer': 'https://jwgl.njtech.edu.cn/xtgl/login_slogin.html',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
	}
	r = s.get('https://jwgl.njtech.edu.cn/xtgl/login_slogin.html?language=zh_CN')
	exponent_modulus = s.get('https://jwgl.njtech.edu.cn/xtgl/login_getPublicKey.html').json()
#	print(exponent_modulus)
	#获得exponent与modulus用于制造公钥
	exponent = exponent_modulus['exponent']
	modulus = exponent_modulus['modulus']
#	print('{}\n{}'.format(exponent, modulus))
	
	html = etree.HTML(r.text)
#	print(html)
	
	result = html.xpath('//form')
	action = result[0].xpath('@action')[0]
	post_url = 'https://jwgl.njtech.edu.cn' + action
#	print(post_url)
	
	csrf_token = result[0].xpath('./input[@id="csrftoken"]/@value')[0]
#	print(csrf_token)
	#模拟制造公钥
	rsaKey = rsa.PublicKey(int(b64tohex(modulus), 16), int(b64tohex(exponent), 16))
	password = rsa.encrypt(mm.encode('utf-8'),rsaKey)
#	print(password)
	enPassword = hex2b64(binascii.b2a_hex(password))
	#print(etree.tostring(csrftoken, encoding="unicode"))
	data = {
		'csrftoken': csrf_token,
		'yhm': yhm,
		'mm': enPassword,
		'hidMm': enPassword,
	}
	s.post(post_url, data = data)
	#res = s.get('https://jwgl.njtech.edu.cn/xtgl/index_initMenu.html')
	#print(res.text)
	return s
		
def get_grade(s, n):
	grade = s.post('https://jwgl.njtech.edu.cn/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005', data = {'xnm': '2017', 'xqm': '3'})
	msg = ''
	items = grade.json()['items']
	#print('获取成功')
	if n < len(items):
		for item in items:
			msg += ('课程名称:' + item['kcmc'] + '\n' + '成绩:' + item['cj'] + '\n\n')
		n = len(items)
	return (msg,n)
if __name__ == '__main__':
	yhm = input('请输入学号(初始化):')
	mm = getpass.getpass('请输入密码:')
	eemail = input('请输入你要发送的邮箱账号:')
	n = 0
	nn = 0
	try:
		s = login_web()
	except:
		pass
	while True:
		try:
			msg, n = get_grade(s, n)
			nn = 1 
			if msg:
				try:
					send_email(msg, eemail)
					print(msg)
				except KeyboardInterrupt:
					raise
				except:
					print('你的邮箱账号有误,请更改:')
					eemail = input('邮箱:')
					continue
		except KeyboardInterrupt:
			raise
		except:
			try:
				if nn == 0:
					print('Emmm...你的账号或密码可能错了,再输一遍试试:')
					yhm = input('学号:')
					mm = getpass.getpass('密码:')
				s = login_web()
			except KeyboardInterrupt:
				raise
			except:
				continue
		else:
			#从早上8:00点开始,到23:00休息
			now = datetime.now()
			if now < datetime(now.year, now.month, now.day, 8) or now > datetime(now.year, now.month, now.day, 23):
				time.sleep(60 * 60 * 9)
			else:
				time.sleep(60 * 5)
			count += 1
			print('haha-%s' % count)
