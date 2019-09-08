import os
import argparse
import re
from time import time
import cv2
import numpy as np
import kcftracker_cnn_caffe as kcftracker
parser = argparse.ArgumentParser(description='Generating video from images')
parser.add_argument('-inp','--input_images_folder', required=True, help='Input image folder')
parser.add_argument('-mo','--mode', default="None", help='Type of features used: one of "rgb", "cnn", "hog"')
count = 0
args = parser.parse_args()

print(args)

net = None
if args.mode == "cnn":
	import caffe
	caffe.set_device(0)
	caffe.set_mode_gpu()
	model_def = 'vgg16/VGG_ILSVRC_16_layers_deploy.prototxt'
	model_weights = 'vgg16/VGG_ILSVRC_16_layers.caffemodel'
	net = caffe.Net(model_def,      # defines the structure of the model
	                model_weights,  # contains the trained weights
	                caffe.TEST)     # use test mode (e.g., don't perform dropout)
	# input preprocessing: 'data' is the name of the input blob == net.inputs[0]
	transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
	transformer.set_transpose('data', (2, 0, 1))
	# set net to batch size of 1
	image_resize = 224
	net.blobs['data'].reshape(1,3,image_resize,image_resize)

def get_images(data_path, extension='.jpg'):
	files = []
	for file_name in os.listdir(data_path):
		name, extension = os.path.splitext(file_name)
		if extension == '.jpg':
			files.append(os.path.join(data_path,file_name))
	return sorted(files)

def get_features(z):
	transformed_image = transformer.preprocess('data', z)
	net.blobs['data'].data[...] = transformed_image

	# Forward pass.
	out = net.forward(end='conv1_2')['conv1_2']
	y = out[0,:,:,:]
	#y = cv2.resize(y,(z.shape[1],z.shape[0]))
	return y

images = get_images(args.input_images_folder)
ground_truth_txt = open('ground_truth.txt', 'r')
output_txt = open('region.txt', 'wb')
output_list=[]
ground_truth = ground_truth_txt.readline()
output_list.append(ground_truth)
ix, iy, wi, he = re.split(',|\t| |;', ground_truth)
tracker = kcftracker.KCFTracker(True, False, args.mode)
onTracking = False
for i,im in enumerate(images):
	frame = cv2.imread(im)

	if i == 0:
		w = int(wi)
		h = int(he)
		ix = int(ix)
		iy = int(iy)
		tot_time = 0
		cv2.rectangle(frame,(ix,iy), (ix+w,iy+h), (0,255,255), 2)
		tracker.init([ix,iy,w,h], frame, feat = get_features)
		print(ix,iy,w,h)
		onTracking =True

	elif(onTracking):
		t0 = time()
		boundingbox = tracker.update(frame, feat = get_features )
		t1 = time()
		boundingbox = list(map(int, boundingbox))
		cv2.rectangle(frame,(boundingbox[0],boundingbox[1]), (boundingbox[0]+boundingbox[2],boundingbox[1]+boundingbox[3]), (0,255,255), 1)
		print(i,boundingbox)
		output_list.append("{},{},{},{}".format(*boundingbox))
		tot_time += (t1 - t0) 
		cv2.putText(frame, 'FPS: '+str((i)/tot_time), (8,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
	cv2.imwrite("vid/frame%d.jpg" % i, frame)  
#output_txt.write("\n".join(output_list))
output_txt.close()
