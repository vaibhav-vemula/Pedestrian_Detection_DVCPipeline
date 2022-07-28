import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError

ACCESS_KEY = st.secrets['ACCESS_KEY']
SECRET_KEY = st.secrets['SECRET_KEY']

def main():
    st.title("Clear S3")
    
    tt = st.button("Clearrrr")
    if tt:
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        response = s3.list_objects_v2(Bucket='objectdetpipeline')
        if 'Contents' in response:
            for item in response['Contents']:
                print('deleting file', item['Key'])
                s3.delete_object(Bucket='objectdetpipeline', Key=item['Key'])
                while response['KeyCount'] == 1000:
                    response = s3.list_objects_v2(
                    Bucket='objectdetpipeline',
                    StartAfter=response['Contents'][0]['Key'],
                    )
                for item in response['Contents']:
                    print('deleting file', item['Key'])
                    s3.delete_object(Bucket='objectdetpipeline', Key=item['Key'])
                    
main()