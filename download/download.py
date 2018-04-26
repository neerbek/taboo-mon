import os
import sys
import getopt
from time import sleep
import io
import requests
import html
from urllib import parse


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

inputfile = "links2.txt"
outdir = "../data_monsanto/2018-03-29"
baseurl = "http://baumhedlundlaw.com/pdf/monsanto-documents/"

def usage(exitCode=0):
    print('download.py [-i <infile>] [-o <outdir>] [-b <baseurl>] [-h]')
    sys.exit(exitCode)


argv = sys.argv[1:]  # first arg is filename
try:
    opts, args = getopt.getopt(argv, "hi:o:b:", ["help", "inputfile=", "outdir=", "baseurl="])
except getopt.GetoptError:
    usage(exitCode=2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage(exitCode=0)
    elif opt in ("-i", "--inputfile"):
        inputfile = arg
    elif opt in ("-o", "--outdir"):
        outdir = arg
    elif opt in ("-b", "--baseurl"):
        baseurl = arg
        if len(baseurl) > 0 and baseurl[-1] != '/':
            print("Warning, baseurl does not end with a '/', this is probably not what you want")

# f = io.open(inputfile, 'r', encoding='utf8')
# url = f.readline()
# url
# f.close()

notHandled = []
count = 0
with io.open(inputfile, 'r', encoding='utf8') as f:
    for url in f:
        url = url[:-1]  # strip \n
        if not url.endswith(".pdf"):
            print("url was not for a pdf document: " + url)
            notHandled.append(url)
            continue
        url = html.unescape(url)   # convert html entities (&amp;)
        url = parse.unquote_plus(url)  # convert url encoding (%20)
        url = parse.urljoin(baseurl, url)
        index = url.rfind("/")  # reverse find
        filename = os.path.join(outdir, url[index + 1:])  # index+1 works even if index=-1 :)
        # filename becomes loaded with potential weird characters, probably a problem on windows
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception("wrong status_code {} ".format(response.status_code) + url)
        with io.open(filename, 'wb') as outfile:
            outfile.write(response.content)
        count += 1
        if count % 5 == 0:
            print("{}".format(count))
        sleep(0.75)
for url in notHandled:
    print("Not downloaded: " + url)
print("Done. Downloaded {}".format(count))
