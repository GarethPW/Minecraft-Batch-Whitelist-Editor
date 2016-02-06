'''
    edit.py for Python 2.7 by Gareth Welch (www.garethpw.net)
    You may distribute and edit this code as you please, provided that credit is given.

    Appends to or creates a whitelist.json file based on a list of usernames.
    
    wl   -> whitelist
    wlf  -> whitelist file
    wol  -> whitelist original length (players before update)
    np   -> new players
    npf  -> new players file
    fp   -> failed players
    fpf  -> failed players file
    reqs -> urllib2 Requests
'''

import json,urllib2,codecs
from time import sleep
from webbrowser import open as webopen

def info(s,c=0):
    print '['+["INFO","WARNING"][c]+"] "+s

def make_wl():
    with codecs.open("whitelist.json",'w',encoding="utf-8-sig") as wlf:
            wlf.write("[]") #Create empty whitelist.json if the file does not exist
            wlf.close()

def csreplace(s,o,n):
    for i in o:
        s = s.replace(i,n)
    return s

# Enable the update checker?
check_for_updates = True

# Do not edit this value!
ver = "1.4.0"

print "Batch Whitelist Editor v"+ver+" by GarethPW"

usuc = not check_for_updates
if check_for_updates:
    info("Checking for a new version...")
    try:
        if ver == urllib2.urlopen("http://garethpw.net/dev/bwe/currentver.txt").read():
            usuc = True
            info("Version is up to date!")
        else:
            info("Version is outdated! Please download the latest version from the website.")
            sleep(0.5)
            webopen("http://garethpw.net/repo/nav/misc/Batch%20Whitelist%20Editor/")
    except urllib2.HTTPError:
        info("Failed to check for an update!",1)
        usuc = True
else:
    info("Update checking is disabled! This is not recommended.",1)
sleep(0.5)

if usuc:
    fp = []
    wl = []

    info("Loading whitelist.json...")

    while True:
        try:
            with codecs.open("whitelist.json",'r',encoding="utf-8-sig") as wlf:
                wl = list(set([(i['uuid']+i['name']).lower() for i in json.loads(wlf.read())])) #Decode whitelist.json file
                wlf.close()
                break
        except IOError:
            info("whitelist.json does not exist; creating...")
            make_wl()
        except ValueError:
            info("whitelist.json is corrupted or badly formatted; recreating...")
            make_wl()

    wol = len(wl)
                
    info("Done!")
    sleep(0.5)

    info("Loading UUIDs of new players and appending to whitelist...")

    with codecs.open("new_players.txt",'r',encoding="utf-8-sig") as npf:
        np = list(set([csreplace(l,"\r\n ",'').lower() for l in npf])) #List new players from new_players.txt and remove duplicates
        for i in range(len(np)):
            if ',' in np[i]: #If iteration contains a comma,
                split = np[i].split(',') #Split into seperate names
                np[i] = split[0] #Replace existing iteration with first name
                for e in range(1, len(split)):
                    np.append(split[e]) #Give other names their own entry in np
        try:
            for i in np:
                np.remove('') #Remove all empty iterations of np
        except:
            pass
        np = list(set(np)) #Remove duplicates
        fp = np[:]
        reqs = [urllib2.Request("https://api.mojang.com/profiles/minecraft",json.dumps(np[i*100:(None if i > len(np)//100 else (i+1)*100)]),{'Content-Type':'application/json'}) for i in range(len(np)//100+1)] #Create Request objects with payloads so that they can be easily accessed later
        for i in range(len(reqs)): #For each Request object,
            for i2 in range(15): #Attempt fifteen times
                try:
                    for c in json.loads(urllib2.urlopen(reqs[i]).read()): #Open the Request, read it, and decode
                        wl.append((c['id'][0:8]+'-'+c['id'][8:12]+'-'+c['id'][12:16]+'-'+c['id'][16:20]+'-'+c['id'][20:32] #For each compound in the returned list, record uuid and name
                                  +c['name']).lower())
                        fp.remove(c['name'].lower())
                    if i2 > 0:
                        info("Success!") #If we didn't succeed originally, announce our success
                    break #On success, continue to next Request
                except ValueError: #If all names are non-existant,
                    break #Continue to next request
                except urllib2.HTTPError: #If we encounter an HTTP error (eg. 429 - Too many requests),
                    if i2 == 14:
                        info("Tried fifteen times with no luck; marking all as failed.",1)
                    else:
                        info("HTTP Error; retrying...",1)
                        sleep(2)
            info(str(len(np) if i+1 > len(np)//100 else (i+1)*100)+'/'+str(len(np))+" names processed, "+str((len(np) if i+1 > len(np)//100 else (i+1)*100)-(len(wl)-wol))+" failures.")
            #if i <= len(np)//100:
            #    sleep(0.5) #Uncomment this to enable throttling. Should only be useful when processing 60000+ names
        npf.close()

    wl = [{'uuid':i[:36], #Convert uuid and username data into valid json
           'name':i[36:]} for i in list(set(wl))]

    with codecs.open("whitelist.json",'w',encoding="utf-8-sig") as wlf:
        wlf.write(json.dumps(wl,indent=4,separators=(',', ': '))) #Save file with indents to make it look fancy
        wlf.close()
    with codecs.open("failed_players.txt",'w',encoding="utf-8-sig") as fpf:
        for i in fp:
            fpf.write(i+"\r\n") #Write failed players to failed_players.txt
        fpf.close()

    info("Done with "+str(len(fp))+" failures.")
    sleep(0.5)
