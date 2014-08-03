import json
from time import sleep
import traceback
import urllib2
import MySQLdb
import copy

__author__ = 'samuel'

REST_SERVER_ADDR = 'http://localhost:8080'

DBADRESS = 'localhost'
DBUSER = 'root'
DBPASSWD = '897375'
DBNAME = 'meshsr'

conn = MySQLdb.connect(host=DBADRESS, user=DBUSER, passwd=DBPASSWD, db=DBNAME)
conn.autocommit(True)
cursor = conn.cursor()


def debug(mess):
    pass


def newIndexID():
    newIndexID.serNICID += 1
    return "F00000000000000" + str(newIndexID.serNICID)
newIndexID.serNICID = 0


def main():
    response_hosts = urllib2.urlopen(REST_SERVER_ADDR + '/hosts').read()
    debug(response_hosts)
    hosts_json = json.loads(response_hosts)

    for host in hosts_json:
        port_no = host["port_no"]
        dpid = host["dpid"]
        peer_mac = host["peer_mac"]

        sql = "SELECT portID FROM ports WHERE dpid=%s and number=%s" % (dpid, port_no)
        debug(sql)
        cnt = cursor.execute(sql)
        assert cnt == 1
        portID = cursor.fetchone()[0]

        sql = "INSERT INTO serverNIC VALUE('%s', %s, '%s')" % (newIndexID(), portID, peer_mac)
        debug(sql)
        cursor.execute(sql)

        print "server: [" + str(peer_mac) + "] has connect to port: [" + str(portID) + "]"



if __name__ == "__main__":
    print "**********************************"
    cursor.execute("delete from serverNIC")
    main()
    print "all server information has been into database."
    print "************Exiting**************"