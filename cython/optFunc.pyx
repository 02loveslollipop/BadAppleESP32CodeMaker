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

def solveSubframe(object frameBuffer,int width,int height, int l_pattern):
    cdef l_subframesX = 2
    cdef np.ndarray l_subframes = np.zeros(shape=(l_subframesX,l_pattern,l_pattern),dtype=bool)
    l_subframes[0] = np.asarray([
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False]
        ])

    l_subframes[1] = np.asarray([
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True]
        ])
    l_frames_compress = []
    cdef int total = 0
    cdef int index = 2
    cdef np.ndarray subframe
    cdef np.ndarray subframe_map
    cdef int k
    cdef int val
    cdef bint finded
    for frame in frameBuffer:
        subframe_map = np.zeros(shape=(int(width/l_pattern),int(height/l_pattern)))
        finded = False
        for i in range(len(subframe_map)):
            for j in range(len(subframe_map[0])):
                subframe = np.zeros(shape=(l_pattern,l_pattern))
                for subframe_i in range(l_pattern):
                    for subframe_j in range(l_pattern):
                        subframe[subframe_i][subframe_j] = frame[(i*l_pattern)+(subframe_i)][(j*l_pattern)+(subframe_j)]
                try:
                    subframe_map[i][j] = np.where(np.all(l_subframes==subframe, axis=(1, 2)))[0][0]
                except IndexError:
                    l_subframesX += 1
                    l_subframes.resize((l_subframesX,l_pattern,l_pattern),refcheck=False)
                    l_subframes[index] = subframe
                    subframe_map[i][j] = index
                    index += 1
                total += 1
        l_frames_compress.append(subframe_map)
    
    return l_subframes, l_frames_compress, total, (index-2)