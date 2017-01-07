# -*- coding: utf-8 -*-
from __future__ import division
import httplib2,json
import zlib
import zipfile
import sys
import re
import datetime
import operator
import sqlite3
import os
from datetime import datetime
from datetime import date
import pytz 
from tzlocal import get_localzone
import requests
from termcolor import colored, cprint
import hashlib

from multiprocessing import Process
from Queue import Queue

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time,re,sys
from selenium.webdriver.common.keys import Keys
import datetime
from bs4 import BeautifulSoup
from StringIO import StringIO

from userparse import find_users

import networkx as nx
from compare import compare_likes

requests.adapters.DEFAULT_RETRIES = 10


h = httplib2.Http(".cache")


facebook_username = "fubag01@gmail.com"
facebook_password = "password"

full_user_list = "facebook_accounts.txt"

global uid
uid = ""
username = ""
internetAccess = True
cookies = {}
all_cookies = {}
reportFileName = ""

#For consonlidating all likes across Photos Likes+Post Likes
peopleIDList = []
likesCountList = []
timePostList = []
placesVisitedList = []

#Chrome Options
chromeOptions = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chromeOptions)

#Graph
gr = nx.DiGraph()

def normalize(s):
	if type(s) == unicode: 
       		return s.encode('utf8', 'ignore')
	else:
        	return str(s)

def findUser(findName):
	stmt = "SELECT uid,current_location,username,name FROM user WHERE contains('"+findName+"')"
	stmt = stmt.replace(" ","+")
	url="https://graph.facebook.com/fql?q="+stmt+"&access_token="+facebook_access_token
	resp, content = h.request(url, "GET")
	results = json.loads(content)
	count=1
	for x in results['data']:
		print str(count)+'\thttp://www.facebook.com/'+x['username']
		count+=1

def convertUser2ID2(driver,username):
	url="http://graph.facebook.com/"+username
	resp, content = h.request(url, "GET")
	if resp.status==200:
		results = json.loads(content)
		if len(results['id'])>0:
			fbid = results['id']
			return fbid

def convertUser2ID(username):
	stmt = "SELECT uid,current_location,username,name FROM user WHERE username=('"+username+"')"
	stmt = stmt.replace(" ","+")
	url="https://graph.facebook.com/fql?q="+stmt+"&access_token="+facebook_access_token
	resp, content = h.request(url, "GET")
	if resp.status==200:
		results = json.loads(content)
		if len(results['data'])>0:
			return results['data'][0]['uid']
		else:
			print "[!] Can't convert username 2 uid. Please check username"
			sys.exit()
			return 0
	else:
		print "[!] Please check your facebook_access_token before continuing"
		sys.exit()
		return 0

def convertID2User(uid):
	stmt = "SELECT uid,current_location,username,name FROM user WHERE uid=('"+uid+"')"
	stmt = stmt.replace(" ","+")
	url="https://graph.facebook.com/fql?q="+stmt+"&access_token="+facebook_access_token
	resp, content = h.request(url, "GET")
	results = json.loads(content)
	return results['data'][0]['uid']

def loginFacebook(driver, username = facebook_username, password = facebook_password):
	driver.implicitly_wait(120)
	driver.get("https://www.facebook.com/")
	assert "Welcome to Facebook" in driver.title
	time.sleep(3)
	driver.find_element_by_id('email').send_keys(username)
	driver.find_element_by_id('pass').send_keys(password)
	driver.find_element_by_id("loginbutton").click()
	global all_cookies
	all_cookies = driver.get_cookies()
	html = driver.page_source
	if "Incorrect Email/Password Combination" in html:
		print "[!] Incorrect Facebook username (email address) or password"
		sys.exit()

