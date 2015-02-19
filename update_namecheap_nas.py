#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import re
import commands
import datetime

def ip():
	response = requests.get('http://checkip.dyndns.org')
	ip = re.sub('.*Current IP Address: ', '', response.text)
	ip = re.sub('<.*$', '', ip)
	return ip.strip('\n')

def internal_ip():
	ip = commands.getoutput("ifconfig eth0")
	ip = re.search('inet addr:(\d+.\d+.\d+.\d+)', ip).group(1)
	return ip.strip('\n')

def update_namecheap():
	namecheap_update_url = 'https://dynamicdns.park-your-domain.com/update?host=nas&domain=crespo.in&password=e0d97477ea494beeaac5ffd95b111a0d&ip={0}'
	response = requests.get(namecheap_update_url.format(ip()))
	#print(response.text)
	return re.sub(r'<[^>]*>', ' ', response.text).strip().split('  ')

def main():
	output = open('/volume1/homes/fernando/log/namecheap_updated.log', 'w')
	date = datetime.datetime.today().strftime('%d/%m/%Y %H:%M:%S')
	if update_namecheap()[5] == 'true':
		msg = 'Updated succesful'
	else:
		msg = 'Error updating'
	print(date + " - " + msg + " - IP: " + ip() + " - IPINTERNO: " + internal_ip())
	output.write(date + " - " + msg + " - IP: " + ip() + " - IPINTERNO: " + internal_ip())
	output.close()

if __name__ == '__main__':
	main()
