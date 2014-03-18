import json
from time import sleep
import urllib2
import MySQLdb

__author__ = 'samuel'

REST_SERVER_ADDR = 'http://localhost:8080'

DBADRESS = 'localhost'
DBUSER = 'root'
DBPASSWD = '897375'
DBNAME = 'meshr'

TOPO_PUSH_PERIOD = 5  # count as sec

conn = MySQLdb.connect(host=DBADRESS, user=DBUSER, passwd=DBPASSWD, db=DBNAME)
cursor = conn.cursor()

while True:
# Get JSONs from RYU controller.
    response_switches = urllib2.urlopen(REST_SERVER_ADDR + '/v1.0/topology/switches').read()
    switches_JSON = json.loads(response_switches)

    response_links = urllib2.urlopen(REST_SERVER_ADDR + '/v1.0/topology/links').read()
    links_JSON = json.loads(response_links)

    # Delete All the items in the table to avoid the same switch and edge be inserted.
    cursor.execute("DELETE FROM meshsr_node")
    cursor.execute("DELETE FROM meshsr_connection")

    # Add all the switches and the link to the database.
    for switch in switches_JSON:
        sql_sentence = "INSERT INTO meshsr_node VALUES (NULL, '%s', '0', '0', '1', 'None');" % (switch['dpid'])
        cursor.execute(sql_sentence)


    for link in links_JSON:
        src = link['src']
        dst = link['dst']
        sql_sentence = "INSERT INTO meshsr_connection VALUES (NULL, '%s', '%s', '0', '0');" % (src['dpid'], dst['dpid'])
        print sql_sentence
        cursor.execute(sql_sentence)

    conn.commit()
    #Sleep for a while to avoid high load to SQLServer.
    sleep(TOPO_PUSH_PERIOD)
