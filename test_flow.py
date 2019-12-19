'''
Created on 2015.7.12

@author: Cen
'''
from pox.core import core
from pox.lib.revent.revent import EventMixin
import pox.openflow.libpof_02 as of

#from pox.lib.recoco import Timer
from time import sleep



flow_entry_id_2291=0
dpid_231=2215152430
dpid_230=2215152298
dpid_229=2215146867

device_map = {"SW1": 1,  # 191
              "SW2": 1926449495,  # 192
              #"SW3": 2215152298,  # 230
              #"SW4": 2215152430,  # 231
              }

def _add_protocol(protocol_name, field_list):
    """
    Define a new protocol, and save it to PMDatabase.

    protocol_name: string
    field_list:[("field_name", length)]
    """
    match_field_list = []
    total_offset = 0
    for field in field_list:
        field_id = core.PofManager.new_field(field[0], total_offset, field[1])   #field[0]:field_name, field[1]:length
        total_offset += field[1]
        match_field_list.append(core.PofManager.get_field(field_id))
    core.PofManager.add_protocol("protocol_name", match_field_list)

def add_protocol():
    field_list = [("DMAC",48), ("SMAC",48), ("Eth_Type",16), ("V_IHL_TOS",16), ("Total_Len",16),
                  ("ID_Flag_Offset",32), ("TTL",8), ("Protocol",8), ("Checksum",16), ("SIP",32), ("DIP",32)]
    _add_protocol('ETH_IPv4', field_list)

    field_list = [("DMAC",48), ("SMAC",48), ("Eth_Type",16), ("V_TC_LABLE",32), ("Total_Len",16),
                  ("Protocol",8), ("TTL",8), ("SIP",128), ("DIP",128)]
    _add_protocol('ETH_IPv6', field_list)

    field_list = [("DMAC",20), ("SMAC",28)]
    _add_protocol('FFC', field_list)

class Test(EventMixin):
    def __init__ (self):
        add_protocol()
        core.openflow.addListeners(self, priority=0)

    def _handle_ConnectionUp (self, event):
        if event.dpid == device_map["SW1"]:
            core.PofManager.add_flow_table(event.dpid, 'FirstEntryTable', of.OF_MM_TABLE, 128, [core.PofManager.get_field("DMAC")[0]])  #0  ##
            #core.PofManager.add_flow_table(event.dpid, 'Switch', of.OF_LINEAR_TABLE, 32)   # 16

            sleep(5)
            table_id = core.PofManager.get_flow_table_id(event.dpid, 'FirstEntryTable')
            for i in range(100):
                match = core.PofManager.get_field("DMAC")[0]
                a=hex(i+1)
                addr=a.replace('0x','')
                if i<15:
                    address='0'+addr
                    print address
                else:
                    address=addr
                    print address
                matchx='0000000000'+address
                print matchx
                temp_matchx = core.PofManager.new_matchx(match,matchx, 'FFFFFFFFFFFF')
                action=core.PofManager.new_action_output(0, 0, 0, 0, 0x1)
                ofinstruction=core.PofManager.new_ins_apply_actions([action])
                core.PofManager.add_flow_entry(event.dpid,table_id,[temp_matchx],[ofinstruction],i+1,1)

    def _handle_PortStatus(self, event):
        #print "yes, its the handle PortStatus fuction"
        port_id = event.ofp.desc.port_id
        port_name = event.ofp.desc.name
        if event.dpid == device_map.get("SW1"):
            if port_id == 0x2 or port_id == 0x3:
                core.PofManager.set_port_of_enable(event.dpid, port_id)
        if event.dpid == device_map.get("SW2"):
            if port_id == 0x2 or port_id == 0x3:
                core.PofManager.set_port_of_enable(event.dpid, port_id)

def counter(sw_name, global_table_id, entry_id):   #sw_name:string
    device_id = device_map[sw_name]
    counter_id = core.PofManager.get_flow_entry(device_id, global_table_id, entry_id).counter_id
    core.PofManager.query_counter_value(device_id, counter_id)


def launch ():
    core.registerNew(Test)
    #Timer(25,change,recurring=False)