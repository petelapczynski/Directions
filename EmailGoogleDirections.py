#!/urs/bin/python
import time
import urllib2
import json

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

#Convert ' ' to '+' in address, or use Lat,long
home = 'Home Address'
work = 'Work Address'   

def sendMail(to, subject, body, attach):
   #email vars
   g_user = 'email@gmail.com'
   g_pw = 'password'
   msg = MIMEMultipart()
   msg['From'] = g_user
   msg['To'] = to
   msg['Subject'] = subject
   
   #Plain or HTML
   #msg.attach(MIMEText(body, 'text'))
   msg.attach(MIMEText(body, 'html'))

   #send mail
   s = smtplib.SMTP('smtp.gmail.com',587)
   s.starttls()
   s.login(g_user,g_pw)
   s.sendmail(g_user, to, msg.as_string())
   s.quit()

   print 'Email Sent'
#End sendmail

def googleDirections(orig, dest):
   #Google API key
   api_key = 'AIzaSyAIRBrgzF4UGCOKBXtEfqjBv4FHPEBRAbo'
   #static maps API key
   sapi_key = 'AIzaSyBDdjk6JupH0c0GkOgmczUMCy6dUhpuViM'

   #HTML Data dictionary
   dResp = {}  
   dResp['orig'] = orig
   dResp['dest'] = dest

   #Build URLs
   dResp['apiurl'] = 'https://maps.googleapis.com/maps/api/directions/json?key=' + api_key + '&sensor=false&units=imperial' + '&origin=' + orig + '&destination=' + dest
   print 'API: ' + dResp['apiurl']
   	
   #build email urls 
   dResp['mapurl'] = 'https://maps.googleapis.com/maps/api/staticmap?key=' + sapi_key + '&format=PNG&size=400x250&markers=color:blue%7Clabel:O%7C' + orig + '&markers=color:red%7Clabel:D%7C' + dest
   print 'Map: ' + dResp['mapurl']
	
   dResp['buttonurl'] = 'https://www.google.com/maps/dir/' + orig + '/' + dest + '/@42.3944736,-83.6354304,10z/' 
   print 'Button: ' + dResp['buttonurl']   

   #obtain json object
   json_obj = urllib2.urlopen(dResp['apiurl'])
   data = json.load(json_obj)

   #response status
   print 'API Response: ' + data['status']

   dResp['data'] = data

   return dResp
#End googleDirections

def buildHtml(dHTML):
   #Helper function to build HTML document string
   #Assign status HTML variables
   sp = '<p style="font-size:15px; min-width=500px;">'
   ep = '</p>'
   br = '<br>'
   
   #Assign Data Variables
   sSummary = dHTML['data']['routes'][0]['summary']
   sWarning = dHTML['data']['routes'][0]['warnings']
   sDistance = dHTML['data']['routes'][0]['legs'][0]['distance']['text']
   sDuration = dHTML['data']['routes'][0]['legs'][0]['duration']['text']

   #Update Map Url
   polyline = dHTML['data']['routes'][0]['overview_polyline']['points']
   #dHTML['mapurl'] = dHTML['mapurl'] + '&path=weight:3%7Ccolor:blue%7Cenc:' + polyline 
   print 'MapURL: ' + dHTML['mapurl']
   
   print 'Summary: ' + sSummary + '.'
   dHTML['summary'] = sSummary

   if len(sWarning) > 0:
      print sWarning
      dHTML['summary'] = sSummary + '<br>' + sWarning 	
	
   print 'Distance: ' + sDistance + '.' + ' ETA: ' + sDuration
   spath = sp + sDistance + '.' + ' ETA: ' + sDuration + '.' + ep + br 
   
   counter = 1
   for item in dHTML['data']['routes'][0]['legs'][0]['steps']:
      print counter , item['html_instructions']
      spath = spath + sp + str(counter) + ') ' + item['html_instructions'] + ep 
      counter += 1

      dHTML['path'] = spath

   #Build html document string
   sHTML = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN">
<head><title></title></head>
<body style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #ddf0e6;">
  <div style="min-width: 50%;">
   <div style="Margin: 0 auto;max-width: 70%;min-width: 50%;width: 280px;">
     <div>&nbsp;</div>
   </div>
     
   <div style="Margin: 0 auto;max-width: 70%;min-width: 50%;">
     <div style="width:100%; border-collapse: collapse;display: table;background-color: #ffffff;">
      <div style="text-align: center;color: #697d71;font-size: 14px;font-family: Merriweather,Georgia,serif;">
      <div style="Margin-left: 20px;Margin-right: 20px;Margin-top: 12px;">
         <div style="line-height:10px;font-size:1px">&nbsp;</div>
      </div>
      <div style="Margin-left: 20px;Margin-right: 20px;">
        <div style="font-size: 12px;font-style: normal;font-weight: normal;Margin-bottom: 20px;" align="center">
			<div id="gmap_display" style="height:100%; width:100%;max-width:100%;">
           <img style="border: 0;display: block;height: 250px;width: 400px;max-width: 600px;"  frameborder="0" src=""" + '"' + dHTML['mapurl'] + '"' + """>
			</div>
		  </div>
      </div>
      
      <div style="Margin-left: 20px;Margin-right: 20px;">
        <div style="line-height:5px;font-size:1px">&nbsp;</div>
      </div>
      
      <div style="Margin-left: 20px;Margin-right: 20px;">
        <h1 style="Margin-top: 0;Margin-bottom: 0;font-weight: normal;font-family: &quot;Open Sans&quot;,sans-serif;">Your Commute: """ + dHTML['summary'] + '</h1>' + dHTML['path'] + """</div>
        <div style="Margin-top: 20px; Margin-bottom: 20px;">
         <a style="border-radius: 20px;display: inline-block;font-weight: bold;line-height: 24px;padding: 12px 24px;text-align: center;text-decoration: none !important;color: #fff;background-color: #47805e;font-family: Merriweather, Georgia, serif;" href=""" + '"' + dHTML['buttonurl'] + '"' + """>View Full Screen</a>
        </div>
      </div>
      <div>&nbsp;</div>
     </div>  
   </div>
  </div>
  <div>&nbsp;</div>
</div>
</body>
</html>"""

   print sHTML
   return sHTML
# End BuildHTML


#Based on time of day, send email.
print time.strftime('%p')
if time.strftime('%p') == 'AM':
   sendMail('email@gmail.com', 'Driving Directions', buildHtml(googleDirections(home, work)), '')
else:
   sendMail('email@gmail.com', 'Driving Directions', buildHtml(googleDirections(work, home)), '')

print 'Complete'
