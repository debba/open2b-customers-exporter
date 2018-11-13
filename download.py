#!/usr/bin/env python
# coding: utf-8
import os

import requests
import time
from bs4 import BeautifulSoup
import json, codecs

def log(type, msg):
    print("[B2-dl] [%s] : %s" % (type, msg))


def getInput(soup, name):
    el = soup.find('input', {
        'name': name
    })
    if el is not None:
        return el['value']
    return ''

def getSelect(soup, name):
    el = soup.find('select', {
        'name': name
    })
    if el is not None:
        for option in el.findAll('option'):
            if option.has_attr("selected"):
                return option['value']
    return ''


class NinoDownloaderError(ValueError):
    pass


class NinoDownloader:
    WEBSITE_URL = ""
    login_endpoint = "/open2b/admin/index.asp"
    customers_endpoint = "/open2b/admin/module/user/index.asp"
    customer_endpoint = "/open2b/admin/module/user/user.asp?UserType=0"
    address_endpoint = "/open2b/admin/module/user/user_addresses.asp?UserType=0"
    session = False
    client_url = False
    json = False
    users = []

    def __init__(self, username, password, client_url):

        self.WEBSITE_URL = client_url

        body = {
            'Username': username,
            'Password': password,
            'Login': ' Login'
        }

        self.login_url = self.WEBSITE_URL+"/"+self.login_endpoint
        self.session = requests.Session()
        login = self.session.post(self.login_url, data=body, verify=False)
        soup = BeautifulSoup(login.text, "html.parser")

        loginForm = soup.find("div", {
            "id": "login"
        })

        if loginForm is not None:
            raise NinoDownloaderError("Login is not valid")

    def downloadMainAnag(self, user_id):

        user_url = self.WEBSITE_URL+"/"+self.customer_endpoint+"&Id="+str(user_id)
        us_page = self.session.get(user_url)

        soup = BeautifulSoup(us_page.text, "html.parser")

        main = {"data": {field : getInput(soup, field) for field in [
            'Code',
            'CompanyName',
            'FirstName',
            'LastName',
            'PersonalCode',
            'CompanyCode2',
            'Birthday',
            'Email',
            'PhoneNumber',
            'MobileNumber',
            'FaxNumber',
        ]}}

        main['data']['Gender'] = getSelect(soup, "Gender")

        return main['data']

    def downloadBillingAnag(self, user_id):

        user_url = self.WEBSITE_URL+"/"+self.address_endpoint+"&Id="+str(user_id)
        us_page = self.session.get(user_url)

        soup = BeautifulSoup(us_page.text, "html.parser")

        form = soup.find("form", {
            "name" : "User"
        })

        addresses = {
        }

        rows = form.find("table").findAll("tr")
        CompanyName = rows[0].findAll("td")[-1].text
        FullName = rows[1].findAll("td")[-1].text
        VatNumber = rows[2].findAll("td")[-1].text

        addresses["billingAddress"] = {field : getInput(soup, field) for field in [
            'Street1',
            'Street2',
            'City',
            'PostalCode'
        ]}

        addresses["billingAddress"]['CompanyName'] = CompanyName if CompanyName != '---' else ''
        addresses["billingAddress"]['FullName'] = FullName if CompanyName != '---' else ''
        addresses["billingAddress"]['VatNumber'] = FullName if VatNumber != '---' else ''
        addresses["billingAddress"]['StateProv'] = getSelect(soup, "StateProv")
        addresses["billingAddress"]['Country'] = getSelect(soup, "Country")

        addresses["shippingAddress"] = {field: getInput(soup, field) for field in [
            'ShipName',
            'ShipStreet1',
            'ShipStreet2',
            'ShipCity',
            'ShipPostalCode'
        ]}

        addresses["shippingAddress"]['ShipStateProv'] = getSelect(soup, "ShipStateProv")
        addresses["shippingAddress"]['ShipCountry'] = getSelect(soup, "ShipCountry")

        return addresses

    def downloadFromTable(self, table, page):
        table_body = table.find("tbody")
        rows = table_body.findAll("tr")
        for row in rows:
            cols = row.findAll("td")
            user_id = int(cols[-1].find("input")['value'])
            log("info", "[Page %d] Found user. Email = %s, Id = %d" % (page, cols[2].text, user_id))
            user = {
                "id" : user_id,
                "main" : self.downloadMainAnag(user_id),
                "addresses": self.downloadBillingAnag(user_id)
            }
            self.users.append(user)

    def downloadAnags(self):
        log("info", "Open Json File")

        page = 1
        user_url = self.WEBSITE_URL+"/"+self.customers_endpoint

        while True:
            log("info", "Fetch from page %d" % page )
            anag_page = self.session.get(user_url + "?page=" + str(page))
            soup = BeautifulSoup(anag_page.text, "html.parser")
            table = soup.find("table", {
                "class": "grid"
            })

            if table.find("td", {
                "class" : "gridNoRowsMessage"
            }) is not None:
                log("info", "Yeahhh ended now.")
                break

            self.downloadFromTable(table, page)
            page = page+1

        log("info", "JSON creation with data")
        with open("downloads/results_" + str(time.time()) + ".json", 'w+') as f:
            json.dump(self.users, f, sort_keys=True, indent=4,ensure_ascii=False)
