#!/usr/bin/env python

import os
from os.path import join

from retry import retry
from pwd import getpwnam, getpwuid

def get_pzserver_pid(user):

	proc = '/proc'
	uid = getpwnam(user).pw_uid

	for pid in os.listdir(proc):

		if not pid.isnumeric():
			continue

		filepath = join(proc, pid)
		fileinfo = os.stat(filepath)
		if uid != fileinfo.st_uid:
			continue

		filepath = join(proc, pid, 'comm')
		with open(filepath) as fd:
			command = fd.read().strip()

		#print(command)
		if command not in [ 'ProjectZomboid3', 'ProjectZomboid6' ]:
			continue

		return pid

@retry(tries=5)
def get_mod_updates(mods):

	steam_url = 'https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/'

	if len(mods) == 0:
		return {}

	data = {}
	data['itemcount'] = len(mods)

	for i, workshop_id in enumerate(mods):
		key = 'publishedfileids[%d]' % i
		data[key] = workshop_id

	jsondata = requests.post(steam_url, data=data).json()

	mods = {}

	for workshop_item in jsondata['response']['publishedfiledetails']:

		mod_id = workshop_item['publishedfileid']

		mods[mod_id] = {
			'name':    workshop_item['title'],
			'updated': workshop_item['time_updated'],
		}

	return mods