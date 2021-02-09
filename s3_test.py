from s3 import s3
import random
import string

def main():
    bucket_name = "demo-ca-test-" + ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
    s3_model = s3()
    print(f"Creating bucket: {bucket_name}")
    response = s3_model.create_bucket(bucket_name)
    print(response)
    new_bucket = s3_model.get_bucket(bucket_name)
    print("Creating file 1")
    response = new_bucket.create_object("test.txt")
    print(response)
    new_object = new_bucket.get_object("test.txt")
    print("Updating file 1")
    new_object.content = "This is a test file".encode('utf-8')
    new_object.update()
    print("Deleting file 1")
    new_bucket.delete_object("test.txt")
    print("Creating file 2")
    new_bucket.create_object("test2.txt")
    print("Updating file 2")
    new_object2 = new_bucket.get_object("test2.txt")
    new_object2.content = "This is another test file".encode('utf-8')
    new_bucket.update()
    print(new_object2.content_length)
    print("Deleting Bucket")
    s3_model.delete_bucket(bucket_name)


if __name__ == "__main__":
    main()