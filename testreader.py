#! /usr/bin/python

import settings as bs
import time
import pickle
import shelve

def unpickleData():
    pickle_file = open(bs.STATEFILE, 'rb')
    data_to_unpickle = pickle.load(pickle_file)
    pickle_file.close()
    return data_to_unpickle

print "READER imported settings"
print "READER STATEFILE={0}".format(bs.STATEFILE)

while True:
    d = shelve.open(bs.STATEFILE, writeback=True)
    is_counting = d['is_counting']
    loop_counter = d['loop_counter']
    print "READER is_counting={0}, loop_counter={1}".format(d['is_counting'], d['loop_counter'])
    d.close()
    time.sleep(1)

# EOF
