#Author : ADISH007
from cmath import nan
import pandas as pd
import numpy as np
import streamlit as st
from math import ceil
from bs4 import BeautifulSoup
import pandas as pd
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


from webdriver_manager.chrome import ChromeDriverManager
import os, sys

st.set_page_config(page_title='Named Entities Extractor', page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)




st.header('NAMED ENTITIES EXTRACTOR TOOL')

st.markdown("""
<style>div[data-testid="stToolbar"] { display: none;}</style>
""", unsafe_allow_html=True)

with st.sidebar.expander("Tool info: "):
     st.write("""
         Mention 2 words ( each word followed by a space ) , for which you need to extract Data.
         These 2 words can be anything:
         Eg: Person - Person  ( Putin Biden )
             Location - Location ( India Australia )
     """,width=10,use_column_width=20)
     st.header(' The tool will be extracting data based on Google search results ( in order ) ')
     st.text('Creator : ADISH007')
     st.sidebar.image("https://www.scalevp.com/sites/default/files/designbig.jpg")

query = str(st.text_input('Enter Query:  ', ''))


chrome_options = Options()
chrome_options.add_argument("--headless")
s = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(options=chrome_options)


#query = 'Putin Biden'
if query:
    with st.spinner('Finding matched links ...'):
        k=query.split()
        links = [] # Initiate empty list to capture final results
        # Specify number of pages on google search, each page contains 10 #links
        n_pages = 2
        for page in range(1, n_pages):
            url = "https://www.google.com/search?q=" + query + "&start=" +      str((page - 1) * 10)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # soup = BeautifulSoup(r.text, 'html.parser')

            search = soup.find_all('div', class_="yuRUbf")
            for h in search:
                links.append(h.a.get('href'))
        df = pd.DataFrame(links,columns=['LINKS FETCHED'])
        if len(df):
            #st.set_page_config(page_title="Data", layout="wide") 
            st.write('**Links extracted from Google**')
            st.dataframe(df)

    d={}
    issues={'Connection_issue':[]}
    with st.spinner('Extracting data from matched links ...'):
        for i in links:
            try:
                html_text=requests.get(i,timeout=(10, 10)).text
                #st.write(html_text)
                if html_text:
                    soup=BeautifulSoup(html_text,'lxml')
                    l=[]
                    ir=[]
                    for tag in soup.stripped_strings:
                        if (k[0].capitalize() or k[0].lower() or k[0].upper() or k[0]) in tag:
                            l.append(tag)
                            for j in l:
                                if (k[1].capitalize() or k[1].lower() or k[1].upper() or k[1]) in j:
                                    ir.append(j)
                                    #print(i)
                    if ir!= []:
                        d[i]=list(set(ir))
            except Exception as ex:
                #st.caption('Connection issues found..')
                #st.caption(ex)
                issues['Connection_issue'].append(str(ex))
                continue
            
        dfr=pd.DataFrame.from_dict(d, orient='index')
        if issues['Connection_issue']:
            with st.expander("Connection issue details:"):
                dfi=pd.DataFrame(issues)
                st.dataframe(dfi)
        dfr=pd.DataFrame.from_dict(d, orient='index')
        if len(dfr):
            st.write('**Extracted Data**')
            st.dataframe(dfr.transpose())
            st.success('Data Successfully extracted!!')
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_df(dfr)
            st.write("##")

            st.download_button(
                label="DOWNLOAD EXTRACTED DATA",
                data=csv,
                file_name='data_extracted.csv',
                mime='text/csv',
            )
        else:
            st.caption('No relevant data found for extraction!')
