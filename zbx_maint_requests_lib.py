#!/usr/bin/python

from datetime import datetime, timedelta
import time
import json
import sys
import requests
import argparse

# use get options for this, going forward
user = ''
password = ''
hostnames = ''
server = ''
headers = {'content-type': 'application/json-rpc'}

# setup time periods we need unix time stamps :-|
now = int(time.time())
x = datetime.now() + timedelta(seconds=3600)
float = str(time.mktime(x.timetuple()))
until = int(float.split('.')[0])

parser = argparse.ArgumentParser(description='This program sets a 1 hour maintenance period on the given hosts')
parser.add_argument('-p', action='store', dest='password', help='zabbix user password')
parser.add_argument('-u', action='store', dest='user', help='zabbix user name')
parser.add_argument('-n', action='append', dest='hosts', default=[], help='comma separated list of host names to put in maitenance')
parser.add_argument('-s', action='store', dest='server', help='the zabbix server url')

results = parser.parse_args()
user = results.user
password = results.password
hostnames = results.hosts
server = results.server

api = 'http://' + server + '/zabbix/api_jsonrpc.php'
print api
def get_token():
	'''
	get the auth token for the given credntials
	need to change this so the user_name & password are passed in
	'''
        data = {'jsonrpc': '2.0', 'method': 'user.login', 'params': {'user': user, 'password': password},
            'id': '0'}
	re = requests.get(api, headers=headers, json=data)
	if re.status_code == requests.codes.ok:
	    return_data = re.json()
	    authtoken = return_data['result']
	else:
	    authtoken = False			
		 
 	return authtoken

 
def get_host_id(hostname):
    '''
    We have to have host_id zabbix only uses this
    '''
	
    token = get_token()
    data = {"jsonrpc": "2.0", "method": "host.get", 
		"params": {"output": "extend", 
		"filter": {"host": hostname }
	}, 
	"auth": token, "id": 0}

    re = requests.get(api, headers=headers, json=data)
    if re.status_code == requests.codes.ok:
        return_data = re.json()
	host_id = return_data['result'][0]['hostid']
    else:
	host_id = False
    return host_id

def get_maintenance_id(hostname):
    '''
    get the maintenance id if it exists, you can only have one id with the maintenance name
    	thus we must delete it if it exists befoe we can set a new maintenance period
    	'''
    
    host_id = get_host_id(hostname)
    token = get_token()
    data = {"jsonrpc": "2.0", "method": "maintenance.get", 
    "params": {"output": "extend", "selectGroups": "extend",
            		"selectTimeperiods": "extend", "hostids": host_id},
    "auth": token, "id": 0}
    re = requests.get(api, headers=headers, json=data)
    if re.status_code == requests.codes.ok:
        return_data = re.json()
        try:
    	    maint_id = return_data['result'][0]['maintenanceid']
        except: 
            maint_id = False
    else:
        maint_id =False

    return maint_id    

def del_maintenance(maint_id):
    '''
    we must delete the exisitng id befoe we can create a new one with the same name
    '''
    token = get_token()
    data = {"jsonrpc": "2.0", "method": "maintenance.delete", 
    "params": [maint_id], "auth": token, "id": 1}
    
    re = requests.get(api, headers=headers, json=data)
    if re.status_code == requests.codes.ok:
        deleted = True
    else:
        deleted = False
    return deleted 


def start_maintenance(host_id):
    '''
    Set a new maintenance period
    ''' 
	
    token = get_token()
    data = {"jsonrpc": "2.0", "method": "maintenance.create", "params":
        {"name": "pause_" + hostname, "active_since": now, 
        "active_till": until, "hostids": [host_id], "timeperiods":
        [{"timeperiod_type": 1, "period": 3600}]}, "auth": token, "id": 1}
    
    re = requests.get(api, headers=headers, json=data)
    if re.status_code == requests.codes.ok:
        maint_set = True
    else:
        maint_set = False
    return maint_set 


for hostname in hostnames:
    host_id = get_host_id(hostname)
    print 'The host id for {} is {} '.format(hostname, host_id)
    # check if a maintenance period exisits for this host
    maint_id = get_maintenance_id(hostname)

    # del existing maintenance id if it exist, so we can set a new one
    if maint_id:
        del_maintenance(maint_id)

    # set new maintenance period
    if start_maintenance(host_id):
	print 'Maintenance period for {} is set for 1 hour'.format(hostname)
    else:
	print 'Something went wrong; no maintenance period set for {} '.format(hostname)




