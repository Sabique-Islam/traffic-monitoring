# Docker Commands for Traffic Monitoring Assignment (Complete Guide)

> Note: Docker Desktop does NOT support OVS kernel properly.
> We include both:
> - OVS attempt (may fail but required for OpenFlow flow tables)
> - Working fallback (lxbr)

## 1) Start container (host)

```bash
docker run -it --privileged --name cn-sdn \
  -v "/Users/sabiqueislam/Downloads/os-bs/code-stuff/ipad/sem4/cn:/workspace" \
  -w /workspace \
  ubuntu:22.04 \
  bash
```

```
docker exec -it cn-sdn bash
```

## 2) Install dependencies

```bash
apt update
apt upgrade -y

apt install -y \
  python3 python3-venv python3-pip \
  git mininet openvswitch-switch \
  iproute2 iputils-ping bridge-utils
```

## 3) Setup Python + Ryu (WORKING METHOD)

```bash
python3 -m venv /workspace/ryu-venv
source /workspace/ryu-venv/bin/activate

pip install --upgrade pip
pip install "setuptools<60" wheel
```

### Install Ryu (manual fix)

```bash
cd /workspace
git clone https://github.com/faucetsdn/ryu.git
cd ryu
python setup.py install
```

### Install required dependencies

```bash
pip install \
  netaddr \
  eventlet==0.33.3 \
  dnspython>=2.2.0 \
  oslo.config \
  routes \
  webob \
  msgpack \
  ovs \
  six \
  tinyrpc==1.0.4 \
  packaging==20.9
```

## 4) Verify Ryu

```bash
ryu-manager --version
```

Expected:

```text
ryu-manager 4.34
```

## 5) Try Open vSwitch (may fail in Docker)

```bash
service openvswitch-switch start
ovs-vsctl show
```

## 6) Run controller (Terminal A)

```bash
mkdir -p /workspace/controller/reports

source /workspace/ryu-venv/bin/activate
cd /workspace/controller
ryu-manager traffic_monitor.py --ofp-tcp-listen-port 6653
```

Optional polling:

```bash
POLL_INTERVAL=5 ryu-manager traffic_monitor.py --ofp-tcp-listen-port 6653
```

## 7) Run Mininet (Terminal B)

Run Mininet using the custom firewall topology, pointing at the controller, maintaining Open vSwitch via the userspace datapath (`datapath=user`):

```bash
mn -c
mn --custom /workspace/controller/firewall_topo.py --topo firewalltopo \
   --switch ovs,protocols=OpenFlow13,datapath=user \
   --controller remote,ip=127.0.0.1,port=6653 \
   --mac
```

## 8) Generate traffic (Mininet CLI)

Wait briefly, then run:

```bash
nodes
net

pingall

h1 ping -c 10 h2
iperf h1 h2

h1 ping -c 20 h3
```

## 9) View report

In the Mininet CLI (wait ~10 seconds for the next polling cycle to hit):

```bash
sh cat /workspace/controller/reports/traffic_report_latest.md
```

## 10) Cleanup

```bash
exit
mn -c
pkill -f ryu-manager
```
