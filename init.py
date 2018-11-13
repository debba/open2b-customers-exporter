#!/usr/bin/python3

import sys, getopt

from download import NinoDownloader as ND
from download import NinoDownloaderError as NDErr
from download import log

def main(argv):
    username = ''
    password = ''
    link = ''
    chunk = -1
    try:
        opts, args = getopt.getopt(argv, "hu:p:l:c:", ["user=", "password=", "link=", "chunk="])
    except getopt.GetoptError:
        log('error', 'init.py -u <user> -p <password> -l <link> [ -c <chunk> ]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            log('info', 'init.py -u <user> -p <password> -l <link> [ -c <chunk> ]')
            sys.exit()
        elif opt in ("-u", "--user"):
            username = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-l", "--link"):
            link = arg
        elif opt in ("-c", "--chunk"):
            chunk = arg

    if username == '' or password == '' or link == '':
        log('error', 'init.py -u <user> -p <password> -l <link> [ -c <chunk> ]')
        sys.exit()

    try:
        gtd = ND(username, password, link, chunk)
        gtd.downloadAnags()
    except NDErr as err:
        log("Error", err)


if __name__ == "__main__":
    main(sys.argv[1:])
