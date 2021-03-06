import sys
# sys.path.insert(0, "/home/bw/code/caffe/python")
sys.path.insert(0, "/home/hzzone/caffe/python")
import caffe
import numpy as np
import os
import preprocess
import matplotlib.pyplot as plt
import shutil
from scipy.misc import imsave
import dicom

# predict the age from a new dicom file by a trained caffemodel and deploy file
def visualize_layers(caffemodel, deploy, dicom_file, IMAGE_SIZE=227, mode=True, save_dir=""):
    im = preprocess.process(dicom_file, IMAGE_SIZE=IMAGE_SIZE)
    patientID = dicom.read_file(dicom_file).PatientID
    file_name = dicom_file.split("/")[-1]
    if mode:
        caffe.set_mode_gpu()
    else:
        caffe.set_mode_cpu()
    net = caffe.Net(deploy, caffemodel, caffe.TEST)
    net.blobs['data'].reshape(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    # read a dicom file
    net.blobs['data'].data[...] = im
    net.forward()
    # curr_path = os.path.dirname(os.path.abspath(__file__))
    # get every layer feature map and save to files
    for layer_name, param in net.params.iteritems():
            try:
                features = net.blobs[layer_name].data[0]
            except:
                continue

            features_path = os.path.join(save_dir, "%s_%s" % (patientID, file_name))
            # if os.path.exists(features_path):
            #     shutil.rmtree(features_path)
            if not os.path.exists(features_path):
                os.mkdir(features_path)
            features_path = os.path.join(features_path, layer_name)
            if os.path.exists(features_path):
                shutil.rmtree(features_path)
            os.mkdir(features_path)

            try:
                for i, feature in enumerate(features):
                    p = os.path.join(features_path, str(i))
                    plt.imsave(p, feature, cmap=plt.cm.gray)
                    print(p)
            except:
                os.rmdir(features_path)

def vis_square(data):
    """Take an array of shape (n, height, width) or (n, height, width, 3)
       and visualize each (height, width) thing in a grid of size approx. sqrt(n) by sqrt(n)"""

    # normalize data for display

    # force the number of filters to be square
    n = int(np.ceil(np.sqrt(data.shape[0])))
    padding = (((0, n ** 2 - data.shape[0]),
                (0, 1), (0, 1))  # add some space between filters
               + ((0, 0),) * (data.ndim - 3))  # don't pad the last dimension (if there is one)
    data = np.pad(data, padding, mode='constant', constant_values=1)  # pad with ones (white)

    # tile the filters into an image
    data = data.reshape((n, n) + data.shape[1:]).transpose((0, 2, 1, 3) + tuple(range(4, data.ndim + 1)))
    data = data.reshape((n * data.shape[1], n * data.shape[3]) + data.shape[4:])

    plt.imshow(data)
    plt.axis('off')
    plt.show()

def visualize_output_size(caffemodel, deploy, dicom_file, IMAGE_SIZE=227):
    im = preprocess.process(dicom_file, IMAGE_SIZE=IMAGE_SIZE)
    caffe.set_mode_gpu()
    net = caffe.Net(deploy, caffemodel, caffe.TEST)
    net.blobs['data'].reshape(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    # read a dicom file
    net.blobs['data'].data[...] = im
    net.forward()
    # for each layer, show the output shape
    for layer_name, blob in net.blobs.iteritems():
        print layer_name + '\t' + str(blob.data.shape)
    # the parameters are a list of [weights, biases]
    # filters = net.params['conv1'][0].data
    # print filters.shape
    # vis_square(filters.transpose(0, 2, 3, 1))
    # plt.imshow(filters[0])
    for layer_name, param in net.params.iteritems():
        print layer_name + '\t' + str(param[0].data.shape), str(param[1].data.shape)

def save_dir_feature_map(source_list, save_dir, caffemodel, deploy_file):
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    file_list = []
    for source in source_list:
        for root, dirs, files in os.walk(source):
            for dicom_file in files:
                file_list.append(os.path.join(root, dicom_file))
    for dicom_file in file_list:
        visualize_layers(dicom_file=dicom_file, caffemodel=caffemodel, deploy=deploy_file, save_dir=save_dir)

if __name__=="__main__":
    # for root, dirs, files in os.walk("/Volumes/Hzzone-disk/DeepLearning/male_regression/test"):
    #     for index, dicom_file in enumerate(files):
    #         visualize_layers("/Volumes/Hzzone-disk/DeepLearning/male_regression/CaffeNet/model/caffenet_train_iter_2000.caffemodel",
    #                          "/Volumes/Hzzone-disk/DeepLearning/male_regression/CaffeNet/deploy.prototxt",
    #                          os.path.join(root, dicom_file), mode=False)
    # for root, dirs, files in os.walk("/Volumes/Hzzone-disk/DeepLearning/female_regression/test"):
    #     for index, dicom_file in enumerate(files):
    #         visualize_layers("/Volumes/Hzzone-disk/DeepLearning/female_regression/CaffeNet/model/caffenet_train_iter_2000.caffemodel",
    #                          "/Volumes/Hzzone-disk/DeepLearning/female_regression/CaffeNet/deploy.prototxt",
    #                          os.path.join(root, dicom_file), mode=False)
    save_dir_feature_map(save_dir="/home/hzzone/features/male_test1", source_list=["/home/hzzone/Bone-Age-Data/test1/male"], caffemodel="/home/hzzone/1tb/bone-age-model/bysex/male/alexnet/male_alexnet_train_iter_800.caffemodel", deploy_file="/home/hzzone/Bone-Age-Assessment/train/male/AlexNet/alexnet_deploy.prototxt")
    save_dir_feature_map(save_dir="/home/hzzone/features/male_test2", source_list=["/home/hzzone/Bone-Age-Data/test2/male"], caffemodel="/home/hzzone/1tb/bone-age-model/bysex/male/alexnet/male_alexnet_train_iter_800.caffemodel", deploy_file="/home/hzzone/Bone-Age-Assessment/train/male/AlexNet/alexnet_deploy.prototxt")

    save_dir_feature_map(save_dir="/home/hzzone/features/female_test1", source_list=["/home/hzzone/Bone-Age-Data/test1/female"], caffemodel="/home/hzzone/1tb/bone-age-model/bysex/female/caffenet/female_caffenet_train_iter_3900.caffemodel", deploy_file="/home/hzzone/Bone-Age-Assessment/train/female/CaffeNet/caffenet_deploy.prototxt")
    save_dir_feature_map(save_dir="/home/hzzone/features/female_test2", source_list=["/home/hzzone/Bone-Age-Data/test2/female"], caffemodel="/home/hzzone/1tb/bone-age-model/bysex/female/caffenet/female_caffenet_train_iter_3900.caffemodel", deploy_file="/home/hzzone/Bone-Age-Assessment/train/female/CaffeNet/caffenet_deploy.prototxt")

    save_dir_feature_map(save_dir="/home/hzzone/features/all_test1", source_list=["/home/hzzone/Bone-Age-Data/test1/female", "/home/hzzone/Bone-Age-Data/test1/male"], caffemodel="/home/hzzone/1tb/bone-age-model/all/caffenet/all_caffenet_train_iter_4000.caffemodel", deploy_file="/home/hzzone/Bone-Age-Assessment/train/male/CaffeNet/caffenet_deploy.prototxt")
    save_dir_feature_map(save_dir="/home/hzzone/features/all_test2", source_list=["/home/hzzone/Bone-Age-Data/test2/female", "/home/hzzone/Bone-Age-Data/test2/male"], caffemodel="/home/hzzone/1tb/bone-age-model/all/caffenet/all_caffenet_train_iter_4000.caffemodel", deploy_file="/home/hzzone/Bone-Age-Assessment/train/female/CaffeNet/caffenet_deploy.prototxt")

    save_dir_feature_map(save_dir="/home/hzzone/features/male_train", source_list=["/home/hzzone/Bone-Age-Data/initial_data_train/male", "/home/hzzone/Bone-Age-Data/new_data_train/new_data_processed/male"], caffemodel="/home/hzzone/1tb/bone-age-model/bysex/male/alexnet/male_alexnet_train_iter_800.caffemodel", deploy_file="/home/hzzone/Bone-Age-Assessment/train/male/AlexNet/alexnet_deploy.prototxt")

    save_dir_feature_map(save_dir="/home/hzzone/features/female_train", source_list=["/home/hzzone/Bone-Age-Data/initial_data_train/female", "/home/hzzone/Bone-Age-Data/new_data_train/new_data_processed/female"], caffemodel="/home/hzzone/1tb/bone-age-model/bysex/female/caffenet/female_caffenet_train_iter_3900.caffemodel", deploy_file="/home/hzzone/Bone-Age-Assessment/train/female/CaffeNet/caffenet_deploy.prototxt")

    save_dir_feature_map(save_dir="/home/hzzone/features/all_train", source_list=["/home/hzzone/Bone-Age-Data/initial_data_train", "/home/hzzone/Bone-Age-Data/new_data_train"], caffemodel="/home/hzzone/1tb/bone-age-model/all/caffenet/all_caffenet_train_iter_4000.caffemodel", deploy_file="/home/hzzone/Bone-Age-Assessment/train/female/CaffeNet/caffenet_deploy.prototxt")
