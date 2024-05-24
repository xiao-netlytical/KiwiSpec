# Author: Hong Xiao
# This program translates code in KiwiSpec to python and executes the python code.

from util import *
from kiwi_util import *
from kiwi_update import *
from kiwi_create import *
from kiwi_select import *
from kiwi_lexer import *

def FromPaser(fn, text):
	text = strip_prefix(text, ['read'])
	l = list_strip(text.split(";"))
	r = ''
	for fl in l:
		try:
			f, s = split(fl, ' as ')
			r += f'{s} = read_json_file(f"{f}");'
		except BaseException as e:
			print('The right format for READ is:')
			print('READ file AS v1; file_path/file1 AS v2; d1/d2/file3 AS v3; ...\n')
			print('you may miss ";" or " as "\n')
			raise

	return r

def ToPaser(fn, text):
	text = strip_prefix(text, ['write'])
	text_list = text.split(';')
	r = ''
	for text_t in text_list:
		try:
			f, d = split(text_t, ' from ')
			f = f.strip()
			d = d.strip()
			r += f'\nwrite_json_file(f"{f}", {d});'
		except BaseException as e:
			print('The right format for WRITE is:')
			print('WRITE file FROM r1; file_path/file1 FROM r2; d1/d2/file3 FROM r3; ...\n')
			print('you may miss ";" or " FROM "\n')
			raise

	return r

def DrawPaser(fn, text):
	text = strip_prefix(text, ['draw'])
	text_list = text.split(';')
	r = ''
	for text_t in text_list:
		f = text.strip()
		r += f'\ndraw_conn({f});'
	return r

def CreatePaser(fn, text):
	text = text.strip()

	if not text.lower().startswith('create'):
		return

	boundary = ['create', 'select', 'var']
	query_list = parser_get_query_list(text, boundary)

	result_var = ''
	var_list = []
	body_text = ''
	create_list = {}
	for q in query_list:
		if q.lower().startswith('create'):
			create_text = q[len('create '):]
			tmp_create_list = create_text.split(';')
			for c in tmp_create_list:
				try:
					create_text, result_var = list_strip(split(c, ' as '))
					create_list[result_var] = create_text
				except BaseException as e:
					print('The right format for CREATE is:')
					print('CREATE target_template AS r1; target_template AS r2; ... \n')
					print('you may miss ";" or " as "\n')
					raise
		if q.lower().startswith('select'):
			body_text = q
		if q.lower().startswith('var'):
			var_list = list_strip(q[len('var'):].split(','))

	result_value = {}
	for r, create_text in create_list.items():
		lexer = ResultLexer(fn, create_text)
		tokens = lexer.make_tokens()
		parser = CreateResultParser(tokens, {}, '', '')
		result_value[r] = parser.get_result_value_set()

	body_parser = CreateBodyParser(fn, body_text, var_list, result_value)
	body_parser.parse()
	body_loop = body_parser.gen_clause()

	r_code = ''
	tail_code = ''

	header_flag = True

	for r, create_text in create_list.items():
		lexer = ResultLexer(fn, create_text)
		tokens = lexer.make_tokens()
		parser = CreateResultParser(tokens, body_parser.var_agg_map, body_parser.order_text, r)
		if header_flag:
			r_code = parser.preparse()
			header_flag = False
		header_start, header_tail = parser.parse()

		r_code += header_start

		for tail in header_tail:
			if tail.startswith('update '):
				unit_r, _ = UpdatePaser(fn, tail)
				tail_code += unit_r
			else:
				tail_code += tail

	for l in body_loop:
		r_code += ' ' * l[0] + f'{l[1]}\n'

	return r_code+tail_code, result_var

def UpdatePaser(fn, text):
	text = text.strip()

	if not text.lower().startswith('update'):
		return

	boundary = ['update', 'var', 'set']
	query_list = parser_get_query_list(text, boundary)

	create_text = text
	result_var = ''
	var_list = []
	body_text = ''

	for q in query_list:
		if q.lower().startswith('update'):
			result_var = q[len('update'):].strip()
		if q.lower().startswith('set'):
			body_text = q
		if q.lower().startswith('var'):
			var_list = list_strip(q[len('var'):].split(','))


	parser = UpdateBodyParser(fn, body_text, var_list)
	parser.parse()
	body_loop = parser.gen_clause()

	# dump the code
	offset_space = ''
	r_code = 'init_util()\n'
	for l in body_loop:
		r_code += offset_space + f'{l}\n'
		if l.startswith('for') or l.startswith('if'):
			offset_space += '    '

	return r_code,result_var

