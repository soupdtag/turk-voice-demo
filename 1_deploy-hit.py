# deploy mturk HIT accepting voice recording from worker
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
# deploy HIT
# ---------------------------------------------------------------------------------------

def deployHITs(client, preview_url):

	# -------------------------------------------------------------------------------
	# HIT metadata
	# -------------------------------------------------------------------------------
	TaskAttributes = {
	    'MaxAssignments': 5,                 
	    'LifetimeInSeconds': 60*60,           
	    'AssignmentDurationInSeconds': 60*10, 
	    'Reward': '0.05',                     
	    'Title': 'Provide one-word description for a sound',
	    'Keywords': 'sound, label',
	    'Description': 'Label the sound using one word.'
	}

	# -------------------------------------------------------------------------------
	# sounds to be played in HITs
	# -------------------------------------------------------------------------------
	# sound host directory
	sounds_host = 'https://people.csail.mit.edu/csong23/audio-tests/'
	# all file names of sounds to be played
	sounds = ['car-start.wav', 'dog-bark.wav', 'modem-fax.wav', 'sos-morse.wav']

	# -------------------------------------------------------------------------------
	# HIT render layout
	# -------------------------------------------------------------------------------
	html_layout = open('./template.html', 'r').read()
	QUESTION_XML = """<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
	        <HTMLContent><![CDATA[{}]]></HTMLContent>
	        <FrameHeight>650</FrameHeight>
	        </HTMLQuestion>"""
	question_xml = QUESTION_XML.format(html_layout)

	# -------------------------------------------------------------------------------
	# HIT creations
	# -------------------------------------------------------------------------------
	results = []
	hit_type_id = ''

	# loop through each sound
	for sound in sounds:
		response = client.create_hit(
			**TaskAttributes,
			Question=question_xml.replace('${content}',sounds_host+sound)
		)

		hit_type_id = response['HIT']['HITTypeId']
		results.append({
			'sound': sound,
			'hit_id': response['HIT']['HITTypeId']
		})

	print(' ')
	print("You can view the HITs here:")
	print(preview_url + "?groupId={}".format(hit_type_id))
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

	# deploy HITs
	deployHITs(client, preview_url)