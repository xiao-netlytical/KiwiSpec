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
    for _i in input:
        a,b = _i.split('_')
        port_i = int(_i[len(a)+1:])
        port_s = _i
        for _k, r_i in range_unit.items():
            if port_i >= r_i[0] and port_i <= r_i[1]:
                port_s = _k
                break
        input_unit.append(port_s) 
    return input_unit
        
def eval_logic_expr(logic_input, input):
    if logic_input.strip() =='':
        return True
    global rst
    rep = {"(": " ", ")": " ", " and ": " ", " or ": " "}
    logic_b = logic_input
    for _k, _v in rep.items():
        logic_b = logic_b.replace(_k, _v)
    logic_unit = logic_b.split()
    input_unit = _eval_logic_fix_range(logic_unit, input)
    logic_b = ''.join([_x+'=False;' for _x in logic_unit])
    input_b = ''.join([_x+'=True;' for _x in input_unit])
    r = 'rst='+logic_input
    exec(logic_b + input_b + r, globals())
    return rst



def get_application_protocol(logic_input):
    if logic_input.strip() =='':
        return []
    rep = {"(": " ", ")": " ", "and": " ", "or": " "}
    logic_b = logic_input
    for _k, _v in rep.items():
        logic_b = logic_b.replace(_k, _v)
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
    for _i, char in enumerate(expression):
        if char == '(':
            if count == 0:
                s = _i
            count += 1
        elif char == ')':
            count -= 1
            if count == 0:
                return (s, _i)
    return None


def collect_logic_list(input_logic, identifier_str='not'):
    collect_s = []
    while input_logic:
        start = input_logic.lower().find(identifier_str, 0)
        if start == -1:
            break
        if input_logic[start+len(identifier_str):].strip().startswith('('):
            st,ed = find_matching_parenthesis(input_logic[start:])
            collect_s.append(input_logic[start:start+ed+1])
            input_logic = input_logic[start+ed+1:]
        else:
            input_logic = input_logic[len(identifier_str):]
    return collect_s

def get_var_depend(logic_expr, var_list):
    var_depend = []
    s_curr = ''

    for _i in logic_expr:
        if _i == '[':
            s_curr = _i
        elif _i == ']':
            s_curr = s_curr.strip('[')
            if s_curr in var_list:
                var_depend.append(s_curr.strip())
            s_curr = ''
        else:
            s_curr += _i
    return var_depend

def get_negate_var_depend(condition, var_list):
    negate_sub_logic_list = collect_logic_list(condition, 'not')

    global_condition = condition

    for sub_logic in negate_sub_logic_list:
        global_condition = global_condition.replace(sub_logic, ' ')

    global_depend = get_var_depend(global_condition, var_list)

    negate_sub_logic_var = {}

    for sub_logic in negate_sub_logic_list:
        negate_sub_logic_var[sub_logic] = {'local_depend':[], 
                                        'global_depend':[]}

        local_var = get_var_depend(sub_logic, var_list)
        for t_var in local_var:
            if t_var in global_depend:
                negate_sub_logic_var[sub_logic]['global_depend'].append(t_var)
            else:
                negate_sub_logic_var[sub_logic]['local_depend'].append(t_var)

    return negate_sub_logic_var
    

def collect_eval(logic_input_string, input_ps, con_var_dep):
    input_string = logic_input_string

    input_p_list = input_ps.split(',')
    for input_p in input_p_list:
        _k,_v = input_p.split('=')
        input_string = input_string.replace(_k.strip(), _v.strip())

    unit_sub_logic_list = collect_logic_list(input_string, 'unit')

    result_list = {}
    for sub_logic in unit_sub_logic_list:
        negate_sub_logic_var = get_negate_var_depend(sub_logic, con_var_dep.keys())
        result_list[sub_logic] = execute_logic(sub_logic[len('unit'):], con_var_dep, '', negate_sub_logic_var)

    for r_k, r_v in result_list.items():
        input_string = input_string.replace(r_k, str(r_v))

    r = eval(input_string)
    return  r

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
    return (ex.keys() if isinstance(ex, dict) else (range(len(ex)) if isinstance(ex, list) else []))

def execute_logic(con_string, con_var_dep, value_str='', negate_sub_logic={}):
    if not con_var_dep:
        return test_logic(con_string, value_str)

    con_string_list = get_sub_cond(con_string)
    vr = list(con_var_dep.keys())[0]
    ex = con_var_dep[vr]
    if not test_expr(ex, value_str):
        for ei in con_string_list:
            if ei.lower().strip() != 'not' and ex in ei:
                con_string = con_string.replace(ei, ' False ')

        if test_expr(con_string, value_str):
            return eval_with_var(con_string, value_str)

    for sub_logic, depens in negate_sub_logic.items():
        if (set(depens['global_depend']) - set(con_var_dep.keys()) == set(depens['global_depend'])):
            local_con_var_dep = {}
            for _k in con_var_dep.keys():
                if _k in depens['local_depend']:
                    local_con_var_dep[_k] = con_var_dep[_k]
            sub_r = execute_logic(sub_logic, local_con_var_dep, value_str)
            con_string = con_string.replace(sub_logic, f'{sub_r}')

    new_con_var_dep = {}
    for _k, _v in con_var_dep.items():
        if f'[{_k}]' in con_string:
            new_con_var_dep[_k] = _v 

    con_var_dep = new_con_var_dep

    if not con_var_dep:
        return execute_logic(con_string, con_var_dep, value_str)

    vr = list(con_var_dep.keys())[0]
    ex = con_var_dep[vr]

    del con_var_dep[vr]

    t_ex= eval_with_var(ex, value_str)
    
    if con_string.lower().startswith('not'):
        r = True
        for _i in get_ex_keys(t_ex):
            r = r and execute_logic(con_string, con_var_dep, 
                                    value_str+f'{vr} = "{_i}";' if isinstance(_i, str) else value_str+f'{vr} = {_i};', 
                                    negate_sub_logic)
            if not r:
                return r
        return r 
    else:
        r = False
        for _i in get_ex_keys(t_ex):
            r = execute_logic(con_string, con_var_dep, 
                                    value_str+f'{vr} = "{_i}";' if isinstance(_i, str) else value_str+f'{vr} = {_i};', 
                                    negate_sub_logic)
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


