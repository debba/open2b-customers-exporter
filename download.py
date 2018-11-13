#!/usr/bin/env python
# coding: utf-8
import os

import requests
import time
from bs4 import BeautifulSoup
import re
import csv

def urlify(s):
    s = re.sub(r"[^\w\s]", '', s)
    s = re.sub(r"\s+", '-', s)
    return s

def log( type, msg):
    print("[Nino-dl] [%s] : %s" % (type, msg))

def dwl_info(d):
    if d['status'] == 'finished':
        log("Success", "Video scaricato ora converto...")

class NinoDownloaderError(ValueError):
    pass

class NinoDownloader:

    login_endpoint = "http://www.ninosanremo.com/open2b/admin/index.asp"
    session = False
    client_url = False
    csv = False

    def __init__(self, username, password, client_url):

        body = {
            'Username' : username,
            'Password' : password,
            'Login' : ' Login'
        }

        self.client_url = client_url
        self.session = requests.Session()
        login = self.session.post(self.login_endpoint, data = body, verify=False)
        soup = BeautifulSoup(login.text, "html.parser")

        loginForm = soup.find("div", {
            "id": "login"
        })

        if loginForm is not None:
            raise GTDownloaderError("Login is not valid")

    def downloadFromTable(self, table):
        table_body = table.find("tbody")
        rows = table_body.findAll("tr")
        for row in rows:
            cols = row.findAll("td")
            log("email ",cols[2].text)

    def downloadAnags(self, output_csv=False):
        if output_csv:
            log("info", "Hai scelto di creare il file csv")
            self.csv = csv.writer(open("downloads/results_"+str(time.time())+".csv", "w+"), delimiter=',',quoting=csv.QUOTE_ALL)

        total_pages = 712
        user_url = "http://www.ninosanremo.com/open2b/admin/module/user/index.asp"

        for page in range(1,total_pages):
            anag_page = self.session.get(user_url+"?page="+str(page))
            soup = BeautifulSoup(anag_page.text, "html.parser")
            table = soup.find("table", {
                "class" : "grid"
            })
            self.downloadFromTable(table)


