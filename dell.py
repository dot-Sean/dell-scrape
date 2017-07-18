!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Please install "BeautifulSoup 4" & "progressbar" via pip first:
[user@localhost ~]$ pip install beautifulsoup4 progressbar
Before running this script, a file 'delltags.txt' with one tag each line is required.
Results will be exported to 'delldate.txt'.
'''

from __future__ import division
import urllib2
import re
import threading
from bs4 import BeautifulSoup
from progressbar import ProgressBar, Percentage, Bar, ETA

# Create a class inherited from threading.Thread
class Dell(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    # Redefine run()
    def run(self):
        while len(taglist) > 0:
            #RLock
            mutex.acquire()
            self.tag = taglist[0]
            del taglist[0]
            mutex.release()
            #Get Dell's page
            url = "http://www.dell.com/support/home/uk/en/ukdhs1/product-support/servicetag/" + \
            self.tag + "/configuration?s=BSD"
            try:
                content_stream = urllib2.urlopen(url)
            except urllib2.URLError:
                date = "URLError"
                tagdict[self.tag] = date
                continue
            content = content_stream.read()
            soup = BeautifulSoup(content)
            try:
                date = soup.find(text=re.compile('20\d\d\/')).strip()   # Regular expression matches "20xx/"
            except AttributeError:
                date = "None"
            tagdict[self.tag] = date    # Add a key:value(tag:date) pair to tagdict
            # Next two lines are for progressbar
            percent = len(tagdict) / len(taglistkey)
            pbar.update(percent)     
  
if __name__ == '__main__':
    global mutex, taglist, tagdict, pbar
    with open('delltags.txt') as tagfile:
        taglist = [ tag.strip() for tag in tagfile ]
    taglistkey = tuple(taglist)
    tagdict = {}
    max_conn = 10      # Max threads number
    mutex = threading.RLock()
    threads = [ Dell() for i in xrange(0,max_conn) ]
    # pbar is a progressbar object
    pbar = ProgressBar(widgets=[Percentage(),Bar('>'),ETA()], maxval=1.0).start()
    for i in xrange(0,max_conn):
        threads[i].start()
    for i in xrange(0,max_conn):
        threads[i].join()
    pbar.finish()
    # After all threads ended, write tag:date each line into 'delldate.txt'
    with open('delldate.txt','w') as datefile:
        for i in taglistkey:
            datefile.write(i + ": " + tagdict[i] + "\n")
            
    print("Complete!")
