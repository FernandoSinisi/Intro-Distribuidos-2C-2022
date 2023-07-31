from enum import Enum

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from pox.core import core

import pox.forwarding.l2_learning as l2_learning
import pox.forwarding.l2_pairs as l2_pairs
import pox.openflow.libopenflow_01 as of

from pox.lib.revent import *
from pox.lib.addresses import EthAddr
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.ethernet import ethernet

log = core.getLogger()


class Proto(Enum):
    TCP = ipv4.TCP_PROTOCOL
    UDP = ipv4.UDP_PROTOCOL


class Firewall(EventMixin):
    def __init__(self, fw_switch, firewall_params):
        self.listenTo(core.openflow)
        self.fw_switch = fw_switch
        self.fw_params = firewall_params
        log.info("Enabling Firewall Module")

    def _handle_ConnectionUp(self, event):
        if event.connection.ports[of.OFPP_LOCAL].name == self.fw_switch:
            self.install_firewall(event)

    def install_firewall(self, event):
        handlers = [
            ("rule1", self.install_rule_1),
            ("rule2", self.install_rule_2),
            ("rule3", self.install_rule_3),
        ]

        for rule, installer in handlers:
            if rule in self.fw_params:
                for r in self.fw_params[rule]:
                    installer(event, r)

    def send_of_msg(self, event, **match_args):
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match(dl_type=ethernet.IP_TYPE, **match_args)
        event.connection.send(msg)

    def install_rule_1(self, event, rule):
        log.info(f"Installing Firewall rule #1 for port {rule['dst_port']}")
        for proto in Proto:
            self.send_of_msg(event, nw_proto=proto.value, tp_dst=rule["dst_port"])

    def install_rule_2(self, event, rule):
        log.info(f"Installing Firewall rule #2 for host {rule['src_host']}")
        self.send_of_msg(
            event,
            dl_src=EthAddr(rule["src_host"]),
            nw_proto=Proto[rule["proto"]].value,
            tp_dst=rule["dst_port"],
        )

    def install_rule_3(self, event, rule):
        log.info(f"Installing Firewall rule #3 for hosts {rule['hosts']}")
        for host_src in rule["hosts"]:
            for host_dst in rule["hosts"]:
                if host_src != host_dst:
                    self.send_of_msg(
                        event, dl_src=EthAddr(host_src), dl_dst=EthAddr(host_dst)
                    )


def launch(*, switch="s1", config="rules.toml"):
    # l2_learning.launch()
    l2_pairs.launch()
    core.registerNew(Firewall, switch, get_params(config))


def get_params(config):
    with open(config, "rb") as f:
        return tomllib.load(f)
