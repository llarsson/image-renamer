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
PERIODS = [
    dict(name="morning", start="04:00", end="10:00"),
    dict(name="midday", start="10:00", end="15:00"),
    dict(name="evening", start="15:00", end="22:00")
]

# CONFIGURATION END


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
    mtime = datetime.utcfromtimestamp(modification_time).time()
    start = datetime.time(hour=start_hour, minute=start_minute)
    end = datetime.time(hour=end_hour, minute=end_minute)

    return start <= mtime and mtime <= end


def construct_file_name(period):
    "Construct file name for a given period."
    return TARGET_LABEL + "-" + period["name"] + FILE_TYPE


def construct_newest_file_name():
    "Construct file name for overall most recent file."
    return "most-" + TARGET_LABEL + FILE_TYPE


def find_newest_files(folder):
    """Return absolute paths of newest files on server.

    This function will descend into subdirectories of the folder.

    :param folder: The folder on the FTP server where we shall find the
        newest file. We will descend into subdirectories of this folder.
    :type folder: str

    :returns: The path name of the newest file, i.e., the one with the
        most recent modification time.

    """

    newest_file_name = None
    newest_modification_time = 0.0

    newest_in_period = {"name": period["name"] for period in PERIODS}
    for nip in newest_in_period:
        nip["mtime"] = 0.0
        nip["path"] = None

    file_names_to_avoid = [construct_file_name(period) for period in PERIODS]
    file_names_to_avoid.append(construct_newest_file_name())

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

                # newest overall?
                if mtime > newest_modification_time:
                    newest_file_name = fullpath_filename
                    newest_modification_time = mtime
                # newest in some period?
                for period in PERIODS:
                    if within_period(mtime, period):
                        nip = newest_in_period[period["name"]]
                        if mtime > nip["mtime"]:
                            nip["path"] = fullpath_filename
                            nip["mtime"] = mtime

    newest_files = []
    for nip in newest_in_period:
        newest_files.append({"name": construct_file_name(nip["name"]),
                             "path": nip["path"]})
    newest_files.append({"name": construct_newest_file_name(),
                         "path": newest_file_name})

    return newest_files


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    for folder in FOLDERS:
        temporary_directory = tempfile.mkdtemp()
        for f in find_newest_files(folder):
            local_abspath = os.path.join(temporary_directory, f["name"])
            logging.info("File under %s saved temporarily as %s",
                         folder, local_abspath)
            download_file(f["path"], local_abspath)
            upload_file(local_abspath, folder + "/" + f["name"])
