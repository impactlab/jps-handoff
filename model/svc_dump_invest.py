#!/usr/bin/env python
import mechanize
import cookielib
import urllib
import os,time,datetime,csv,sys
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup

local_svc_mountpoint = 'z:\\'
svc_subdir = 'impactlab'
local_pathsep = '\\'

# Construct some loop variables
meter_list = []
start_dates = []
stop_dates = []
start_dates_evt = []

# Open the subsample file
with open('subsample.csv','r') as f:
  # ...as a csv
  fcsv = csv.reader(f)
  # Skip the header.
  fcsv.next()
  for line in fcsv:
    # The third from last field is the meter ID.
    meter_id = line[-3]
    # If there's no timestamp on the investigation, skip it.
    if line[5]=='': continue
    # Parse the investigation date into a python datetime
    investdate = datetime.datetime.strptime(line[5], '%Y-%m-%d %H:%M:%S')

    # Append the meter and dates to our loop variables.
    meter_list.append(meter_id)
    stop_dates.append(investdate)
    start_dates.append(investdate - datetime.timedelta(days=365))
    start_dates_evt.append(investdate - datetime.timedelta(days=30))

# Parameters
RESP_SLEEP_TIME = 10.0
DUMP_SLEEP_TIME = 10.0

# Prompt for ServiewCom username and password
user_name = raw_input('ServiewCom username: ')
user_pass = raw_input('ServiewCom password: ')

# Some ServiewCom URLs
svc_domain = r'http://jps-amiprod2.jps.net:9090/'
svc_home = svc_domain + 'serview.jsp'
svc_login = svc_domain + 'home_D.jsp'

on_demand_task = svc_domain + 'secure/onDemandTask/onDemandTask_D.jsp'
on_demand_form = svc_domain + 'secure/onDemandTask/onDemandTask_DB.jsp?taskId=link60&TaskManagerID=default'

dump_form_submit = svc_domain + 'secure/onDemandTask/postRequest_F.jsp?chained=&updateDB=true&priority=5&getLog=true&id=link60&requestType=task&TaskManagerID=default&defaultParameter='

event_request = svc_domain + '/servlet/viewReport?type=csv&localFilename=momentaryOutage'


# Create a browser in Mechanize
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
 
# The site doesn't seem to like it when we try to login directly, if we do it gives
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

# Loop through all the subsample data
for meter_string, start_date, stop_date, start_date_evt in \
    zip(meter_list, start_dates, stop_dates, start_dates_evt):
    
    # Get the dates in the formats we need for our request
    working_begin_string = datetime.datetime.strftime(\
      start_date,'%Y-%m-%d %H:%M:%S')
    working_begin_string_evt = datetime.datetime.strftime(\
      start_date_evt,'%Y-%m-%d %H:%M:%S')
    working_end_string = datetime.datetime.strftime(\
      stop_date,'%Y-%m-%d %H:%M:%S')
    
    # Construct the output filenames
    out_filename = meter_string + '__' + \
        datetime.datetime.strftime(start_date,'%Y-%m-%dT%H%M%S') + '__' + \
        datetime.datetime.strftime(stop_date,'%Y-%m-%dT%H%M%S') + '.csv'
    out_filename_evt = 'evt__' + meter_string + '__' + \
        datetime.datetime.strftime(start_date_evt,'%Y-%m-%dT%H%M%S') + '__' + \
        datetime.datetime.strftime(stop_date,'%Y-%m-%dT%H%M%S') + '.csv'
    
    # Parameters for the profile request
    post_fields = {'resourceName': 'link60',
                   'onDemandStartTime.dataType': 'dateTime',
                   'onDemandEndTime.dataType': 'dateTime',
                   'executionMode':'onDemand',
                   'outputFilePath':'/svcdownload/'+svc_subdir,
                   'outputFileName': out_filename,
                   'onDemandType':'list',
                   'onDemandId': meter_string,
                   'onDemandStartTime': working_begin_string,
                   'onDemandEndTime': working_end_string
                 }   
    # Encode the parameters
    print meter_string+' : profile'
    post_data = urllib.urlencode(post_fields)
    # Submit the form (POST request). You get the post_url and 
    # the request type(POST/GET) the same way with the parameters.
    try:
        # Actually do the request
        resp = br.open(dump_form_submit,post_data)
    except:
        # It didn't work, so wait a couple minutes and try again.
        time.sleep(120)
        resp = br.open(dump_form_submit,post_data)
        time.sleep(DUMP_SLEEP_TIME)        
        
    # Now we do the events data.
    post_fields = {'report.class': 'com.trilliantnetworks.svc.report.momentaryoutage.MomentaryOutageReport',
		   'report.remoteUser': user_name,
		   'report.deviceIdPattern.dataType': 'string',
		   'report.groupId.dataType': 'string',
		   'report.dates.specific.startUTC.dataType': 'dateTime',
		   'report.dates.specific.endUTC.dataType': 'dateTime',
		   'report.deviceInputType': 'deviceIdPattern',
                   'report.deviceIdPattern': meter_string,
		   'report.dates.type': 'specific',
		   'report.dates.specific.startUTC': working_begin_string_evt,
		   'report.dates.specific.endUTC': working_end_string,
                 }   
    #Encode the parameters
    post_data = urllib.urlencode(post_fields)
    print meter_string+' : events'

    # This time, we actually have to write out the file; ServiewCom doesn't do it
    # for us.
    resp = br.open(event_request,post_data)
    with open(local_svc_mountpoint+svc_subdir+local_pathsep+out_filename_evt,'w') as f:
	f.write(resp.read())




