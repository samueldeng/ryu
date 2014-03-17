import json
import urllib2
import MySQLdb

__author__ = 'samuel'

REST_server = 'http://localhost:8080'

response_switches = urllib2.urlopen(REST_server + '/v1.0/topology/switches').read()
switches_JSON = json.loads(response_switches)

response_links = urllib2.urlopen(REST_server + '/v1.0/topology/links').read()
links_JSON = json.loads(response_links)

for switch in switches_JSON:
    print switch['dpid']
    for ports in switch['ports']:
        print ports['name']
        print ports['hw_addr']
        print ports['port_no']
        print ports['dpid']

for link in links_JSON:
    src = link['src']
    dst = link['dst']

    print "SRC"
    print src['hw_addr']
    print src['port_no']
    print src['dpid']

    print "DST"
    print dst['hw_addr']
    print dst['port_no']
    print type(dst['dpid'])

db = MySQLdb.connect(host='localhost', user='root', passwd='897375', db='meshr')
cursor = db.cursor()

cursor.execute("SELECT * FROM meshsr_connection")

for row in cursor.fetchall():
    print row

cursor.execute("SELECT * FROM meshsr_node")
for row in cursor.fetchall():
    print row
