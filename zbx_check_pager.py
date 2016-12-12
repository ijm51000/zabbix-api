#!/usr/bin/python

from datetime import datetime, timedelta
import time
import json
import sys
import requests
import argparse
import socket

# use get options for this, going forward
zabbix1 = 'ip server 1'
zabbix2 = 'ip server 2'
user = ''
password = ''
hostnames = ''
server = ''
headers = {'content-type': 'application/json-rpc'}


class MyParser(argparse.ArgumentParser):
     def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)
parser = MyParser()
parser = argparse.ArgumentParser(description='This program sets a 1 hour maintenance period on the given hosts')
parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-p', action='store', dest='password', required=True, help='zabbix user password')
parser.add_argument('-u', action='store', dest='user', required=True, help='zabbix user name')
# parser.add_argument('-s', action='store', dest='server', required=True, help='the zabbix server url')


options = parser.parse_args()
user = options.user
password = options.password
# server = options.server

# api = 'http://' + server + '/zabbix/api_jsonrpc.php'

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

def get_active_zabbix_server(server):
        '''
        check which servers are active
        '''
        print server
        zbx_port = 10051
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.settimeout(5)
        print 'Checking if Zabbix Server at %s is available' % (server)
        try:
                skt.connect((server, zbx_port))
                print 'Connected to zabbix at IP %s on port %s' % (server, zbx_port)
                return server
        except socket.error, exception:
                print 'Zabbix server not available at IP %s  on port %s error is: %s\n' % (server, zbx_port, exception)
                return False




def check_pager_actions(authtoken):

	data = {
		"jsonrpc":"2.0","method":"action.get",
		"params": {
			"output":"extend", 
			"selectConditions":"extend", 
			"selectOperations":"extend", 
			"mediatypeids":"5",
			"filter": { 
				"status": "1"
			}
		},
		"auth":authtoken,
		"id":0
	}

	re = requests.get(api, headers=headers, json=data)
	if re.status_code == requests.codes.ok:
	    return_data = re.json()
	    return return_data
	else:
	    return_data = False			
		 
 	return authtoken

server = get_active_zabbix_server(zabbix2)
if not server:
	server = get_active_zabbix_server(zabbix1)
if not server:
	print 'No zabbix server found, bigger problems, just going to exit'
	sys.exit(0)

api = 'http://' + server + '/zabbix/api_jsonrpc.php'

authtoken = get_token()

pager_data = check_pager_actions(authtoken)
print pager_data['result']
if not pager_data['result']:
	print 'nothing is disabled'
else:
	print 'error there are pager items disbaled'
	
	

