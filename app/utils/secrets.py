import json
import boto3
from botocore.exceptions import ClientError

def get_secret():
    """Fetches the secret from AWS Secrets Manager and returns it as a dictionary."""
    secret_name = "cracktify/server/.env"
    region_name = "ap-southeast-1"

    client = boto3.client(
        service_name="secretsmanager",
        region_name=region_name
    )

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise Exception(f"Failed to fetch secret: {e}")

    secret_string = response["SecretString"]
    return json.loads(secret_string)