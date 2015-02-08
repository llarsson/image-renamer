#!/usr/bin/env python

import tempfile
import datetime
import logging
import os

import ftputil  # external dependency, must be installed via pip or similar


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


class FileInfo(object):
    def __init__(self, mtime=0.0, path=None, name=None):
        self.mtime = mtime
        self.path = path
        self.name = name


def download_file(remote_abspath, local_abspath):
    "Download the remote file to the local path, both absolute"

    with ftputil.FTPHost(FTP_ADDRESS, FTP_USERNAME, FTP_PASSWORD) as ftp:
        ftp.download(remote_abspath, local_abspath)


def upload_file(local_abspath, remote_abspath):
    "Upload the local file to the remote path, both absolute"

    with ftputil.FTPHost(FTP_ADDRESS, FTP_USERNAME, FTP_PASSWORD) as ftp:
        ftp.upload(local_abspath, remote_abspath)


def within_period(modification_time, period):
    "Checks if the given modification time is within the given period"
    start_hour, start_minute = period["start"].split(":")
    end_hour, end_minute = period["end"].split(":")

    # TODO Can we always assume UTC works here?
    mtime = datetime.datetime.utcfromtimestamp(modification_time).time()
    start = datetime.time(hour=int(start_hour), minute=int(start_minute))
    end = datetime.time(hour=int(end_hour), minute=int(end_minute))

    result = start <= mtime and mtime <= end

    logging.debug("%s within interval %s -- %s? %s",
                  str(mtime), period["start"], period["end"],
                  str(result))
    return result


def construct_file_name(period):
    "Construct file name for a given period."
    return TARGET_LABEL + "-" + period["name"] + FILE_TYPE


def find_newest_files(folder):
    """Return absolute paths of newest files on server.

    This function will descend into subdirectories of the folder.

    :param folder: The folder on the FTP server where we shall find the
        newest file. We will descend into subdirectories of this folder.
    :type folder: str

    :returns: The path name of the newest file, i.e., the one with the
        most recent modification time.

    """

    newest_in_period = {period["name"]: FileInfo(name=construct_file_name(period))
                        for period in PERIODS}

    file_names_to_avoid = [construct_file_name(period) for period in PERIODS]

    with ftputil.FTPHost(FTP_ADDRESS, FTP_USERNAME, FTP_PASSWORD) as ftp:
        for dirpath, dirnames, files in ftp.walk(folder):
            for f in [fname for fname in files
                      if fname.endswith(FILE_TYPE)
                      and fname not in file_names_to_avoid]:

                fullpath_filename = dirpath + "/" + f
                statinfo = ftp.stat(fullpath_filename)

                mtime = statinfo.st_mtime

                logging.debug("%s modified at %f",
                              fullpath_filename,
                              mtime)

                for period in PERIODS:
                    if within_period(mtime, period):
                        nip = newest_in_period[period["name"]]
                        if mtime > nip.mtime:
                            nip.path = fullpath_filename
                            nip.mtime = mtime

    newest_files = [fi for fi in newest_in_period.itervalues() if fi.path]

    return newest_files


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    for folder in FOLDERS:
        temporary_directory = tempfile.mkdtemp()
        for fi in find_newest_files(folder):
            local_abspath = os.path.join(temporary_directory, fi.name)
            logging.info("File under %s (%s) saved temporarily as %s",
                         folder, fi.path, local_abspath)
            download_file(fi.path, local_abspath)
            upload_file(local_abspath, folder + "/" + fi.name)
