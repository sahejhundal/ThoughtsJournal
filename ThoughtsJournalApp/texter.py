import smtplib
import random

# at&t:     number@mms.att.net
# t-mobile: number@tmomail.net
# verizon:  number@vtext.com
# sprint:   number@page.nextel.com

carriers = {'att':'@mms.att.net', 'tmobile':'@tmomail.net', 'verizon':'@vtext.com', 'sprint':'@page.nextel.com'}

def text(number, carrier, key):
	msg = ("Use %s to verify your account at sahej.hundal.me" % str(key))
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	server.login('sahej.hundal.me', 'Beretta95')
	server.sendmail('sahej.hundal.me@gmail.com', '%s%s' % (number, carriers[carrier]), msg)
