# script to list hits
#
# author: chris song

import boto3
from datetime import datetime, timezone

# config info provided in config.txt:
# region = 'us-east-1', profile = 'mturk-csong23', env = 'sandbox'


# ---------------------------------------------------------------------------------------
# initiate connection to mturk
# ---------------------------------------------------------------------------------------

def init(profile, env):

	# user AWS credentials (--profile)
	session = boto3.Session(profile_name = profile)
	
	# sandbox vs production environment (--env)
	if env == 'production':
		print('initializing to PRODUCTION environment...')
		endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'
		preview_url = 'https://www.mturk.com/mturk/preview'
	else:
		# invalid input defaults to sandbox environment
		if env != 'sandbox': print('invalid user input for \'environment\'')

		print('initializing to SANDBOX environment...')
		endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
		preview_url = 'https://workersandbox.mturk.com/mturk/preview'
	
	# initiate connection using above params
	client = session.client(
		service_name='mturk', endpoint_url=endpoint_url, region_name=region)

	return client, preview_url


# ---------------------------------------------------------------------------------------
# print list of hits
# ---------------------------------------------------------------------------------------
def listHITs(client):

	# Return info on all past (up to 10) requester's HITs
	response = client.list_hits(MaxResults=10)

	print(' ')
	print(' ')
	print('All requester\'s HITs (up to 10):')
	print('-----------------------------------------------')
	print(' ')

	for item in response['HITs']:

		print(' HIT Id: ', item['HITId'])
		print(' GroupId:', item['HITGroupId'])
		print(' TypeId: ', item['HITTypeId'])
		print(' Status: ', item['HITStatus'])

		expiredStatus = ' Expired ' if item['Expiration'] < datetime.now(timezone.utc) else ' Active until '
		print(expiredStatus, item['Expiration'])
		print(' # assignments pending: ', item['NumberOfAssignmentsPending'])
		print(" You can view the HITs here:")
		print(' ', preview_url + "?groupId={}".format(item['HITTypeId']))
		print(' ')


# ---------------------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------------------
if __name__ == "__main__":
	# parse config info
	with open("config.txt", "r+") as config:
		for line in config: exec(line)

	# initiate connection to turk server
	client, preview_url = init(profile, env)

	# print list of HITs
	listHITs(client)