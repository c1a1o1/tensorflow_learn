'''
Retraining (Finetuning) Example with vgg.tflearn. Using weights from VGG model to retrain
network for a new task (your own dataset).All weights are restored except
last layer (softmax) that will be retrained to match the new task (finetuning).

edited by wei li for vgg finetuning

'''

# coding=utf8
import tflearn
from tflearn.data_preprocessing import ImagePreprocessing
import os


def vgg16(input, num_class):

    #in the model, we added trainable=False to make sure the parameter are not updated during training
    x = tflearn.conv_2d(input, 64, 3, activation='relu', scope='conv1_1',trainable=False)
    x = tflearn.conv_2d(x, 64, 3, activation='relu', scope='conv1_2',trainable=False)
    x = tflearn.max_pool_2d(x, 2, strides=2, name='maxpool1')

    x = tflearn.conv_2d(x, 128, 3, activation='relu', scope='conv2_1',trainable=False)
    x = tflearn.conv_2d(x, 128, 3, activation='relu', scope='conv2_2',trainable=False)
    x = tflearn.max_pool_2d(x, 2, strides=2, name='maxpool2')

    x = tflearn.conv_2d(x, 256, 3, activation='relu', scope='conv3_1',trainable=False)
    x = tflearn.conv_2d(x, 256, 3, activation='relu', scope='conv3_2',trainable=False)
    x = tflearn.conv_2d(x, 256, 3, activation='relu', scope='conv3_3',trainable=False)
    x = tflearn.max_pool_2d(x, 2, strides=2, name='maxpool3')

    x = tflearn.conv_2d(x, 512, 3, activation='relu', scope='conv4_1',trainable=False)
    x = tflearn.conv_2d(x, 512, 3, activation='relu', scope='conv4_2',trainable=False)
    x = tflearn.conv_2d(x, 512, 3, activation='relu', scope='conv4_3',trainable=False)
    x = tflearn.max_pool_2d(x, 2, strides=2, name='maxpool4')

    x = tflearn.conv_2d(x, 512, 3, activation='relu', scope='conv5_1')
    x = tflearn.conv_2d(x, 512, 3, activation='relu', scope='conv5_2')
    x = tflearn.conv_2d(x, 512, 3, activation='relu', scope='conv5_3')
    x = tflearn.max_pool_2d(x, 2, strides=2, name='maxpool5')

    x = tflearn.fully_connected(x, 4096, activation='relu', scope='fc6')
    x = tflearn.dropout(x, 0.5, name='dropout1')
    #we changed the structure here to let the fc only have 2048, less parameter, enough for our task
    x = tflearn.fully_connected(x, 2048, activation='relu', scope='fc7',restore=False)
    x = tflearn.dropout(x, 0.5, name='dropout2')

    x = tflearn.fully_connected(x, num_class, activation='softmax', scope='fc8',
                                restore=False)

    return x


# data_dir = "webemo_tr/"
model_path = "."
# the file gen by generated by gen_files_list.py
files_list = "./train_fvgg_emo.txt"

from tflearn.data_utils import image_preloader

X, Y = image_preloader(files_list, image_shape=(224, 224), mode='file',
                       categorical_labels=True, normalize=False,
                       files_extension=['.jpg', '.png'], filter_channel=True)
# or use the mode 'floder'
# X, Y = image_preloader(data_dir, image_shape=(224, 224), mode='folder',
#                        categorical_labels=True, normalize=True,
#                        files_extension=['.jpg', '.png'], filter_channel=True)
# print X.shape
num_classes = 7 # num of your dataset

# VGG preprocessing
img_prep = ImagePreprocessing()
img_prep.add_featurewise_zero_center(mean=[123.68, 116.779, 103.939],
                                     per_channel=True)
# VGG Network
x = tflearn.input_data(shape=[None, 224, 224, 3], name='input',
                       data_preprocessing=img_prep)
softmax = vgg16(x, num_classes)
regression = tflearn.regression(softmax, optimizer='adam',
                                loss='categorical_crossentropy',
                                learning_rate=0.0001, restore=False)

model = tflearn.DNN(regression, checkpoint_path='vgg-finetuning',
                    max_checkpoints=3, tensorboard_verbose=2,
                    tensorboard_dir="./logs")

model_file = os.path.join(model_path, "vgg16.tflearn")
model.load(model_file, weights_only=True)

# Start finetuning
model.fit(X, Y, n_epoch=20, validation_set=0.1, shuffle=True,
          show_metric=True, batch_size=64, snapshot_epoch=False,
          snapshot_step=200, run_id='vgg-finetuning')

model.save('ChinaHadoop_vgg_finetune_emo.tfmodel')
##let's just test if the model can predict image right
# model.predict(img_array) to see the final result

