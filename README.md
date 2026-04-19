# Traffic Monitoring and Statistics Collector

Build a controller module that collects and displays traffic statistics using Mininet + Ryu.

## What is implemented

- A modular Ryu controller with entrypoint at `controller/traffic_monitor.py`
- Handles packet-in events (learning-switch behavior)
- Installs explicit OpenFlow match-action rules per learned flow
- Periodically requests flow statistics from the switch
- Prints packet and byte counters in controller logs
- Writes a simple markdown report to `reports/traffic_report_latest.md`

## Deliverables coverage

- Retrieve flow statistics: yes (periodic `OFPFlowStatsRequest`)
- Display packet/byte counts: yes (console output + report table)
- Periodic monitoring: yes (default every 10 seconds)
- Generate simple reports: yes (`reports/traffic_report_latest.md`)

## Files

- Entrypoint app: `controller/traffic_monitor.py`
- Learning logic module: `controller/flow_learning.py`
- Stats/report module: `controller/stats_reporter.py`
- Command runbook: `DOCKER_COMMANDS.md`
- Generated report: `reports/traffic_report_latest.md`

## Quick run summary

1. Start the controller:

```bash
/workspace/ryu-venv/bin/ryu-manager controller/traffic_monitor.py
```

2. Start Mininet with remote controller:

```bash
mn --topo single,3 --mac --switch ovs,protocols=OpenFlow13 --controller remote,ip=127.0.0.1,port=6653
```

3. Generate traffic:

```bash
pingall
iperf h1 h2
h1 ping -c 20 h3
```

4. Check results:

```bash
cat reports/traffic_report_latest.md
```

## Test scenarios to demonstrate

1. Normal connectivity test
- Run `pingall` and confirm all hosts are reachable.
- Check that flows appear in `ovs-ofctl dump-flows` and in the report.

2. Higher traffic load test
- Run `iperf h1 h2` and repeated `ping`.
- Confirm packet and byte counts increase across monitoring cycles.

## Notes

- Full Docker commands are listed in `DOCKER_COMMANDS.md`.
- You can change polling frequency with environment variable:

```bash
POLL_INTERVAL=5 /workspace/ryu-venv/bin/ryu-manager controller/traffic_monitor.py
```
---