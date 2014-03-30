import json
from time import sleep
import urllib2
import MySQLdb

__author__ = 'samuel'

REST_SERVER_ADDR = 'http://localhost:8080'

DBADRESS = 'localhost'
DBUSER = 'root'
DBPASSWD = '897375'
DBNAME = 'meshsr'

TOPO_PUSH_PERIOD = 10  # count as sec

conn = MySQLdb.connect(host=DBADRESS, user=DBUSER, passwd=DBPASSWD, db=DBNAME)
cursor = conn.cursor()

dp_cord_x = dict()
dp_cord_y = dict()
dp_cord_x['0000000000000010'] = 0
dp_cord_y['0000000000000010'] = 0

dp_cord_x['0000000000000011'] = 0
dp_cord_y['0000000000000011'] = 0

dp_cord_x['0000000000000012'] = 0
dp_cord_y['0000000000000012'] = 0

dp_cord_x['0000000000000013'] = 0
dp_cord_y['0000000000000013'] = 0

dp_cord_x['0000000000000014'] = 0
dp_cord_y['0000000000000014'] = 0

dp_cord_x['0000000000000015'] = 0
dp_cord_y['0000000000000015'] = 0

dp_cord_x['0000000000000016'] = 0
dp_cord_y['0000000000000016'] = 0

dp_cord_x['0000000000000017'] = 0
dp_cord_y['0000000000000017'] = 0

dp_cord_x['0000000000000018'] = 0
dp_cord_y['0000000000000018'] = 0

dp_cord_x['0000000000000019'] = 0
dp_cord_y['0000000000000019'] = 0


while True:
    # Get JSONs from RYU controller.
    response_switches = urllib2.urlopen(REST_SERVER_ADDR + '/v1.0/topology/switches').read()
    switches_JSON = json.loads(response_switches)

    response_links = urllib2.urlopen(REST_SERVER_ADDR + '/v1.0/topology/links').read()
    links_JSON = json.loads(response_links)

    # Delete All the items in the table to avoid the same switch and edge be inserted.
    cursor.execute("DELETE FROM phyLink")
    cursor.execute("DELETE FROM ports")
    cursor.execute("DELETE FROM switches")

    # Add all the switches and the link to the database.
    for switch in switches_JSON:
        switch_dpid = switch['dpid'].encode()
        sql = "INSERT INTO switches VALUE ('%s', '%s', '%s');" \
              % (switch_dpid, dp_cord_x[switch_dpid], dp_cord_y[switch_dpid])
        cursor.execute(sql)

        for port in switch['ports']:
            port_dpid = port['dpid'].encode()
            port_name = port['name'].encode()
            port_hw_addr = port['hw_addr'].encode()
            port_port_no = port['port_no'].encode()
            sql = "INSERT INTO ports VALUE (NULL, '%s', '%s', '%s', '%s');" \
                  % (switch_dpid, port_name, port_hw_addr, port_port_no)
            cursor.execute(sql)
    conn.commit()

    for link in links_JSON:
        src = link['src']
        src_dpid = src['dpid'].encode()
        src_port_no = src['port_no'].encode()
        src_hw_addr = src['hw_addr'].encode()
        sql = "SELECT portID FROM ports WHERE dpid='%s' AND number='%s';" \
              % (src_dpid, src_port_no)
        count = cursor.execute(sql)
        assert count == 1
        result = cursor.fetchone()
        src_port_id = result[0]

        dst = link['dst']
        dst_dpid = dst['dpid'].encode()
        dst_port_no = dst['port_no'].encode()
        dst_hw_addr = dst['hw_addr'].encode()
        sql = "SELECT portID FROM ports WHERE dpid='%s' AND number='%s';" \
              % (dst_dpid, dst_port_no)
        count = cursor.execute(sql)
        assert count == 1
        result = cursor.fetchone()
        dst_port_id = result[0]

        sql = "INSERT INTO phyLink VALUE (NULL, %s, %s);" \
              % (src_port_id, dst_port_id)
        cursor.execute(sql)
    conn.commit()

    #Sleep for a while to avoid high load to SQLServer.
    sleep(TOPO_PUSH_PERIOD)
