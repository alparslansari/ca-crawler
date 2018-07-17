import urllib2
import re
import sys
from bs4 import BeautifulSoup
from urlparse import urlparse

courtesyStop = 300; # If we parse .. number of urls, stop crawling
priorityListSize = 30

keywords = ['login', 'cart','subscribe','password','sign','register','join','auth','upload','account','registration']

### HELPER FUNCTIONS ###
def num(s):
    try:
        return int(s)
    except ValueError:
        return 0

def writeCaptchaData(cid, responseData):
    saveCFile = open('captcha_'+filename+'_'+str(cid)+'_.htm','w')
    saveCFile.write(responseData)
    saveCFile.close()

def writeErrors(err):
    errorFile = open('error_'+filename+'.txt','a')
    errorFile.write(err)
    errorFile.close()

def writeReport(data):
    reportFile = open('report_'+filename+'.txt','a')
    reportFile.write(data)
    reportFile.close()

def findAllwSpecialLinks(respData, url, domain, openList, specialList):
    print "DOMAIN [" + domain +"]Finding all related links for : " + url
    soup = BeautifulSoup(respData, "html5lib", from_encoding="utf-8") #BeautifulSoup.
    for link in soup.findAll("a"):
        tlink = link.get("href")
        if tlink is None:
            print "None object found, skipping..."
            continue
        if (tlink in tempList) or (tlink in closedList) or (tlink in openList):
            continue
        if tlink.count("http") > 1:
            print "Skipping :"+tlink
            continue
        if (len(openList) + len(specialList)) >= courtesyStop:
            break # Stop loop or use return
        if(tlink.find(url) > -1):
            if not tlink in tempList:
                for word in keywords:
                    if(tlink.find(word) > -1) and len(specialList) < priorityListSize:
                        specialList.append(tlink)
                        break
                    else:
                        openList.append(tlink)
                        break
        else:
            if len(tlink) < 1:
                continue
            if tlink[0] == '/': # ilk eleman / ise
                if(url.find(domain)<0):
                    print "2- Skipping: " + url
                    continue
                cturl = urllib2.urlparse.urljoin(url,tlink)
                for word in keywords:
                    if(cturl.find(word) > -1) and len(specialList) < priorityListSize:
                        specialList.append(cturl)
                        break
                    else:
                        openList.append(cturl)
                        break
            else: # find subdomains
                if(tlink.find("."+domain) > -1):
                    if not tlink in tempList:
                        for word in keywords:
                            if(tlink.find(word) > -1) and len(specialList) < priorityListSize:
                                specialList.append(tlink)
                                break
                            else:
                                openList.append(tlink)
                                break

# This function parses a web page to find all href
# returns all urls as a list
def findAllLinks(respData, url, domain, openList, closedList):
    print "DOMAIN [" + domain +"]Finding all related links for : " + url
    tempList = []
    soup = BeautifulSoup(respData, "html5lib", from_encoding="utf-8") #BeautifulSoup.
    for link in soup.findAll("a"):
        tlink = link.get("href")
        if tlink is None:
            print "None object found, skipping..."
            continue
        if (tlink in tempList) or (tlink in closedList) or (tlink in openList):
            continue
        if tlink.count("http") > 1:
            print "Skipping :"+tlink
            continue
        if(tlink.find(url) > -1):
            if not tlink in tempList:
                tempList.append(tlink)
        else:
            if len(tlink) < 1:
                continue
            if tlink[0] == '/': # ilk eleman / ise
                if(url.find(domain)<0):
                    print "2- Skipping: " + url
                    continue
                cturl = urllib2.urlparse.urljoin(url,tlink)
                tempList.append(cturl)
            else: # find subdomains
                if(tlink.find("."+domain) > -1):
                    if not tlink in tempList:
                        tempList.append(tlink)
    print "The openList is grown by ",len(tempList)," urls"
    return tempList

