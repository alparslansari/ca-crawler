import urllib2
import re
import sys
from bs4 import BeautifulSoup
from urlparse import urlparse

captchaUrlList = []
allDataList = []
courtesyStop = 10000;


# ayni urli tekrar tekrar parse etme
filename = sys.argv[1]
print filename

file = open(filename, "r") 
for line in file: 
   allDataList.append(line.strip())
print "File is Loaded..."

def writeCaptchaData(url, cid, responseData):
    saveCFile = open('captcha_'+filename+'_'+str(cid)+'_.htm','w')
    saveCFile.write(responseData)
    saveCFile.close()

def findAllLinks(respData, url, domain, openList, closedList):
    print "Finding all related links for : " + url
    print "Domain                        : " + domain
    tempList = []
    soup = BeautifulSoup(respData, "html5lib") #BeautifulSoup.
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
                #print "adding to tempList: "+tlink
            #else:
                #print "Duplicate URL: "+tlink
        else:
            if len(tlink) < 1:
                continue
            if tlink[0] == '/': # ilk eleman / ise
                #print "add list " + tlink
                cturl = urllib2.urlparse.urljoin(url,tlink)
                tempList.append(cturl)
                #print "added   :" + cturl
            else: # find subdomains
                if(tlink.find("."+domain) > -1):
                    if not tlink in tempList:
                        tempList.append(tlink)
                        #print "adding SUBDOMAIN to tempList: "+tlink
                    #else:
                        #print "Duplicate URL: "+tlink
                #else:
                    #print "ignored: " + tlink
    print "The openList is grown by ",len(tempList)," urls"
    return tempList    

def crawlPage(url, cid):
    print "Crawling :"+url
    try:
        # now, with the below headers, we defined ourselves as a simpleton who is
        # still using internet explorer.
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = urllib2.Request(url, headers = headers)
        resp = urllib2.urlopen(req)
        respData = resp.read()
        if re.search('captcha', respData, re.IGNORECASE):
            print "Captcha is found: "+url
            writeCaptchaData(url, cid, respData)
            return 'c'
        elif re.search('spambot', respData, re.IGNORECASE):
            print "Spambot is found: "+url
            writeCaptchaData(url, cid, respData)
            return 's'
        else:
            #print "NOT FOUND!"
            return respData
            

        #saveFile = open('withHeaders.txt','w')
        #saveFile.write(str(respData))
        #saveFile.close()
    except Exception as e:
        print(str(e))
        return str(e)

cid = 0        
for url in allDataList:
    cid = cid + 1
    if url == '\n' or url == "" or url is None:
        continue
    result = crawlPage(url, cid)
    if(result == 'c'):
        captchaUrlList.append("captcha\t"+str(cid)+"\t1\t"+url+"\tNA\n")
    elif(result=='s'):
        captchaUrlList.append("spambot\t"+str(cid)+"\t1\t"+url+"\t\NA\n")
    else:
        closedList = []
        domain = urlparse(url).hostname.split('.')[1]
        hostname = urlparse(url).hostname
        print "hostname: "+hostname
        closedList.append(hostname)
        closedList.append(url)
        if url[-1:] == "/":
            url = url[:-1]
            closedList.append(url)
        #print "closedList"+closedList
        tempList = []
        tempList = findAllLinks(result, url, domain, tempList, closedList)
        while len(tempList) > 0:
            print "remaining urls: ",len(tempList)
            print "closed urls   : ",len(closedList)
            if len(closedList) > courtesyStop:
                break
            turl = tempList.pop(0)
            closedList.append(turl)
            result = crawlPage(turl, cid)
            if(result == 'c'):
                captchaUrlList.append("captcha\t"+str(cid)+"\t"+str(len(closedList))+"\t"+url+"\t"+turl+"\n")
                print "CAPTCHA IS FOUND"
                break
            elif(result=='s'):
                captchaUrlList.append("spambot\t"+str(cid)+"\t"+str(len(closedList))+"\t"+url+"\t"+turl+"\n")
                print "SPAM BOT IS FOUND"
                break
            else:
                tempList2 = findAllLinks(result, turl, domain, tempList, closedList)
                for link in tempList2:
                    tempList.append(link)
        if(result != 'c' or result != 's'):
            captchaUrlList.append("notfound\t"+str(cid)+"\t"+str(len(closedList))+"\t"+url+"\tNA\n")
print captchaUrlList
saveFile = open('report_'+filename,'w')
saveFile.write("".join(captchaUrlList))
saveFile.close()