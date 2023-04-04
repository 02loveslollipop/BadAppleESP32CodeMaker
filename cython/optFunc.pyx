import cv2
import numpy as np
cimport numpy as np
cimport cython

def convertionWithResize(int height,int width,int threshold,object video,object resample):
    cdef int count = 0
    cdef bint success = True
    l_vectors = []
    while True:
        vector = np.zeros(shape=(width,height),dtype=bool)
        success,image = video.read()
        if not success:
            break
        imgArray = np.asarray(cv2.resize(src=image,dsize=(height,width),interpolation=resample))
        for j in range(len(imgArray[1])):
            for i in range(len(imgArray)):
                if imgArray[i][j][0] < threshold or imgArray[i][j][1] < threshold or imgArray[i][j][2] < threshold:
                    vector[i][j] = True
                else:
                    vector[i][j] = False
        print(f"Cached frame: {count+1}")
        l_vectors.append(vector)           
        count += 1
    return l_vectors

def convertion(int height,int width,int threshold,object video):
    cdef int count = 0
    cdef bint success = True
    l_vectors = []
    while True:
        vector = np.zeros(shape=(height,width),dtype=bool)
        success,image = video.read()
        if not success:
            break
        imgArray = np.asarray(image)
        for i in range(height):
            for j in range(width):
                if imgArray[i][j][0] < threshold or imgArray[i][j][1] < threshold or imgArray[i][j][2] < threshold:
                    vector[i][j] = True
                else:
                    vector[i][j] = False
        print(f"Cached frame: {count+1}")
        l_vectors.append(vector) 
        count += 1
    return l_vectors

def findSubFrame(object list_buffer,object subframe):
    cdef int val = 0
    for listed_subframes in list_buffer:
        
        if np.array_equal(listed_subframes,subframe):
            return int(val)
        else:
            val += 1
            
    raise Exception("subFrame not found")
