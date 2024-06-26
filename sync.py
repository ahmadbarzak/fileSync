#!/usr/bin/env python3
import os
import shutil
import hashlib
import json
import sys
import time

def readJsonFile(jsonPath):
    if (not os.path.exists(jsonPath)):
        open(jsonPath, "x")
        Dict = {}
    elif os.path.getsize(jsonPath) == 0:
            Dict = {}
    else:
        with open(jsonPath) as f:
            Dict = json.load(f)
    return Dict

def getTimeString(timeFloat):
    return time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(timeFloat))
            
def getDigest(path):
    sha256Hash = hashlib.sha256()
    with open(path,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byteBlock in iter(lambda: f.read(4096),b""):
            sha256Hash.update(byteBlock)
    return sha256Hash.hexdigest()

def updateLastModTime(path, syncTime):
    updatedTime = time.mktime(time.strptime(syncTime, "%Y-%m-%d %H:%M:%S %z"))    
    os.utime(path, (os.path.getatime(path), updatedTime))

def getLastModTime(syncTime):
    return time.mktime(time.strptime(syncTime, "%Y-%m-%d %H:%M:%S %z"))
                        
def updateSyncFile(dir):
    jsonPath = os.path.join(dir, ".sync")
    Dict = readJsonFile(jsonPath)
    #go through the other directory's files
    for file in os.listdir(dir):
        if(file == ".sync"):
            continue
        currentPath = os.path.join(dir, file)
        #if it's a file, copy it over
        if os.path.isfile(currentPath):
            #get the file's time
            fullTimeString = getTimeString(os.path.getmtime(currentPath))
            #get the file's digest
            digest = getDigest(currentPath)
            
            #Check if the current file is in the json file (dictionary) already
            if file not in Dict:
            #if not, then add it in
                Dict[file] = [[fullTimeString, digest]]
            
            #check if the current file digest matches the newest corresponding sync file digest
            elif Dict[file][0][1] != digest:
                #if it doesn't, then append this data to the front of the sync file
                Dict[file] = [[fullTimeString, digest]] + Dict[file]
                #if the current file has a matching digest, then update the current file's modified time
                #to match the sync file  (we can do this step even if the time is already the same)
            else:
                updateLastModTime(currentPath, Dict[file][0][0])       
    for key in Dict:
        if not os.path.isfile(os.path.join(dir, key)):
            if not (Dict[key][0][1] == "deleted"): 
                currentTime = time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(time.time()))
                Dict[key] = [[currentTime, "deleted"]] + Dict[key]
    
    with open(jsonPath, "w") as outfile:
        json.dump(Dict, outfile, indent = 4)
    return Dict

def fileMerge(DictA, DictB, dirA, dirB, key):
    if not (key in DictB):
        DictB[key] = [[DictA[key][0][0], DictA[key][0][1]]]
    else:
        DictB[key] = [[DictA[key][0][0], DictA[key][0][1]]] + DictB[key]
    shutil.copy(os.path.join(dirA, key), dirB)
    updateLastModTime(os.path.join(dirA, key), DictA[key][0][0])
    updateLastModTime(os.path.join(dirB, key), DictA[key][0][0])

def matchDigests(DictA, DictB, dirA, dirB, key):
    for pair in DictB[key]:
        if DictA[key][0][1] == pair[1]:
            os.remove(os.path.join(dirA, key))
            shutil.copy(os.path.join(dirB, key), dirA) 
            DictA[key] = [[DictB[key][0][0], DictB[key][0][1]]] + DictA[key]
            updateLastModTime(os.path.join(dirA, key), DictB[key][0][0])
            return 1
    return 0

