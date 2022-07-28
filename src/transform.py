import sys
import os
import yaml
import pandas as pd
import glob
import xml.etree.ElementTree as ET

if len(sys.argv) != 3:
    sys.stderr.write('Arguments error. Usage:\n')
    sys.stderr.write(
        '\tpython3 src/transform.py data/prepared data/transformed\n'
    )
    sys.exit(1)

params = yaml.safe_load(open('params.yaml'))['ingest']

images = os.path.join(sys.argv[1],f"v{params['dcount']}",'images')
annots = os.path.join(sys.argv[1],f"v{params['dcount']}",'annotations')

outputannot = os.path.join(sys.argv[2],f"v{params['dcount']}")
os.makedirs(outputannot, exist_ok=True)

def generate_data( Annotpath, Imagepath):
    information={'xmin':[],'ymin':[],'xmax':[],'ymax':[],'ymax':[],'name':[] ,'label':[], 'image':[]}
    for file in sorted(glob.glob(str(Annotpath+'/*.xml*'))):
        dat=ET.parse(file)
        for element in dat.iter():    
            if 'object'==element.tag:
                for attribute in list(element):
                    if 'name' in attribute.tag:
                        name = attribute.text
                        file_name = file.split('/')[-1][0:-4]
                        f = os.path.basename(file_name)
                        information['label'] += [name]
                        information['name'] +=[f+'.jpg']
                        information['image'] += [os.path.join(images,f+'.jpg')]
                    if 'bndbox'==attribute.tag:
                        for dim in list(attribute):
                            if 'xmin'==dim.tag:
                                xmin=int(round(float(dim.text)))
                                information['xmin']+=[xmin]
                            if 'ymin'==dim.tag:
                                ymin=int(round(float(dim.text)))
                                information['ymin']+=[ymin]
                            if 'xmax'==dim.tag:
                                xmax=int(round(float(dim.text)))
                                information['xmax']+=[xmax]
                            if 'ymax'==dim.tag:
                                ymax=int(round(float(dim.text)))
                                information['ymax']+=[ymax]
    return pd.DataFrame(information)


print("-------------------------------")
print("Converting XML files to dataframe.....")
print("-------------------------------")
df = generate_data(annots,images)
df.to_pickle(os.path.join(outputannot,'v{}.pkl'.format(params['dcount'])))