import smtplib
import subprocess
import time
hostname = subprocess.check_output(['hostname', '-I'])
hostname = hostname.replace('\n', '')
hostname = hostname.split(' ')
addr = hostname[0] 
#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = 'dmrose100@gmail.com' #change this to match your gmail account
GMAIL_PASSWORD = 'Mannyb123'  #change this to match your gmail password
 
class Emailer:
	def sendmail(self, recipient, subject, content):
         
        #Create Headers
        	headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
               	"MIME-Version: 1.0", "Content-Type: text/html"]
        	headers = "\r\n".join(headers)
 
        	#Connect to Gmail Server
        	session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        	session.ehlo()
        	session.starttls()
        	session.ehlo()
 
        	#Login to Gmail
        	session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
 
        	#Send Email & Exit
        	session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        	session.quit
 
sender = Emailer()
 
sendTo = 'drose@glimpsewearables.com'
emailSubject = "I'm online"
emailContent = addr + '/livestream'
 
#Sends an email to the "sendTo" address with the specified "emailSubject" as the subject and "emailContent" as the email content.
sender.sendmail(sendTo, emailSubject, emailContent)  
	
