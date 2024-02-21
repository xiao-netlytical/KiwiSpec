# Author: Hong Xiao
# This program translates code in KiwiSpec to python and executes the python code.

from util import *
from kiwi_util import *
from kiwi_update import *
from kiwi_create import *
from kiwi_select import *

def FromPaser(fn, text):
	text = strip_prefix(text, ['read'])
	l = list_strip(text.split(";"))
	r = ''
	for fl in l:
		f, s = split(fl, ' as ')
		r += f'{s} = read_json_file(f"{f}");'
	return r

def ToPaser(fn, text):
	text = strip_prefix(text, ['write'])
	text_list = text.split(';')
	r = ''
	for text_t in text_list:
		f, d = split(text_t, ' from ')
		f = f.strip()
		d = d.strip()
		r += f'\nwrite_json_file(f"{f}", {d});'
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
				create_text, result_var = list_strip(split(c, ' as '))
				create_list[result_var] = create_text
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
	boundary = ['create', 'with', 'read', 'write', 'update', 'draw']
	query_list = parser_get_query_list(text, boundary)

	result_list = []
	unit_v = ''
	for q in query_list:
		print(q, '\n')
		if q.lower().startswith('read'):
			result_list.append(FromPaser(fn, q))
		if q.lower().startswith('with'):
			continue
		if q.lower().startswith('write'):
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
	
	def _pass_define(line):
		define_list = list_strip(line.split(','))
		for d in define_list:
			if not d:
				continue
			_k, _v = d.strip().split('=')
			path_define[_k.strip()] = _v.strip()
	
	if len(sys.argv) < 2:
		print("Please provide a filename as an argument")
		sys.exit(1)

	filename = sys.argv[1]

	path_define = {}
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


if __name__=="__main__":
    main()
