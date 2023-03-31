def count_one(i):
    return 1
    
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
        port_i = int(i[len('TCP_'):])
        port_s = i
        for k, r_i in range_unit.items():
            if port_i >= r_i[0] and port_i <= r_i[1]:
                port_s = k
                print(port_s, i)
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


