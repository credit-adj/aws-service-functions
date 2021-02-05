import boto3, random, string, os, botocore, json

class pinpoint_project(object):
	"""AWS Pinpoint project"""
	def __init__(self, client_project=None):
		super(pinpoint_project, self).__init__()
		if client_project == None:
			self._client_project = pipo.create_app(CreateApplicationRequest={'Name':"demo-"+"".join(random.choice(string.ascii_letters) for _ in range(12)), 'tags':{'stage':'demo'}})["ApplicationResponse"]
		else:
			self._client_project = client_project
		self.name = self._client_project["Name"]
		self.tags = self._client_project["Tags"]
		self.arn = self._client_project["Arn"]
		self.id = self._client_project["Id"]


	def __str__(self):
		return f"{self.id}, {self.arn}, {self.name}, {self.tags}"
