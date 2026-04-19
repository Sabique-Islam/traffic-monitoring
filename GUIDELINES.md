# SDN Assignment (Mininet + OpenFlow Controller)

## Goal

The goal of this assignment is to implement an SDN-based solution using **Mininet** and an **OpenFlow controller (Ryu/POX)** that demonstrates:

- Controller–switch interaction  
- Flow rule design (match–action)  
- Network behavior observation  

---

## Requirements

- Use **Mininet** for topology  
- Use **Ryu or POX controller**  
- Implement **explicit OpenFlow flow rules**  
- Controller logic must:
  - Handle `packet_in` events  
  - Implement match + action logic  
- Demonstrate functional behavior using tools like:
  - Wireshark  
  - iperf  

---

## Testing & Validation

You must:

- Demonstrate working behavior clearly  
- Show at least **2 test scenarios**, such as:
  - Allowed vs Blocked traffic  
  - Normal vs Failure case  
- Include basic validation (or regression testing if applicable)

---

## Final Deliverables

### 1. Working Demonstration
- Live demo in Mininet  
- Functional correctness  

### 2. Source Code (GitHub Repository)
- Public repository  
- Clean and modular code  
- Proper comments  

### 3. README Documentation
Include:
- Problem statement  
- Setup / execution steps  
- Expected output  

### 4. Proof of Execution
(Include in README)

- Screenshots / logs using tools like Wireshark  
- Evidence of:
  - Flow tables  
  - Ping results  
  - iperf results  

---

## References

- All references must be clearly mentioned and cited.

---

## Evaluation Criteria

| Component | Evaluation Criteria | Marks |
|----------|-------------------|------|
| **1. Problem Understanding & Setup** | Clear explanation of the problem and objective. Correct Mininet topology creation. Proper controller setup (Ryu/POX). Justification of topology and design choice. | 4 |
| **2. SDN Logic & Flow Rule Implementation** | Correct handling of `packet_in` events. Proper match-action rule design. Correct installation of flow rules (priority, timeouts). Logical correctness of controller behavior. | 6 |
| **3. Functional Correctness (Demo)** | Demonstrates intended functionality: <br>• Forwarding (Learning Switch) <br>• Blocking/Filtering (Firewall/Access Control) <br>• Monitoring/Logging <br>• Routing/QoS behavior <br>Clear working demo in Mininet. | 6 |
| **4. Performance Observation & Analysis** | Measurement and interpretation of metrics: <br>• Latency (ping) <br>• Throughput (iperf) <br>• Flow table changes <br>• Packet statistics <br>Clear explanation of observed behavior. | 5 |
| **5. Explanation, Viva & Validation** | Understanding of SDN concepts and implementation. Ability to explain logic and results. Includes validation/regression testing. Ability to answer questions clearly. | 4 |

---