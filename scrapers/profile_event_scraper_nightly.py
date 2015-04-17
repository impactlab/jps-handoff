#!/usr/bin/env python
import mechanize
import cookielib
import urllib
import os,time,datetime,csv,sys,shutil
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup

svc_domain = r'http://jps-amiprod2.jps.net:9090/'
user_name = os.environ.get('SVC_USER')
user_pass = os.environ.get('SVC_PASS')
output_directory = '/data/nightly_extract/'
local_svc_mountpoint = '/data/svcdownload'
svc_subdir = 'impactlab'
local_pathsep = '/'

meter_list = []
end_date = datetime.datetime.now()
n_days_profile = 1
n_days_event = 1

start_date_profile = end_date - \
		     datetime.timedelta(days=n_days_profile)
start_date_event = end_date - datetime.timedelta(days=n_days_event)

for f in os.listdir(output_directory):
  os.remove(f)

with open('meter_list.csv','r') as f:
  fcsv = csv.reader(f)
  meter_list = fcsv.next()

# Parameters
RESP_SLEEP_TIME = 10.0
DUMP_SLEEP_TIME = 10.0

svc_home = svc_domain + 'serview.jsp'
svc_login = svc_domain + 'home_D.jsp'

on_demand_task = svc_domain + 'secure/onDemandTask/onDemandTask_D.jsp'
on_demand_form = svc_domain + 'secure/onDemandTask/onDemandTask_DB.jsp?taskId=link60&TaskManagerID=default'

dump_form_submit = svc_domain + 'secure/onDemandTask/postRequest_F.jsp?chained=&updateDB=true&priority=5&getLog=true&id=link60&requestType=task&TaskManagerID=default&defaultParameter='

event_request = svc_domain + '/servlet/viewReport?type=csv&localFilename=momentaryOutage'

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

br.addheaders = [('User-agent', r'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko')]
 
# THe site doesn't seem to like it when we try to login directly, if we do it gives
# "Invalid direct reference to form login page"
# So we request the home page first, then try to log in.  
resp = br.open(svc_home)
time.sleep(RESP_SLEEP_TIME)

# Now open the login page
resp = br.open(svc_login)

# Select the first form on the login page
br.select_form(nr=0)

# User credentials
br.form['j_username'] = user_name
br.form['j_password'] = user_pass

# Login
resp = br.submit()
time.sleep(RESP_SLEEP_TIME)

# On Demand Task
resp = br.open(on_demand_task)
time.sleep(RESP_SLEEP_TIME)

# On Deand Form 
resp = br.open(on_demand_form)
time.sleep(RESP_SLEEP_TIME)

#working_begin_date = start_date
start_date_profile_string = datetime.datetime.strftime(\
		start_date_profile,'%Y-%m-%d %H:%M:%S')
start_date_event_string = datetime.datetime.strftime(\
		start_date_event,'%Y-%m-%d %H:%M:%S')
end_date_string = datetime.datetime.strftime(\
		end_date,'%Y-%m-%d %H:%M:%S')

n_read = 0
for meter in meter_list:
    out_filename_profile = meter + '__' + \
        datetime.datetime.strftime(start_date_profile,\
	'%Y-%m-%dT%H%M%S') + '__' + \
        datetime.datetime.strftime(end_date,\
	'%Y-%m-%dT%H%M%S') + '.csv'
    out_filename_event = 'evt__' + meter + '__' + \
        datetime.datetime.strftime(start_date_event,\
	'%Y-%m-%dT%H%M%S') + '__' + \
        datetime.datetime.strftime(end_date,\
	'%Y-%m-%dT%H%M%S') + '.csv'

    if os.path.exists(output_directory+out_filename_profile): continue
    
    post_fields = {'resourceName': 'link60',
                   'onDemandStartTime.dataType': 'dateTime',
                   'onDemandEndTime.dataType': 'dateTime',
                   'executionMode':'onDemand',
                   'outputFilePath':'/svcdownload/'+svc_subdir,
                   'outputFileName': out_filename_profile,
                   'onDemandType':'list',
                   'onDemandId': meter,
                   'onDemandStartTime': start_date_profile_string,
                   'onDemandEndTime': end_date_string
                 }   
    #Encode the parameters
    print meter+' : profile'
    post_data = urllib.urlencode(post_fields)
    #Submit the form (POST request). You get the post_url and the request type(POST/GET) the same way with the parameters.
    try:
        resp = br.open(dump_form_submit,post_data)
    except:
        time.sleep(120)
        resp = br.open(dump_form_submit,post_data)
        time.sleep(DUMP_SLEEP_TIME)        
        
    
    post_fields = {'report.class': 'com.trilliantnetworks.svc.report.momentaryoutage.MomentaryOutageReport',
		   'report.remoteUser': user_name,
		   'report.deviceIdPattern.dataType': 'string',
		   'report.groupId.dataType': 'string',
		   'report.dates.specific.startUTC.dataType': 'dateTime',
		   'report.dates.specific.endUTC.dataType': 'dateTime',
		   'report.deviceInputType': 'deviceIdPattern',
                   'report.deviceIdPattern': meter,
		   'report.dates.type': 'specific',
		   'report.dates.specific.startUTC': start_date_event_string,
		   'report.dates.specific.endUTC': end_date_string,
                 }   
    #Encode the parameters
    post_data = urllib.urlencode(post_fields)
    print meter+' : events'

    try:
    	resp = br.open(event_request,post_data)
    except:
        time.sleep(120)
        resp = br.open(dump_form_submit,post_data)
        time.sleep(DUMP_SLEEP_TIME)        
    with open(local_svc_mountpoint+svc_subdir+local_pathsep+out_filename_event,'w') as f:
	f.write(resp.read())
    n_read = n_read + 1
    if os.path.exists(local_svc_mountpoint+svc_subdir+local_pathsep+out_filename_profile):
        if os.path.exists(output_directory+out_filename_profile):
            os.remove(output_directory+out_filename_profile)
        shutil.move(local_svc_mountpoint+svc_subdir+local_pathsep+out_filename_profile, \
                    output_directory)
    if os.path.exists(local_svc_mountpoint+svc_subdir+local_pathsep+out_filename_event):
        if os.path.exists(output_directory+out_filename_event):
            os.remove(output_directory+out_filename_event)
        shutil.move(local_svc_mountpoint+svc_subdir+local_pathsep+out_filename_event, \
                    output_directory)
    if n_read >= 100: 
        br = mechanize.Browser()
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        br.addheaders = [('User-agent', r'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko')]
 
        resp = br.open(svc_home)
        time.sleep(RESP_SLEEP_TIME)
        resp = br.open(svc_login)
        br.select_form(nr=0)
        br.form['j_username'] = user_name
        br.form['j_password'] = user_pass

        resp = br.submit()
        time.sleep(RESP_SLEEP_TIME)
        n_read = 0
