import boto3, random, string, os, botocore, json

class pinpoint_campaign(object):
	"""AWS Pinpoint campaign"""
	def __init__(self, arg):
		super(pinpoint_campaign, self).__init__()
		self.arg = arg
