#!/usr/bin/env python
import os
import rosbag
import sys
import math
import numpy as np
import matplotlib.pyplot as plt


class moving_average(object):
    def __init__(self, name, windowsize=5000):
        self.name = name
        self.window_size = windowsize
        self.last_t = None
        self.dts = list()

    def update(self, t):
        if self.last_t is None:
            self.last_t = t
        else:
            self.dts.append(t-self.last_t)
            self.last_t = t
            if len(self.dts) > self.window_size-1:
                print "hit window size"
                self.dts.pop(0)

    def get_stats(self):
        n = len(self.dts)
        if n > 0:
            mean = sum(self.dts)/n
            rate = 1./mean if mean > 0 else 0.
            std_dev = math.sqrt(sum((x - mean)**2 for x in self.dts) /n)
            min_dt = min(self.dts)
            max_dt = max(self.dts)
            return [rate, mean, std_dev, min_dt, max_dt]
        else:
            return [0,0,0,0,0]


    # was used for debugging ...
    def plot(self,separate_figure=False):
        if separate_figure:
            s = self.get_stats()
        f = plt.figure(self.name)
        plt.hold(True)
        n = len(self.dts)
        plt.plot(np.array(self.dts))
        plt.plot([0,n], [s[1],s[1]],'r')
        plt.plot([0,n], [s[1]+3*s[2],s[1]+3*s[2]],'g')
        plt.plot([0,n], [s[1]-3*s[2],s[1]-3*s[2]],'g')
        if separate_figure:
            f.show()


for bagfile in sys.argv[1:]:

    print "Bag:", bagfile

    # Go through the bag file:
    tfs = dict()
    for topic, msg, t in rosbag.Bag(bagfile).read_messages(topics= ['/tf']):
        for t in msg.transforms:
            key = t.header.frame_id + ' -> ' + t.child_frame_id
            if not key in tfs:
                tfs[key] = moving_average(key, 50000)
            tfs[key].update(t.header.stamp.to_sec())
            
    # Create a nice table with the stats
    max_len = max([len(str(x)) for x in tfs.keys()]+[len('Transformation')])
    total_len =(max_len + 3 + 5*9) 
    titles = 'rate[Hz] mean(dt) std(dt) max(dt) min(dt)'.split()
    print '-'*total_len
    print format('Transformation','>%is' % max_len) + '   ' + ''.join([format(x,'<9s') for x in titles])
    print '-'*total_len
    for k,v in tfs.iteritems():
        print format(k,'>%is' % max_len) + '   ' + ''.join([format(format(x,'.4f'),'<9s') for x in v.get_stats()])
    print '-'*total_len
    
    
