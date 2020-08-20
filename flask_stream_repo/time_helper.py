import datetime

#convert date in string format to datetime object
#eg. 'Wed Mar 08 03:11:05 +0000 2019' to 2019-03-08 03:11:05
def dstr_obj(dtstr):
 dt = datetime.datetime.strptime(dtstr, '%a %b %d %H:%M:%S %z %Y')
 dtstr2 = dt.strftime('%Y-%m-%d %H:%M:%S')
 return datetime.datetime.strptime(dtstr2,'%Y-%m-%d %H:%M:%S')

#return current time
def current_time():
 timenow = datetime.datetime.utcnow()
 return datetime.datetime.strptime(timenow.strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

#Return time x minutes ago.
def lag_time(timenow,x):
 return timenow-datetime.timedelta(minutes=x)

#True if x is dt1<= x <dt2
def time_between(dt1,dt2,x):

 if x>=dt1 and x<dt2:
  flg=True
 else:
  flg=False

 return flg 
