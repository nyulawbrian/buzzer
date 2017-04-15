#! /usr/bin/python

import settings as bs
import time
import pickle
import shelve

def pickleData(data_to_pickle):
    pickle_file = open(bs.STATEFILE, 'wb')
    pickle.dump(data_to_pickle, pickle_file)
    pickle_file.close()

print "LOOPER imported settings"
print "LOOPER STATEFILE={0}".format(bs.STATEFILE)

loop_counter = 0
is_counting = False

while loop_counter < 50:
    is_counting = True
    loop_counter += 1
    print "LOOPER loop_counter={0}".format(loop_counter)

    d = shelve.open(bs.STATEFILE, writeback=True)
    d['is_counting'] = is_counting
    d['loop_counter'] = loop_counter
    d.close()

    time.sleep(1)

is_counting = False
d = shelve.open(bs.STATEFILE, writeback=True)
d['is_counting'] = is_counting
d.close()

# EOF
