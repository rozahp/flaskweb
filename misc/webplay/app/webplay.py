#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Filename:    webplay.py
##
## Created:     2020-11-15
##
## Modified:    None
##
## Description: Gets live link from webplay and sends it to kodi
##

import requests
from bs4 import BeautifulSoup
import re
import json
import argparse
import dateparser
import os
import time
import datetime

##
## Global Variables
##

LINK="https://webplay"
SERVER="http://someserver:80/jsonrpc"
INDEX="data/index"
MAXSEC=600

def get_programs(theme_id=0, search=False):
    ##
    ## CHECK IF INDEX HAS TO BE UPDATED
    ##
    DATE=time.strftime("%Y-%m-%d")
    SECNOW=int(datetime.datetime.now().strftime("%s"))
    INDEXFILE=INDEX+"_"+DATE+".html"
    REQUEST_FROM_SERVER=True
    if os.path.exists(INDEXFILE):
        mod_timestamp = int(datetime.datetime.fromtimestamp(os.stat(INDEXFILE).st_mtime).strftime("%s"))
        if SECNOW-mod_timestamp<MAXSEC:
            REQUEST_FROM_SERVER=False
    if search: 
        theme_id=0
    headers=requests.utils.default_headers()
    headers.update(
        {
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'Accept-Language: en-US,en;q=0.5',
           'DNT': '1',
           'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1',
           'Cache-Control': 'max-age=0',
           'TE':'Trailers',
           'Referer':'https://www.google.com'
        }
    )
    ##
    ## GET INDEX FROM SERVER
    ##
    if REQUEST_FROM_SERVER:
        #print("REQUEST_FROM_SEARCH=True")
        response = requests.get(LINK, headers=headers)
        text=response.text
        with open(INDEXFILE,"w") as fp:
                fp.write(text)
    else:
        #print("REQUEST_FROM_SEARCH=False")
        with open(INDEXFILE) as fp:
            text=fp.read()
    ##
    ## CREATE SOUP
    ##
    soup = BeautifulSoup(text, 'html.parser')
    ##
    ## CHECK IF LIVE LINK EXISTS
    ##
    links = soup.find_all('a')
    live_link=False
    for l in links:
        txt=l.get_text()
        if "Live nu" in txt:
            live_link=l['href']
            break
    ##
    ## GET THEMES LIST
    ##
    themes = soup.find_all('li', class_='Tab-handle')
    theme_list=[]
    for t in themes:
        theme_list.append(t.get_text())
    if not len(theme_list):
        theme_list['EMPTY']
    save_theme_list=list(theme_list)
    ##
    ## GET PROGRAMS
    ##
    programs=soup.find_all('div', class_='Tiles')
    ##
    ## POPULATE DICTIONARY
    ##
    program_dir={"themes": list(theme_list),"live":live_link,"programs": []}
    ##
    ## START LOOPING THROUGH PROGRAMS
    ##
    program_id=0
    for p in programs:
        ##
        ## GET THEME FROM LIST
        ##
        if len(theme_list)==0:
            theme="EMPTY"
        else: theme=theme_list.pop(0)
        ##
        ## FILTER THEME ID
        ##
        if theme_id:
            if save_theme_list.index(theme)+1!=theme_id:
                continue
        ##
        ## SET UP DICTIONARY
        ##
        divs = p.find_all('a')
        for d in divs:
            program_link=d['href']
            program_data = d.find_all(class_=['Tile-cover u-fullSizeBg','Tile-title','Tile-date'])
            if len(program_data)<3:
                program_image=False
                program_title=False
                program_speaker=False
                program_date=False
            else:
                program_image=str(program_data[0]['style'].split('(')[1].split(')')[0])
                program_title=str(program_data[1].get_text().strip())
                # GET SPEAKER
                speaker=d.find_all('span')
                if len(speaker)>1:
                    program_speaker=str(speaker[0].get_text().strip())
                    if len(program_speaker)==0:
                        program_speaker="No speaker found"
                else: program_speaker="No speaker found"
                ##
                ## Dont trim program_title
                ##
                #if program_speaker in program_title:
                #    program_title=str(program_title[0:len(program_title)-len(program_speaker)])
                program_date=program_data[2].get_text().strip()
                program_date=str(dateparser.parse(program_date).strftime('%Y-%m-%d'))
            if search:
                newline='{0} {1} {2} {3}'.format(theme, program_date, program_title, program_speaker).lower()
                if search.lower() not in newline: continue
            program_id+=1
            program_dir['programs'].append({"theme":theme, "link":program_link, "date":program_date, 
                    "title_name":program_title, "speaker":program_speaker,"image":program_image,"id":program_id})
    return program_dir

##
## Get Kodi Link
##

def get_kodilink(program_link):
    headers=requests.utils.default_headers()
    headers.update(
        {
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'Accept-Language: en-US,en;q=0.5',
           'DNT': '1',
           'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1',
           'Cache-Control': 'max-age=0',
           'TE':'Trailers',
           'Referer':'https://webplay'
        }
    )
    response = requests.get(LINK+program_link, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('div', id='player-wrapper')    
    kodi_link=False
    for l in links:
        try:
            kodi_link=l['data-file']
            #if "starttime=" in kodi_link:
            #    kodi_link=kodi_link.split("?")[0]
            if "url=" in kodi_link:
                kodi_link=kodi_link.split("=")[1].split("&")[0]
        except Exception:
            continue
    return kodi_link

##
## Send to kodi
##
def send_to_kodi(kodi_link):
    data={  "jsonrpc": "2.0",
            "method": "Player.Open",
            "params": {
                "item": {
                    "file": str(kodi_link),
                    },
                },
                "id": 1,
            }
    headers=requests.utils.default_headers()
    headers.update(
        {
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'Accept-Language: en-US,en;q=0.5',
           'DNT': '1',
           'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1',
           'Cache-Control': 'max-age=0',
           'Content-Type': 'application/json',
           'TE':'Trailers',
           'Referer':'https://webplay'
        }
    )
    print("Log: sending to kodi:", data)
    response = requests.post(SERVER, headers=headers, data=json.dumps(data))
    if response.status_code!=200:
        print("Err: error sending link to kodi:", response.text)
        return False
    else:
        print("response.status_code:", response.text)
    return True


##
## PLAY PROGRAM
##
def play_program(video_link):

    if video_link:
        print("Log: video_link:", video_link)
        ##
        ## GET KODI LINK
        ##
        kodi_link=get_kodilink(video_link)
        if kodi_link:
            print("Log: kodi_link:", kodi_link)
            send_status=send_to_kodi(kodi_link)
            if send_status==False:
                return False, "Error sending link on mediaplayer: "+str(kodi_link)
        else:
            print("Err: kodi_link not found")
            return False, "Error finding link on site: "+str(video_link)
    else:
        print("Err: video_link not sent to process")  
        return False, "Video Link not sent to process!"

    return True, "Video should now be playing! Enjoy!"

##
## EOF
## 
