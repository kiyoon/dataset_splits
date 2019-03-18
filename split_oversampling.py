#!/usr/bin/env python

import numpy as np
import sys, os
import pickle

if len(sys.argv) < 6:
    print "usage: %s [files_pickle] [split_indices_pickle] [input_dir] [output_dir] [extension (normally avi or npy)] [makedir=False] [split=-1]" % sys.argv[0]
    print "if split=-1, split all splits. Otherwise split specific split."
    sys.exit()

files_pickle = sys.argv[1]
split_indices_pickle = sys.argv[2]
input_dir = sys.argv[3]
output_dir = sys.argv[4]
extension = sys.argv[5]

makedir=False
if len(sys.argv) >= 7:
    makedir = sys.argv[6] == 'True'

split_num = -1
if len(sys.argv) >= 8:
    split_num = int(sys.argv[7])

with open(files_pickle, 'rb') as f:
    files = pickle.load(f)

with open(split_indices_pickle, 'rb') as f:
    split_indices = pickle.load(f)

classes = sorted(files.keys())

nb_negative = len(files[classes[0]])

for split in xrange(split_indices.shape[0]) if split_num < 0 else xrange(split_num,split_num+1):
    for class_index in xrange(split_indices.shape[1]):
        nb_positive = len(files[classes[class_index]])
        nb_duplicate = int(round(nb_negative / nb_positive)) - 1    # note 1 subtracted. There will be (nb_duplicate+1) same samples

        class_name = classes[class_index]
        input_class_dir = os.path.join(input_dir, class_name)
        for train_val in xrange(split_indices.shape[2]):
            if train_val == 0:
                train_val_dir = 'train%d' % split
            else:
                train_val_dir = 'val%d' % split
            output_class_dir = os.path.join(output_dir, train_val_dir, class_name)

            files_in_class = [files[class_name][i] for i in split_indices[split,class_index,train_val]]
            for file_in_class in files_in_class:
                input_filepath = os.path.join(input_class_dir, file_in_class)
                output_filepath = os.path.join(output_class_dir, file_in_class)
                input_file_dirname = os.path.dirname(input_filepath)
                output_file_dirname = os.path.dirname(output_filepath)

                if not os.path.isdir(input_file_dirname):
                    os.makedirs(input_file_dirname)
                if not os.path.isdir(output_file_dirname):
                    os.makedirs(output_file_dirname)

                os.system('cp -al "%s"* "%s"' % (input_filepath, output_file_dirname))
                # oversampling (only for training data)
                if class_index != 0 and train_val == 0:
                    for dup_idx in xrange(nb_duplicate):
                        # only if you want to make it as a directory (multiple same names" e.g. opticalflow sliced
                        if makedir:
                            os.system('mkdir -p "%s.dup%03d.%s"' % (output_filepath, dup_idx, extension))
                        os.system('cp -al "%s"* "%s.dup%03d.%s"' % (input_filepath, output_filepath, dup_idx, extension))




