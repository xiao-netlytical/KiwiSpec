
def write_json_file(file_name, data):
    import json
    json_data = json.dumps(data, indent=4)
    with open(file_name, 'w') as file:
        file.write(json_data)

def read_json_file(file_name):
    import json
    with open(file_name, 'r') as file:
        json_data = json.load(file)
        return json_data

import ipaddress
def is_internet_ip(ip):
    cidrs = ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']
    for cidr in cidrs:
        if ipaddress.ip_address(ip) in ipaddress.ip_network(cidr):
            return False
    return True


from datetime import datetime
def epoch_time(t):
    dt =datetime.strptime(t.split('.')[0], '%Y-%m-%dT%H:%M:%S')
    return dt.timestamp()

def _eval_logic_fix_range(logic_range, input):
    range_unit = {}
    input_unit = []
    for i_range in logic_range:
        if '_to_' in i_range:
            r = i_range[len('TCP_'):].split('_to_')
            range_unit[i_range] = [int(r[0]), int(r[1])]
    if not range_unit:
        return input
    for i in input:
        a,b = i.split('_')
        port_i = int(i[len(a)+1:])
        port_s = i
        for k, r_i in range_unit.items():
            if port_i >= r_i[0] and port_i <= r_i[1]:
                port_s = k
                break
        input_unit.append(port_s) 
    return input_unit
        
def eval_logic_expr(logic_input, input):
    if logic_input.strip() =='':
        return True
    global rst
    rep = {"(": " ", ")": " ", " and ": " ", " or ": " "}
    logic_b = logic_input
    for k, v in rep.items():
        logic_b = logic_b.replace(k, v)
    logic_unit = logic_b.split()
    input_unit = _eval_logic_fix_range(logic_unit, input)
    logic_b = ''.join([x+'=False;' for x in logic_unit])
    input_b = ''.join([x+'=True;' for x in input_unit])
    r = 'rst='+logic_input
    exec(logic_b + input_b + r, globals())
    return rst

def get_application_protocol(logic_input):
    if logic_input.strip() =='':
        return []
    rep = {"(": " ", ")": " ", "and": " ", "or": " "}
    logic_b = logic_input
    for k, v in rep.items():
        logic_b = logic_b.replace(k, v)
    logic_unit = logic_b.split()
    return logic_unit


_index_by = {}
def index_by(*args):
    _index_by[args] = _index_by.get(args, len(_index_by.keys())+1)
    return (_index_by[args])
    

def init_util():
    global _index_by
    _index_by = {}

def draw_conn(result):
    import networkx as nx
    import matplotlib.pyplot as plt

    # Define your list of point-to-point connections as tuples (source, target)

    connections = []          
    for i in result:
        connections.extend(i)

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges to the graph
    for src, tgt in connections:
        G.add_node(src)
        G.add_node(tgt)
        G.add_edge(src, tgt)

    # Define the layout for the graph (e.g., spring_layout, circular_layout, etc.)
    layout = nx.spring_layout(G)

    # Draw the graph
    nx.draw(G, layout, with_labels=True, node_size=500, node_color='lightblue', font_size=5, font_color='black', font_weight='bold', arrows=True, connectionstyle="arc3,rad=0.2")
    plt.title("Point-to-Point Link Graph")
    plt.axis('off')  # Turn off the axis
    plt.show()
