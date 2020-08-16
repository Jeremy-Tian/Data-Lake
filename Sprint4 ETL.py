
# Parallel ETL

# In[1]:


get_ipython().run_line_magic('load_ext', 'sql')


# In[2]:


import boto3
import configparser
import matplotlib.pyplot as plt
import pandas as pd
from time import time


# # STEP 1: Get the params of the created redshift cluster 

# In[3]:


config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))
KEY=config.get('AWS','key')
SECRET= config.get('AWS','secret')

DWH_DB= config.get("DWH","DWH_DB")
DWH_DB_USER= config.get("DWH","DWH_DB_USER")
DWH_DB_PASSWORD= config.get("DWH","DWH_DB_PASSWORD")
DWH_PORT = config.get("DWH","DWH_PORT")


# In[4]:


DWH_ENDPOINT="dwhcluster.cp036ra8veyx.us-west-2.redshift.amazonaws.com" 
    
DWH_ROLE_ARN="arn:aws:iam::927367974077:role/dwhRole"


# # STEP 2: Connect to the Redshift Cluster

# In[5]:


conn_string="postgresql://{}:{}@{}:{}/{}".format(DWH_DB_USER, DWH_DB_PASSWORD, DWH_ENDPOINT, DWH_PORT,DWH_DB)
print(conn_string)
get_ipython().run_line_magic('sql', '$conn_string')


# In[6]:


import boto3

s3 = boto3.resource('s3',
                       region_name="us-west-2",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                     )

sampleDbBucket =  s3.Bucket("nyulabs")

for obj in sampleDbBucket.objects.filter(Prefix="tickets"):
    print(obj)


# In[7]:


for obj in sampleDbBucket.objects.filter(Prefix="tickets"):
    print(obj)


# # STEP 3: Create Tables

# In[8]:


get_ipython().run_cell_magic('sql', '', 'DROP TABLE IF EXISTS "sporting_event_ticket";\nCREATE TABLE "sporting_event_ticket" (\n    "id" double precision DEFAULT nextval(\'sporting_event_ticket_seq\') NOT NULL,\n    "sporting_event_id" double precision NOT NULL,\n    "sport_location_id" double precision NOT NULL,\n    "seat_level" numeric(1,0) NOT NULL,\n    "seat_section" character varying(15) NOT NULL,\n    "seat_row" character varying(10) NOT NULL,\n    "seat" character varying(10) NOT NULL,\n    "ticketholder_id" double precision,\n    "ticket_price" numeric(8,2) NOT NULL\n);')


# # STEP 4: Load Partitioned data into the cluster

# In[9]:


get_ipython().run_cell_magic('time', '', 'qry = """\n    copy sporting_event_ticket from \'s3://nyulabs/tickets/split/part\'\n    credentials \'aws_iam_role={}\'\n    gzip delimiter \';\' compupdate off region \'us-west-2\';\n""".format(DWH_ROLE_ARN)\n\n%sql $qry')


# # STEP 5: Create Tables for the non-partitioned data

# In[10]:


get_ipython().run_cell_magic('sql', '', 'DROP TABLE IF EXISTS "sporting_event_ticket_full";\nCREATE TABLE "sporting_event_ticket_full" (\n    "id" double precision DEFAULT nextval(\'sporting_event_ticket_seq\') NOT NULL,\n    "sporting_event_id" double precision NOT NULL,\n    "sport_location_id" double precision NOT NULL,\n    "seat_level" numeric(1,0) NOT NULL,\n    "seat_section" character varying(15) NOT NULL,\n    "seat_row" character varying(10) NOT NULL,\n    "seat" character varying(10) NOT NULL,\n    "ticketholder_id" double precision,\n    "ticket_price" numeric(8,2) NOT NULL\n);')


# # STEP 6: Load non-partitioned data into the cluster


# In[11]:


get_ipython().run_cell_magic('time', '', '\nqry = """\n    copy sporting_event_ticket_full from \'s3://nyulabs/tickets/full/full.csv.gz\' \n    credentials \'aws_iam_role={}\' \n    gzip delimiter \';\' compupdate off region \'us-west-2\';\n""".format(DWH_ROLE_ARN)\n\n%sql $qry')


# In[ ]:




