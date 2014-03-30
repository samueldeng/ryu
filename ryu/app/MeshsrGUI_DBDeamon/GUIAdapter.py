import json
from time import sleep
import MySQLdb

__author__ = 'samuel'

REST_SERVER_ADDR = 'http://localhost:8080'

DBADRESS = 'localhost'
DBUSER = 'root'
DBPASSWD = '897375'
DBNAME = 'meshsr'

conn = MySQLdb.connect(host=DBADRESS, user=DBUSER, passwd=DBPASSWD, db=DBNAME)
cursor = conn.cursor()

GUI_ADAPTER_REFRESH_PERIOD = 5

while True:

    # adapter for the meshsr_node
    cursor.execute("DELETE FROM meshsr_node")
    NIC_nums = cursor.execute("SELECT * FROM serverNIC")
    NICs = cursor.fetchall()

    dp_nums = cursor.execute("SELECT * FROM switches")
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
    conn.commit()

    # adapter for the default flow in meshsr_connection.
    default_flow = list()
    cursor.execute("DELETE FROM meshsr_connection WHERE flow_info = 'default';")

    count = cursor.execute("SELECT * FROM phyLink")
    links_dps = cursor.fetchall()
    for link_dp in links_dps:
        #ensure every entry has 3 fields.
        assert len(link_dp) == 3
        # link_dp[0]:phyLinkID(int11)
        # link_dp[1]:srcPort(int11)
        # link_dp[1]:dstPort(int11)
        linkID = link_dp[0]
        srcPort = link_dp[1]
        dstPort = link_dp[2]

        sql = "SELECT dpid FROM ports WHERE portID=%s" % srcPort
        cnt = cursor.execute(sql)
        assert cnt == 1
        src_dpid = cursor.fetchone()[0]

        sql = "SELECT dpid FROM ports WHERE portID=%s" % dstPort
        cnt = cursor.execute(sql)
        assert cnt == 1
        dst_dpid = cursor.fetchone()[0]

        default_flow.append(
            dict(bid=src_dpid, eid=dst_dpid, type="dis")
        )

    count = cursor.execute("SELECT * FROM serverNIC")
    links_NIC = cursor.fetchall()
    for link_NIC in links_NIC:
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
    conn.commit()


    # adapter for every single flow in meshsr_connection
    cursor.execute("DELETE FROM meshsr_connection WHERE flow_info != 'default';")
    flowIDs = list()

    flowIDs_num = cursor.execute("SELECT DISTINCT flowID FROM flowEntry")
    # TODO assuming that there must be entries.
    resu_flowIDs = cursor.fetchall()
    for f in resu_flowIDs:
        flowIDs.append(f[0])

    for flow in flowIDs:
        sql = "SELECT flowSeqNum, dpid, inPort, outPort, meterValue FROM flowEntry ORDER BY flowSeqNum"
        cnt = cursor.execute(sql)
        assert cnt != 0
        entries = cursor.fetchall()

        complete_flow = default_flow

        # complete_flow = list({
        #     "bid": None
        #     "eid": None
        #     "type": None
        # })
        prev_dpid = None
        for entry in entries:
            seq = entry[0]
            curr_dpid = entry[1]
            in_port = entry[2]
            out_port = entry[3]
            meter = entry[4]

            # make the type from dis to conn in complete_flow
            def find_peerNICID_from_port(port):
                return None
            # find the ownner of the port
            def find_dpid_from_port(port):
                return None

            def activate_link(cmplt_flow, ac_link):
                assertISInstance(cmplt_flow,list)
                assertISInstance(ac_link,dict)

            if seq == 0:
                cnt = cursor.execute("SELECT serNICID FROM serverNIC WHERE peer=%s") % in_port
                assert cnt == 1
                serNICID = cursor.fetchone()[0]
                serNICID = find_peerNICID_from_port(in_port)
                active_link = dict(node = serNICID, peer = curr_dpid)
                # TODO stub of unimplemented func
                activate_link(complete_flow, active_link)
                prev_dpid = find_dpid_from_port(out_port)

            elif seq != len(entries)-1:

                active_link = dict(node = prev_dpid, peer = curr_dpid)
                activate_link(complete_flow, activate_link)
                prev_dpid = find_dpid_from_port(out_port)
                
            else:
                active_link = dict(node = prev_dpid, peer = curr_dpid)
                activate_link(complete_flow, activate_link)
                # add the final server linking it.
                serNICID = find_peerNICID_from_port(out_port)
                active_link = dict(node = curr_dpid, peer = serNICID)

    sleep(GUI_ADAPTER_REFRESH_PERIOD)