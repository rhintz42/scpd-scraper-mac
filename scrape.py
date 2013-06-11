import re
import os
import sys
from getpass import *
from mechanize import Browser
from bs4 import BeautifulSoup

"""

This program downloads scpd videos for a given class in the order
that they happened as a wmv, then converts them to a mp4. Each time 
the script is run, it will update to download all of the undownloaded
videos. 

This script is modified from the one by Ben Newhouse (https://github.com/newhouseb).

Unfortunately, there are lots of dependencies to get it up and running
1. Handbrake CLI, for converting to mp4: http://handbrake.fr/downloads2.php
2. BeautifulSoup for parsing: http://www.crummy.com/software/BeautifulSoup/
3. Mechanize for emulating a browser, http://wwwsearch.sourceforge.net/mechanize/

To run:
Change to your username
When prompted, type your password

Usage: python scrape.py "Interactive Computer Graphics"

The way I use it is to keep a folder of videos, and once I have watched them, move them
into a subfolder called watched. So it also wont redowload files that are in a subfolder
called watched.


"""

num_vids_already_downloaded = 0
first_class = ""
current_folder = "/home/roberth/scpd-scraper"
courses_to_download_local_txt = "test_courses_to_download.txt"

def _file_exists(file):
	return os.path.isfile(file)

def _first_line_to_back_of_file(list_to_reorder, file):
	course_to_download = list_to_reorder.pop(0)
	f = open(file, 'w')
	f.writelines(list_to_reorder)
	f.write(course_to_download)
	f.close()
	return course_to_download

def _file_to_list(file, no_new_line=False):
	f = open(file, 'r')
	n_list = f.readlines()
	f.close()
	if no_new_line:
		tmp_list = []
		for line in n_list:
			tmp_list.append(_remove_end_newline(line))
		return tmp_list
	return n_list

def _remove_end_newline(line):
	return line.split('\n')[0]

def _append_line_to_file(file, line):
	file_list = _file_to_list(file)
	f = open(file, 'w')
	f.writelines(file_list)
	f.write("%s%s" %(line, '\n'))
	f.close()



def convertToMp4(wmv, mp4):
	print "Converting ", mp4
	os.system('/usr/bin/HandBrakeCLI -i %s -o %s' % (wmv, mp4))
	os.system('rm -f %s' % wmv)

def download(work):
	# work[0] is url, work[1] is wmv, work[2] is mp4
	class_name = re.search('(.*)_', work[2])
	folder_name = "%s/%s" % (current_folder, class_name.group(1))
	
	path_to_vid_mp4 = "%s/%s" % (folder_name, work[2])
	path_to_vid_wmv = "%s/%s" % (folder_name, work[1])
	
	if not os.path.exists(folder_name):
		os.makedirs(folder_name)
	
	downloaded_videos_path = "%s/%s" % (folder_name, "videos_downloaded.txt")
	
	if not _file_exists(downloaded_videos_path):
		f = open(downloaded_videos_path, 'w')
		f.close()
	
	#import pdb;pdb.set_trace()
	
	downloaded_videos_list = _file_to_list(downloaded_videos_path, no_new_line=True)
	
	global num_vids_already_downloaded
	a = num_vids_already_downloaded
	
	if work[2] in downloaded_videos_list or\
	   work[1] in downloaded_videos_list:
		num_vids_already_downloaded = a + 1
		print "Already downloaded", work[2]
		return
	elif os.path.exists("%s/%s" %(folder_name, work[2])) or\
	     os.path.exists("%s/%s/%s" %(folder_name, "watched", work[2])) or\
	     os.path.exists("%s/%s" %(folder_name, work[1])) or\
	     os.path.exists("%s/%s/%s" %(folder_name, "watched", work[1])):
		num_vids_already_downloaded = a + 1
		_append_line_to_file(downloaded_videos_path, work[2])
		print "Already downloaded", work[2]
		return
	#Comment out this line and uncomment out the other copy of this line
	#_append_line_to_file(downloaded_videos_path, work[2])
	
	print "Starting", path_to_vid_wmv
	
	#This is where the video gets put into the "Videos already Downloading" file
	###Should make this into some sort of method because it's a common operation###
	current_files_downloading_path = "%s/%s" %(current_folder, "current_files_downloading.txt")
	if not _file_exists(current_files_downloading_path):
		f = open(current_files_downloading_path, 'w')
		f.close()
	
	_append_line_to_file(current_files_downloading_path, path_to_vid_wmv)


	os.system("mplayer -dumpstream %s -dumpfile %s" % (work[0], path_to_vid_wmv))
	convertToMp4(path_to_vid_wmv, path_to_vid_mp4)
	_append_line_to_file(downloaded_videos_path, work[2])
	
	###Need to make a "Remove line from file" function that removes a line from a file###
	#if not _file_exists(current_files_downloading_path):
	#	f = open(current_files_downloading_path, 'w'):
	#	f.close()
	
	
	#import pdb; pdb.set_trace()
	
	new_current_files_downloading_list = []
	current_files_downloading_list = _file_to_list(current_files_downloading_path, no_new_line=True)
	for current_file in current_files_downloading_list:
		if current_file != path_to_vid_wmv:
			new_current_files_downloading_list.append("%s%s" %(current_file,'\n'))
	
	f = open(current_files_downloading_path, 'w')
	f.writelines(new_current_files_downloading_list)
	f.close()
	
	
	print "Finished", path_to_vid_wmv


