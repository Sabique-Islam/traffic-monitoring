# Docker Commands for Traffic Monitoring Assignment (Working Guide)

> **Important:** Docker Desktop (Mac/Windows) does not include the OVS Linux kernel module (`modprobe: FATAL`).
> To completely fix this, we run Open vSwitch entirely in userspace using `datapath=user`.

## 1) Start the Container (Host Machine)

```bash
docker run -it --privileged --name cn-sdn \
  -v "/Users/sabiqueislam/Downloads/os-bs/code-stuff/ipad/sem4/cn:/workspace" \
  -w /workspace \
  ubuntu:22.04 \
  bash
```

If you need to open additional terminals inside the running container, use:
```bash
docker exec -it cn-sdn bash
```

## 2) Install OS Dependencies

```bash
apt update && apt upgrade -y

apt install -y \
  python3 python3-venv python3-pip \
  git mininet openvswitch-switch \
  iproute2 iputils-ping bridge-utils
```

## 3) Setup Python Environment & Ryu

Modern Python environments block global package installs. We use a virtual environment.

```bash
python3 -m venv /workspace/ryu-venv
source /workspace/ryu-venv/bin/activate

pip install --upgrade pip
pip install "setuptools<60" wheel

# Install Ryu manually
cd /workspace
git clone https://github.com/faucetsdn/ryu.git
cd ryu
python setup.py install

# Install Ryu dependencies
pip install netaddr eventlet==0.33.3 dnspython>=2.2.0 oslo.config routes webob msgpack ovs six tinyrpc==1.0.4 packaging==20.9
```

## 4) Start the Open vSwitch Service

Before running Mininet, you must start the OVS service in the background:

```bash
service openvswitch-switch start
ovs-vsctl show
```

---

## 5) Run the SDN Controller (Terminal 1)

Keep this terminal open so the controller stays active.

```bash
source /workspace/ryu-venv/bin/activate
cd /workspace/controller
ryu-manager traffic_monitor.py --ofp-tcp-listen-port 6653
```

---

## 6) Run Mininet with Userspace OVS (Terminal 2)

In a second terminal (attached via `docker exec`), start Mininet. 
**Critically**, we add `datapath=user` to bypass the missing kernel module, and point to the custom topology.

```bash
mn -c

mn --custom /workspace/controller/firewall_topo.py \
   --topo firewalltopo \
   --switch ovs,protocols=OpenFlow13,datapath=user \
   --controller remote,ip=127.0.0.1,port=6653 \
   --mac
```

---

## 7) Generate Traffic & View Report (Inside Mininet CLI)

Wait for Mininet to start processing (you should see nodes `c0 h1 h2 h3 h4 s1`). Then generate traffic:

```text
mininet> pingall
mininet> h1 iperf -c h2
```

Because your Ryu controller is running and pushing flow statistics every 10 seconds, you can immediately view the generated markdown report directly from the Mininet shell:

```text
mininet> sh cat /workspace/controller/reports/traffic_report_latest.md
```

## 8) Cleanup

When you are done:
```bash
mininet> exit
mn -c
pkill -f ryu-manager
```
