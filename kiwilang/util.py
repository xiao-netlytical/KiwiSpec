# Author: Hong Xiao
# This file includes the utility code for translating code in KiwiSpec to python and executes the python code.

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


def collect_negate_list(input_logic):
    collect_s = []
    while input_logic:
        start = input_logic.find('not', 0)
        if start == -1:
            break
        if input_logic[start:].strip().startswith('('):
            st,ed = find_matching_parenthesis(input_logic[start:])
            collect_s.append(input_logic[start:start+ed+1])
            input_logic = input_logic[start+ed+1:]
        else:
            input_logic = input_logic[len('not'):]
    return collect_s

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

import re

def get_sub_cond(con):
    cond_expr = re.split(r'\b(?:and|or|not)\b', con, flags=re.IGNORECASE)
    return cond_expr

def eval_with_var(ex, value_str):
    if value_str:
        exec(value_str, globals())
    return eval(ex)

def test_expr(ex, value_str):
    try:
        lg = eval_with_var(ex, value_str)
        return True
    except:
        return False
    
def test_logic(ex, value_str):
    if test_expr(ex, value_str):
        return eval_with_var(ex, value_str)
    else:
        return False
    
def get_ex_keys(ex):
    return (ex.keys() if isinstance(ex, dict) else range(len(ex)))

def execute_logic(con_string, con_var_dep, value_str='', negate_sub_logic={}):
    if not con_var_dep:
        return test_logic(con_string, value_str)

    con_string_list = get_sub_cond(con_string)
    vr = list(con_var_dep.keys())[0]
    ex = con_var_dep[vr]
    if not test_expr(ex, value_str):
        for ei in con_string_list:
            if ei.strip() != 'not' and ex in ei:
                con_string = con_string.replace(ei, ' False ')

        if test_expr(con_string, value_str):
            return eval_with_var(con_string, value_str)

    for sub_logic, depens in negate_sub_logic.items():
        if (set(depens['global_depend']) - set(con_var_dep.keys()) == set(depens['global_depend'])):
            local_con_var_dep = {}
            for k in con_var_dep.keys():
                if k in depens['local_depend']:
                    local_con_var_dep[k] = con_var_dep[k]
            sub_r = execute_logic(sub_logic, local_con_var_dep, value_str)
            con_string = con_string.replace(sub_logic, f'{sub_r}')

    new_con_var_dep = {}
    for k, v in con_var_dep.items():
        if f'[{k}]' in con_string:
            new_con_var_dep[k] = v 

    con_var_dep = new_con_var_dep

    if not con_var_dep:
        execute_logic(con_string, con_var_dep, value_str)

    vr = list(con_var_dep.keys())[0]
    ex = con_var_dep[vr]

    del con_var_dep[vr]

    t_ex= eval_with_var(ex, value_str)
    
    if con_string.startswith('not'):
        r = True
        for i in get_ex_keys(t_ex):
            r = r and execute_logic(con_string, con_var_dep, value_str+f'{vr} = {i};', negate_sub_logic)
            if not r:
                return r
        return r 
    else:
        r = False
        for i in get_ex_keys(t_ex):
            r = execute_logic(con_string, con_var_dep, value_str+f'{vr} = {i};', negate_sub_logic)
            if r:
                return r
        return r   


def execute_code(result, result_v):
    exec(result, globals())
    if result_v:
        return globals()[result_v]

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


