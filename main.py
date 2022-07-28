import streamlit as st
import yaml
import os
import glob
import sys
import boto3
from botocore.exceptions import NoCredentialsError

ACCESS_KEY = st.secrets['ACCESS_KEY']
SECRET_KEY = st.secrets['SECRET_KEY']

@st.experimental_memo(ttl=600)
def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    try:
        s3.put_object(Bucket=bucket, Key=(s3_file+'/'))
        for root,_,files in os.walk(local_file):
            for file in files:
                s3.upload_file(os.path.join(root,file),bucket, s3_file+'/'+file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def main():
    st.title("Pedestrian Detection Pipeline")
    st.write(sys.executable)
    
    if "load_state" not in st.session_state:
        st.session_state.load_state = True
    
    imgs = []
    imgs = st.file_uploader("Choose Images (Zip File)")
    params = yaml.safe_load(open('params.yaml'))['ingest']
    
    ev = st.button('Evaluate')
    if imgs and ev and st.session_state.load_state:
        
        ddd = {'ingest': {'dcount': params['dcount']+1}}
        yaml.dump(ddd, open('params.yaml', 'w'))
        
        os.makedirs('buffer', exist_ok=True)
        for ff in os.listdir('buffer'):
            os.remove(f'buffer/{ff}')
    
        with open(f'buffer/dataset{params["dcount"]+1}.zip', "wb") as f:
            f.write(imgs.getbuffer())
        
        print('hello................', sys.executable)
        
        if not os.system("dvc repro"):
            st.success('Pipeline executed successfully')
            imgname = os.listdir("data/store/v{}/evaluated".format(params["dcount"]+1))
            preds = glob.glob("data/store/v{}/evaluated/*.*".format(params["dcount"]+1), recursive=True)
            for index,im in enumerate(preds):
                st.image(im, imgname[index])
            print('done')
            st.session_state.load_state = False
    
    if st.button('Push To S3'):
        st.session_state.load_state  = True
        uploaded = upload_to_aws(
            "data/evaluated/v{}".format(params["dcount"]), 
            'objectdetpipeline', 
            'v{}'.format(params["dcount"]))
        if uploaded:
            st.success("Uploaded to S3")
        else:
            st.error("Failed to push to S3")


main()