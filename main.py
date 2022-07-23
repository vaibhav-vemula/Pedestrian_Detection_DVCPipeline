import streamlit as st
import yaml
import os
import glob

def main():
    st.title("Hello World")
    
    imgs = st.file_uploader("Choose Images (Zip File)")
    
    if imgs:
        params = yaml.safe_load(open('params.yaml'))['ingest']
        ddd = {'ingest': {'dcount': params['dcount']+1}}
        yaml.dump(ddd, open('params.yaml', 'w'))
        
        for ff in os.listdir('buffer'):
            os.remove(f'buffer/{ff}')
    
        with open(f'buffer/dataset{params["dcount"]+1}.zip', "wb") as f:
            f.write(imgs.getbuffer())
        
        if not os.system("dvc repro"):
            imgname = os.listdir("data/store/v{}/predictions".format(params["dcount"]+1))
            preds = glob.glob("data/store/v{}/predictions/*.*".format(params["dcount"]+1), recursive=True)
            for index,im in enumerate(preds):
                st.image(im, imgname[index])
            print('done')
        
    else:
        return


if __name__ == '__main__':
    main()