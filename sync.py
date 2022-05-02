import os
import shutil
import hashlib
import json


# Get the file directories, check if they're actual valid directories.

# dir1 = input("please input dir1\n")
# dir2 = input("please input dir2\n")
# isDir1 = os.path.isdir(dir1)
# isDir2 = os.path.isdir(dir2)
# if (not isDir1) and (not isDir2):
#     print("Insert error here and exit")
# elif (not isDir1):
#     print("create Dir1 directory, copy Dir2 stuff into dir1")
#     print("sync files")
# elif (not isDir2): 
#     print("create Dir1 directory, copy Dir2 stuff into dir1")
#     print("sync files")
# else:
#     print("sync files")
#     print("try to merge directories, account for deletions")



#Get last modified time of a file

# def getLMT(path):
# path = "C:/Users/Ahmad Barzak/Desktop/howdyg.txt"
# date = os.path.getmtime(path)
# print(date)



#Copy file contents of one directory into another

# path = "C:/Users/Ahmad Barzak/Desktop/demo"
# newpath = "C:/Users/Ahmad Barzak/Desktop/demo2/"
# for file in os.listdir(path):
#     currentPath = os.path.join(path, file)
#     if os.path.isfile(currentPath):
#         print(file + " is a file")
#         shutil.copy(currentPath, newpath)
#     if os.path.isdir(currentPath):
#         print(file + " is a directory")



# Obtain the digest of a file

# currentFile = "C:/Users/Ahmad Barzak/Desktop/demo/hello.txt"
# sha256Hash = hashlib.sha256()
# with open(currentFile,"rb") as f:
#     # Read and update hash string value in blocks of 4K
#     for byteBlock in iter(lambda: f.read(4096),b""):
#         sha256Hash.update(byteBlock)
# print(sha256Hash.hexdigest())



# Make a JSON file and write to it
#example:

# dictionary = {
#     "file1_1.txt" : [
#         [
#             "2022-03-26 12:03:44 +1200",
#             "d6072668c069d40c27c3f982789b32e33f23575316ebbbc11359c49929ac8adc"
#         ],
#         [
#             "2022-03-26 12:03:42 +1200",
#             "a2ebea1d55e6059dfb7b8e8354e0233d501da9d968ad3686c49d6a443b9520a8"
#         ]
#     ],
#     "file1_2.txt" : [
#         [
#             "2022-03-26 12:03:42 +1200",
#             "c62b8de531b861db068eac1129c2e3105ab337b225339420d2627c123c7eae04"
#         ]
#     ],
#     "file2_1.txt" : [
#         [
#             "2022-03-26 12:03:42 +1200",
#             "3032e7474e22dd6f35c618045299165b0b42a9852576b7df52c1b22e3255b112"
#         ]
#     ],
# }

# with open(".sync.json", "w") as outfile:
#     json.dump(dictionary, outfile)


# step 1:

#Get your two directories
dir1 = "dir1"
dir2 = "dir2"

#check if each directory is actually valid
isDir1 = os.path.isdir(dir1)
isDir2 = os.path.isdir(dir2)


#if neither directory is valid, then an error message should display
#and the programme should stop running
if (not isDir1) and (not isDir2):
    print("Insert error here and exit")
    
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
    
    
    jsonPath = os.path.join(full, ".sync.JSON")
    open(os.path.join(empty, ".sync.JSON"), "x")
    emptyDict = {}
    if (not os.path.exists(jsonPath)):
        open(jsonPath, "x")
        fullDict = {}
    elif os.path.getsize(jsonPath) == 0:
            fullDict = {}
    else:
        with open(jsonPath) as f:
            fullDict = json.load(f)
    
    
    
    #go through the other directory's files
    for file in os.listdir(full):
        if(file == ".sync.JSON"):
            continue
        currentPath = os.path.join(full, file)
        #if it's a file, copy it over
        if os.path.isfile(currentPath):
            shutil.copy(currentPath, empty)
            
            #update the json file for both
            emptyDict[file] = ["date", "time"]
            
            if file in fullDict:
                fullDict[file] = ["date", "time"] + fullDict[file]
            else:
                fullDict[file] = ["date", "time"]
                        
        #if it's a directory, copy it over recursively
        if os.path.isdir(currentPath):
            shutil.copytree(currentPath, os.path.join(empty, file))
    
    with open(jsonPath, "w") as outfile:
        json.dump(fullDict, outfile)
    with open(os.path.join(empty, ".sync.JSON"), "w") as outfile:
        json.dump(emptyDict, outfile)
    
else:
    print("sync files")
    print("try to merge directories, account for deletions")







#Read JSON file into a dictionary to easily manipulate

# with open('.sync.JSON') as f:
#     data = json.load(f)
    
# print("\nfile1_1.txt:\n")
# print(data["file1_1.txt"][0][0])
# print(data["file1_1.txt"][0][1] + "\n")
# print(data["file1_1.txt"][1][0])
# print(data["file1_1.txt"][1][1])
# print("\nfile1_2.txt:\n")
# print(data["file1_2.txt"][0][0])
# print(data["file1_2.txt"][0][1])
# print("\nfile2_1.txt:\n")
# print(data["file2_1.txt"][0][0])
# print(data["file2_1.txt"][0][1] + "\n")