# This function takes a url, retrieves it and search if it has captcha
def crawlPageSource(url, cid):
    print cid, "-) Crawling :"+url
    try:
        # now, with the below headers, we defined ourselves as a simpleton who is
        # still using internet explorer.
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = urllib2.Request(url, headers = headers)
        resp = urllib2.urlopen(req, timeout=20)

        if(num(resp.headers.get('content-length','0')) > 1000000):
            print "Page size is too big"
            err = "err:PGS->" + resp.headers['content-length'] + '\t' + url +"\n"
            writeErrors(err)
            return '<html><head><title>ERROR</title></head><body></body></html>'
        respData = resp.read()
        return respData
    except Exception as e:
        print("ERROR!")
        try:
            writeErrors("ERROR\t"+url.decode('ascii', 'ignore')+"\t"+str(e)+"\n")
        except UnicodeEncodeError:
            writeErrors("ERROR:Unicode err\t see cid:"+str(cid)+"\n")
        return "<html><head><title>ERROR</title></head><body></body></html>"
# This function takes a url, retrieves it and search if it has captcha
def searchCaptcha(cid,url,data):
    try:
        if re.search('captcha', data, re.IGNORECASE):
            print "crawlPage:Captcha is found: "+url
            writeCaptchaData(cid, data)
            writeReport("1\tcaptcha\t"+str(cid)+"\t1\t"+url+"\tNA\n")
            return True
        elif re.search('spambot', data, re.IGNORECASE):
            print "crawlPage:Spambot is found: "+url
            writeCaptchaData(cid, data)
            writeReport("1\tspambot\t"+str(cid)+"\t1\t"+url+"\t\NA\n")
            return True
    except Exception as e:
        print("ERROR!")
        try:
            writeErrors("ERROR\t"+url.decode('ascii', 'ignore')+"\t"+str(e)+"\n")
        except UnicodeEncodeError:
            writeErrors("ERROR:Unicode err\t see cid:"+str(cid)+"\n")
        return False

# This function takes a url, retrieves it and search if it has captcha
def crawlPage(url, cid):
    print cid, "-) Crawling :"+url
    try:
        # now, with the below headers, we defined ourselves as a simpleton who is
        # still using internet explorer.
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = urllib2.Request(url, headers = headers)
        resp = urllib2.urlopen(req, timeout=20)

        if(num(resp.headers.get('content-length','0')) > 1000000):
            print "Page size is too big"
            err = "err:PGS->" + resp.headers['content-length'] + '\t' + url +"\n"
            writeErrors(err)
            return 'err'
        print "OK"
        respData = resp.read()
        if re.search('captcha', respData, re.IGNORECASE):
            print "crawlPage:Captcha is found: "+url
            writeCaptchaData(cid, respData)
            return 'c'
        elif re.search('spambot', respData, re.IGNORECASE):
            print "crawlPage:Spambot is found: "+url
            writeCaptchaData(cid, respData)
            return 's'
        else:
            #print "NOT FOUND!"
            return respData
    except Exception as e:
        print("ERROR!")
        try:
            writeErrors("ERROR\t"+url.decode('ascii', 'ignore')+"\t"+str(e)+"\n")
        except UnicodeEncodeError:
            writeErrors("ERROR:Unicode encode err\t see cid:"+str(cid)+"\n")
        except UnicodeDecodeError:
            writeErrors("ERROR:Unicode decode err\t see cid:"+str(cid)+"\n")
        return "<html><head><title>ERROR</title></head><body></body></html>"

def countAllLinks(respData):
    soup = BeautifulSoup(respData, "html5lib", from_encoding="utf-8") #BeautifulSoup.
    return len(soup.findAll("a"))

### END OF HELPER FUNCTIONS ###

# We should not crawl the same URL!
regular = True
if len(sys.argv) == 2:
    filename = sys.argv[1] # get a file name
    startidx = 0
elif len(sys.argv) == 3:
    filename = sys.argv[1] # get a file name
    startidx = num(sys.argv[2])
elif len(sys.argv) == 4:
    filename = sys.argv[1]
    startidx = num(sys.argv[2])
    stopidx = num(sys.argv[3])
    regular = False
else:
    print "Wrong syntax. Use as 'python crawler.py data.txt' or 'python crawler.py data.txt <index>'"
    print "or 'python crawler.py data.txt <index> <stop>'"
    print "<index> is the starting point should be a number"
    sys.exit()


allDataList = []
# read the file: It should contain URLS for crawling
if(not regular):
    file = open(filename, "r")
    count = 0
    for line in file:
       count = count + 1
       if count >=startidx and count <= stopidx:
           print line.strip().split(',')[1]
           allDataList.append(line.strip().split(',')[1])
       elif count > stopidx:
           break
    print "special method: File is Loaded..."
    filename = sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]
else:
    file = open(filename, "r")
    for line in file:
       allDataList.append(line.strip())
    print "File is Loaded..."