def QueryParser(fn, text):
	boundary = [ 'define', 'with', 'read', 'create', 'update',  'write',  'draw']
	query_list = parser_get_query_list(text, boundary)

	result_list = []
	unit_v = ''
	for q in query_list:
		print('\n',q,'\n')
		if q.lower().strip().startswith('define'):
			q = q.strip()[len('define'):]
			_pass_define(q)
		if q.lower().startswith('read'):
			for _k,_v in path_define.items():
				q = q.replace(_k, _v)
			result_list.append(FromPaser(fn, q))
		if q.lower().startswith('with'):
			continue
		if q.lower().startswith('write'):
			for _k,_v in path_define.items():
				q = q.replace(_k, _v)
			result_list.append(ToPaser(fn, q))
		if q.lower().startswith('draw'):
			result_list.append(DrawPaser(fn, q))
		if q.lower().startswith('create'):
			unit_r, unit_v = CreatePaser(fn, q)
			result_list.append(unit_r)
		if q.lower().startswith('update'):
			unit_r, unit_v = UpdatePaser(fn, q)
			result_list.append(unit_r)


	r_code ='\n'
	for q in result_list:
		r_code +=  f'{q}\n'
	r_code += '\n'

	print(r_code)
	return r_code, unit_v

def cli():
	query = ''
	while True:
		text = input('basic > ')
		if text == '':
			result, result_v = QueryParser('<stdin>', query)
			exec(result)
			print(r)
			query = ''
		else:
			query += text


path_define = {}
def _pass_define(line):
	define_list = list_strip(line.split(','))
	for d in define_list:
		if not d:
			continue
		try:
			_k, _v = d.strip().split('=')
		except BaseException as e:
			print('The right format for DEFINE is:')
			print('DEFINE v1=x1/x2/file1, v2=x1/x2/file2, ...\n')
			print('you may miss "," or "="\n')
			raise

		path_define[_k.strip()] = _v.strip()

def kiwi(text):
	result, result_v = QueryParser(None, text)
	result_r = execute_code(result, result_v)
	if result_r:
		return result_r

import sys

def main():

	def _startswith_list(s, l):
		for _i in l:
			if  s.strip().lower().startswith(_i):
				return _i.lower()
		return ''
	
	if len(sys.argv) < 2:
		print("Please provide a filename as an argument")
		sys.exit(1)

	filename = sys.argv[1]

	try:
		with open(filename, 'r') as file:
			command_buffer = ''
			line_buffer = []
			pre_start = ''

			mini_buff = []

			for line in file:
				if line.strip().startswith('#'):
					continue
				start = _startswith_list(line, ['read ', 'define ', 'write ', 'create '])
				if start:
					if mini_buff:
						mini_buff_start  = _startswith_list(mini_buff[0], ['read ', 'define ', 'write '])
						if mini_buff_start == 'define ':
							for l in mini_buff:
								if l.strip().startswith('define '):
									l = l.strip()[len('define '):]
								_pass_define(l)
						elif mini_buff_start in ['read ', 'write ']:
							for l in mini_buff:
								for _k,_v in path_define.items():
									l = l.replace(_k, _v)		
								line_buffer.append(l)
						else:
							line_buffer += mini_buff 
						mini_buff = []	
				mini_buff.append(line)

			if mini_buff:
				mini_buff_start  = _startswith_list(mini_buff[0], ['read ', 'write '])
				if mini_buff_start == 'define ':
					for l in mini_buff:
						if l.strip().startswith('define '):
							l = l.strip()[len('define '):]
						_pass_define(l)
				elif mini_buff_start in ['read ', 'write ']:
					for l in mini_buff:
						for _k,_v in path_define.items():
							l = l.replace(_k, _v)		
						line_buffer.append(l)
				else:
					line_buffer += mini_buff 

			for line in line_buffer:
				print(line)
				start = _startswith_list(line, ['read ', 'create '])
				if command_buffer.strip() != '' and (start =='read ' or start=='create ' and  pre_start != 'read '):
					kiwi(command_buffer)
					command_buffer = ''

				if line.strip("' ', '\n', '\t'"):
					command_buffer += line

				if start:
					pre_start = start
			
			if command_buffer:
				kiwi(command_buffer)

	except FileNotFoundError:
		print(f"File {filename} not found")
		sys.exit(1)


