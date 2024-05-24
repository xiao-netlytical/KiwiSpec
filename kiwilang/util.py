# Author: Hong Xiao
# This file includes the utility code for translating code in KiwiSpec to python and executes the python code.
from logic_expr import *

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

def collect_eval(logic_input_string, input_ps, con_var_dep):
    input_string = logic_input_string

    input_p_list = input_ps.split(',')
    for input_p in input_p_list:
        _k,_v = input_p.split('=')
        input_string = input_string.replace(_k.strip(), _v.strip())

    unit_sub_logic_list = collect_logic_list(input_string, 'unit')

    result_list = {}
    for sub_logic in unit_sub_logic_list:
        use_con_var_dep = {}
        for k, v in con_var_dep.items():
            if k in sub_logic:
               use_con_var_dep[k] = v 

        sub_logic_r = execute_logic(sub_logic[len('unit'):], use_con_var_dep)

        input_string.replace(sub_logic, str(sub_logic_r))
        if test_expr(input_string.replace('unit', ' '), ''):
            return eval_with_var(input_string.replace('unit', ' '), '')
        
    return  test_and_eval_logic(input_string.replace('unit', ' '), '')


def eval_with_var(ex, value_str):
    if value_str:
        exec(value_str.replace('\n', ' '), globals())
    return eval(ex)

def test_expr(ex, value_str):
    try:
        lg = eval_with_var(ex, value_str)
        return True
    except:
        return False
    
def test_and_eval_logic(ex, value_str):
    try:
        return eval_with_var(ex, value_str)
    except:
        return False
    
    
def execute_logic(con_string, con_var_dep):
    
    lexer = LogicLexer(con_string)
    tokens, error = lexer.make_tokens()
    if error: raise

    parser = LogicParser(tokens)
    ast = parser.parse()
    if ast.error: raise

    return execute_logic_call(tokens, con_string, con_var_dep, '', ast)

def execute_logic_call(tokens, con_string, con_var_dep, value_str, ast):
    while con_var_dep:
        vr = list(con_var_dep.keys())[0]
        ex = con_var_dep[vr]
        if not test_expr(ex, value_str):
            for ei in tokens:
                if ei.value is not None and ex in ei.value:
                    if ' not ' in ei.value:
                        ei.value = 'True'
                    else:
                        ei.value = 'False'
            del con_var_dep[vr]
        else:
            break
    
    if not con_var_dep:
        interpreter = LogicInterpreter()
        return interpreter.visit(ast.node, value_str)
    
    vr = list(con_var_dep.keys())[0]
    ex = con_var_dep[vr]
    del con_var_dep[vr]

    v_vr = eval_with_var(f'{ex}.keys() if isinstance({ex}, dict) else (range(len({ex})) if isinstance({ex}, list) else [])', value_str)

    result = True

    for _v in v_vr:
        value_str += f'{vr} = "{_v}";' if isinstance(_v, str) else f'{vr} = {_v};' 
        result = result and execute_logic_call(tokens, con_string, con_var_dep, value_str, ast)
        if not result:
            return result
    return result

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


#######################################
# INTERPRETER
#######################################

class LogicInterpreter:
    def visit(self, node, value_str):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, value_str)

    def no_visit_method(self, node, value_str):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    def visit_L_ExprNode(self, node, value_str):
        return test_and_eval_logic(node.tok.value, value_str)
    
    def visit_BinOpNode(self, node, value_str):
        left = self.visit(node.left_node, value_str)
        right = self.visit(node.right_node, value_str)

        if node.op_tok.type == TT_OR:
            result = left or right
        elif node.op_tok.type == TT_AND:
            result = left and right
		
        return result

    def visit_UnaryOpNode(self, node, value_str):
        l_not = self.visit(node.node, value_str)

        if node.op_tok.type == TT_NOT:
            return not l_not


#######################################
# RUN
#######################################

def logic_eval(text, value_str):
	# Generate tokens
	lexer = LogicLexer(text)
	tokens, error = lexer.make_tokens()
	if error: raise
	
	# Generate AST
	parser = LogicParser(tokens)
	ast = parser.parse()
	if ast.error: raise

	# Run program
	interpreter = LogicInterpreter()
	result = interpreter.visit(ast.node, value_str)

	return result