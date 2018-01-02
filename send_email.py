#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
#from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr

def _format_addr(s):
	name, addr = parseaddr(s)
	return formataddr((Header(name, 'utf-8').encode(), addr))
smtp_server = 'smtp.163.com'
port = 465
def send_email(msg, to_addr):
#msg = MIMEMultipart()
#msg.attach(MIMEText('hello', 'plain', 'utf-8')
	msg = MIMEText(msg, 'plain', 'utf-8')
	msg['From'] = _format_addr('Sr0 <%s>' % from_addr)
	msg['To'] = _format_addr('<%s>' % to_addr)
	msg['Subject'] = Header('', 'utf-8').encode()

#if you use the qq email, you must to use SMTP_SSL
#server = smtplib.SMTP_SSL('smtp.qq.com', 465)
	server = smtplib.SMTP_SSL(smtp_server, port)
#so if you use SSL you can't use starttls()
#server.starttls()
	server.login(from_addr, password)
	server.sendmail(from_addr, [to_addr], msg.as_string())
	server.quit()
