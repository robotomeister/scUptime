# Author: William W. Lee <william@solidcoding.com>

#system imports
import sys, os
from ConfigParser import SafeConfigParser
from ConfigParser import Error
import smtplib
import string
import datetime

#third party imports
import requests
import argparse

#globals
dbAddress = "127.0.0.1"
dbType = "MySQL"
dbDatabase = ""
dbUsername = ""
dbPassword = ""
emailFrom = ""
emailTo = ""
emailServer = "localhost"
emailMode = "default"
emailUsername = ""
emailPassword = ""

dbConn = None
dbCur = None

#setup arguments
parser = argparse.ArgumentParser(description='Moderately more advanced website uptime checker')
parser.add_argument('--config', type=str, help='scUptime configuration file. scUptime.ini by default')
parser.add_argument('--urls', type=str, help='Comma-delimited file containing URLs to check. urls.ini by default')
args = parser.parse_args()

#load configuration
scriptPathName = os.path.dirname(sys.argv[0])        
scriptFullPath = os.path.abspath(scriptPathName)

if args.config != None:
    configFileStr = args.config
else:
    configFileStr = scriptFullPath + '/scUptime.ini'

if args.urls != None:
    urlFileStr = args.urls
else:
    urlFileStr = scriptFullPath + '/urls.ini'

parser = SafeConfigParser()
parser.read(configFileStr)

#setup database
try:
    dbType = parser.get('configuration','dbType')
    dbAddress = parser.get('configuration','dbAddress')
    dbUsername = parser.get('configuration','dbUsername')
    dbPassword = parser.get('configuration','dbPassword')
    dbDatabase = parser.get('configuration','dbDatabase')
    emailFrom = parser.get('configuration','emailFrom')
    emailTo = parser.get('configuration','emailTo')
    
    emailServer = parser.get('configuration','emailServer')
    emailMode = parser.get('configuration','emailMode')
    emailUsername = parser.get('configuration','emailUsername')
    emailPassword = parser.get('configuration','emailPassword')        
except Error as e:
    print "Error Encountered: Configuration option missing - " + e.message    
    sys.exit("Script terminating.")

if dbType == "MySQL":
    import MySQLdb
if dbType == "MongoDB":
    import pymongo
    from pymongo import MongoClient

try:
    if dbType == "MySQL":
        dbConn = MySQLdb.connect(dbAddress, dbUsername, dbPassword, dbDatabase);
    if dbType == "MongoDB":
        dbConn = MongoClient()   
        dbCur = dbConn[dbDatabase]             
except MySQLdb.Error, e:
    print "Database Error Encountered %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)

#setup email
emailSubjectTemplate = "scUptime: "

#read from urls file and process each section
parser = SafeConfigParser()
parser.read(urlFileStr)
for sectionName in parser.sections():
    try:
        siteDict = {'siteURL':parser.get(sectionName,'siteURL'),'searchStr':parser.get(sectionName,'searchStr'),'requestType':parser.get(sectionName,'requestType')}
        
        #get site at URL
        requestResultObj = requests.get(siteDict['siteURL'])
        
        #search for searchStr 
        searchPos = requestResultObj.text.find(siteDict['searchStr'])
        
        #log result
        status = "Down"
        msg = ""
        if searchPos > -1:
            status = "Up"
        else: 
            msg = "Unable to find " + siteDict['searchStr'] + " for " + siteDict['siteURL']  
    
        with dbConn:
            if dbType == "MySQL":
                dbCur = dbConn.cursor()
                dbCur.execute("INSERT INTO weblog (siteName, status, msg) VALUES(%s, %s, %s)",
                              (sectionName,status,msg))
            if dbType == "MongoDB":
                weblog = dbCur.weblog
                
                weblogEntryObj = {
                    "siteName": sectionName,
                    "status": status,
                    "msg": msg,
                    "created": datetime.datetime.utcnow()
                }
                
                weblog.insert(weblogEntryObj)
                    
        if status == "Down":
            emailSubject = emailSubjectTemplate + sectionName + " down"
            emailBody = string.join((
                    "From: %s" % emailFrom,
                    "To: %s" % emailTo,
                    "Subject: %s" % emailSubject,
                    "",
                    sectionName + " is down"
                    ), "\r\n")            
            if emailMode == "default":         
                smtpServer = smtplib.SMTP(emailServer)
                smtpServer.sendmail(emailFrom, [emailTo], emailBody)
                smtpServer.quit()
            if emailMode == "gmail":
                headers = ["from: " + sender,
                   "subject: " + emailSubject,
                   "to: " + emailTo,
                   "mime-version: 1.0",
                   "content-type: text/html"]
                headers = "\r\n".join(headers)
                server = smtplib.SMTP('smtp.gmail.com',587)  
                server.ehlo()
                server.starttls()  
                server.ehlo()
                server.login(emailUsername,emailPassword)
                session.sendmail(sender, recipient, headers + "\r\n\r\n" + sectionName + " is down")  
                server.quit()  
    except Error as e:
        print "Configuration Error Encountered in [" + sectionName + "]: " + e.message

