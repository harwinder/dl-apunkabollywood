from BeautifulSoup import BeautifulSoup
import urllib2
import re
import sys
import os
import getopt
import time
import string

std_headers = {	
	'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.5) Gecko/2008120122 Firefox/3.0.5',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
	'Accept-Language': 'en-us,en;q=0.5',
}

user_agent="Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.5) Gecko/2008120122 Firefox/3.0.5"

# variable to hold multiple urls
url_list = []

# variable to hold output directory
output_dir = ""

# variable to hold download lists
# obtained by looking at each url in url list
# or these links come from the restart file
dl_list = []

# restart file
flag_restart_file = False
restart_file = ""

def usage():
	print "Usage: ", sys.argv[0], "[-h] -u url [-d] [-r]"
	print "Available Switches:"
	print "-h, --help   : Shows this message"
	print "-u, --url    : Provide album urls"
	print "-d, --dir    : Set output directory"
	print "-r, --restart: provide restart file"

def handle_args(argv):
	global output_dir
	global restart_file
	global flag_restart_file
	try:
		opts, args = getopt.getopt(argv, "hu:d:r:", ["url=", "dir=", "restart="])
	except getopt.GetOptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-u", "--url"):
			url_list.append(arg)
		elif opt in ("-r", "--restart"):
			restart_file = arg
			flag_restart_file = True
		elif opt in ("-d", "--dir"):
			if not output_dir:
				print "Error: only one output directory expected"
				usage()
				sys.exit(2)
			else:
				output_dir = arg
	if output_dir == "":
		output_dir=os.curdir

def get_song(url):
	block_size = 4096
	print "Downloading from url:", url
	before = time.time()
	filename = url.split('/')[-1]
	request = urllib2.Request(string.replace(url, " ", "%20"), None, std_headers)
	stream = open(filename, "wb")
	data = urllib2.urlopen(request)
	print data.code, data.msg
	print data.info()
	print data.geturl()
	file_len = data.info().get('Content-Length', None)
	while True:
		data_block = data.read(block_size)
		data_block_len = len(data_block)
		if (data_block_len == 0):
			break
		stream.write(data_block)
	stream.close()
	print "Downloaded File:", filename, "Time Taken", time.time()-before

def process_album_urls():
	dl_page = []
	for url in url_list:
		request = urllib2.Request(url)
		request.add_header("User-agent", user_agent)
		page = urllib2.urlopen(request)
		soup = BeautifulSoup(page)
		alltags = soup.findAll('a', href=re.compile('download'))
		for tag in alltags:
			if not dl_page or (dl_page[-1] != tag['href']):
				dl_page.append(tag['href'])
				
	try:
		f = open("restart", "w")
	except:
		print "Unable to open restart file"
	for dl_page_url in dl_page:
		request = urllib2.Request(dl_page_url)
		request.add_header("User-agent", user_agent)
		page = urllib2.urlopen(request)
		soup = BeautifulSoup(page)
		alltags = soup.findAll('a', href=re.compile('download'))
		dl_list.append(alltags[0]['href'])
		try:
			f.write(alltags[0]['href']+"\n")
		except:
			print "Unable to write to the restart file"
	f.close()
		
def process_restart_file(restart_file):
	global dl_list
	f = open(restart_file, "r")
	dl_list = f.readlines()
	for i in range(len(dl_list)):
		if dl_list[i][-1] == '\n':
			dl_list[i] = dl_list[i][0:-1]
	f.close()

if __name__ == "__main__":
	handle_args(sys.argv[1:])
	if not flag_restart_file:
		process_album_urls()
	else:
		process_restart_file(restart_file)
	for song_url in dl_list:
		get_song(song_url)
