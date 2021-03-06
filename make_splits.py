#!/usr/bin/env python

import sys

if len(sys.argv) < 5:
    print "usage: %s [input_dataset_dir] [output_dir] [nb_splits] [validation_count] [training_count=None]" % sys.argv[0]
    print "Author: Kiyoon Kim (yoonkr33@gmail.com)"
    print "Make random splits from dataset. If training_count == None, training_count becomes (# of samples of a class of least number of samples) - (validation_count)"
    print "Creates 'split_indices.pkl' and 'files.pkl' in [output_dir]"
    sys.exit()

""" Output_dir/split_indices.pkl File format:
    numpy 3d array of list objects

    arr[split_num, class_index, train_or_val (0 or 1)] contains file index list

    ex) arr[3, 5, 0] gives file indices of 4th(3+1) split, 6th(5+1) class, training samples. """

import numpy as np
import os
import random
import pickle

input_dataset_dir = sys.argv[1]
output_dir = sys.argv[2]
nb_split = int(sys.argv[3])
validation_count = int(sys.argv[4])
training_count = None

if len(sys.argv) >= 6:
    if sys.argv[5] == 'None':
        training_count = None
    else:
        training_count = sys.argv[5]

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

white_list_formats = {'avi', 'mp4'}

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

if training_count is None:
    training_count = samples_per_class.min() - validation_count

print "training sample count: " + str(training_count)
print "validation sample count: " + str(validation_count)

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
splits = np.zeros((nb_split, nb_class, 2), dtype=object)
for split in xrange(nb_split):
    for class_idx in xrange(nb_class):
        file_indices = range(samples_per_class[class_idx])

        # training
        training_indices = random.sample(file_indices, training_count)
        splits[split,class_idx,0] = sorted(training_indices)

        # validation
        # delete training indices first and sample
        for index in sorted(training_indices, reverse=True):
            del file_indices[index]
        splits[split,class_idx,1] = sorted(random.sample(file_indices, validation_count))


print splits
with open(os.path.join(output_dir, 'split_indices.pkl'), 'wb') as f:
    pickle.dump(splits, f)
