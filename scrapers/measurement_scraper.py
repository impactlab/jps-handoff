import mechanize
import cookielib
import urllib
import os,time,datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import csv

# Parameters
with open('meter_list.csv','r') as f:
  fcsv = csv.reader(f)
  meters = fcsv.next()
svc_domain = r'http://jps-amiprod2.jps.net:9090/'
user_name = os.environ.get('SVC_USER')
user_pass = os.environ.get('SVC_PASS')
output_file = r'measurement.csv'

# Serviewcom parameters
from_date = datetime.datetime.now()
fromDate_string = datetime.datetime.strftime(from_date,'%Y-%m-%d')

svc_home = svc_domain + 'serview.jsp'
svc_login = svc_domain + 'home_D.jsp'

presentValues_task = svc_domain + 'secure/presentValues/presentValues_DBT.jsp'

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
#br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

br.addheaders = [('User-agent', r'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko')]
 
# THe site doesn't seem to like it when we try to login directly, if we do it gives
# "Invalid direct reference to form login page"
# So we request the home page first, then try to log in.  
resp = br.open(svc_home)
time.sleep(0.2)

# Now open the login page
resp = br.open(svc_login)

# Select the first form on the login page
br.select_form(nr=0)

# User credentials
br.form['j_username'] = user_name
br.form['j_password'] = user_pass

# Login
resp = br.submit()
time.sleep(1.0)

first_time_through = True
columns, values = ['DeviceId'], []

for meter in meters:    
  get_fields = {'isFirst': 'true',
		'typeOfData': 'All',
		'fromDate': fromDate_string,
		'deviceId': meter,
		'commModuleId': '',
		'Select': 'Select'}

  #Encode the parameters
  get_data = urllib.urlencode(get_fields)
  resp = br.open(presentValues_task,get_data)
  time.sleep(0.2)
  data = resp.read()

  soup = BeautifulSoup(data)
  tables = soup.find_all('table')
  if len(tables) < 5:
    print 'Failed on meter '+meter
    continue
  else:
    print 'Meter '+meter
  header_table = tables[1]
  main_table = tables[3]
  if not first_time_through:
    values.append([None for i in values[0]])
  else:
    values.append([None])
  values[-1][0]=meter

  for header_row in header_table.find_all('tr'):
    header_cols = header_row.find_all('td')
    if len(header_cols) < 2: continue
    if header_cols[0].text.strip() == '': continue
    thisheader = header_cols[0].text.strip()
    if first_time_through: 
      columns.append(thisheader)
      values[-1].append(None)
    try:
      thiscol = columns.index(thisheader)
      values[-1][thiscol] = header_cols[1].text.strip()
    except:
      pass

  for main_row in main_table.find_all('tr'):
    main_cols = main_row.find_all('td')
    if len(main_cols) < 2: continue
    if main_cols[0].text.strip() == '': continue
    thisheader = main_cols[0].text.strip()
    if first_time_through: 
      columns.append(thisheader)
      values[-1].append(None)
    try:
      thiscol = columns.index(thisheader)
      values[-1][thiscol] = main_cols[1].text.strip()
    except: 
      pass
  first_time_through = False  

with open(output_file,'w') as f:
  fcsv = csv.writer(f)
  fcsv.writerow(columns)
  for row in values:
    fcsv.writerow(row)


