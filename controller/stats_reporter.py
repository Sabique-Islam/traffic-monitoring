"""Flow statistics aggregation and report generation."""

import os
from datetime import datetime


class StatsReporter:
    def __init__(self, logger, report_path):
        self.logger = logger
        self.report_path = report_path
        self.flow_baseline = {}

    def _flow_key(self, dpid, stat):
        in_port = stat.match.get("in_port", "-")
        eth_src = stat.match.get("eth_src", "-")
        eth_dst = stat.match.get("eth_dst", "-")

        out_port = "-"
        if stat.instructions and hasattr(stat.instructions[0], "actions") and stat.instructions[0].actions:
            out_port = stat.instructions[0].actions[0].port

        return (dpid, in_port, eth_src, eth_dst, out_port)

    def handle_flow_stats_reply(self, dpid, body):
        learned_flows = [
            stat
            for stat in body
            if stat.priority == 1 and stat.match.get("eth_src") and stat.match.get("eth_dst")
        ]

        flow_rows = []
        total_packets = 0
        total_bytes = 0

        self.logger.info("dpid in_port src_mac dst_mac out_port packets bytes delta_packets delta_bytes")

        for stat in sorted(
            learned_flows,
            key=lambda s: (
                s.match.get("in_port", 0),
                s.match.get("eth_src", ""),
                s.match.get("eth_dst", ""),
            ),
        ):
            key = self._flow_key(dpid, stat)
            prev_packets, prev_bytes = self.flow_baseline.get(key, (0, 0))

            delta_packets = stat.packet_count - prev_packets
            delta_bytes = stat.byte_count - prev_bytes
            self.flow_baseline[key] = (stat.packet_count, stat.byte_count)

            in_port = stat.match.get("in_port", "-")
            src = stat.match.get("eth_src", "-")
            dst = stat.match.get("eth_dst", "-")
            out_port = key[4]

            total_packets += stat.packet_count
            total_bytes += stat.byte_count

            self.logger.info(
                "%016x %s %s %s %s %d %d %d %d",
                dpid,
                in_port,
                src,
                dst,
                out_port,
                stat.packet_count,
                stat.byte_count,
                delta_packets,
                delta_bytes,
            )

            flow_rows.append(
                {
                    "in_port": in_port,
                    "src": src,
                    "dst": dst,
                    "out_port": out_port,
                    "packets": stat.packet_count,
                    "bytes": stat.byte_count,
                    "delta_packets": delta_packets,
                    "delta_bytes": delta_bytes,
                }
            )

        self._write_report(dpid, flow_rows, total_packets, total_bytes)

    def _write_report(self, dpid, flow_rows, total_packets, total_bytes):
        os.makedirs(os.path.dirname(self.report_path) or ".", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        top_flow = max(flow_rows, key=lambda x: x["bytes"], default=None)

        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write("# Traffic Monitoring Report\n\n")
            f.write(f"Generated at: {timestamp}\n\n")
            f.write(f"Switch DPID: {dpid:016x}\n\n")
            f.write(f"Total learned flows: {len(flow_rows)}\n\n")
            f.write(f"Total packets: {total_packets}\n\n")
            f.write(f"Total bytes: {total_bytes}\n\n")

            if top_flow:
                f.write("## Top Flow by Bytes\n\n")
                f.write(
                    "- "
                    f"{top_flow['src']} -> {top_flow['dst']} "
                    f"({top_flow['bytes']} bytes, {top_flow['packets']} packets)\n\n"
                )

            f.write("## Flow Table Snapshot\n\n")
            f.write("| In Port | Source MAC | Destination MAC | Out Port | Packets | Bytes | dPackets | dBytes |\n")
            f.write("|---|---|---|---:|---:|---:|---:|---:|\n")

            for row in flow_rows:
                f.write(
                    f"| {row['in_port']} | {row['src']} | {row['dst']} | {row['out_port']} | "
                    f"{row['packets']} | {row['bytes']} | {row['delta_packets']} | {row['delta_bytes']} |\n"
                )
