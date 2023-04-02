import sys
import cv2
import numpy as np
from PIL import Image



def count_frames(path: str, override:str=False):
    if override:
        return int(count_frames_manual(cv2.VideoCapture(path)))
    else:
        return int(cv2.VideoCapture(path).get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
def count_frames_manual(video):
	# initialize the total number of frames read
	total = 0
	# loop over the frames of the video
	while True:
		# grab the current frame
		(grabbed, frame) = video.read()
	 
		# check to see if we have reached the end of the
		# video
		if not grabbed:
			break
		# increment the total number of frames read
		total += 1
	# return the total number of frames in the video file
	return total

def convertionWithResize(height: int,width: int,video,resample):
    count = 0
    success = True
    l_vectors = []
    while success:
        vector = np.zeros(shape=(height,width),dtype=bool)
        success,image = video.read()
        imgArray = np.asarray(cv2.resize(src=image,dsize=(height,width),interpolation=resample))
        print(imgArray.size)
        for i in range(height):
            for j in range(width):
                if np.array_equal(np.array([0,0,0]),imgArray[i][j]):
                    vector[i][j] = False
                else:
                    vector[i][j] = True
        print(f"Cached frame: {count+1}")
        l_vectors.append(vector)           
        count += 1
    return l_vectors

def convertion(height: int,width: int,video):
    count = 0
    success = True
    l_vectors = []
    while success:
        vector = np.zeros(shape=(height,width),dtype=bool)
        success,image = video.read()
        imgArray = np.asarray(image)
        for i in range(height):
            for j in range(width):
                if np.array_equal(np.array([0,0,0]),imgArray[i][j]):
                    vector[i][j] = False
                else:
                    vector[i][j] = True
        print(f"Cached frame: {count+1}")
        l_vectors.append(vector) 
        count += 1
    return l_vectors

args = sys.argv
#print(args)
#args = ['c:/Users/Katana GF66 11UC/Documents/BadAppleESP32 Project/Code maker/main.py', 'C:\\Users\\Katana GF66 11UC\\Documents\\BadAppleESP32 Project\\Code maker\\main_1000.mp4', '-l', '-r', '320x200']
if len(args) <= 1:
    raise Exception ("You must give at least the video path")
else:
    l_pattern = 8
    dither = False
    nex_i = False
    custom_res = False
    ready = False
    resize = False
    resample = Image.LANCZOS
    batch = False
    for i in range(len(args)):
        if i == 0:
            pass
        elif(args[i] == "-r"):
            height = int(args[i+1].split("x")[0])
            width = int(args[i+1].split("x")[1])
            custom_res = True
            nex_i = True
        elif args[i] == "-d":
            dither = True
        elif args[i] == "-lc" and resize == False:
            resample = cv2.INTER_LANCZOS4
        elif args[i] == "-lc" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-nr" and resize == False:
            resample = cv2.INTER_NEAREST
        elif args[i] == "-nr" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-bc" and resize == False:
            resample = cv2.INTER_CUBIC
        elif args[i] == "-bc" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-bl" and resize == False:
            resample = cv2.INTER_LINEAR
        elif args[i] == "-bl" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-b2" and resize == False:
            resample = cv2.INTER_BITS2
        elif args[i] == "-b2" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-ar" and resize == False:
            resample = cv2.INTER_AREA
        elif args[i] == "-ar" and resize == True:
            print("You can only use 1 resize algoritm")
        elif nex_i:
            nex_i = False
        elif args[i] == "-a":
            batch=True
        elif custom_res:
            path = args[i]
        elif not custom_res and not ready:
            path = args[i]
            vid = cv2.VideoCapture(path)
            height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            ready = True
        elif not ready:
            path = args[i]
            vid = cv2.VideoCapture(path)
            ready = True
if not batch:
    print(f"----SUMMARY----\nFile path: {path}\nDither: {dither}\nResample algoritm: {resample}\nHeight: {height}\nWidth: {width}\nThe convertion will start, Press 1 to make a test of the resample algoritm\npress anything else to start the convertion.")
    sel = input()
    if sel == "1":
        print("Frame for testing: ")
        frame = int(input())
        sus = True
        con = 0
        while sus and frame != con:
            sus,img = vid.read()
            con += 1
        imgTest = cv2.resize(src=img,dsize=(height,width),interpolation=resample)
        cv2.imwrite(filename="test.png",img=imgTest)
        print("File save as test.png, press any button to start convertion\n\nDuring convertion press ESC to cancel the process")
        input()
    else:     
        print("Press any button to start convertion\n\nDuring convertion press ESC to cancel the process")

if resize:
    lFrames = convertionWithResize(width=width,height=height,video=vid,resample=resample)
else:
    lFrames = convertion(width=width,height=height,video=vid)

l_subframes = []
l_frames_compress = []

i = 0
j = 0
k = 0
h_sprite = 0
w_sprite = 0

# de cada fotograma se coge sub fotogramas cuadrados de orden l_pattern x l_pattern, 
# entonce hay que hacer que el programa coja desde 0 hasta 8 y lo meta en un vector, 
# ahora mismo mi idea es que vaya sean 5 for (si, extremadamente eficiente),entonces 
# el primero es el de los frames, luego el otro es el de los subframes horizontales y 
# el otro los subframes verticales, el siguiente lo que hace es llenar los subframes 
# entonces deben ser desde 0 hasta l_pattern, y yo creeria que deberia ser desde 1, 
# porque hay que ver como solucionar lo de 0, porque eso me puede tirar problemas aunque 
# creo que podria ser ((sprite_actual)*l_pattern)+(p_actual)) YO CREO Y ESPERO QUE SIRVA
for frame in lFrames:
    subframe_map = np.zeros(shape=(height/l_pattern,width/l_pattern))
    for i in range(height/l_pattern):
        for j in range(width/l_pattern):
            subframe = np.zeros(shape=(l_pattern,l_pattern),dtype=bool)
            for subframe_i in range(l_pattern):
                for subframe_j in range(l_pattern):
                    subframe[subframe_i][subframe_j] = frame[(i*l_pattern)+(subframe_i)][(i*l_pattern)+(subframe_i)]
            if l_subframes.count(subframe) > 0:
                subframe_map[i][j] = l_subframes.index(subframe)
            else:
                l_subframes.append(subframe)
                subframe_map[i][j] = l_subframes.index(subframe)
                print("new subframe created")
    l_frames_compress.append(subframe_map)
    print(subframe_map)
    print(l_subframes)                  
                        
                    
                
            
        
    

