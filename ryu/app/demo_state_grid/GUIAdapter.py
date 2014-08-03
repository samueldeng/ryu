import json
from time import sleep
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

GUI_ADAPTER_REFRESH_PERIOD = 10


def activate_link(cmplt_flow, ac_link):
    ac_bid = ac_link["node"]
    ac_eid = ac_link["peer"]

    for flow in cmplt_flow:
        _bid = flow["bid"]
        _eid = flow["eid"]
        if (_bid == ac_bid and _eid == ac_eid) or (_bid == ac_eid and _eid == ac_bid):
            flow["type"] = "con"
            return cmplt_flow


# make the type from dis to conn in complete_flow
def find_peerNICID_from_portID(portID):
    _sql = "SELECT serNICID FROM serverNIC WHERE peer = %s" % str(portID)
    _cnt = cursor.execute(_sql)
    assert _cnt == 1
    _peerNICID = cursor.fetchone()
    return _peerNICID[0]


# find the owner of the port
def find_dpid_from_port(portID):
    _sql = "SELECT dpid FROM ports WHERE portID=%s" % str(portID)
    _cnt = cursor.execute(_sql)
    assert _cnt == 1
    dpid = cursor.fetchone()
    return dpid[0]


def push_all_nodes():
    """
    make a query from serverNIC and switches table and convert them into meshsr_ndoe table.

    """
    cursor.execute("SELECT * FROM serverNIC")
    NICs = cursor.fetchall()

    cursor.execute("SELECT * FROM switches")
    dps = cursor.fetchall()

    for dp in dps:
        assert len(dp) == 3
        # dp[0]:dpid(char16)
        # dp[1]:x(int11)
        # dp[2]:y(int11)
        sql = "INSERT INTO meshsr_node VALUE(NULL, '%s', '%s', '%s', 0, 'dpid:%s')" \
              % (dp[0], dp[1], dp[2], dp[0])
        cursor.execute(sql)

    for nic in NICs:
        assert len(nic) == 3
        # nic[0]:serNICID(char16)
        # nic[1]:peer(int11)
        # nic[2]:MAC(varchar20)
        sql = "INSERT INTO meshsr_node VALUE(NULL, '%s', '%s', '%s', 1, 'server_nic_MAC:%s')" \
              % (nic[0], 0, 0, nic[2])
        cursor.execute(sql)


def push_phy_link():
    """
    make a query to fetch the phyLink table and serverNIC table, and concatenation them into a entry where the
    flow_info is default.

    """
    default_flow = list()

    cursor.execute("SELECT * FROM phyLink")
    links_dps = cursor.fetchall()
    for link_dp in links_dps:
        #ensure every entry has 3 fields.
        assert len(link_dp) == 3
        # link_dp[0]:phyLinkID(int11)
        # link_dp[1]:srcPort(int11)
        # link_dp[1]:dstPort(int11)
        link_id = link_dp[0]
        src_port = link_dp[1]
        dst_port = link_dp[2]

        sql = "SELECT dpid FROM ports WHERE portID=%s" % src_port
        cnt = cursor.execute(sql)
        assert cnt == 1
        src_dpid = cursor.fetchone()[0]

        sql = "SELECT dpid FROM ports WHERE portID=%s" % dst_port
        cnt = cursor.execute(sql)
        assert cnt == 1
        dst_dpid = cursor.fetchone()[0]

        default_flow.append(
            dict(bid=src_dpid, eid=dst_dpid, type="dis")
        )

    cursor.execute("SELECT * FROM serverNIC")
    links_network_card_interface = cursor.fetchall()
    for link_NIC in links_network_card_interface:
        assert len(link_NIC) == 3
        # link_NIC[0]:serNICID(char16)
        # link_NIC[1]:peer(int11)
        # link_NIC[2]:MAC(varchar20)
        serNICID = link_NIC[0]
        peer_port = link_NIC[1]
        sql = "SELECT dpid FROM ports WHERE portID=%s" % peer_port
        cnt = cursor.execute(sql)
        assert cnt == 1
        peer_dpid = cursor.fetchone()[0]

        default_flow.append(
            dict(bid=serNICID, eid=peer_dpid, type="dis")
        )

    # FIXME the links between dps are bidirection but the dp2server.
    sql = "INSERT INTO meshsr_connection VALUE (NULL, 'default', '%s','physical links','')" \
          % (json.dumps(default_flow))
    cursor.execute(sql)
    print default_flow


def get_link_nums():
    return cursor.execute("SELECT * FROM phyLink")


def main():
    push_all_nodes()
    cursor.execute("DELETE FROM meshsr_connection WHERE flow_info = 'default';")
    push_phy_link()

    link_nums = 0
    while True:
        cursor.execute("DELETE FROM meshsr_node")
        push_all_nodes()
        print "push all nodes successfully"

        # link_now = get_link_nums()
        # if link_now != link_nums:
        #     print 'link change'
        #     link_nums = link_now
        cursor.execute("DELETE FROM meshsr_connection WHERE flow_info = 'default';")
        push_phy_link()
        print "push phy link successfully"

        sleep(GUI_ADAPTER_REFRESH_PERIOD)


if __name__ == "__main__":
    cursor.execute("DELETE FROM meshsr_node")
    cursor.execute("DELETE FROM meshsr_connection")
    main()