def syncDirectories(dir1, dir2):
    #check if each directory is actually valid
    isDir1 = os.path.isdir(dir1)
    isDir2 = os.path.isdir(dir2)
    #if neither directory is valid, then an error message should display
    #and the programme should stop running
    if (not isDir1) and (not isDir2):
        print("Directories do not exist, please insert two valid directories.")
        quit()
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
        fullDict = readJsonFile(jsonPath)
        #go through the other directory's files
        for file in os.listdir(full):
            if(file == ".sync"):
                continue
            currentPath = os.path.join(full, file)
            #if it's a file, copy it over
            if os.path.isfile(currentPath):
                shutil.copy(currentPath, empty)     
                #get the file's time
                fullTimeString = getTimeString(os.path.getmtime(currentPath)) 
                #get the file's digest    
                digest = getDigest(currentPath)    
                #Check if the current file is in the json file (dictionary) already
                if file not in fullDict:
                    #if not, then add it in
                    fullDict[file] = [[fullTimeString, digest]]        
                #check if the current file digest matches the newest corresponding sync file digest
                elif fullDict[file][0][1] != digest:
                    #if it doesn't, then append this data to the front of the sync file
                    fullDict[file] = [[fullTimeString, digest]] + fullDict[file]
                #if the current file has a matching digest, then update the current file's modified time
                #to match the sync file  (we can do this step even if the time is already the same)
                else:
                    #get the newest sync time  
                    updateLastModTime(currentPath, fullDict[file][0][0])        
                #update the json file for both
                emptyDict[file] = [[fullDict[file][0][0], digest]]
                updateLastModTime(os.path.join(empty, file), fullDict[file][0][0])                  
            #if it's a directory, copy it over recursively
            if os.path.isdir(currentPath):
                shutil.copytree(currentPath, os.path.join(empty, file))
        
        #check if a file's been deleted:
        for key in fullDict:
            if not os.path.isfile(os.path.join(full, key)):
                if not (fullDict[key][0][1] == "deleted"):
                    currentTime = time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(time.time()))
                    fullDict[key] = [[currentTime, "deleted"]] + fullDict[key]
        
        with open(jsonPath, "w") as outfile:
            json.dump(fullDict, outfile, indent = 4)
        with open(os.path.join(empty, ".sync"), "w") as outfile:
            json.dump(emptyDict, outfile, indent = 4)
    else:
        Dict1 = updateSyncFile(dir1)
        Dict2 = updateSyncFile(dir2)
    
        #go through each file in dictionary 1
        for key in Dict1:
            # if it's in dictionary 2 then we can make comparisons with the file
            if key in Dict2:
                #get the lmts of the dicts
                dir1ModTime = getLastModTime(Dict1[key][0][0])
                dir2ModTime = getLastModTime(Dict2[key][0][0])
            
                #if they have matching digests update the modified time
                if (Dict1[key][0][1] == "deleted" and Dict2[key][0][1] == "deleted"):
                    if dir1ModTime < dir2ModTime:
                        Dict2[key][0][0] = Dict1[key][0][0]
                    else:
                        Dict1[key][0][0] = Dict2[key][0][0]
                
                elif Dict1[key][0][1] == Dict2[key][0][1]:
                    if dir1ModTime < dir2ModTime:
                        Dict2[key][0][0] = Dict1[key][0][0]
                        updateLastModTime(os.path.join(dir2, key), Dict1[key][0][0])
                    else:
                        Dict1[key][0][0] = Dict2[key][0][0]
                        updateLastModTime(os.path.join(dir1, key), Dict2[key][0][0])
                else:
                    if (Dict1[key][0][1] == "deleted" or Dict2[key][0][1] == "deleted"):
                        #if not, then check if one of them is deleted.
                        checkedDict1 = 0
                        if Dict1[key][0][1] == "deleted":
                            checkedDict1 = 1
                            # if dict one is deleted, check if the directory before it is not deleted
                            if (not Dict1[key][1][1] == "deleted") and ((len(Dict2[key]) == 1) or (not Dict2[key][1][1] == "deleted")):
                                #if this is the case, delete this file in the other directory
                                Dict2[key] = [[Dict1[key][0][0], "deleted"]] + Dict2[key]
                                os.remove(os.path.join(dir2, key))
                                # if both previous directorys are deleted, then update the
                                # current deleted file to match the present one
                            elif (Dict1[key][0][1] == "deleted" and Dict2[key][1][1] == "deleted"):
                                fileMerge(Dict2, Dict1, dir2, dir1, key)
                    
                        if Dict2[key][0][1] == "deleted" and checkedDict1 == 0:
                            # if dict one is deleted, check if the directory before it is not deleted
                            if (((len(Dict1[key]) == 1) or (not Dict1[key][1][1] == "deleted")) and (not Dict2[key][1][1] == "deleted")):
                                #if this is the case, delete this file in the other directory
                                Dict1[key] = [[Dict2[key][0][0], "deleted"]] + Dict1[key]
                                os.remove(os.path.join(dir1, key))
                                # if both previous directorys are deleted, then update the
                                # current deleted file to match the present one
                            elif (Dict1[key][1][1] == "deleted" and Dict2[key][0][1] == "deleted"):
                                fileMerge(Dict1, Dict2, dir1, dir2, key)
                    
                    else:
                        if dir1ModTime > dir2ModTime:
                            updated = matchDigests(Dict1, Dict2, dir1, dir2, key)
                            if not updated:
                                os.remove(os.path.join(dir2, key))
                                fileMerge(Dict1, Dict2, dir1, dir2, key)
                        else:
                            updated = matchDigests(Dict2, Dict1, dir2, dir1, key)
                            if not updated:
                                os.remove(os.path.join(dir1, key))
                                fileMerge(Dict2, Dict1, dir2, dir1, key)
            # if not then chuck it into the other directory
            else:
                if not (Dict1[key][0][1] == "deleted"):
                    fileMerge(Dict1, Dict2, dir1, dir2, key)
    
        for key2 in Dict2:
            if not (key2 in Dict1) and (not (Dict2[key2][0][1] == "deleted")):
                fileMerge(Dict2, Dict1, dir2, dir1, key2) 
            
        with open(os.path.join(dir1, ".sync"), "w") as outfile:
            json.dump(Dict1, outfile, indent = 4)
        with open(os.path.join(dir2, ".sync"), "w") as outfile:
            json.dump(Dict2, outfile, indent = 4)

    # This last part implements recursion for subdirectories:
    for dir in os.listdir(dir1):
        if os.path.isdir(os.path.join(dir1, dir)):
            syncDirectories(os.path.join(dir1, dir), os.path.join(dir2, dir))
    for dir in os.listdir(dir2):
        if not (dir in os.listdir(dir1)):
            syncDirectories(os.path.join(dir1, dir), os.path.join(dir2, dir))

if not(len(sys.argv) == 3): 
    print("Invalid number of inputs: please insert two valid directories.")
    quit()

dir1 = sys.argv[1]
dir2 = sys.argv[2]
#this whole process synchronizes two directories:

syncDirectories(dir1, dir2)