cid = 0 # index
testWflag = False
# Loop all urls from file
for url in allDataList:
    cid = cid + 1
    if startidx > 0 and startidx > cid and regular:
        print "Skipping url...cid=",cid
        continue
    if url == '\n' or url == "" or url is None:
        continue

    closedList = []
    tempUrl = "https://www."+url
    result = crawlPageSource(tempUrl, cid)
    returnedLinks = countAllLinks(result)
    print "https://www. Found links: ",returnedLinks
    closedList.append(tempUrl)
    if(returnedLinks < 1):
        tempUrl = "https://"+url
        result = crawlPage(tempUrl, cid)
        returnedLinks = countAllLinks(result)
        print "https:// Found links: ",returnedLinks
        closedList.append(tempUrl)
        if(returnedLinks < 1):
            tempUrl = "http://www."+url
            result = crawlPage(tempUrl, cid)
            returnedLinks = countAllLinks(result)
            closedList.append(tempUrl)
            print "http://www. Found links: ",returnedLinks
            if(returnedLinks < 1):
                tempUrl = "http://"+url
                result = crawlPage(tempUrl, cid)
                returnedLinks = countAllLinks(result)
                closedList.append(tempUrl)
                print "https:// Found links: ",returnedLinks
                if(returnedLinks < 1):
                    writeReport("0\tnotfound\t"+str(cid)+"\t"+str(4)+"\t"+url+"\tNA\n")
                    continue

    url = tempUrl
    print "Initial Crawling completed"
    specialList = []
    tempList = []
    openList = []
    if(searchCaptcha(cid,url,result)):
        continue
    else:
        hostname = urlparse(url).hostname
        if(hostname[0:4] == 'www.'):
            domain = urlparse(url).hostname.split('.')[1]
        else:
            domain = urlparse(url).hostname.split('.')[0]
            testWflag = True

        print "hostname: "+hostname
        print "domain:"+domain
        #break
        closedList.append(hostname)
        closedList.append(url)
        if url[-1:] == "/":
            url = url[:-1]
            closedList.append(url)
            
        findAllwSpecialLinks(result, url, domain, openList, specialList)
        print "Adding urls to queue: openList:",len(openList)," specialList:",len(specialList)
        for ele in specialList:
            tempList.append(ele)
        for ele in openList:
            tempList.append(ele)
        print "SIZE OF TEMPLIST:",len(tempList)

        

        if len(tempList) == 0:
            writeReport("0\tnotfound\t"+str(cid)+"\t"+str(len(closedList))+"\t"+url+"\tNA\n")
            continue

        while len(tempList) > 0:
            print "remaining urls: ",len(tempList)
            print "closed urls   : ",len(closedList)
            if len(closedList) > courtesyStop:
                print "Exiting..."
                tempList = []
                break
            turl = tempList.pop(0)
            closedList.append(turl)

            if(turl.find(domain)<0):
                print "----> domain: "+domain+" not found in " + turl
                continue
            result = crawlPage(turl, cid)

            if(result == 'c'):
                writeReport("1\tcaptcha\t"+str(cid)+"\t"+str(len(closedList))+"\t"+url+"\t"+turl+"\n")
                print "CAPTCHA IS FOUND"
                break
            elif(result=='s'):
                writeReport("1\tspambot\t"+str(cid)+"\t"+str(len(closedList))+"\t"+url+"\t"+turl+"\n")
                print "SPAM BOT IS FOUND"
                break
            elif(result=='err'):
                #append url to error.txt
                print "err found, skipping"
            else:
                if courtesyStop > len(tempList) + len(closedList):
                    try:
                        tempList2 = findAllLinks(result, turl, domain, tempList, closedList)
                        for link in tempList2:
                            if courtesyStop > len(tempList) + len(closedList):
                                tempList.append(link)
                            else:
                                break
                    except Exception as e:
                        try:
                            writeErrors("ERROR\t"+turl.decode('ascii', 'ignore')+"\n")
                            print str(e)
                        except UnicodeEncodeError:
                            writeErrors("ERROR:Unicode err\t see cid:"+str(cid)+"\n")
                            print "ERROR in findAllLinks"
        if(result != 'c' and result != 's'):
            writeReport("0\tnotfound\t"+str(cid)+"\t"+str(len(closedList))+"\t"+url+"\tNA\n")
print "The END"