def begin_scraper():
	#import pdb;pdb.set_trace()
	global first_class
	global num_vids_already_downloaded
	
	courses_to_download = []
	courses_file = "%s/%s" % (current_folder, courses_to_download_local_txt)
	
	if _file_exists(courses_file):
		courses_to_download = _file_to_list(courses_file)
	else:
		print "There is no courses_to_download.txt file.\nPlease create one and populate it with courses"
		sys.exit()
	
	if len(courses_to_download) == 0:
		print "There are no courses in your courses_to_download.txt file"
		sys.exit()
	
	#import pdb;pdb.set_trace()
	
	course_to_download = _first_line_to_back_of_file(courses_to_download, courses_file)
	course_to_download = _remove_end_newline(course_to_download)
	
	if len(first_class) == 0:
		first_class = course_to_download
	elif first_class == course_to_download:
		return
	#import pdb;pdb.set_trace()
	if "->" in course_to_download:
		index = course_to_download.find('->')
		course_to_download = course_to_download[0:index]
	#if not _file_exists("vidoes_downloaded.txt"):
	#	f = open("videos_downloaded.txt", 'w')
	#	f.close()
	#
	#temp = _file_to_list("videos_downloaded.txt")
	
	br = Browser()
	br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_8; rv:16:0) Gecko/20100101 Firefox/16.0')]
	br.set_handle_robots(False)
	br.open("https://myvideosu.stanford.edu/oce/currentquarter.aspx")
	assert br.viewing_html()
	br.select_form(name="login")
	br["username"] = "rhintz42" #Put your username here
	br["password"] = getpass()

	# Open the course page for the title you're looking for 
	response = br.submit()
	response = br.follow_link(text=course_to_download)
        #print response.read()	
	
	#response = br.follow_link(text="WMP", nr=2)#(text="SL", nr=0)#(text="HERE", nr=0)
	#response = br.open('https://myvideosu.stanford.edu/player/slplayer.aspx?coll=6d44dcc5-9136-42ab-a0fa-1475fcbfa463&course=CS140&co=66ce29bd-4bbc-4cb0-b166-8589ebb14e60&lecture=120924&authtype=WA&wmp=true')
  #print response.read()
	# Build up a list of lectures
	links = []
	for link in br.links(text="WMP"):
		links.append(re.search(r"'(.*)'",link.url).group(1))

	link_file = open('links.txt', 'w')
	
  # So we download the oldest ones first.
	links.reverse()
  
	videos = []
	
	for link in links:
		response = br.open(link)
		soup = BeautifulSoup(response.read())
		video = soup.find('object', id='WMPlayer')['data']
		video = re.sub("http","mms",video)		
		video = video.replace(' ', '%20') # remove spaces, they break urls
		output_name = re.search(r"[a-z]+[0-9]+[a-z]?/[0-9]+",video).group(0).replace("/","_") #+ ".wmv"
		output_wmv = output_name + ".wmv"
		link_file.write(video + '\n')
		#import pdb
		#pdb.set_trace()
		print video
		output_mp4 = output_name + ".mp4"
		videos.append((video, output_wmv, output_mp4))
	
	
	link_file.close()
	num_vids_already_downloaded = 0
	
	#This needs to be fixed to handle classes that have no videos
	class_name = ''
	if len(videos) > 0:
		class_name = re.search('(.*)_', videos[0][2])
	else:
		return
	
	if not os.path.exists("%s/%s" %(current_folder, class_name.group(1))):
		os.makedirs("%s/%s" %(current_folder, class_name.group(1)))
	
	vid_urls_path = "%s/%s/%s" %(current_folder, class_name.group(1), "video_urls.txt")
	
	if not _file_exists(vid_urls_path):
		f = open(vid_urls_path, 'w')
		f.close()
	
	#import pdb;pdb.set_trace()
	
	vid_urls_list = _file_to_list(vid_urls_path, no_new_line=True)
	
	add_to_vid_urls_list = _file_to_list(vid_urls_path)
	
	for video in videos:
		if video[0] not in vid_urls_list:
			add_to_vid_urls_list.append("%s%s" %(video[0],'\n'))
		download(video)
	
	f = open(vid_urls_path, 'w')
	f.writelines(add_to_vid_urls_list)
	f.close()
	#import pdb;pdb.set_trace()
	
	if num_vids_already_downloaded >= len(videos):
		begin_scraper()

	print "complete"
if __name__ == '__main__':
	begin_scraper()
