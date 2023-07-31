from mininet.topo import Topo


class MyTopo(Topo):
    def __init__(self, n):
        if n < 1:
            raise ValueError("Number of switches must be positive")

        Topo.__init__(self)

        h1 = self.addHost("h1")
        h2 = self.addHost("h2")
        h3 = self.addHost("h3")
        h4 = self.addHost("h4")

        prev_switch = self.addSwitch("s1")

        self.addLink(h1, prev_switch)
        self.addLink(h2, prev_switch)

        for i in range(2, n + 1):
            s = self.addSwitch(f"s{i}")
            self.addLink(prev_switch, s)
            prev_switch = s

        self.addLink(prev_switch, h3)
        self.addLink(prev_switch, h4)


topos = { "topoTP": MyTopo }
