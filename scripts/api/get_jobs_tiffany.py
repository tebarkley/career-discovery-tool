#!/usr/bin/env python

import pandas as pd
import requests
import xmltodict
import json
from os import path, pardir
import settings
import sys
import datetime
from pandas.io.json import json_normalize

#read in dataframe from job search
master_df = pd.io.pickle.read_pickle(path.join(pardir, pardir, 'data', 'tiff_jobs_Feb9.pkl'))

#Get the job descriptions that we've already called
if path.isfile(path.join(pardir, pardir, 'data', 'job_descriptions.pkl')):
    obtained_jobs = pd.io.pickle.read_pickle(path.join(pardir, 'data', 'job_descriptions.pkl'))
    obtained = set([job_id.encode('ascii', 'ignore') for job_id in obtained_jobs.DID])
else:
    obtained_jobs = pd.DataFrame()
    obtained = set()

#create a set of the job ids already found to be valid
if path.isfile(path.join(pardir, 'data', 'invalid_job_ids.pkl')):
    invalid = set(pd.io.pickle.read_pickle(path.join(pardir, 'data', 'invalid_job_ids.pkl')))
else:
    invalid = set()

 #get list of job ids for which we still need to obtain descriptions
job_ids = [job_id.encode('ascii', 'ignore') for job_id in master_df.DID]
job_ids = [job_id for job_id in job_ids if job_id not in invalid and job_id not in obtained]

#function for api call
def get_jobs(num_jobs=500, invalid=invalid):
    daily_jobs_call = pd.DataFrame()
    for i, job_id in enumerate(job_ids):
        parameters = {'DeveloperKey': settings.CB_API_KEY, 
                      'DID': job_id}
        r = requests.get('http://api.careerbuilder.com/v3/job/', params=parameters)
        o = xmltodict.parse(r.content)
        j = json.dumps(o)
        raw_df = pd.read_json(j)
        if 'Job' in raw_df.index:
            new_df = json_normalize(raw_df.T.Job)
            daily_jobs_call = pd.concat([daily_jobs_call, new_df], ignore_index=True)
        else:
            invalid.add(job_id)
        if i == num_jobs - 1:
            break
    return daily_jobs_call, invalid

jobs, invalid = get_jobs()

#write invalid jobs to a pkl file
if invalid:
    invalid_series = pd.Series(list(invalid))
    invalid_series.to_pickle(path.join(pardir, pardir, 'data', 'invalid_job_ids.pickle'))

#write today's jobs to a file
filetime = str(datetime.datetime.now()).replace(' ', '_').replace(':', '_').replace('.','_').replace('-','_')[:16]
jobs.to_pickle(path.join(pardir, pardir, 'data', 'no_git','jobs_call_' + filetime + '.pkl'))

#write jobs obtained to data to a file
all_jobs = pd.concat([obtained_jobs, jobs], ignore_index=True)
all_jobs.to_pickle(path.join(pardir, pardir, 'data', 'job_descriptions.pkl'))