#!/usr/bin/env python3

from mininet.topo import Topo

class FirewallTopo(Topo):
    "Custom Firewall Topology"

    def build(self):
        # Add host and switch nodes
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')
        
        # Central switch
        s1 = self.addSwitch('s1', protocols='OpenFlow13')

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)


topos = { 'firewalltopo': ( lambda: FirewallTopo() ) }
