# -*- coding: utf-8 -*-
"""Untitled11.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IrNMxNQ_QPMOkfGrZDPSkSr62pRcinBT
"""

from autocorrect import Speller
from num2words import num2words
import re
import PIL
import easyocr
import numpy as np
import pandas as pd 
import cv2 
import os
import glob

def remove_end_spaces(string):
    return "".join(string.rstrip())

def autocorrection(url) :
    path = r'C:\Users\Lenovo\OneDrive\Bureau\4DS6\4DS6\4DS6\crm1\static\images/' + url
    image = cv2.imread(path)
    emptycheck = cv2.imread(r'C:\Users\Lenovo\OneDrive\Bureau\4DS6\4DS6\4DS6\crm1\static\images\vierge.tif')
    resizedempty = cv2.resize(emptycheck,(2365,1100), interpolation = cv2.INTER_AREA)
    resizedcheque = cv2.resize(image,(2365,1100), interpolation = cv2.INTER_AREA)
    grayempty=cv2.cvtColor(resizedempty,cv2.COLOR_RGB2GRAY)
    graycheque=cv2.cvtColor(resizedcheque,cv2.COLOR_RGB2GRAY)
    MAX_FEATURES = 5000 
    GOOD_MATCH_PERCENT = 0.50
    orb = cv2.ORB_create(MAX_FEATURES)
    keypoints1, descriptors1 = orb.detectAndCompute(grayempty, None)
    keypoints2, descriptors2 = orb.detectAndCompute(graycheque, None)
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors1, descriptors2, None)
    matches2=list(matches)
    matches2.sort(key=lambda x: x.distance, reverse=False)
    numGoodMatches = int(len(matches2) * GOOD_MATCH_PERCENT)
    matches2 = matches2[:numGoodMatches]
    imMatches = cv2.drawMatches(grayempty, keypoints1, graycheque, keypoints2, matches, None)
    cv2.imwrite("matches.jpg", imMatches)
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)
    for i, match in enumerate(matches2):
      points1[i, :] = keypoints1[match.queryIdx].pt
      points2[i, :] = keypoints2[match.trainIdx].pt
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
    height, width= graycheque.shape
    alignedtemplate = cv2.warpPerspective(grayempty, h, (width, height))
    median_blurtemplate= cv2.medianBlur(alignedtemplate, 3)
    threshholded_template = cv2.adaptiveThreshold(median_blurtemplate,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,15,16)
    median_blurcheque= cv2.medianBlur(graycheque, 3)
    threshholded_cheque = cv2.adaptiveThreshold(median_blurcheque,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,15,16)
    substracted_cheque = -threshholded_cheque + threshholded_template
    clean_cheque= cv2.medianBlur(substracted_cheque, 3)
    mask = np.zeros(clean_cheque.shape[:2], dtype="uint8")
    cv2.rectangle(mask, (200, 200), (1650, 450), 255, -1)
    cv2.rectangle(mask,(1650,330),(2300,520),255,-1)
    cv2.rectangle(mask,(50,900),(1500,1100),255,-1)
    masked_cheque = cv2.bitwise_and(clean_cheque, clean_cheque, mask=mask)
    client_name=masked_cheque[183:340,168:1930]
    legal_amount=masked_cheque[300:480,168:1900]
    courtesy_amount=masked_cheque[361:628,1700:2231]
    cheque_id=masked_cheque[950:1241, 350:1100]
    reader = easyocr.Reader(['ch_sim','en'])
    result = reader.readtext(courtesy_amount,allowlist ='0123456789',detail = 0)
    print(result)
    extracted_courtesy=''
    for i in result :
      extracted_courtesy=i+' '
    result2 = reader.readtext(legal_amount,detail = 0)
    extracted_legal=''
    print(result2)
    for i in range(len(result2)) :  
        extracted_legal=extracted_legal+ result2[i] + ' '
    print(extracted_legal)    
    spell = Speller(lang='en')
    converted_courtesy=num2words(extracted_courtesy,lang='en')
    extracted_legal_formated = re.sub(r"[^a-zA-Z0-9]+", ' ', extracted_legal)
    converted_courtesyformated = re.sub(r"[^a-zA-Z0-9]+", ' ', converted_courtesy)
    extracted_legal_formated2=remove_end_spaces(extracted_legal_formated)
    print(len(extracted_legal_formated2))
    print(len(converted_courtesyformated))
    correction=''
    if converted_courtesyformated==extracted_legal_formated2 :
       correction='no mistakes found'   
    else :
       correction=spell(extracted_legal_formated)
    return correction


