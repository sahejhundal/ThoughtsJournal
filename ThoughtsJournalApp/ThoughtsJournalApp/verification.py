import smtplib
import random
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

class Verification():
	def email(email, key):
		fromaddr="sahej.hundal.me@gmail.com"
		mainbody = ("""
		<body>
		  <p>Use %s for your Account Verification at <a href="http://sahej.hundal.me">ThoughtsJournal</a>
		</body>
		""") % key
		msg = MIMEMultipart('alternative')
		msg['From'] = fromaddr
		msg['To'] = toaddr
		msg['Subject'] = 'Account Verification Code'
		msg.preamble = 'Account Authentication from no-reply at <a href="sahej.hundal.me">sahej.hundal.me</a>'
		HTML_BODY = MIMEText(mainbody, 'html')
		msg.attach(HTML_BODY)
		#msg.attach(MIMEText(text))
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login('sahej.hundal.me@gmail.com', 'Beretta95')
		server.sendmail(fromaddr, email, msg.as_string())
		server.quit()

	def text(number, carrier, key):
		carriers = {'att':'@mms.att.net', 'tmobile':'@tmomail.net', 'verizon':'@vtext.com', 'sprint':'@page.nextel.com'}
		msg = ("Use %s to verify your account at sahej.hundal.me" % str(key))
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.starttls()
		server.login('sahej.hundal.me', 'Beretta95')
		server.sendmail('sahej.hundal.me@gmail.com', '%s%s' % (number, carriers[carrier]), msg)