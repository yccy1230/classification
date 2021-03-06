# This script is a test for transfer learning, which used VGG16 made by machrisaa
# and referred the tutorial of Movan. It is just a test for this classification task.
# PS:为了满足任务需要，还是自己写了一个空的VGG16,上面的注释作废
import tensorflow as tf
import numpy as np
import os
import Classification_label as Cl
from PIL import Image
from tensorflow.contrib import layers


class VGG:
    vgg_mean = [103.939, 116.779, 123.68]
    def __init__(self, vgg16_npy_path=None,restore_from=None):
        # pre-trained parameters
        try:
            self.data_dict = np.load(vgg16_npy_path, encoding='latin1').item()

        except FileNotFoundError:
            print('Please download VGG16 parameters from here https://mega.nz/#!YU1FWJrA!O1ywiCS2IiOlUCtCpI6HTJOMrneN-Qdv3ywQP5poecM\nOr from my Baidu Cloud: https://pan.baidu.com/s/1Spps1Wy0bvrQHH2IMkRfpg')

        self.batch_size=10

        self.tfx = tf.placeholder(tf.float32, [None, 224, 224, 3])
        self.tfy = tf.placeholder(tf.float32, [None, 2])

        #Convert RGB to BGR
        # red, green, blue = tf.split(axis=3, num_or_size_splits=3, value=self.tfx * 255.0)
        # bgr = tf.concat(axis=3, values=[
        #     blue - self.vgg_mean[0],
        #     green - self.vgg_mean[1],
        #     red - self.vgg_mean[2],
        # ])

        # pre-trained VGG layers are fixed in fine-tune
        conv1_1 = self.conv_layer(self.tfx, "conv1_1")
        conv1_2 = self.conv_layer(conv1_1, "conv1_2")
        pool1 = self.max_pool(conv1_2, 'pool1')

        conv2_1 = self.conv_layer(pool1, "conv2_1")
        conv2_2 = self.conv_layer(conv2_1, "conv2_2")
        pool2 = self.max_pool(conv2_2, 'pool2')

        conv3_1 = self.conv_layer(pool2, "conv3_1")
        conv3_2 = self.conv_layer(conv3_1, "conv3_2")
        conv3_3 = self.conv_layer(conv3_2, "conv3_3")
        pool3 = self.max_pool(conv3_3, 'pool3')

        conv4_1 = self.conv_layer(pool3, "conv4_1")
        conv4_2 = self.conv_layer(conv4_1, "conv4_2")
        conv4_3 = self.conv_layer(conv4_2, "conv4_3")
        pool4 = self.max_pool(conv4_3, 'pool4')

        conv5_1 = self.conv_layer(pool4, "conv5_1")
        conv5_2 = self.conv_layer(conv5_1, "conv5_2")
        conv5_3 = self.conv_layer(conv5_2, "conv5_3")

        pool5 = self.max_pool(conv5_3, 'pool5')
#-----------------------之前自己搭的没有任何参数的VGG网络，以注释形式保留，以防万一-------------------------------#
        # conv1_1=tf.layers.conv2d(self.tfx,64,[3,3],strides=(1,1),padding='SAME',name='conv1_1')
        # conv1_2=tf.layers.conv2d(conv1_1,64,[3,3],strides=(1,1),padding='SAME',name='conv1_2')
        # pool1=tf.layers.max_pooling2d(conv1_2,[2,2],[2,2],padding='SAME',name='pool1')
        # pool1_bn=tf.layers.batch_normalization(pool1)
        #
        # conv2_1=tf.layers.conv2d(pool1_bn,128,[3,3],strides=(1,1),padding='SAME',name='conv2_1')
        # conv2_2=tf.layers.conv2d(conv2_1,128,[3,3],strides=(1,1),padding='SAME',name='conv2_2')
        # pool2=tf.layers.max_pooling2d(conv2_2,[2,2],[2,2],name='pool2')
        # pool2_bn=tf.layers.batch_normalization(pool2)
        #
        # conv3_1=tf.layers.conv2d(pool2_bn,256,[3,3],strides=(1,1),padding='SAME',name='conv3_1')
        # conv3_2=tf.layers.conv2d(conv3_1,256,[3,3],strides=(1,1),padding='SAME',name='conv3_2')
        # conv3_3=tf.layers.conv2d(conv3_2,256,[3,3],strides=(1,1),padding='SAME',name='conv3_3')
        # pool3=tf.layers.max_pooling2d(conv3_3,[2,2],[2,2],name='pool3')
        # pool3_bn = tf.layers.batch_normalization(pool3)
        #
        # conv4_1=tf.layers.conv2d(pool3_bn,512,[3,3],strides=(1,1),padding='SAME',name='conv4_1')
        # conv4_2=tf.layers.conv2d(conv4_1,512,[3,3],strides=(1,1),padding='SAME',name='conv4_2')
        # conv4_3=tf.layers.conv2d(conv4_2,512,[3,3],strides=(1,1),padding='SAME',name='conv4_3')
        # pool4=tf.layers.max_pooling2d(conv4_3,[2,2],[2,2],name='pool4')
        # pool4_bn=tf.layers.batch_normalization(pool4)
        #
        # conv5_1=tf.layers.conv2d(pool4_bn,512,[3,3],strides=(1,1),padding='SAME',name='conv5_1')
        # conv5_2=tf.layers.conv2d(conv5_1,512,[3,3],strides=(1,1),padding='SAME',name='conv5_2')
        # conv5_3=tf.layers.conv2d(conv5_2,512,[3,3],strides=(1,1),padding='SAME',name='conv5_3')
        # pool5=tf.layers.max_pooling2d(conv5_3,[2,2],[2,2],name='pool5')
