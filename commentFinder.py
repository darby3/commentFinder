import requests
import sys
from bs4 import BeautifulSoup
from bs4 import Comment

print('Hit ctrl-c at any time to exit.\n')

"""
sys.argv for command line arguments.
Makes it easier to rerun and/or modify searches.

sys.argv[1] -> target string
sys.argv[2] -> url prefix
sys.argv[3] -> starting path

Get inputs direct from user if the arguments are empty.
"""

targetStringCL = sys.argv[1]
urlPrefixCL = sys.argv[2]
startingPathCL = sys.argv[3]

if targetStringCL:
    print ('Searching for ' + targetStringCL)
    targetString = targetStringCL
else:
    targetString = input('Enter a string to search for in the comments: ')

if urlPrefixCL:
    print ('At the site ' + urlPrefixCL)
    urlPrefix = urlPrefixCL
else:
    urlPrefix = input('Enter a url prefix; do not add trailing slash: ')

if startingPathCL:
    print ('Starting at ' + startingPathCL)
    startingPath = startingPathCL
else:
    startingPath = input('Enter a starting path; begin with a trailing slash, or leave blank: ')


currentUrl = ''
soup = None
comments = None

filename = 'output.txt'
pathsFile = 'filelist.txt'


# Update our soup object
def updateSoupObject(urlPostfix):
    global currentUrl
    currentUrl = urlPrefix + urlPostfix

    r = requests.get(currentUrl)
    if r.status_code != 200:
        print("Status code:", r.status_code)

    global soup
    soup = BeautifulSoup(r.text, 'html.parser')

updateSoupObject(startingPath)

# Search comments for a target string


def updateComments():
    global comments
    comments = soup.find_all(string=lambda text:isinstance(text,Comment))

updateComments()

def checkComments(incomingComments):
    print('\nChecking comments in ' + currentUrl)
    for c in incomingComments:
        if targetString in c:
            print('***** Target found in ' + currentUrl)
            print(c)
            print('\n')

            with open(filename, 'a') as file_object:
                file_object.write('***** Target found in ' + currentUrl + '\n')

checkComments(comments)

# Get some outbound links to crawl

outboundLinks = []
outboundLinksMaxLength = 0

def buildLinkList(incomingLinks):
    global outboundLinksMaxLength

    for link in incomingLinks:
        href = str(link.get('href'))
        if (len(href) > 1):
            if urlPrefix in href:
                href = href[len(urlPrefix):]
            if (href[0] == '/') and (href[-4:] != '.pdf'):
                if (href not in outboundLinks):
                    outboundLinks.append(href)
                    # print(link.get('href'))

    print('Outbound links: ' + str(len(outboundLinks)))
    if len(outboundLinks) > outboundLinksMaxLength:
        outboundLinksMaxLength = len(outboundLinks)
        print('New outboundLinksMaxLength:' + str(outboundLinksMaxLength))

        with open(pathsFile, 'w') as paths_file_object:
            for item in outboundLinks:
                paths_file_object.write(item + "\n")

    # for item in outboundLinks:
    #     print(item)

buildLinkList(soup.find_all('a'))

# print(outboundLinks)

"""
so by this point we've generated a starting list of url postfixes to work with.
now the job is to start looping over this list, feeding them back into the
functions above, until we find the match we're looking for. and then keep going
or drop out.
"""

for newPostfix in outboundLinks:
    updateSoupObject(newPostfix)
    updateComments()
    checkComments(comments)
    buildLinkList(soup.find_all('a'))
