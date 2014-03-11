#!/usr/bin/env python
import rosbag
import sys
import argparse

parser = argparse.ArgumentParser(description='Extract gps coordinates from bag' 
                   'files to kml files. outputs one kml file per bag file.')
parser.add_argument('bagfiles', metavar='bagfiles', type=str, nargs='+',
                   help='the bag file that should be parsed')
parser.add_argument('-t', 
                    dest='gps_topic', 
                    metavar='gps_topic',
                    action='store',
                    default='/tpcGPS',
                    help='the gps topic name. default is /tpcGPS')
parser.add_argument('-n', 
                    dest='latitude', 
                    metavar='latitude', 
                    default='msg/latitude', 
                    help='the latitude info in the message. Default is: msg/latitude')
parser.add_argument('-e', 
                    dest='longitude', 
                    metavar='longitude', 
                    default='msg/longitude', 
                    help='the longitude info in the message. Default is: msg/longitude')
parser.add_argument('-a', 
                    dest='altitude', 
                    metavar='altitude', 
                    default='0', 
                    help='the altitude info in the message (same as in -e or'
                    '-n. Can be set to 0, this will clamp the path to the'
                    'ground in google earth. Default is: 0')


args = vars(parser.parse_args())
lng = args['longitude'].split('/')
lat = args['latitude'].split('/')
alt = args['altitude'].split('/')
lng = lng[1:] if lng[0] == 'msg' else lng
lat = lat[1:] if lat[0] == 'msg' else lat
alt = alt[1:] if alt[0] == 'msg' else alt

def get_field(msg, path):
    el = msg 
    for i in path:
        el = getattr(el,i)
    return el

def kmlhead(name):
    return '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
    <name>%s</name>
    <Placemark>
        <name>%s</name>
        <LineString>
            <coordinates>
''' % (name, name)

def kmltail():
    return '''
            </coordinates>
            <tesselate>1</tesselate>
        </LineString>
    </Placemark>
</Document>
</kml>
'''

for bagfile in args['bagfiles']:
    print "Parsing bag:", bagfile
    fid = open(bagfile[:-4] + '.kml','w')
    fid.write(kmlhead(bagfile[:-4]))
    for topic, msg, t in rosbag.Bag(bagfile).read_messages(topics=args['gps_topic']):
        if topic == args['gps_topic']:
            if alt[0] == '0':
                fid.write("%f,%f,0 " % (get_field(msg, lng), get_field(msg, lat)))
            else:
                fid.write("%f,%f,%f " % (get_field(msg, lng), get_field(msg, lat), get_field(msg, alt)))
    fid.write(kmltail())
    fid.close()
     

 
