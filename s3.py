from typing import List
import boto3, botocore

class s3Object(object):
	def __init__(self, bucket:'s3Bucket', key:str, s3client:botocore.client, fetch_content=False):
		super(s3Object, self).__init__()
		self.bucket = bucket
		self.key = key
		self.client = s3client
		self.arn = f"arn:aws:s3:::{bucket}/{key}"
		self.content = b""
		self.exists = False
		self.content_length = 0
		self.last_updated_timestamp = None

		self.fetch(with_content=fetch_content)

	def fetch(self, with_content=False):
		"""Get object metadata and, optionally, file contents from s3"""
		# check if file exists
		# grab last updated timestamp
		# get content if with_content flag enabled
		resp_obj = {}
		try:
			if with_content:
				resp_obj = self.client.get_object(Bucket=self.bucket, Key=self.key)
				self.content = resp_obj['Body'].read()
			else:
				resp_obj = self.client.head_object(Bucket=self.bucket, Key=self.key)
			self.last_updated_timestamp = resp_obj['LastModified']
			self.content_length = resp_obj['ContentLength']
			self.exists = True
		except self.client.exceptions.NoSuchKey:
			self.content = b""
			self.exists = False
			self.content_length = 0
			self.last_updated_timestamp = None

	def update(self):
		"""Push changes to file contents to s3"""
		resp_obj = self.client.put_object(Bucket=self.bucket, Key=self.key, Body=self.content)
		self.fetch(with_content=False)
		return resp_obj


class s3Bucket(object):
	def __init__(self, name:str, s3_client:botocore.client):
		super(s3Bucket, self).__init__()
		self.name = name
		self.arn = f"arn:aws:s3:::{name}"
		self.client = s3_client
		self.objects: List[s3Object] = []

		self.fetch(with_content=False)

	def create_object(self, key: str):
		"""Create a new empty object"""
		resp_obj = self.client.put_object(Bucket=self.name, Key=key, Body=b"")
		self.objects.append(s3Object(self.name, key, self.client, fetch_content=False))
		return resp_obj

	def delete_object(self, key: str):
		"""Delete an object by its key"""
		s3_object = self.get_object(key)
		if not s3_object:
			raise ValueError("Object not found in bucket")

		# delete s3 object and class instance by key
		resp_obj = self.client.delete_object(
			Bucket=self.name,
			Key=key,
		)
		self.objects.remove(s3_object)
		return resp_obj

	def get_object(self, key: str) -> s3Object:
		"""Get an s3Object in s3Bucket by key"""
		for s3_object in self.objects:
			if s3_object.key == key:
				return s3_object
		return None

	def fetch(self, with_content=False):
		"""Update bucket object metadata, and optionally object content"""
		# note: we are not currently handling pagination
		# limit of 1,000 objects per bucket
		# update List of objects
		resp_obj = self.client.list_objects_v2(Bucket=self.name)
		for s3_object_info in resp_obj.get('Contents', []):
			s3_object = self.get_object(s3_object_info['Key'])
			if s3_object:
				s3_object.fetch(with_content=with_content)
			else:
				self.objects.append(s3Object(self.name, s3_object_info['Key'], self.client, fetch_content=with_content))

	def update(self):
		"""Update contents of all files within the bucket"""
		for s3_object in self.objects:
			s3_object.update()

	def empty_bucket(self):
		"""Delete all files in bucket"""
		self.fetch(with_content=False)
		# delete all objects from bucket
		resp_obj = self.client.delete_objects(
			Bucket=self.name,
			Delete={
				'Objects': [{'Key': s3_object.key} for s3_object in self.objects]
			}
		)
		self.objects = []
		return resp_obj


class s3(object):
	def __init__(self, region: str = None, profile_name: str = None):
		super(s3, self).__init__()

		if profile_name:
			profile = boto3.Session(profile_name=profile_name)
		else:
			profile = boto3
		if not region:
			# boto will use the default region
			self.resource = profile.resource('s3')
			self.client = profile.client('s3')
		else:
			self.resource = profile.resource('s3', region_name=region)
			self.client = profile.client('s3', region_name=region)
		self.buckets: List[s3Bucket] = []

	def create_bucket(self, bucket_name: str):
		"""Create a new bucket"""

		resp_obj = self.client.create_bucket(Bucket=bucket_name)
		bucket = s3Bucket(bucket_name, self.client)
		self.buckets.append(bucket)
		return resp_obj

	def get_bucket(self, bucket_name: str) -> 's3Bucket':
		"""Get bucket by bucket name"""

		for bucket in self.buckets:
			if bucket.name == bucket_name:
				return bucket
		return None

	def delete_bucket(self, bucket_name: str):
		"""Removes all data in a bucket and deletes it"""

		bucket = self.get_bucket(bucket_name=bucket_name)
		if not bucket:
			raise ValueError("Bucket not managed by this s3 object or does not exist.")
		# delete objects in bucket
		bucket.empty_bucket()
		# delete bucket in S3
		self.client.delete_bucket(Bucket=bucket_name)
		# remove bucket from List of buckets
		self.buckets.remove(bucket)

	def update(self):
		"""Update contents of all buckets in the model"""
		for bucket in self.buckets:
			bucket.update()

	def fetch_buckets(self, buckets: List[s3Bucket] = None, with_content=False):
		"""refresh bucket and object data for specified buckets or self.buckets"""
		if not buckets:
			buckets = self.buckets
		else:
			for bucket in buckets:
				if bucket not in self.buckets:
					raise ValueError(f"Bucket '{bucket.name}' not managed by this s3 object.")

		for bucket in buckets:
			bucket.fetch(with_content=with_content)