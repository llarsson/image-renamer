# image-renamer
Finds the most recent image on an FTP server, downloads it and uploads it again as a specific file name. This rather odd way of doing it is required, since FTP does not have a native copy operation. The highly specific task is due to a webcam that uploads images directly to an FTP site, and we want to embed the latest picture on a web page.

This program has been written and tested with Python 2.x, not with Python 3.x. Please, make a note of that.

## prerequisites
This program requires [ftputil](http://ftputil.sschwarzer.net/trac) to be installed. In UNIX-like systems, make a `virtualenv`, activate it, and install ftputil by running `pip install -r requirements.txt`. 

In Windows, if you have Python 2.7.9 (or later) installed (which you should, keeping up to date is important!), you also have `pip` available. If you just installed Python with default settings, all you need to do is type `cmd` in your Start menu, hit Enter, then type `cd \Python27\Scripts` (hit Enter), type `pip install ftputil==3.2` (hit Enter). That should install ftputil for you, using Pip. Python will then find it for you when `image-renamer` runs.

## usage
Configure the program in the source code (this is a quick and dirty script, after all!) by editing the values that are in the top part of the file, that looks as follows:

	# CONFIGURATION START
	
	# Set this to the hostname of the FTP server
	FTP_ADDRESS = "some.host.name.here.com"
	
	FTP_USERNAME = "anonymous"  # change these to a user that can upload files!
	FTP_PASSWORD = "anonymous@"
	
	# List the folders we are supposed to work with. Remember to make them
	# absolute, i.e., have them start with a slash.
	FOLDERS = [
	    "/an/absolute/path",
	    "/some/other/absolute path",
	    "/note/that/spaces are not escaped",
	    "/at least not for windows hosts",
	]
	
	# The file name that we want to output in the end, e.g., current.jpg
	TARGET_NAME = "current.jpg"
	
	# What file types are we working with? (default: have Python try to figure it
	# out, based on what the TARGET_NAME is set to)
	FILE_TYPE = os.path.splitext(TARGET_NAME)
	
	# CONFIGURATION END

Once that is done, just run the program. In Windows, this means finding the Python executable and passing the name of the script to it as a parameter. In UNIX-like systems, you just have to run the program as usual.
