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

dp_cord_x = dict(str, int)
dp_cord_y = dict(str, int)

dp_cord_x['000000000001'] = 0
dp_cord_y['000000000001'] = 0

dp_cord_x['000000000002'] = 0
dp_cord_y['000000000002'] = 0

dp_cord_x['000000000003'] = 0
dp_cord_y['000000000003'] = 0

dp_cord_x['000000000004'] = 0
dp_cord_y['000000000004'] = 0

dp_cord_x['000000000005'] = 0
dp_cord_y['000000000005'] = 0

dp_cord_x['000000000006'] = 0
dp_cord_y['000000000006'] = 0

dp_cord_x['000000000007'] = 0
dp_cord_y['000000000007'] = 0

dp_cord_x['000000000008'] = 0
dp_cord_y['000000000008'] = 0

dp_cord_x['000000000009'] = 0
dp_cord_y['000000000009'] = 0


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
        switch_dpid = switch['dpid']
        description = str()
        for ports in switch['ports']:
            description += ports['name'] + '\n'
            description += ports['hw_addr'] + '\n'
            description += ports['port_no'] + '\n'
            description += ports['dpid'] + '\n'

        x = str(dp_cord_x[switch_dpid])
        y = str(dp_cord_y[switch_dpid])
        sql_sentence = "INSERT INTO meshsr_node VALUES (NULL, '%s', '%s', '%s', '%s', '%s');" \
                       % (switch_dpid, 0, x, y, str(description))
        cursor.execute(sql_sentence)

    for link in links_JSON:
        src = link['src']
        dst = link['dst']

        src_port = src['port_no']
        dst_port = dst['port_no']
        description = src_port + '-->' + dst_port

        sql_sentence = "INSERT INTO meshsr_connection VALUES (NULL, '%s', '%s', '%s', '%s');" \
                       % (src['dpid'], dst['dpid'], 0, description)
        cursor.execute(sql_sentence)

    conn.commit()
    #Sleep for a while to avoid high load to SQLServer.
    sleep(TOPO_PUSH_PERIOD)
