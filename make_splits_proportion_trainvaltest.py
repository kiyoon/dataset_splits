#!/usr/bin/env python

import sys

if len(sys.argv) < 6:
    print "usage: %s [input_dataset_dir] [output_dir] [nb_splits] [validation_proportion (e.g. 0.25)] [test_proportion (e.g. 0.25)]" % sys.argv[0]
    print "Author: Kiyoon Kim (yoonkr33@gmail.com)"
    print "Make random splits from dataset for positive sample oversampling"
    print "Creates 'split_indices.pkl' and 'files.pkl' in [output_dir]"
    print "CAN be used for both oversampling and not oversampling."
    sys.exit()

""" Output_dir/split_indices.pkl File format:
    numpy 3d array of list objects

    arr[split_num, class_index, train_or_val_or_test (0 or 1 or 2)] contains file index list

    ex) arr[3, 5, 0] gives file indices of 4th(3+1) split, 6th(5+1) class, training samples. """

import numpy as np
import os
import random
import pickle
import operator

input_dataset_dir = sys.argv[1]
output_dir = sys.argv[2]
nb_split = int(sys.argv[3])
validation_proportion = float(sys.argv[4])
test_proportion = float(sys.argv[5])

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

white_list_formats = {'jpg'}

classes = []
for subdir in sorted(os.listdir(input_dataset_dir)):
    if os.path.isdir(os.path.join(input_dataset_dir, subdir)):
        classes.append(subdir)
nb_class = len(classes)

samples_per_class = np.zeros(nb_class, dtype='int')

def _recursive_list(subpath):
    return sorted(os.walk(subpath, followlinks=True), key=lambda tpl: tpl[0])

for i, subdir in enumerate(classes):
    subpath = os.path.join(input_dataset_dir, subdir)
    for root, _, files in _recursive_list(subpath):
        for fname in files:
            is_valid = False
            for extension in white_list_formats:
                if fname.lower().endswith('.' + extension):
                    is_valid = True
                    break
            if is_valid:
                samples_per_class[i] += 1

print "# of samples per class: " + str(samples_per_class)


test_count = map(lambda x: int(round(x*test_proportion)), samples_per_class)
validation_count = map(lambda x: int(round(x*validation_proportion)), samples_per_class)
training_count = map(operator.sub, map(operator.sub, samples_per_class, validation_count), test_count)

print "training sample count: " + str(training_count)
print "validation sample count: " + str(validation_count)
print "test sample count: " + str(test_count)

print "minimum training sample count: " + str(min(training_count))
print "minimum validation sample count: " + str(min(validation_count))
print "minimum test sample count: " + str(min(test_count))

filenames = {}
for subdir in classes:
    filenames[subdir] = []
    subpath = os.path.join(input_dataset_dir, subdir)
    for root, _, files in _recursive_list(subpath):
        for fname in sorted(files):
            is_valid = False
            for extension in white_list_formats:
                if fname.lower().endswith('.' + extension):
                    is_valid = True
                    break
            if is_valid:
                # add filename relative to directory
                absolute_path = os.path.join(root, fname)
                filenames[subdir].append(os.path.relpath(absolute_path, subpath))

#import pprint
#pprint.pprint(filenames)
with open(os.path.join(output_dir, 'files.pkl'), 'wb') as f:
    pickle.dump(filenames, f)

# now, we really start random selecting
splits = np.zeros((nb_split, nb_class, 3), dtype=object)
for split in xrange(nb_split):
    for class_idx in xrange(nb_class):
        file_indices = range(samples_per_class[class_idx])
        file_indices2 = range(samples_per_class[class_idx])

        # training
        training_indices = random.sample(file_indices, training_count[class_idx])
        splits[split,class_idx,0] = sorted(training_indices)

        # validation
        # delete training indices first and sample
        for index in sorted(training_indices, reverse=True):
            del file_indices[index]
        validation_indices = random.sample(file_indices, validation_count[class_idx])
        splits[split,class_idx,1] = sorted(validation_indices)

        # test 
        # delete training and validation indices first and sample
        for index in sorted(training_indices + validation_indices, reverse=True):
            del file_indices2[index]
        splits[split,class_idx,2] = sorted(random.sample(file_indices2, test_count[class_idx]))

print splits
with open(os.path.join(output_dir, 'split_indices.pkl'), 'wb') as f:
    pickle.dump(splits, f)