#-------------------之前自己搭的没有任何参数的VGG网络，以注释形式保留，以防万一---------------------------------#
        #My reconstruct network
        pool5_bn=tf.layers.batch_normalization(pool5)
        self.flatten=tf.reshape(pool5_bn,shape=[-1,7*7*512])
        self.fc6 = tf.layers.dense(self.flatten, 4096, activation=None,name='fc6')
        self.fc7=tf.layers.dense(self.fc6,4096,activation=None,name='fc7')
        self.fc7=tf.nn.dropout(self.fc7,keep_prob=0.7)
        self.fc8=tf.layers.dense(self.fc7,2,activation=None,name='fc8')
        #self.fc8 = tf.nn.dropout(self.fc8, keep_prob=0.9)
        self.out=tf.nn.softmax(self.fc8)
        self.sess=tf.Session()

        if restore_from:
            saver = tf.train.Saver()
            saver.restore(self.sess, restore_from)
        else:  # training graph
            self.loss = tf.reduce_mean(-tf.reduce_sum(self.tfy*tf.log(self.out),reduction_indices=[1]))
            self.train_op = tf.train.AdamOptimizer(learning_rate=1e-5).minimize(self.loss)
            self.train_op_1=tf.train.AdamOptimizer(learning_rate=1e-6).minimize(self.loss)
            self.sess.run(tf.global_variables_initializer())

        print('Load Complete!')
    def max_pool(self, bottom, name):
        return tf.nn.max_pool(bottom, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME', name=name)

    def conv_layer(self, bottom, name):
        with tf.variable_scope(name):  # CNN's filter is constant, NOT Variable that can be trained
            conv = tf.nn.conv2d(bottom, self.data_dict[name][0], [1, 1, 1, 1], padding='SAME')
            lout = tf.nn.relu(tf.nn.bias_add(conv, self.data_dict[name][1]))
            return lout

    def train(self):
        # load the tfrecord
        coord = tf.train.Coordinator()
        image, label = Cl.read_and_decode('catch_classification_train.tfrecords', [224, 224, 3])
        label = tf.one_hot(label, 2, dtype=tf.float32)
        img_batch, label_batch = tf.train.shuffle_batch([image, label],
                                                        batch_size=self.batch_size, capacity=5000,
                                                        min_after_dequeue=1000, num_threads=1)
        image_eval, label_eval = Cl.read_and_decode('catch_classification_eval.tfrecords', [224, 224, 3])
        label_eval = tf.one_hot(label_eval, 2, dtype=tf.float32)
        img_eval_batch, label_eval_batch = tf.train.shuffle_batch([image_eval, label_eval],
                                                                  batch_size=self.batch_size, capacity=5000,
                                                                  min_after_dequeue=1000, num_threads=1)
        threads = tf.train.start_queue_runners(sess=self.sess,coord=coord)
        for i in range(1,500):

            val,l=self.sess.run([img_batch,label_batch])
            #print(l)
            if i>=1000:
                self.sess.run(self.train_op_1, feed_dict={self.tfx: val, self.tfy: l})
            else:
                self.sess.run(self.train_op,feed_dict={self.tfx:val,self.tfy:l})
            print("this is the %d th "%i,"loss=",self.sess.run(self.loss,feed_dict={self.tfx:val,self.tfy:l}))
            if i%100==0:
                eval,l_eval=self.sess.run([img_eval_batch,label_eval_batch])
                print("eval=",self.accuracy(eval,l_eval))
                # coord.request_stop()
                # coord.join(threads)
        coord.request_stop()
        coord.join(threads)
        saver=tf.train.Saver()
        saver.save(self.sess,"/home/anguo/PycharmProjects/random_catch/pre_classification_vgg.ckpt")
    def accuracy(self,v_xs,v_ys):

        y_pre = self.sess.run(self.out, feed_dict={self.tfx: v_xs})  # ys:v_ys can be deleted
        correct_prediction = tf.equal(tf.argmax(y_pre,1), tf.argmax(v_ys,1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        acc = self.sess.run(accuracy, feed_dict={self.tfx: v_xs, self.tfy: v_ys})
        return acc

    def eval(self,input):
        input=np.resize(input,[1,224,224,3])
        result=self.sess.run(self.out,feed_dict={self.tfx:input})
        #print(result)
        if np.argmax(result,axis=1)==0:
            out='Uncatchable'
            print("Uncatchable")
        else:
            out='Catchable'
            print("Catchable")
        return out

if __name__ == '__main__':
    # vgg=VGG(vgg16_npy_path='/home/anguo/PycharmProjects/random_catch/vgg16.npy')
    # vgg.train()
    file_path="/media/anguo/Entertainment/Program Files2/BaiduNetdiskDownload/and/Uncatchable"
    vgg=VGG(vgg16_npy_path='/home/anguo/PycharmProjects/random_catch/vgg16.npy',restore_from='/home/anguo/PycharmProjects/random_catch/pre_classification_vgg.ckpt')
    counter=0
    for img_name in os.listdir(file_path):
        path=file_path+'/'+img_name
        input=Image.open(path)
        input=input.resize((224,224))
        out=vgg.eval(input)
        if out=='Uncatchable':
            counter+=1
    print(float(counter/395))
    # input=Image.open('/media/anguo/Entertainment/Program Files2/BaiduNetdiskDownload/Catchable/20180610_145943.jpg')
    # input=input.resize((224,224))
    # vgg.eval(input)