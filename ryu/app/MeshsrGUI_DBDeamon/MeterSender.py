import json
from time import sleep
import urllib2
import MySQLdb
import copy

__author__ = 'samuel'

REST_SERVER_ADDR = 'http://localhost:8080'

DBADRESS = 'localhost'
DBUSER = 'root'
DBPASSWD = 'mysql'
DBNAME = 'meshsr'

conn = MySQLdb.connect(host=DBADRESS, user=DBUSER, passwd=DBPASSWD, db=DBNAME)
conn.autocommit(True)
cursor = conn.cursor()


def find_diff_entry(_curr_ctrl_entry, _prev_ctrl_table):
    assert _prev_ctrl_table is not None
    for _prev_ctrl_entry in _prev_ctrl_table:
        if _curr_ctrl_entry[0] == _prev_ctrl_entry[0] and str(_curr_ctrl_entry[1]) != str(_prev_ctrl_entry[1]):
            return _prev_ctrl_entry
    return None


def find_modified_dpid(_curr_ctrl_entry, _prev_diff_entry):
    curr = json.loads(_curr_ctrl_entry[1])
    prev = json.loads(_prev_diff_entry[1])

    for i_curr in curr:
        for i_prev in prev:
            if str(i_curr["nid"]) == str(i_prev["nid"]) and str(i_curr["meter"]) != str(i_prev["meter"]):
#		print "previous meter value is ", i_prev["meter"], "type is", type(i_prev["meter"])
#		print "current meter value is ", i_curr["meter"], "type is", type(i_curr["meter"])
                return str(i_curr["nid"]), str(i_curr['meter'])


def debug(mess):
    print mess


prev_ctrl_table = None
while True:
    cnt = cursor.execute("SELECT id,control_node FROM meshsr_connection WHERE flow_info != 'default'")
    if cnt == 0:
        print "there are no flow entries in the whole network, sleep for a while."
        sleep(1)
        continue
    curr_ctrl_table = cursor.fetchall()
    # debug(curr_ctrl_table)
    # debug(prev_ctrl_table)
    if prev_ctrl_table is not None:
        for curr_ctrl_entry in curr_ctrl_table:
            prev_diff_entry = None
            prev_diff_entry = find_diff_entry(curr_ctrl_entry, prev_ctrl_table)
            if prev_diff_entry is None:
                continue
            dpid, value = find_modified_dpid(curr_ctrl_entry, prev_diff_entry)
            dpid = int(dpid, 16)
            if value is None:
                continue
            post_data = {
                "dpid": dpid,
                "meter_id": 1,
                "flags": "KBPS",
                "bands": [
                    {
                        "type": "DROP",
                        "rate": value
                    }
                ]

            }

            debug(post_data)
            # TODO require onBoard Test.
            req = urllib2.Request('http://localhost:8080/stats/meterentry/modify')
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req, json.dumps(post_data))

    #prev_ctrl_table = list(curr_ctrl_table)
    prev_ctrl_table = copy.deepcopy(curr_ctrl_table)
    sleep(1)
