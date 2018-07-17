import sys

allDataList = []
filename = sys.argv[1] # get a file name
c_root = 0
c_http = 0
c_https = 0
c_spambot = 0
finalDict = {}

file = open(filename, "r")
for line in file:
    #print line
    tmp = line.split("\t")
    if tmp[1] == 'captcha':
        if tmp[5].strip() == 'NA':
            allDataList.append('*root*')
            c_root = c_root + 1
        else:
            allDataList.append(tmp[5].strip())
    elif tmp[1] == 'spambot':
        c_spambot = c_spambot + 1

for url in allDataList:
    if url == '*root*':
        continue
    tmp = url.split("://")
    if tmp[0] == 'http':
        c_http = c_http + 1
    elif tmp[0] == 'https':
        c_https = c_https + 1
    else:
        print "WARNING"
        break
        
    if len(tmp) > 2:
        print tmp
    
    iurl = tmp[1].split("/")
    for ele in iurl:
        try:
            finalDict[ele] = finalDict[ele] + 1
        except:
            finalDict[ele] = 1
        
for k, v in finalDict.items(): 
    if v > 1:
        print k + ';'+ str(v)

#print allDataList
print "All: ",len(allDataList)
print "Root: ", c_root
print "Http: ", c_http
print "Https: ", c_https
print "spambot", c_spambot
##print finalDict