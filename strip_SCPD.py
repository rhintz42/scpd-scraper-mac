#!/usr/bin/env python

import os
import errno
import subprocess,sys
import urllib, urllib2
import json


scpd_vid_urls = '/Users/roberth/scpd_scraper/scpd_vid_urls.txt'
recently_stripped_urls = '/Users/roberth/scpd_scraper/recently_stripped_urls.txt'
video_stripped_website = "http://myvideosu.stanford.edu/"




def start_mplayer_subprocess(web_vid, vid_name):
    mplayer = "/usr/local/bin/mplayer "
    subprocess.Popen([mplayer + web_vid + " -dumpstream -dumpfile " + vid_name], shell=True)


def create_folder(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def _file_exists(file):
    return os.path.isfile(file)

"""
Future implementation should check to see if the scpd site is up or not
"""
def test_site_is_working(site):
    #import pdb
    #pdb.set_trace()
    #req = urllib2.Request(site)
    #response = urllib2.urlopen(req).read()
    #data = response['data']
    return True

def _get_vid_name(web_vid):
    important_info = web_vid[7:]
    important_info = important_info[important_info.find("/")+1:]
    important_info = important_info[important_info.find("/")+1:]
    
    class_name = important_info[:important_info.find("/")]
    class_name = class_name.upper()

    important_info = important_info[important_info.find("/")+1:]
    vid_date = important_info[:important_info.find("/")]
    path_1 = "%s" % ("summer_SCPD")
    path_2 = "%s/%s_%s" % (path_1, class_name, "SUMMER_2012")
    path_3 = "%s/%s_%s" % (path_2, class_name, "videos")
    
    #import pdb
    #pdb.set_trace()
    
    create_folder(path_1)
    create_folder(path_2)
    create_folder(path_3)
    path = path_3
    
    vid_type = "Lecture"

    if "ps" in vid_date:
        vid_type = "Problem_Session"
    if "rs" in vid_date:
        vid_type = "Review_Session"
    
    vid_date = vid_date[2:4] + "_" + vid_date[4:6] + "_" + "20" + vid_date[:2]
    
    filename = "%s/%s_%s_%s.wmv" % (path, class_name, vid_type, vid_date)
    if _file_exists(filename):
        return False
    
    return filename

def _put_url_in_file(url):
    stripped_urls = []
    if _file_exists(recently_stripped_urls):
        f = open(recently_stripped_urls, 'r')
        stripped_urls = f.readlines()
	f.close()
    
    stripped_urls.append(url)

    f = open(recently_stripped_urls, 'w')
    f.writelines(stripped_urls)
    f.close()


def _format_vid_url(url):
    web_vid = ""
    if 'http://' in url:
        web_vid = url[7:]
    elif 'https://' in url:
        web_vid = url[8:]
    else:
        web_vid = url
    
    _put_url_in_file(url)
   
    web_vid = web_vid[:-1]
    
    return "mms://%s" % (web_vid)
    


def strip():
    if not test_site_is_working(video_stripped_website):
        print "SCPD is down"
	return False
    
    f = open(scpd_vid_urls, 'r') 
    data_list = f.readlines()
    f.close()
    
    if len(data_list) <= 0:
        print("Nothing in File")
        return
    
    web_vid = _format_vid_url(data_list[0])

    if len(data_list) > 0:
        del data_list[0]
    
    f = open(scpd_vid_urls, 'w')
    
    f.writelines(data_list)
    f.close()
    
    vid_name = _get_vid_name(web_vid)
    
    if not vid_name:
        print "File already exists"
	return

    start_mplayer_subprocess(web_vid, vid_name)
   
 
if __name__=="__main__":
    #strip(sys.argv[1])
    print "Starting"
    strip()
    strip()
