import os
import shutil
import hashlib
import json
import sys
import datetime


def readJsonFile(dir, jsonPath):
    if (not os.path.exists(jsonPath)):
        open(jsonPath, "x")
        Dict = {}
    elif os.path.getsize(jsonPath) == 0:
            Dict = {}
    else:
        with open(jsonPath) as f:
            Dict = json.load(f)
    return Dict

def getTimeString(path):
    fullDateFloat = os.path.getmtime(path)
    fullDateTime = datetime.datetime.fromtimestamp(fullDateFloat)
    return fullDateTime.strftime("%Y-%m-%d %H:%M:%S +1200")
            
def getDigest(path):
    sha256Hash = hashlib.sha256()
    with open(path,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byteBlock in iter(lambda: f.read(4096),b""):
            sha256Hash.update(byteBlock)
    return sha256Hash.hexdigest()

def updateLastModTime(path, syncTime):
    
    syncTime = syncTime[:-6]
    updatedTime = datetime.datetime.strptime(syncTime, '%Y-%m-%d %H:%M:%S').timestamp()
    os.utime(path, (os.path.getatime(path), updatedTime))
    
def getLastModTime(syncTime):
    syncTime = syncTime[:-6]
    return datetime.datetime.strptime(syncTime, '%Y-%m-%d %H:%M:%S').timestamp()
                    
def updateSyncFile(dir):
    jsonPath = os.path.join(dir, ".sync")
    Dict = readJsonFile(dir, jsonPath)
    #go through the other directory's files
    for file in os.listdir(dir):
        if(file == ".sync"):
            continue
        currentPath = os.path.join(dir, file)
        #if it's a file, copy it over
        if os.path.isfile(currentPath):
            #get the file's time
            #get the file's time
            fullDateString = getTimeString(currentPath)
            #fullDateString = time.ctime(fullDateFloat)
            #get the file's digest
            digest = getDigest(currentPath)
            
            #Check if the current file is in the json file (dictionary) already
            if file not in Dict:
            #if not, then add it in
                Dict[file] = [[fullDateString, digest]]
            
            #check if the current file digest matches the newest corresponding sync file digest
            elif Dict[file][0][1] != digest:
                #if it doesn't, then append this data to the front of the sync file
                Dict[file] = [[fullDateString, digest]] + Dict[file]
                #if the current file has a matching digest, then update the current file's modified time
                #to match the sync file  (we can do this step even if the time is already the same)
            else:
                #get the newest sync time
                syncTime = Dict[file][0][0]
                #get the corresponding datetime from this string
                updateLastModTime(currentPath, syncTime)
    with open(jsonPath, "w") as outfile:
        json.dump(Dict, outfile, indent = 4)
    return Dict

def fileMerge(DictA, DictB, dirA, dirB, key):
    os.remove(os.path.join(dirB, key))
    shutil.copy(os.path.join(dirA, key), dirB) 
    DictB[key] = [[DictA[key][0][0], DictA[key][0][1]]] + DictB[key]
    updateLastModTime(os.path.join(dirA, key), DictA[key][0][0])
    updateLastModTime(os.path.join(dirB, key), DictA[key][0][0])

def matchDigests(DictA, DictB, dirA, dirB, key, found):
    if found == 0:
        for pair in DictB[key]:
            if DictA[key][0][1] == pair[1]:
                found = 1
                os.remove(os.path.join(dirB, key))
                shutil.copy(os.path.join(dirA, key), dirB) 
                DictB[key] = [[DictA[key][0][0], DictA[key][0][1]]] + DictB[key]
                updateLastModTime(os.path.join(dirA, key), DictA[key][0][0])
                updateLastModTime(os.path.join(dirB, key), DictA[key][0][0])
                break
        return found
   
#Get your two directories

# if not(len(sys.argv) == 3): 
#     print("Invalid number of inputs: please insert two valid directories.")
#     quit()

dir1 = "dir1" # sys.argv[1]
dir2 = "dir2" # sys.argv[2]
#check if each directory is actually valid
isDir1 = os.path.isdir(dir1)
isDir2 = os.path.isdir(dir2)
#if neither directory is valid, then an error message should display
#and the programme should stop running
if (not isDir1) and (not isDir2):
    print("Directories do not exist, please insert two valid directories.")
#if one directory is valid but the other isn't, then the other
#directory should be created and the files of the valid one
#should be copied into the other directory    
elif (not isDir1) or (not isDir2):
    if(not isDir1):
        empty = dir1
        full = dir2
    else:
        empty = dir2
        full = dir1
    #make the directory
    os.mkdir(empty)
    open(os.path.join(empty, ".sync"), "x")
    emptyDict = {}
    jsonPath = os.path.join(full, ".sync")
    fullDict = readJsonFile(full, jsonPath)
    #go through the other directory's files
    for file in os.listdir(full):
        if(file == ".sync"):
            continue
        currentPath = os.path.join(full, file)
        #if it's a file, copy it over
        if os.path.isfile(currentPath):
            shutil.copy(currentPath, empty)     
            #get the file's time
            fullDateString = getTimeString(currentPath) 
            #fullDateString = time.ctime(fullDateFloat)
            #get the file's digest    
            digest = getDigest(currentPath)    
            #Check if the current file is in the json file (dictionary) already
            if file not in fullDict:
                #if not, then add it in
                fullDict[file] = [[fullDateString, digest]]        
            #check if the current file digest matches the newest corresponding sync file digest
            elif fullDict[file][0][1] != digest:
                #if it doesn't, then append this data to the front of the sync file
                fullDict[file] = [[fullDateString, digest]] + fullDict[file]
            #if the current file has a matching digest, then update the current file's modified time
            #to match the sync file  (we can do this step even if the time is already the same)
            else:
                #get the newest sync time
                syncTime = fullDict[file][0][0]
                #get the corresponding datetime from this string        
                updateLastModTime(currentPath, syncTime)        
            #update the json file for both
            emptyDict[file] = [[fullDict[file][0][0], digest]]                   
        #if it's a directory, copy it over recursively
        if os.path.isdir(currentPath):
            shutil.copytree(currentPath, os.path.join(empty, file))
    with open(jsonPath, "w") as outfile:
        json.dump(fullDict, outfile, indent = 4)
    with open(os.path.join(empty, ".sync"), "w") as outfile:
        json.dump(emptyDict, outfile, indent = 4)
else:
    Dict1 = updateSyncFile(dir1)
    Dict2 = updateSyncFile(dir2)
    
    for key in Dict1:
        if key in Dict2:
            dir1ModTime = getLastModTime(Dict1[key][0][0])
            dir2ModTime = getLastModTime(Dict2[key][0][0])
            if Dict1[key][0][1] == Dict2[key][0][1]:
                if dir1ModTime < dir2ModTime:
                    Dict2[key][0][0] = Dict1[key][0][0]
                    updateLastModTime(os.path.join(dir2, key), Dict1[key][0][0])
                else:
                    Dict1[key][0][0] = Dict2[key][0][0]
                    updateLastModTime(os.path.join(dir1, key), Dict2[key][0][0])
            else:
                found = matchDigests(Dict1, Dict2, dir1, dir2, key, 0)
                found = matchDigests(Dict2, Dict1, dir2, dir1, key, found)
                if found == 0:
                    if dir1ModTime > dir2ModTime:
                        fileMerge(Dict1, Dict2, dir1, dir2, key)
                    else:
                        fileMerge(Dict2, Dict1, dir2, dir1, key)
    with open(os.path.join(dir1, ".sync"), "w") as outfile:
        json.dump(Dict1, outfile, indent = 4)
    with open(os.path.join(dir2, ".sync"), "w") as outfile:
        json.dump(Dict2, outfile, indent = 4)
                