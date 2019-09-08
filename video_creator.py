import argparse
import cv2
import os
parser = argparse.ArgumentParser()



parser.add_argument('-inp','--input_images_folder', required=True, help='Input image folder')
parser.add_argument('-o','--output_folder', required=True, help='Base output folder for storing generated video')

args = parser.parse_args()



def get_images(data_path, extension='.jpg'):
	files = []
	for file_name in os.listdir(data_path):
		name, extension = os.path.splitext(file_name)
		if extension == '.jpg':
			files.append(os.path.join(data_path,file_name))
	return sorted(files)

images = get_images(args.input_images_folder)
print(images)
print("Total number of frames are {}".format(len(images)))
#for i,im in enumerate(images):
	#frame = cv2.imread(im)
	#cv2.imshow('Images',frame)
	#cv2.waitKey(0)


if not os.path.isdir(args.output_folder):
	os.makedirs(args.output_folder)

shape = cv2.imread(images[0]).shape
new_shape = (shape[0]*2,shape[1]*21, shape[2])
print(shape)
fourcc = cv2.VideoWriter_fourcc(*'MJPG')

out = cv2.VideoWriter(os.path.join(args.output_folder, args.input_images_folder.split('/')[-1] + '.avi'),fourcc, 50.0, (new_shape[1], new_shape[0]))
print(out.isOpened())


for im in images:
	image = cv2.imread(im)
	image = cv2.resize(image, (new_shape[1], new_shape[0]))
	out.write(image)
out.release()
