import json
import urllib2
import MySQLdb

__author__ = 'samuel'

REST_server = 'http://localhost:8080'
DBhost = 'localhost'
DBuser = 'root'
DBpaasswd = '897375'
DBname = 'meshr'

db = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpaasswd, db=DBname)
cursor = db.cursor()

response_switches = urllib2.urlopen(REST_server + '/v1.0/topology/switches').read()
switches_JSON = json.loads(response_switches)

response_links = urllib2.urlopen(REST_server + '/v1.0/topology/links').read()
links_JSON = json.loads(response_links)

for switch in switches_JSON:
    # FIXME every insert query will be executed into the table, so there must be more than one instance for one switch.
    sql_sentence = "INSERT INTO meshsr_node ('id', 'node_id', 'x', 'y', 'type', 'des')\
                    VALUES (NULL, %s, '0', '0', '1', 'None);" % (switch['dpid'])
    cursor.execute(sql_sentence)
    # print switch['dpid']
    # for ports in switch['ports']:
    #     print ports['name']
    #     print ports['hw_addr']
    #     print ports['port_no']
    #     print ports['dpid']

for link in links_JSON:
    src = link['src']
    dst = link['dst']
    sql_sentence = "INSERT INTO meshsr_connection ('id', `begin_node_id`, `end_node_id`, `type`, `des`) \
                    VALUES (NULL, %s, %s, '0', '0');" % (src['dpid'], dst['dpid'])
    cursor.execute(sql_sentence)
    # print "SRC"
    # print src['hw_addr']
    # print src['port_no']
    # print src['dpid']

    # print "DST"
    # print dst['hw_addr']
    # print dst['port_no']
    # print dst['dpid']
