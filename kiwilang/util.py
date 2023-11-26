
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
    try:
        dt =datetime.strptime(str(t).split('.')[0], '%Y-%m-%dT%H:%M:%S')
        return dt.timestamp()
    except:
        return int(t)
    
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

def find_matching_parenthesis(expression):
    count = 0
    s = 0
    for i, char in enumerate(expression):
        if char == '(':
            if count == 0:
                s = i
            count += 1
        elif char == ')':
            count -= 1
            if count == 0:
                return (s, i)
    return None


def collect_eval(input_string, input_p):
    result_str = ''
    tmp_result_str = ''
    process_str = input_string
    exec(input_p, globals())
    def find_and_eval_first_unit(input_string):
        unit = input_string.find("unit")
        if (unit == -1):
            return -1, -1, -1
        next = unit + len("unit")
        start, end = find_matching_parenthesis(input_string[next:])
        eval_result = eval(input_string[next+start:next+end+1])
        return eval_result, unit, next+end

    while (process_str):
        r, start, end = find_and_eval_first_unit(process_str)
        if r == -1:
            result_str += process_str
            tmp_result_str += process_str
            break
        if r:
            result_str += process_str[:start] + " True "
            tmp_result_str += process_str[:start] + " True "
            process_str = process_str[end+1:]
        else:
            result_str += process_str[:end+1]
            tmp_result_str += process_str[:start] + " False "
            process_str = process_str[end+1:]


    r = eval(tmp_result_str)
    return  r, result_str


def draw_conn(connections):
    import networkx as nx
    import matplotlib.pyplot as plt

    # Define your list of point-to-point connections as tuples (source, target)

    # connections = []          
    # for i in result:
        # connections.extend(i)

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
    nx.draw(G, layout, with_labels=True, node_size=500, node_color='lightblue', font_size=5, font_color='black', font_weight='bold', arrows=True, connectionstyle="arc3,rad=0.1")
    plt.title("Point-to-Point Link Graph")
    plt.axis('off')  # Turn off the axis
    plt.show()
