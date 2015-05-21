#!/usr/bin/env python
import numpy as np
import pandas as pd
import datetime, time, csv, sys, os, fnmatch, django
sys.path.append('/home/impactlab/jps-handoff/webapp')
os.environ['DJANGO_SETTINGS_MODULE'] = 'jps.settings'
from django.conf import settings
from viewer import models
django.setup()

# A class for generating features from AMI events
class EventFeatures:
    def __init__(self, meter):
        self.features = None
        start_date = datetime.datetime.now() - datetime.timedelta(days=30)
        self.read_data(meter, start_date)

    def read_data(self, meter, start_date):
        try:
            m = models.Meter.objects.get(meter_id=meter)
        except:
            print 'Meter '+meter+' not found in DB'
            return
        # Initialize the data arrays
        d = m.events.filter(ts__gte=start_date).order_by('-ts')
        ts, ev = [i.ts for i in d], [i.event for i in d]

        self.feature_names = ['Event count']
        self.features = [len(ev)]


# A class for generating features from AMI profiles
class ProfileFeatures:
    def __init__(self, meter):
        self.features = None
        start_date = datetime.datetime.now() - datetime.timedelta(days=365)
        self.read_data(meter, start_date)

    def read_data(self, meter, start_date):
        # Initialize the data arrays
        ts, kw = [], []
        try:
            m = models.Meter.objects.get(meter_id=meter)
        except:
            print 'Meter '+meter+' not found in DB'
            return
        d = m.profile_points.filter(ts__gte=start_date).order_by('-ts')
        ts, kw = [i.ts for i in d], [i.raw for i in d]

        if len(ts) == 0:
            # In the case that no data was found, don't generate the features
            self.features = None
            return

        # Convert the profile into a pandas series at 15 minute intervals
        self.s = pd.Series(kw, index=ts).resample('15T').dropna()
        self.n = float(self.s.count())
        # Initialize the feature arrays
        self.features = []
        self.feature_names = []

        # Quantiles to check for skewness
        qs = [0.0, .005, .01, .05, .1, .25, .75, .9, 1.0, 0.5]
        pct = self.s.quantile(qs).values
        # Prevent divide-by-zeros
        if pct[-1]==0: pct[-1]=1e-9
        # Add features normalized by 50th percentile
        self.features.extend(list(pct[:-1]/pct[-1]))
        self.feature_names.extend(['quantile%f'%i for i in qs[:-1]])
        
        # Fraction below threshhold of low usage
        frac01 = self.s[self.s < 0.1].count() / self.n
        frac1 = self.s[self.s < 1.0].count() / self.n

        self.features.extend([frac01, frac1])
        self.feature_names.extend(['frac01','frac1'])
        if frac01 > 0.9:
            # If it's 90% low usage, don't generate features.
            self.features = None
            return

        # Time breakdowns: weekday, weekend, day, night
        weekday = self.s[self.s.index.dayofweek < 5]
        weekend = self.s[self.s.index.dayofweek >= 5]
        workday = weekday[(weekday.index.hour >= 9) & \
                          (weekday.index.hour < 17)]
        worknight = weekday[(weekday.index.hour < 9) | \
                            (weekday.index.hour >= 17)]
        weekday_median = weekday.median()
        weekend_median = weekend.median()
        workday_median = workday.median()
        worknight_median = worknight.median()
        self.features.extend([weekday_median, weekend_median, \
                              workday_median, worknight_median])
        self.feature_names.extend(['weekday median', 'weekend median',\
          'workday median', 'worknight median'])

        weekday_mean = weekday.mean()
        weekend_mean = weekend.mean()
        workday_mean = workday.mean()
        worknight_mean = worknight.mean()

        lastyear = self.s[self.s.index < self.s.index[-1] - \
          datetime.timedelta(days=335)]
        thisyear = self.s[self.s.index >= self.s.index[-1] - \
          datetime.timedelta(days=30)]
        meanyoy = lastyear.mean()/thisyear.mean() if \
          thisyear.mean()>0 and not np.isnan(thisyear.mean()) \
          and not np.isnan(lastyear.mean()) else 0
        medianyoy = lastyear.median()/thisyear.median() if \
          thisyear.median()>0 and not np.isnan(thisyear.median()) \
          and not np.isnan(lastyear.median()) else 0

        self.features.extend([weekday_mean, weekend_mean, \
                              workday_mean, worknight_mean, meanyoy, medianyoy])
        self.feature_names.extend(['weekday mean', 'weekend mean', \
          'workday mean', 'worknight mean', 'meanyoy', 'medianyoy'])

        self.features.extend([weekday_median/weekend_median if \
            weekend_median>0 and not np.isnan(weekend_median) else 0,\
          workday_median/worknight_median if \
            worknight_median>0 and not np.isnan(worknight_median) else 0,\
          workday_median/weekend_median if \
            weekend_median>0 and not np.isnan(weekend_median) else 0])
        self.feature_names.extend(['weekday/weekend med', \
          'workday/worknight med', 'workday/weekend med'])
                              

        # First and second derivatives
        deriv = self.s[1:].values - self.s[:-1].values
        deriv_median = np.median(deriv)
        deriv_mean = np.mean(deriv)
        deriv_abs_median = np.median(np.abs(deriv))
        deriv_abs_mean = np.mean(np.abs(deriv))
        deriv2 = deriv[1:] - deriv[:-1]
        deriv2_median = np.median(deriv2)
        deriv2_mean = np.mean(deriv2)
        deriv2_abs_median = np.median(np.abs(deriv2))
        deriv2_abs_mean = np.mean(np.abs(deriv2))
        self.features.extend([deriv_median, deriv_mean, \
                              deriv_abs_median, deriv_abs_mean, \
                              deriv2_median, deriv2_mean, \
                              deriv2_abs_median, deriv2_abs_mean])
        self.feature_names.extend(['d med', 'd mean', 'd abs med', \
          'd abs mean', 'd2 med', 'd2 mean', 'd2 abs med', 'd2 abs mean'])
        
        #High frequency power spectrum
        ps = np.abs(np.fft.fft(self.s.values))
        hfps = sum(ps[len(ps)/4:len(ps)/2])/sum(ps)
        hfps2 = sum(ps[len(ps)/8:len(ps)/2])/sum(ps)
        hfps3 = sum(ps[len(ps)/16:len(ps)/2])/sum(ps)
        if np.isfinite(hfps): self.features.extend([hfps])
        else: self.features.extend([0])
        if np.isfinite(hfps2): self.features.extend([hfps2])
        else: self.features.extend([0])
        if np.isfinite(hfps3): self.features.extend([hfps3])
        else: self.features.extend([0])
        self.feature_names.extend(['hfps','hfps2','hfps3'])
        
if __name__ == '__main__':
       # Open the output features file
       meters = [i.meter_id for i in models.Meter.objects.all()]
       out = open('/data/features.csv','w')
       # Write the features as a CSV
       outcsv = csv.writer(out)
       header = ['id']

       # Loop through the subsample file
       for meterid in meters:
           p = ProfileFeatures(meterid)
           e = EventFeatures(meterid)

           if e.features is None or p.features is None:
               print '---> Not found for '+meterid
               continue

           # If there are both profile and event features...
           if p.features is not None and e.features is not None:
               # Print the meter id to let the user know something is happening
               print meterid
               # Append the two feature vectors
               features = p.features + e.features

               # If this is the first time through, construct the output header
               if len(header)==1:
                   header.extend(p.feature_names)
                   header.extend(e.feature_names)
                   outcsv.writerow(header)
               
               # Write out the features, starting with the primary key
               outrow = [meterid]
               outrow.extend(features)
               outcsv.writerow(outrow)

       # Close the output file, we're done.
       out.close()
