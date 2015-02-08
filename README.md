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
	
	# The label we want to give all files. Will be used for naming, e.g., if set
	# to "recent", most recent file will be called "most-recent".
	TARGET_LABEL = "recent"
	
	# What file types are we working with?
	FILE_TYPE = ".jpg"
	
	# Define interesting times of day here. The most recent file for each period
	# will be found and uploaded to the server, with a name constructed as:
	# TARGET_LABEL-PERIOD(name).FILE_TYPE
	# e.g., "recent-morning.jpg".
	# Make the list empty if there are no interesting times of day that should
	# be dealt with particularly.
	# Periods can overlap. This is intentional: if you want to find the most
	# recent file overall, make a period that covers the entire day like in
	# the example below, and call it "overall". A file can then match both
	# a "morning" period and the "overall" period, for example.
	PERIODS = [
	    dict(name="morning", start="04:00", end="09:59"),
	    dict(name="midday", start="10:00", end="14:59"),
	    dict(name="overall", start="00:00", end="23:59"),
	    dict(name="evening", start="15:00", end="22:00")
	]
	
	# CONFIGURATION END

Once that is done, just run the program. In Windows, this means finding the Python executable and passing the name of the script to it as a parameter. In UNIX-like systems, you just have to run the program as usual.
