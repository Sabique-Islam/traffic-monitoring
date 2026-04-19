#!/usr/bin/env python3
"""Ryu app entrypoint for modular traffic monitoring controller.

The app wires together three concerns:
- datapath lifecycle tracking,
- packet forwarding logic (learning switch),
- periodic statistics polling and reporting.
"""

import os

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, DEAD_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_3

from flow_learning import LearningSwitch
from stats_reporter import StatsReporter


class TrafficMonitor(app_manager.RyuApp):
    """Main Ryu application class coordinating learning and monitoring modules."""

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficMonitor, self).__init__(*args, **kwargs)
        # Active datapaths keyed by DPID.
        self.datapaths = {}
        self.poll_interval = int(os.getenv("POLL_INTERVAL", "10"))
        self.report_path = os.getenv("REPORT_PATH", "reports/traffic_report_latest.md")

        # Delegate packet logic and report logic to dedicated modules.
        self.learning_switch = LearningSwitch()
        self.stats_reporter = StatsReporter(self.logger, self.report_path)

        # Background green thread that polls stats periodically.
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        """Track switch connect/disconnect events for polling."""
        datapath = ev.datapath
        dpid = datapath.id

        if ev.state == MAIN_DISPATCHER:
            if dpid not in self.datapaths:
                self.datapaths[dpid] = datapath
                self.logger.info("Switch registered: dpid=%016x", dpid)
        elif ev.state == DEAD_DISPATCHER:
            if dpid in self.datapaths:
                del self.datapaths[dpid]
                self.logger.info("Switch disconnected: dpid=%016x", dpid)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Install initial table-miss behavior when switch features arrive."""
        datapath = ev.msg.datapath
        self.learning_switch.add_table_miss(datapath)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        """Forward packet-in events to the learning switch module."""
        self.learning_switch.handle_packet_in(ev.msg)

    def _monitor(self):
        """Periodic polling loop for all connected switches."""
        while True:
            for datapath in list(self.datapaths.values()):
                self._request_stats(datapath)
            hub.sleep(self.poll_interval)

    def _request_stats(self, datapath):
        """Request flow statistics from a given datapath."""
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        """Forward flow stats replies to the reporting module."""
        dpid = ev.msg.datapath.id
        self.stats_reporter.handle_flow_stats_reply(dpid, ev.msg.body)