# if __name__=="__main__":
    # main()


kiwi(
"""READ 
../../KiwiSpec/sample_data/result/ip_to_servers.json AS srvs; 
../../KiwiSpec/sample_data/result/server_to_ips.json AS ips;
../../KiwiSpec/sample_data/zeek/conn.json AS flows

CREATE {d_ip: ipg} as r
VAR i SELECT
	flows[i]["id.resp_h"] as d_ip;
    collect set(ips[srvs[d_ip][_]]) AS ipg
WRITE ip_groups.json FROM r
"""
)

# kiwi(
"""
define conn_path=../sample_data/zeek, write_path=../sample_data/result

READ config.json as object; conn_path/conn.json AS flows; 
../sample_data/cloud/pod_config.json as pod_config


create violate_rules as result
VAR k SELECT
	object["spec"][k] as spec_k;
	collect eval("unit(spec_k_token == True) and unit(match1 == 'abc') and unit(not(match2 == 'abcd'))": 
	spec_k_token = spec_k["automountServiceAccountToken"], 
	match1=spec_k["containers"][i1]["volumeMounts"][j1]["mountPath"], 
	match2=spec_k["initContainers"][i2]["volumeMounts"][j2]["mountPath"]) by i1,j1,i2,j2 as condition;
	collect set(spec_k["automountServiceAccountToken"]) where condition group by NONE as violate_rules
write logic_test_1.json from result

create [violate_name] as r;
var i select
   ["something"] as allowed;
   ["must_drop", "another_one"] as must_drop;
    pod_config[_] as object;
    object["spec"][i][_] as container;
    object["metadata"]["name"] as name;
    container["name"] as container_name;
    name+":"+container_name as violate_name;
where i in ["containers", "initContainers", "ephemeralContainers"];
   not container["securityContext"]["capabilities"]["add"][_] in allowed or
    must_drop and not(must_drop[_] in container["securityContext"]["capabilities"]["drop"]) 
write logic_test.json from r

"""
# )

"""
define conn_path=../sample_data/zeek, write_path=../sample_data/result
read write_path/ip_to_group.json as traffic
create [tr] as traffic_list
var i select
    [traffic[i]["src"], traffic[i]["dst"]] as tr

write write_path/traffic_list.json from traffic_list
"""
"""
define read_path_flow=../sample_data/zeek/conn.json,
read_dns_path = ../sample_data/zeek/dns.json, 
write_path=../sample_data/result;

read write_path/ip_to_servers.json as srv
update srv 
var ip set 
    srv[ip] as list(set(srv[ip]) - {"WebServer"}); 
    where srv[ip] != ["WebServer"]
write write_path/clean_ip_to_servers.json from srv

"""
# kiwi(
"""
define read_path_flow=../sample_data/zeek/conn.json,
read_dns_path = ../sample_data/zeek/dns.json, 
write_path=../sample_data/result;

read read_dns_path AS flows; 
write_path/ip_to_servers.json as srv_names;

create [t] as r
var i  select 
flows[i]["id.orig_h"] as ips;
flows[i]["id.resp_h"] as ipd;
srv_names[ips][_] as server_s;
srv_names[ips][_] as server_d;
[server_s, server_d] as t;
where srv_names[ips] and srv_names[ipd]
write dns_domain_requests.json FROM r

"""
# )
"""

create [{"src":s_ip, "base_domain":domain, "requests": ct, "srv":srv}] AS r
var i  select 
    flows[i]["id.orig_h"] as s_ip;
    ".".join(flows[i]["query"].split(".")[-2:]) as domain;
    count distinct(i) GROUP BY s_ip,domain AS ct;
	srv_names[s_ip|" "] as srv;
	order by ct DESC limit 1000;
write write_path/dns_domain_requests.json FROM r


create {s_ip: i} as r1
var i  select 
	i from range[100][i];
	r[i]["src"] as s_ip;
	where not srv_names[r[i]["src"]];
 write write_path/dns_domain_requests_r1.json from r1  

update var i set 
	i from range[10][i];
    r[i]["server"] as srv_names[r[i]["src"]|"none"];
	r[i]["base_domain"] delete;
	where r[i]["requests"] < 1000

write write_path/dns_domain_requests.json from r

update set 
	r ORDER BY "requests":DESC

write write_path/dns_domain_requests.json from r
"""
