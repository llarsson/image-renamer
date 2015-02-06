#!/usr/bin/env python

import tempfile
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

# The file name that we want to output in the end, e.g., current.jpg
TARGET_NAME = "current.jpg"

# What file types are we working with? (default: have Python try to figure it
# out, based on what the TARGET_NAME is set to)
FILE_TYPE = os.path.splitext(TARGET_NAME)

# CONFIGURATION END


def download_file(remote_abspath, local_abspath):
    "Download the remote file to the local path, both absolute"

    with ftputil.FTPHost(FTP_ADDRESS, FTP_USERNAME, FTP_PASSWORD) as ftp:
        ftp.download(remote_abspath, local_abspath)


def upload_file(local_abspath, remote_abspath):
    "Upload the local file to the remote path, both absolute"

    with ftputil.FTPHost(FTP_ADDRESS, FTP_USERNAME, FTP_PASSWORD) as ftp:
        ftp.upload(local_abspath, remote_abspath)


def find_newest_file(folder):
    """Return absolute path of newest file with given suffix.

    This function will descend into subdirectories of the folder.

    :param folder: The folder on the FTP server where we shall find the
        newest file. We will descend into subdirectories of this folder.
    :type folder: str

    :returns: The path name of the newest file, i.e., the one with the
        most recent modification time.

    """

    newest_file_name = None
    newest_modification_time = 0.0

    with ftputil.FTPHost(FTP_ADDRESS, FTP_USERNAME, FTP_PASSWORD) as ftp:
        for dirpath, dirnames, files in ftp.walk(folder):
            for f in [fname for fname in files
                      if fname.endswith(FILE_TYPE)
                      and fname is not TARGET_NAME]:
                fullpath_filename = dirpath + "/" + f
                statinfo = ftp.stat(fullpath_filename)
                logging.debug("%s modified at %f",
                              fullpath_filename,
                              statinfo.st_mtime)
                if statinfo.st_mtime > newest_modification_time:
                    newest_file_name = fullpath_filename
                    newest_modification_time = statinfo.st_mtime

    logging.info("Newest file under %s is %s", folder, newest_file_name)
    return newest_file_name


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    for folder in FOLDERS:
        newest_image_name = find_newest_file(folder)
        if newest_image_name:
            temporary_directory = tempfile.mkdtemp()
            local_abspath = os.path.join(temporary_directory, TARGET_NAME)
            logging.info("Newest file under %s saved temporarily as %s",
                         folder, local_abspath)
            download_file(newest_image_name, local_abspath)
            upload_file(local_abspath, folder + "/" + TARGET_NAME)
