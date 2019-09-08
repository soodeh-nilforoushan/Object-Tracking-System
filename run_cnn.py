import numpy as np 
import cv2
import sys
from time import time
import argparse
import os
import theano
import kcftracker_cnn as kcftracker
from generic_utils import *
import new_vgg16
import new_vgg16.vgg16
parser = argparse.ArgumentParser()
parser.add_argument('-inv','--input_video_name', required=False, help='Input image folder')
parser.add_argument('-opt','--output_folder', required=True, help='Output file path')
parser.add_argument('-mo','--mode', default="None",  help='One of cnn or hog or rgb')
count = 0

args = parser.parse_args()
selectingObject = False
initTracking = False
onTracking = False
ix, iy, cx, cy = -1, -1, -1, -1
w, h = 0, 0

inteval = 30
duration = 0.01

if args.mode == "cnn":
	vgg_net = new_vgg16.vgg16.build_model()	
	get_conv1 = new_vgg16.vgg16.get_layer_output_function(vgg_net,'conv1_2')

if not os.path.isdir(args.output_folder):
	os.makedirs(args.output_folder)

'''def get_features(z):
	image = cv2.resize(z,(256,256))
	if np.max(image) <= 1:
		image = (image*255).astype(theano.config.floatX)
	image = image.transpose(2,0,1)
	image = image[None,:,:,:]
	start = time()
	y = get_conv1(image)[0]
	print("Vgg_net  %s" %(time()-start))
	y = y[6]
	y = y[None,:,:]
	y =y.transpose(1,2,0)
	y = cv2.resize(y,(z.shape[0],z.shape[1]))
	print("y shape", y.shape)
	#y = y[None,:,:]

	return y'''

def get_features(z):
	#print("z", z.shape)
	image = cv2.resize(z,(256,256))
	if np.max(image) <= 1:
		image = (image*255).astype(theano.config.floatX)
	image = image.transpose(2,0,1)
	image = image[None,:,:,:]
	start = time()
	y = get_conv1(image)[0]
	#print("Vgg_net  %s" %(time()-start))
	y = y[9]
	y = y[None,:,:]
	y =y.transpose(1,2,0)
	#print("y trans", y.shape)
	y = cv2.resize(y,(z.shape[1],z.shape[0]))
	#print("y shape", y.shape)

	#y = y[None,:,:]
	#y = y.transpose(1,2,0)
	return y
	


# mouse callback function
def draw_boundingbox(event, x, y, flags, param):
	global selectingObject, initTracking, onTracking, ix, iy, cx,cy, w, h
	
	if event == cv2.EVENT_LBUTTONDOWN:
		selectingObject = True
		onTracking = False
		ix, iy = x, y
		cx, cy = x, y
	
	elif event == cv2.EVENT_MOUSEMOVE:
		cx, cy = x, y
	
	elif event == cv2.EVENT_LBUTTONUP:
		selectingObject = False
		if(abs(x-ix)>10 and abs(y-iy)>10):
			w, h = abs(x - ix), abs(y - iy)
			ix, iy = min(x, ix), min(y, iy)
			initTracking = True
		else:
			onTracking = False
	
	elif event == cv2.EVENT_RBUTTONDOWN:
		onTracking = False
		if(w>0):
			ix, iy = x-w/2, y-h/2
			initTracking = True



if __name__ == '__main__':
	if(args.input_video_name==None):
		cap = cv2.VideoCapture(0)
	else:
		cap = cv2.VideoCapture(args.input_video_name)
	tracker = kcftracker.KCFTracker(True, False, args.mode)  # hog, fixed_window, multiscale
	#if you use hog feature, there will be a short pause after you draw a first boundingbox, that is due to the use of Numba.

	cv2.namedWindow('tracking')
	cv2.setMouseCallback('tracking',draw_boundingbox)

	while(cap.isOpened()):
		ret, main_frame = cap.read()
		#print(main_frame.shape)
		w_x = main_frame.shape[0]
		w_y = main_frame.shape[1]
		if(w_x<w_y) and (w_y>=224):
			scale = w_x
		elif (w_y<w_x) and (w_x>=224):
			scale = w_y
		else:
			scale = 224
		frame = main_frame
		main_frame = cv2.resize(main_frame, (scale,scale))
		frame = cv2.resize(frame, (224,224))
		scaleframe = scale/frame.shape[0]
		if not ret:
			break

		if(selectingObject):
			cv2.rectangle(main_frame,(ix,iy), (cx,cy), (0,255,255), 1)
		elif(initTracking):
			cv2.rectangle(main_frame,(ix,iy), (ix+w,iy+h), (0,255,255), 2)

			tracker.init([int(ix/scaleframe),int(iy/scaleframe),int(w/scaleframe),int(h/scaleframe)], frame, feat = get_features)

			initTracking = False
			onTracking = True
		elif(onTracking):
			t0 = time()
			boundingbox = tracker.update(frame,feat = get_features)
			t1 = time()

			boundingbox = list(map(int, boundingbox))
			#print(boundingbox)
			for i in range(0,4):
				boundingbox[i] = int(boundingbox[i]*scaleframe)
			#print(boundingbox)
			cv2.rectangle(main_frame,(boundingbox[0],boundingbox[1]), (boundingbox[0]+boundingbox[2],boundingbox[1]+boundingbox[3]), (0,255,255), 1)
			
			duration = 0.8*duration + 0.2*(t1-t0)
			#duration = t1-t0
			cv2.putText(main_frame, 'FPS: '+str(1/duration)[:4].strip('.'), (8,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
		#frame1 =cv2.resize(frame,(main_frame.shape[1],main_frame.shape[0]))
		cv2.imshow('tracking', main_frame)
		cv2.imwrite("vid/frame%d.jpg" % count, main_frame)  
		count += 1
		c = cv2.waitKey(inteval) & 0xFF
		if c==27 or c==ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()
