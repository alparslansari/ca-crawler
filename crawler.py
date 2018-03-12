import urllib2
import re
import sys
from bs4 import BeautifulSoup
from urlparse import urlparse

courtesyStop = 250; # If we parse .. number of urls, stop crawling

def num(s):
    try:
        return int(s)
    except ValueError:
        return 0
        
# We should not crawl the same URL!

if len(sys.argv) == 2:
    filename = sys.argv[1] # get a file name
    startidx = 0
elif len(sys.argv) == 3:
    filename = sys.argv[1] # get a file name
    startidx = num(sys.argv[2])
else:
    print "Wrong syntax. Use as 'python crawler.py data.txt' or 'python crawler.py data.txt <index>'"
    print "<index> is the starting point should be a number"
    sys.exit()


allDataList = []
# read the file: It should contain URLS for crawling
file = open(filename, "r") 
for line in file: 
   allDataList.append(line.strip())
print "File is Loaded..."

# The purpose of this function is store the page source
def writeCaptchaData(cid, responseData):
    saveCFile = open('captcha_'+filename+'_'+str(cid)+'_.htm','w')
    saveCFile.write(responseData)
    saveCFile.close()
    
def writeErrors(err):
    errorFile = open('error_'+filename,'a')
    errorFile.write(err)
    errorFile.close()
    
def writeReport(data):
    reportFile = open('report_'+filename,'a')
    reportFile.write(data)
    reportFile.close()

# This function parses a web page to find all href
# returns all urls as a list
def findAllLinks(respData, url, domain, openList, closedList):
    print "Finding all related links for : " + url
    print "Domain                        : " + domain
    tempList = []
    soup = BeautifulSoup(respData, "html5lib", from_encoding="utf-8") #BeautifulSoup.
    for link in soup.findAll("a"):
        tlink = link.get("href")
        if (tlink in tempList) or (tlink in closedList) or (tlink in openList):
            #print "In list, skipping " + tlink
            continue
        if tlink is None:
            print "None object found, skipping..."
            continue
        
        if tlink.count("http") > 1:
            print "Skipping :"+tlink
            continue
        
        if(tlink.find(url) > -1):
            if not tlink in tempList:
                tempList.append(tlink)
                #print "1- adding to tempList: "+tlink
            #else:
                #print "Duplicate URL: "+tlink
        else:
            if len(tlink) < 1:
                continue
            if tlink[0] == '/': # ilk eleman / ise
                #print "add list " + tlink
                if(url.find(domain)<0):
                    print "2- Skipping: " + url
                    continue
                cturl = urllib2.urlparse.urljoin(url,tlink)
                tempList.append(cturl)
                #print "2- added   :" + cturl
            else: # find subdomains
                if(tlink.find("."+domain) > -1):
                    if not tlink in tempList:
                        tempList.append(tlink)
                        #print "3- adding SUBDOMAIN -"+domain+"- to tempList: "+tlink
                    #else:
                        #print "Duplicate URL: "+tlink
                #else:
                    #print "ignored: " + tlink
    print "The openList is grown by ",len(tempList)," urls"
    return tempList    

# This function takes a url, retrieves it and search if it has captcha
def crawlPage(url, cid):
    print cid, "-) Crawling :"+url
    try:
        # now, with the below headers, we defined ourselves as a simpleton who is
        # still using internet explorer.
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = urllib2.Request(url, headers = headers)
        resp = urllib2.urlopen(req)
        #print "->"+resp.headers.get('content-length','0')
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
            writeErrors("ERROR:Unicode err\t see cid:"+str(cid)+"\n")
        return "<html><head><title>ERROR</title></head><body></body></html>"

cid = 0 # index
testWflag = False
# Loop all urls from file
for url in allDataList:
    cid = cid + 1
    if startidx > 0 and startidx > cid:
        print "Skipping url...cid=",cid
        continue
    if url == '\n' or url == "" or url is None:
        continue
    result = crawlPage(url, cid)
    if(result == 'c'):
        writeReport("captcha\t"+str(cid)+"\t1\t"+url+"\tNA\n")
    elif(result=='s'):
        writeReport("spambot\t"+str(cid)+"\t1\t"+url+"\t\NA\n")
    else:
        closedList = []
        
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
        #print "closedList"+closedList
        tempList = []
        tempList = findAllLinks(result, url, domain, tempList, closedList)
        
        # Check www condition
        if len(tempList) == 0 and testWflag:
            tempList.append("https://www."+hostname)
            tempList.append("http://www."+hostname)
            print "Try crawling http|s://www."+hostname
                
        while len(tempList) > 0:
            print "remaining urls: ",len(tempList)
            print "closed urls   : ",len(closedList)
            if len(closedList) > courtesyStop:
                break
            turl = tempList.pop(0)
            closedList.append(turl)
            
            if(turl.find(domain)<0):
                print "----> domain: "+domain+" not found in " + turl
                continue
            result = crawlPage(turl, cid)
            
            if(result == 'c'):
                writeReport("captcha\t"+str(cid)+"\t"+str(len(closedList))+"\t"+url+"\t"+turl+"\n")
                print "CAPTCHA IS FOUND"
                break
            elif(result=='s'):
                writeReport("spambot\t"+str(cid)+"\t"+str(len(closedList))+"\t"+url+"\t"+turl+"\n")
                print "SPAM BOT IS FOUND"
                break
            elif(result=='err'):
                #append url to error.txt
                print "err found, skipping"
            else:
                try:
                    tempList2 = findAllLinks(result, turl, domain, tempList, closedList)
                    
                    for link in tempList2:
                        if (courtesyStop * 10) > len(tempList):
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
            
            # Check www condition
            if len(tempList) == 0 and len(closedList) < courtesyStop and testWflag:
                tlink = "www."+hostname
                if not tlink in closedList:
                    tempList.append(tlink)
                tlink = "https://www."+hostname
                if not tlink in closedList:
                    tempList.append(tlink)
                tlink = "http://www."+hostname
                if not tlink in closedList:
                    tempList.append(tlink)
                print "Try crawling last resort"

                
        if(result != 'c' and result != 's'):
            writeReport("notfound\t"+str(cid)+"\t"+str(len(closedList))+"\t"+url+"\tNA\n")

print "The END"

