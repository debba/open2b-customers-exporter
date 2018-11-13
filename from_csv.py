#!/usr/bin/python3

import sys, getopt

from download import GTDownloader as GTD
from download import GTDownloaderError as GTDErr
from download import log
import csv

def main(argv):
    csv_out = False
    try:
        opts, args = getopt.getopt(argv, "c:", ["csv="])
    except getopt.GetoptError:
        log('error', 'init.py -c [filename]')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-c", "--csv"):
            csv_out = arg

    if csv_out is not False:
        file_path = 'downloads/'+csv_out+".csv"
        log("info", "Apro il file %s" % file_path)
        gtd = GTD("andrea@debbaweb.it", "hacker20",
                  "https://www.gtmasterclub.it/eventi/2017/web-marketing-festival-2017")
        with open(file_path, 'rt') as csvfile:
            videos = csv.reader(csvfile, delimiter=',')
            read = 1
            for row in videos:
                log("info", "Scarico il video %d" % read )
                '''gtd.downloadVideo(row[0], row[1], row[2], row[3], row[4])'''
                gtd.downloadSlide(row[0], row[2], row[5])
                read = read + 1



if __name__ == "__main__":
    main(sys.argv[1:])
