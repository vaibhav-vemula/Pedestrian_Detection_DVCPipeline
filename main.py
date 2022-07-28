import streamlit as st
import yaml
import os
import glob
import sys

def main():
    st.title("Pedestrian Detection Pipeline")
    st.write(sys.executable)
    imgs = st.file_uploader("Choose Images (Zip File)")
    
    if imgs:
        params = yaml.safe_load(open('params.yaml'))['ingest']
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
    else:
        return

if __name__ == '__main__':
    main()