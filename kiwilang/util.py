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

def eval_logic_expr(logic_input, input):
    if logic_input.strip() =='':
        return True
    global rst
    rep = {"(": " ", ")": " ", " and ": " ", " or ": " "}
    logic_b = logic_input
    for k, v in rep.items():
        logic_b = logic_b.replace(k, v)
    s = logic_b.split()
    logic_b = ''.join([x+'=False;' for x in s])
    input_b = ''.join([x+'=True;' for x in input])
    r = 'rst='+logic_input
    exec(logic_b + input_b + r, globals())
    return rst


