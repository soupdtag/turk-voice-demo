# script to delete all existing hits
# author: chris song

import boto3

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
# delete HITs
# ---------------------------------------------------------------------------------------
def deleteHITs(client):

	response = client.list_hits(MaxResults=10)

	print('deleting all HITs...')
	print(' ')

	for item in response['HITs']:
		# delete HIT
		HITId = item['HITId']
		print(' deleting HIT Id: ', HITId)
		response = client.delete_hit(HITId=HITId)
		print('  ... done.')

	print(' ')
	print('...done.')


# ---------------------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------------------
if __name__ == "__main__":
	# parse config info
	with open("config.txt", "r+") as config:
		for line in config: exec(line)

	# initiate connection to turk server
	client, preview_url = init(profile, env)

	# review HITs
	deleteHITs(client)