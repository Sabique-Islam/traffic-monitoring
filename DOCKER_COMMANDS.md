# Docker Commands for Traffic Monitoring Assignment (Fixed)

> Note: Docker Desktop does NOT support OVS kernel properly.
> We include both:
> - OVS attempt (may fail)
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

```
mn --switch=lxbr --controller=remote
```

## 6) Run controller (Terminal A)

```bash
mkdir -p reports

source /workspace/ryu-venv/bin/activate
ryu-manager controller/traffic_monitor.py
```

Optional polling:

```bash
POLL_INTERVAL=5 ryu-manager controller/traffic_monitor.py
```

## 7) Run Mininet (Terminal B)

Try OVS (required for full SDN):

```bash
mn --topo single,3 --mac \
   --switch ovs,protocols=OpenFlow13 \
   --controller remote,ip=127.0.0.1,port=6653
```

If OVS fails, use fallback (works reliably):

```bash
mn --topo single,3 --mac \
   --switch lxbr \
   --controller remote,ip=127.0.0.1,port=6653
```

## 8) Generate traffic (Mininet CLI)

```bash
nodes
net

pingall

h1 ping -c 10 h2
iperf h1 h2

h1 ping -c 20 h3
```

## 9) Validate flows (ONLY works if OVS works)

```bash
sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

If using lxbr, this will not work (expected).

## 10) View report

```bash
exit
cd /workspace
cat reports/traffic_report_latest.md
```

## 11) Cleanup

```bash
mn -c
pkill -f ryu-manager
```

## Important Notes

### What works in Docker

| Feature | Status |
| --- | --- |
| Mininet topology | ✅ |
| Ryu controller | ✅ |
| Traffic generation | ✅ |
| Logging/monitoring | ✅ |

### What is limited

| Feature | Status |
| --- | --- |
| OVS kernel datapath | ❌ |
| True OpenFlow switching | ❌ |
| Flow table inspection | ⚠️ partial |

## Recommendation

For full SDN behavior (best marks):
- Use Ubuntu VM instead of Docker.

For demo + submission:
- Docker setup is sufficient if limitations are explained clearly.
