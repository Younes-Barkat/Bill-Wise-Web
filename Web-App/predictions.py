#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import numpy as np
import pandas as pd
import cv2
import pytesseract
from glob import glob
import spacy 
import re
import string
import warnings
warnings.filterwarnings('ignore')

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_ner = spacy.load(os.path.join(BASE_DIR, 'output', 'model-best'))


def cleanText(txt):
    whitespace = string.whitespace
    punctuation = '!"#$%&\'-()*+:;<=>?[\\]^_`{|}~'
    tableWhitespace = str.maketrans('','',whitespace)
    tablePunctuation = str.maketrans('','',punctuation)
    text = str(txt)

    removeWhitespace = text.translate(tableWhitespace)
    removePunctuation = removeWhitespace.translate(tablePunctuation)

    return str(removePunctuation)

class group_gen():
    def __init__(self):
        self.id = 0
        self.text = ''

    def get_group(self,text):
        if self.text == text:
            return self.id
        else:
            self.id += 1
            self.text = text
            return self.id



def parser(text, label): 
    if label == 'ID':
        text = text.lower()
        text = re.sub(r'\D', '', text)

    elif label == 'TOTAL':
        dec_match = re.search(r'[,](\d{2})$', text.strip())
        digits_only = re.sub(r'\D', '', text)
        if dec_match and len(digits_only) > 2:
            integer_part = digits_only[:-2]
            decimal_part = digits_only[-2:]
            text = integer_part + ',' + decimal_part
        else:
            text = digits_only

    elif label == 'DATE' :
        text = text.lower()
        allowed_special_characters = '/'
        text = re.sub(r'[^0-9{} ]'.format(allowed_special_characters), '', text)

    elif label == 'SN' or label == 'CN':
        text = text.lower()
        allowed_special_characters = ','
        text = re.sub(r'[^A-Za-z{} ]'.format(allowed_special_characters), '', text)

    elif label == 'IBAN' :
        text = text.lower()
        text = re.sub(r'[^A-Za-z0-9{} ]','', text)

    return text





grp_gen = group_gen()



def get_predictions(image): 
    grp_gen.id = 0
    grp_gen.text = ''
    tess_data = pytesseract.image_to_data(image)
    tess_list = list(map(lambda x: x.split('\t'), tess_data.split('\n')))
    df = pd.DataFrame(tess_list[1:], columns= tess_list[0])
    df.dropna(inplace=True)
    df['text'] =df['text'].apply(cleanText)
    
    df_clean = df.query('text != "" ')
    content = " ".join([w for w in df_clean['text']])
    print(content)
    
    doc = model_ner(content)
    
    docjson = doc.to_json()
    doc_text = docjson['text']
    
    
    df_tokens = pd.DataFrame(docjson['tokens'])
    df_tokens.head()
    
    
    df_tokens = pd.DataFrame(docjson['tokens'])
    df_tokens['token'] = df_tokens[['start','end']].apply(lambda x:doc_text[x['start']:x['end']], axis = 1)
    
    df_tokens.head(10)
    
    
    
    right_table = pd.DataFrame(docjson['ents'])[['start','label']]
    df_tokens = pd.merge(df_tokens,right_table, how = "left", on='start')
    
    df_tokens.fillna('O', inplace=True)
    
    
    # In[15]:
    df_clean['end']= df_clean['text'].apply(lambda x:len(x)+1).cumsum() - 1
    df_clean['start'] = df_clean[['text','end']].apply(lambda x: x['end'] - len(x['text']), axis = 1)
    
    
    
    
    df_info = pd.merge(df_clean,df_tokens[['start','token','label']],how="left",on="start")
    bb_df = df_info.query("label != 'O' ")

    bb_df['label'] = bb_df['label'].apply(lambda x: x[2:])
    
    
    
    bb_df['group'] = bb_df['label'].apply(grp_gen.get_group)
    
    
    bb_df[['left','top','width','height']] = bb_df[['left','top','width','height']].astype(int)
    bb_df['right'] = bb_df['left'] + bb_df['width']
    bb_df['bottom'] = bb_df['top'] + bb_df['height']
    
    
    
    col_group = ['left','top','right','bottom','label','token', 'group']
    group_tag_img = bb_df[col_group].groupby(by='group')
    
    
    
    
    img_tagging = group_tag_img.agg({
    
        'left':min,
        'right':max,
        'top':min,
        'bottom':max,
        'label':lambda x: x.iloc[0],
        'token':lambda x: " ".join(x)
    
    })
    
    
    
    
    img_bb = image.copy()
    for l,r,t,b,label,token in img_tagging.values:
        cv2.rectangle(img_bb,(l,t),(r,b),(255,0,0),2)
        cv2.putText(img_bb,label,(l,t),cv2.FONT_HERSHEY_PLAIN,1,(0,0,255),2)
    
    
    
    info_array = df_info[['token','label']].values
    entities = dict(ID=[],DATE=[],SN=[],CN=[],IBAN=[],TOTAL=[])
    for token, label in info_array:
        bio_tag = label[:1]
        label_tag = label[2:]

        if bio_tag not in ('B', 'I'):
            continue

        text = parser(token, label_tag)

        if bio_tag == 'B':
            entities[label_tag].append(text)
        else:
            if entities[label_tag]:
                if label_tag in ('SN', 'CN'):
                    entities[label_tag][-1] = entities[label_tag][-1] + " " + text
                else:
                    entities[label_tag][-1] = entities[label_tag][-1] + text
            else:
                entities[label_tag].append(text)
    
    return img_bb, entities    
    
    
