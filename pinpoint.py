import boto3, random, string, os, botocore, json

class pinpoint(object):
	"""Python Pinpoint client wrapper"""
	def __init__(self, client:boto3.client=pipo):
		super(pinpoint, self).__init__()
		self.client = client
		self.projects = []

	def create_project(self, project:dict=None) -> pinpoint_project:
		if project == None:

		project = pinpoint_project(client_project=project)
		self.projects.append(project)
		return project

	def delete_project(self, name=None, app_id=None, arn=None):
		if not name is None:
			app_filter = filter(lambda x: (x.name == name), self.projects)
			if len(list(app_filter)) == 1:
				for app_filter in out:
					app_id = app_filter.id
			else:
				raise Exception("project does not exist in memory, cannot reference by name.")
		elif not app_id is None:
			pass
		elif not arn is None:
			app_id = 0
		else:
			raise Exception("No identifier provided.")
		try:
			resp_obj = self.client.delete_app(ApplicationId=str(app_id))
			self.projects = list(filter(lambda x:x.id == app_id, self.projects))
		except botocore.client.ClientError as e:
			raise
		return resp_obj


	def send_message(self, number="4193888164", message="Run. Now."):
		pass

	def create_segment_import_s3(self, s3Bucket=None, Key:string=None):
		# if key is not none check for key's existance
			# then wrap single item in list.
		# else every file in the bucket is added to the list for import.
		ImportJobRequest={
			'DefineSegment': True,
			'Format': 'CSV',
			'RegisterEndpoints': True,
			'RoleArn': '', # create a role for this
			'S3Url': f"s3://{s3Bucket}/{Key}",
			'SegmentId': name,
			'SegmentName': name
		}
		return self.client.create_import_job(ApplicationId=ApplicationId, ImportJobRequest=ImportJobRequest)

	def create_segment(self, WriteSegmentRequest=None, ApplicationId=None):
		if ApplicationId is None:
			ApplicationId = self.projects[-1].id

		if WriteSegmentRequest is None:
			WriteSegmentRequest = {
				"Name": list(filter(lambda x: x.id == ApplicationId, self.projects))[0].name,
				"tags":{},
				"SegmentGroups": {
					"Groups": [
						{
							"SourceSegments":[],
							"SourceType": "ALL",
							"Type": "ANY"
						}
					],
					"Include":"ALL"
				}
			}

		return self.client.create_segment(WriteSegmentRequest=WriteSegmentRequest,
		ApplicationId=ApplicationId)

	def create_campaign(self):
		pass