def downloadPagesLiked(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/pages-liked')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Pages liked list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(5)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True

                #match=True
	return driver.page_source


#My code
#Start scanning users given a starting point and increment
#Built for multiprocessing
def begin_pages_liked_scan(username, password, starting, increment, pageid):

	#create new driver for each user
	chromeOptions = webdriver.ChromeOptions()
	prefs = {"profile.managed_default_content_settings.images":2}
	chromeOptions.add_experimental_option("prefs",prefs)
	unique_driver = webdriver.Chrome(chrome_options=chromeOptions)

	loginFacebook(unique_driver, username, password)

	#Get the list of usernames we should be scanning
	all_users = find_users(pageid, starting, increment)
	
	#Testing for graph stuff
	user_id=1
	
	for user in all_users:
		filename = "User Likes/"+pageid+"/Cache/"+user+"_"+pageid+"_cache.htm"
		if not os.path.exists(filename):
			print "[*] Caching Pages Liked By: "+user
			html = downloadPagesLiked(unique_driver,convertUser2ID2(unique_driver,user))
			text_file = open(filename, "w")
			text_file.write(html.encode('utf8'))
			text_file.close()
		else:
			html = open(filename, 'r').read()
			
		page_list_ = parsePagesLiked(html)
		pages_txt = open("User Likes/"+pageid+"/"+user+"_pagesliked.txt", "w")

		print "[*] Saving pages liked..."
		gr.add_node(user_id)
		page_id = user_id*10000
		
		for i in page_list:	
			page_name = normalize(i[1])

			gr.add_node(hashlib.sha224(page_name).hexdigest())
			gr.add_edge(user_id, hashlib.sha224(page_name).hexdigest())

			pages_txt.write(page_name+'\n')
			page_id +=1
			
		pages_txt.close()

		user_id += 1

	#Make some fancy graphs
	if not os.path.exists("Graphs"):
		os.makedirs("Graphs")
	if not os.path.exists("Graphs/"+pageid):
		os.makedirs("Graphs/"+pageid)

	nx.write_gml(gr, "Graphs/"+pageid+"/graph.gml")

	unique_driver.close()
	unique_driver.quit

def getPageLikers(driver,pageid):
	driver.get('https://www.facebook.com/search/'+str(pageid)+'/likers')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Pages liked list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(4)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
                #uncomment this if you only want a small set of users ~15(?)
                #good for testing all functions before wasting time on a large set
                #match = True

    #much faster now that we filter an extra step
	return driver.find_elements_by_css_selector("a[href*='browse_search']")

def downloadPage(url):
	driver.get(url)	
	html = driver.page_source
	return html

def parsePagesLiked(html):
	soup = BeautifulSoup(html)	
	pageName = soup.findAll("div", {"class" : "_zs fwb"})
	pageCategory = soup.findAll("div", {"class" : "_dew _dj_"})
	tempList = []
	count=0
	r = re.compile('a href="(.*?)\?ref=')
	for x in pageName:
		m = r.search(str(x))
		if m:
			pageCategory[count]
			tempList.append([uid,x.text,pageCategory[count].text,m.group(1)])
		count+=1
	return tempList

def mainProcess(username, page, increment_amount):
	pageid = page
	username = username.strip()
	print "[*] Username:\t"+str(username)
	print "[*] Page:\t"+str(page)
	global uid
	
	loginFacebook(driver)
	uid = convertUser2ID2(driver,username)
	if not uid:
		print "[!] Problem converting username to uid"
		sys.exit()
	else:
		print "[*] Uid:\t"+str(uid)

	if not os.path.exists("Cache"):
		os.makedirs("Cache")

	filename = "Cache/"+pageid+'_likers.htm'
	if not os.path.lexists(filename):
		print "[*] Caching Page Likers: "+pageid
		html = getPageLikers(driver,pageid)
		print "[*] Collecting links..."
		text_file = open(filename, "w")
		for i in html:
			text_file.write(str(i.get_attribute('href')) + '\n')
		text_file.close()
	else:
		html = open(filename, 'r').read()


	#Show this - my code
	#Caching Pages Liked - Start
	if not os.path.exists("User Likes"):
		os.makedirs("User Likes")

	if not os.path.exists("User Likes/"+pageid):
		os.makedirs("User Likes/"+pageid)

	if not os.path.exists("User Likes/"+pageid+"/Cache"):
		os.makedirs("User Likes/"+pageid+"/Cache")

	users_from_page = find_users(pageid)

	user_list = open(full_user_list, "r")
	starting_point = 0

	#For all the accounts in the .txt, start a new process to scan
	for new_user in user_list:
		new_user_name = new_user.split(",")[0]
		new_user_password = new_user.split(",")[1].rstrip()
		
		u = Process(target=begin_pages_liked_scan, args=(new_user_name, new_user_password, starting_point, increment_amount, pageid))
		u.start()

		starting_point+=1

	u.join()

	compare_likes(pageid)

	#Caching Pages Liked - End

	print "[*] Report has been written to: Reports/"+pageid

	
	driver.close()
	driver.quit


def options(arguments):
	user = ""
	count = 0
 	for arg in arguments:
  		if arg == "-user":
			count+=1
   			user = arguments[count+1]
   		if arg == "-page":
   			count+=1
   			page = arguments[count+2]
   		if arg == "-accounts":
   			count+=1
   			increment_amount = int(arguments[count+3])
  	mainProcess(user, page, increment_amount)


def showhelp():

	print ""
	print "	MMMMMM$ZMMMMMDIMMMMMMMMNIMMMMMMIDMMMMMMM"
	print "	MMMMMMNINMMMMDINMMMMMMMZIMMMMMZIMMMMMMMM"
	print "	MMMMMMMIIMMMMMI$MMMMMMMIIMMMM8I$MMMMMMMM"
	print "	MMMMMMMMIINMMMIIMMMMMMNIIMMMOIIMMMMMMMMM"
	print "	MMMMMMMMOIIIMM$I$MMMMNII8MNIIINMMMMMMMMM"
	print "	MMMMMMMMMZIIIZMIIIMMMIIIM7IIIDMMMMMMMMMM"
	print "	MMMMMMMMMMDIIIIIIIZMIIIIIII$MMMMMMMMMMMM"
	print "	MMMMMMMMMMMM8IIIIIIZIIIIIIMMMMMMMMMMMMMM"
	print "	MMMMMMMMMMMNIIIIIIIIIIIIIIIMMMMMMMMMMMMM"
	print "	MMMMMMMMM$IIIIIIIIIIIIIIIIIII8MMMMMMMMMM"
	print "	MMMMMMMMIIIIIZIIIIZMIIIIIDIIIIIMMMMMMMMM"
	print "	MMMMMMOIIIDMDIIIIZMMMIIIIIMMOIIINMMMMMMM"
	print "	MMMMMNIIIMMMIIII8MMMMM$IIIZMMDIIIMMMMMMM"
	print "	MMMMIIIZMMM8IIIZMMMMMMMIIIIMMMM7IIZMMMMM"
	print "	MMM$IIMMMMOIIIIMMMMMMMMMIIIIMMMM8IIDMMMM"
	print "	MMDIZMMMMMIIIIMMMMMMMMMMNIII7MMMMNIIMMMM"
	print "	MMIOMMMMMNIII8MMMMMMMMMMM7IIIMMMMMM77MMM"
	print "	MO$MMMMMM7IIIMMMMMMMMMMMMMIII8MMMMMMIMMM"
	print "	MIMMMMMMMIIIDMMMMMMMMMMMMM$II7MMMMMMM7MM"
	print "	MMMMMMMMMIIIMMMMMMMMMMMMMMMIIIMMMMMMMDMM"
	print "	MMMMMMMMMII$MMMMMMMMMMMMMMMIIIMMMMMMMMMM"
	print "	MMMMMMMMNIINMMMMMMMMMMMMMMMOIIMMMMMMMMMM"
	print "	MMMMMMMMNIOMMMMMMMMMMMMMMMMM7IMMMMMMMMMM"
	print "	MMMMMMMMNINMMMMMMMMMMMMMMMMMZIMMMMMMMMMM"
	print "	MMMMMMMMMIMMMMMMMMMMMMMMMMMM8IMMMMMMMMMM"

	print """
	#####################################################
	#                  fbStalker.py                 #
	#               [Trustwave Spiderlabs]              #
	#####################################################
	Usage: python fbStalker.py [OPTIONS]

	[OPTIONS]

	-user   [Facebook Username]
	-page    [Page ID]
	-accounts [# accounts used to get data]
	"""

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		showhelp()
		driver.close()
		driver.quit
		conn.close()
		sys.exit()
 	else:
		if len(facebook_username)<1 or len(facebook_password)<1:
			print "[*] Please fill in 'facebook_username' and 'facebook_password' before continuing."
			sys.exit()
  		options(sys.argv)
 
