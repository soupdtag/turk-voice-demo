# script to review + automatically accept/reject hits
# author: chris song

import boto3
import xmltodict

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
# retreive and print review of hits
# ---------------------------------------------------------------------------------------
def reviewHITs(client):

	# Return info on all past (up to 10) requester's HITs
	response = client.list_hits(MaxResults=10)

	print(' ')
	print(' ')
	print('Reviewing most recent (up to 10) HITs:')
	print('-----------------------------------------------')
	print(' ')

	# --------------------------------------------------------------------------------
	# iterate through each hit
	# --------------------------------------------------------------------------------
	for r, item in enumerate(response['HITs']):

		print(' response', r)
		print(' HIT Id: ', item['HITId'])

		# Get the status of the HIT
		hit = client.get_hit(HITId=item['HITId'])
		item['status'] = hit['HIT']['HITStatus']

		# --------------------------------------------------------------------------------
		# Get a list of the Assignments that have been submitted by Workers
		# --------------------------------------------------------------------------------
		assignmentsList = client.list_assignments_for_hit(
			HITId=item['HITId'],
			AssignmentStatuses=['Submitted', 'Approved'],
			MaxResults=10
		)

		assignments = assignmentsList['Assignments']
		item['assignments_submitted_count'] = len(assignments)

		print(' # assignments submitted: ', item['assignments_submitted_count'])

		answers = []

		# --------------------------------------------------------------------------------
		# evaluating each assignment
		# --------------------------------------------------------------------------------
		for a in assignments:
			print(' ... assignment status:', a['AssignmentStatus'])
			# Retreive the attributes for each Assignment
			worker_id = a['WorkerId']
			assignment_id = a['AssignmentId']

			# Retrieve the value submitted by the Worker from the XML
			answer_dict = xmltodict.parse(a['Answer'])
			answer = answer_dict['QuestionFormAnswers']['Answer']['FreeText']
			answers.append(answer)

			print(' answers: ', answers)
			
	        	# --------------------------------------------------------------------------------
			# Approve the Assignment (if it hasn't already been approved)
			# --------------------------------------------------------------------------------
			if a['AssignmentStatus'] == 'Submitted':
				client.approve_assignment(
					AssignmentId=assignment_id,
					OverrideRejection=False
				)
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

	# review HITs
	reviewHITs(client)