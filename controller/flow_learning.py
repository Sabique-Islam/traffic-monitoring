"""Learning-switch flow handling for the traffic monitor app.

This module is responsible for:
- installing base forwarding rules,
- learning host MAC-to-port mappings,
- and forwarding packets while pushing learned flows to the switch.
"""

from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import packet


class LearningSwitch:
    """Encapsulates OpenFlow learning-switch behavior."""

    def __init__(self):
        # Per-switch MAC learning table: {dpid: {mac: in_port}}
        self.mac_to_port = {}

    def add_table_miss(self, datapath):
        """Install the table-miss rule so unknown traffic reaches the controller."""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, priority=0, match=match, actions=actions)

    def add_flow(self, datapath, priority, match, actions, idle_timeout=60, hard_timeout=0):
        """Send a flow-mod to the switch with the provided match/action rule."""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        instructions = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=instructions,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout,
        )
        datapath.send_msg(mod)

    def handle_packet_in(self, msg):
        """Process packet-in, learn source, and forward/flow-install accordingly."""
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        in_port = msg.match["in_port"]
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        # Ignore LLDP and malformed frames to avoid polluting learning state.
        if eth is None or eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src

        # Learn where the source host is reachable from.
        self.mac_to_port[dpid][src] = in_port

        # If destination is known, unicast; otherwise flood for discovery.
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Install a learned rule only for resolved unicast forwarding.
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_src=src, eth_dst=dst)
            self.add_flow(datapath, priority=1, match=match, actions=actions)

        # Some packet-in messages have no switch buffer; send full payload then.
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )
        datapath.send_msg(out)
