# Author: Hong Xiao
# This program translates code in kiwilang to python and executes the python code.

from util import *
import functools

def strip_operator(s, pre_list):
	for ss in pre_list:
		if s.lower().startswith(ss):
			new_s = s[len(ss):]
			return new_s.strip()[1:-1]
	return s

def strip_prefix(s, pre_list):
	for ss in pre_list:
		if s.lower().startswith(ss):
			new_s = s[len(ss):]
			return new_s.strip()
	return s

def split(s, t):
	if t.lower() in s:
		x, y = s.split(t.lower())
		return x, y
	elif t.upper() in s:
		x, y = s.split(t.upper())
		return x, y
	return s
	
def str_in(t, s):
	return t.lower() in s or t.upper() in s

class Position:
		def __init__(self, idx, ln, col, fn, ftxt):
				self.idx = idx
				self.ln = ln
				self.col = col
				self.fn = fn
				self.ftxt = ftxt

		def advance(self, current_char=None):
				self.idx += 1
				self.col += 1

				if current_char == '\n':
						self.ln += 1
						self.col = 0
				return self

class Token:
	def __init__(self, type_, value=None):
		self.type = type_
		self.value = value

	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'


class ResultLexer:
	def __init__(self, fn, text):
		self.fn = fn
		self.text = text
		self.pos = Position(-1, 0, -1, fn, text)
		self.current_char = None
		self.advance()

	def advance(self):
		self.pos.advance(self.current_char)
		self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def make_tokens(self):
		tokens = []
		while self.current_char != None:
			if self.current_char in ' \t\n':
				self.advance()
			elif self.current_char in '[{}],:()=':
				tokens.append(Token('TOKEN', self.current_char))
				self.advance()
			elif self.current_char == '"' or self.current_char == "'" :
				tokens.append(self.make_str())
			else:
				tokens.append(self.make_expr())
		return tokens

	def make_str(self):
		id_str = self.current_char
		str_q = {"'":0, '"':0}
		str_q[self.current_char] = 1
		self.advance()
		while str_q["'"] != 0 or str_q['"'] != 0:
			if self.current_char == "'":
				str_q["'"] = str_q["'"]+1 if str_q["'"]%2 == 0 else str_q["'"]-1
			if self.current_char == '"':
				str_q['"'] = str_q['"']+1 if str_q['"']%2 == 0 else str_q['"']-1
			id_str += self.current_char
			self.advance()

		tok_type = 'STR'
		return Token(tok_type, id_str)

	def make_expr(self):
		id_str = ''
		while self.current_char != None and self.current_char not in ' ={}()[]:,\t\n':
			id_str += self.current_char
			self.advance()

		tok_type = 'EXPR'
		return Token(tok_type, id_str)

class CreateResultParser:
	def __init__(self, tokens, var_agg_map, order_text, result_var):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()
		self.var_agg_map = var_agg_map
		self.result_var = result_var
		self.order_text = order_text

	def advance(self):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
			return self.current_tok


	def parse_result_list(self, head):
		r_tail = ''

		self.advance()
		if self.current_tok.value == '{':
			self.advance()
			tmp_string = ''
			while self.tok_idx < len(self.tokens) and self.current_tok.value != '}':
				if self.current_tok.type == 'STR':
					tmp_string += self.current_tok.value
					self.advance()
				elif self.current_tok.type == 'EXPR':
					if self.current_tok.value in self.var_agg_map.keys():
						tmp_string += f"""eval(r_tuple['{self.current_tok.value}'])"""
					else:
						tmp_string += f"""r_tuple['{self.current_tok.value}']"""
					self.advance()
				else:
					tmp_string += self.current_tok.value
					self.advance()

				if self.current_tok.value == ':':
					tmp_string += self.current_tok.value
					self.advance()
					if self.current_tok.type == 'EXPR':
						if self.current_tok.value in self.var_agg_map.keys():
							tmp_string += f"""eval(r_tuple['{self.current_tok.value}'])"""
						else:
							tmp_string += f"""r_tuple['{self.current_tok.value}']"""
					self.advance()

			tmp_string = '{' + tmp_string + '}'
			r_tail += f"""{head}.append({tmp_string})\n"""

		elif self.current_tok.type == 'EXPR':
			if self.current_tok.value in self.var_agg_map.keys():
				r_tail += f"""eval({head}.append(r_tuple['{self.current_tok.value}']))"""
			else:
				r_tail += f"""{head}.append(r_tuple['{self.current_tok.value}'])"""
			self.advance()
		return r_tail

	def parse_result_dict(self, head):
		self.advance()
		tmp_values = {}
		if self.current_tok.type == 'STR':
			tmp_values["key"]=self.current_tok.value
		elif self.current_tok.type == 'EXPR':
			if self.current_tok.value in self.var_agg_map.keys():
				tmp_values["key"]=f"""eval(r_tuple['{self.current_tok.value}'])"""
			else:
				tmp_values["key"]=f"""r_tuple['{self.current_tok.value}']"""

		self.advance()
		r_tail = ''
		if self.current_tok.value == ':':
			self.advance()
			if self.current_tok.type == 'EXPR':
				if self.current_tok.value in self.var_agg_map.keys():
					val = f"""eval(r_tuple['{self.current_tok.value}'])"""
				else:
					val =  f"""r_tuple['{self.current_tok.value}']"""
				tmp_values["val"] = val
				self.advance()
				r_tail+=f"""{head}[{tmp_values["key"]}]={tmp_values["val"]}"""
			elif self.current_tok.value == '[':
				tmp_result = self.parse_result_list(f"""{head}.setdefault({tmp_values["key"]}, [])""")
				# r_tail+=f"""{head}[{tmp_values["key"]}]={tmp_result}"""   
				r_tail+=f"""{tmp_result}"""          
			elif self.current_tok.value == '{':
				tmp = '{}'
				r_tail = self.parse_result_dict(f"""{head}.setdefault({tmp_values["key"]}, {tmp})""")
			else:
				print("error - format")

		return r_tail

	def preparse(self):
		r_head = 'default_group_by="default_group_by"\n'
		for k in self.var_agg_map.keys():
			if self.var_agg_map[k]["op"] in ['collect list', 'collect set', 'count distinct', 'sum', 'min', 'max']:
				tmp = '{}'
				r_head += f"""{k} = {tmp}\n"""
				r_head += f"""_{k}_check = []\n"""
				r_head += f"""_{k}_flag = True\n"""
			if self.var_agg_map[k]["op"] == 'count distinct':
				tmp = '{}'
				r_head += f"""{k}_ = {tmp}\n"""
		return r_head

	def parse(self):
		self.group_by = set()
		self.group_by_base = set()
		self.agg_list_expr = set()
		self.agg_set_expr = set()
		self.agg_sum_expr = set()
		self.agg_min_expr = set()
		self.agg_max_expr = set()
		self.agg_count_distinct = set()
		
		r_tail = ''
		r_head = ''
		if self.order_text != '':
			order_text_list = self.order_text.split(';')
			for order_l in order_text_list:

				if str_in(' for ', order_l):
					order_t, order_v = split(order_l, ' for ')
				else:
					order_t = order_l
					order_v = self.result_var

				order_t = order_t.strip()
				order_v = order_v.strip()
				if order_v != self.result_var:
					continue

				if str_in(' limit ', order_t):
					order_t, limit_v = split(order_t, ' limit ')
					limit_v =  int(limit_v.strip())
				else:
					limit_v = -1

				reversed = False
				if order_t.lower().endswith('desc'):
					reversed = True
					order_t = order_t[:-len('desc')].strip()
				elif order_t.lower().endswith('asc'):
					order_t = order_t[:-len('asc')].strip()

				if order_t.lower().endswith('desc'):
					reversed = True
					order_t = order_t[:-len('desc')].strip()
				elif order_t.lower().endswith('asc'):
					order_t = order_t[:-len('asc')].strip()

				if order_t in self.var_agg_map.keys():
					r_tail += f"""result_tuple['{self.result_var}'] = sorted(result_tuple['{self.result_var}'], key=lambda l: eval(l['{order_t}']), reverse={reversed})[:{limit_v}]\n"""
				else:
					r_tail += f"""result_tuple['{self.result_var}'] = sorted(result_tuple['{self.result_var}'], key=lambda l: l['{order_t}'], reverse={reversed})[:{limit_v}]\n"""

		if self.current_tok.type == 'STR' or self.current_tok.type == 'EXPR':
			tmp_expr = self.current_tok.value
			if tmp_expr in self.var_agg_map.keys():
				r_tail += f"""if result_tuple['{self.result_var}']: \n"""
				r_tail += f"""    {self.result_var} = eval(result_tuple['{self.result_var}'][0]['{tmp_expr}']) \n"""
				r_tail += f"""else: \n"""
				r_tail += f"""    {self.result_var} = [] \n"""
			else:
				r_tail += f"""if result_tuple['{self.result_var}']: \n"""
				r_tail += f"""    {self.result_var} = result_tuple['{self.result_var}'][0]['{tmp_expr}'] \n"""
				r_tail += f"""else: \n"""
				r_tail += f"""    {self.result_var} = [] \n"""
		else:
			r_tail += f"""for r_tuple in result_tuple['{self.result_var}']:\n"""
			if self.current_tok.value == '{':
				tmp = '{}'
				r_head += f"""{self.result_var} = {tmp}\n"""
				r_tail += "    " + self.parse_result_dict(self.result_var)+"\n"

			if self.current_tok.value == '[':
				r_head += f"""{self.result_var} = []\n"""
				r_tail += "    " + self.parse_result_list(self.result_var)+"\n"
		return r_head, r_tail

	def get_result_value_set(self): 
		def _get_result_value_set_dict():
			self.advance()
			if self.current_tok.type == 'EXPR':
				self.result_value_set.add(self.current_tok.value)
			self.advance()
			if self.current_tok.value == ':':
				self.advance()
				if self.current_tok.type == 'EXPR':
					self.result_value_set.add(self.current_tok.value)
					self.advance()
				elif self.current_tok.value == '[':
					_get_result_value_set_list()
				elif self.current_tok.value == '{':
					_get_result_value_set_dict()
			

		def _get_result_value_set_list():
			self.advance()
			if self.current_tok.value == '{':
				self.advance()
				while self.tok_idx < len(self.tokens) and self.current_tok.value != '}':
					if self.current_tok.type == 'EXPR':
						self.result_value_set.add(self.current_tok.value)
					self.advance()

		self.result_value_set = set()
		if self.current_tok.type == 'STR' or self.current_tok.type == 'EXPR':
			self.result_value_set.add(self.current_tok.value)
		else:
			if self.current_tok.value == '{':
				_get_result_value_set_dict()
			if self.current_tok.value == '[':
				_get_result_value_set_list()

		return self.result_value_set
			


class BodyLexer:
	def __init__(self, fn, text):
		self.fn = fn
		self.text = text
		self.pos = Position(-1, 0, -1, fn, text)
		self.current_char = None
		self.advance()

	def advance(self):
		self.pos.advance(self.current_char)
		self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def make_tokens(self):
		tokens = []
		while self.current_char != None:
			if self.current_char in '\t\n':
				self.advance()
			elif self.current_char in '[]':
				tokens.append(Token("TOKEN", self.current_char))
				self.advance()
			else:
				tokens.append(self.make_expr())
		return tokens

	def make_expr(self):
		id_str = ''
		while self.current_char != None and self.current_char not in '[]':
			# +-*/%^={}()[]:,\t\n':
			id_str += self.current_char
			self.advance()

		tok_type = 'EXPR'
		return Token(tok_type, id_str)

def get_var_access(tokens, var_list, value_list):
	tmp_s = ''
	tmp_c = 0
	i_depend = set()
	var_depend = []
	var_map = {}
	for token in tokens:
		i = token.value
		if i == '[':
			tmp_c += 1
		elif i == ']':
			tmp_c -= 1
		if i in var_list:
			if tmp_c == 1:
				var_map[i] = tmp_s.strip('[')
			var_depend.append(i)
			i_depend.add(i)
		if i in value_list:
			i_depend.add(i)
		tmp_s += i
	return i_depend, var_depend, var_map


def get_unit_access(tokens, var_list, value_list):
	tmp_h = tokens[0].value
	tmp_s = ''
	tmp_c = 0
	i_depend = set()
	access_map = []
	map_flag = False

	if len(tokens) < 3 or tokens[2].value in var_list:
		return i_depend, access_map

	for token in tokens[1:]:
		i = token.value
		if tmp_c > 0:
			tmp_s += i
		if i == '[':
			tmp_c += 1
		elif i == ']':
			tmp_c -= 1
			if tmp_c == 0 and tmp_h != 'range':
				access_map = [tmp_h, tmp_s[0:-1]]
				break
		else:
			if i in value_list or i in var_list:
				i_depend.add(i)
				map_flag = True

	return i_depend, access_map if map_flag else []

def fix_default_format(assign_a):
#a[x|y] a[b[x|y]] a[i][j][x|y] a[i|k][j][x|y] a[b[x|y]|z] a[b[x]|c[y]]
#a[b[x]|c[y]] | a[b[x|y]|c[z]] | a[b[x]|c[y|z]]
	lexer = BodyLexer(None, assign_a)
	tokens = lexer.make_tokens()

	s_curr = ''
	s_stack = []
	for token in tokens:
		i = token.value
		if i == '[':
			if s_curr:
				s_stack.append(s_curr)
				s_curr = i
		elif i == ']':
			s_curr += i
			if '|' in s_curr:
				x,y = s_curr[1:-1].split('|')
				s_curr = f'.get({x}, {y})'

			if s_stack:
				pre_s = s_stack.pop()
				s_curr = pre_s+s_curr
		else:
			s_curr += i
	return s_curr

def check_access_map(access_map_list, check_str):
	match_str_list = []
	tmp_access_map_list = []
	for i in access_map_list:
		if f"{i[0]}[{i[1]}]" in check_str.replace(' ', ''):
			match_str_list.append(i)
		else:
			tmp_access_map_list.append(i)
	con_collect = ''
	if match_str_list:
		con_collect = 'if '
		for i in match_str_list:
			con_collect += f""" {i[1]} in {i[0]}.keys() if isinstance({i[0]}, dict) else {i[1]} in range(len({i[0]})) and """
		con_collect = con_collect[:-4] + ':'
	return con_collect, tmp_access_map_list

class CreateBodyParser:
	def __init__(self, fn, text, var_list, result_value_list):
		i = 1

		while '[_]' in text:
			text = text.replace('[_]', f"[v_{str(i)}]", 1)
			var_list.append('v_'+str(i))
			i+=1
		self.fn = fn
		self.var_list =  var_list
		self.result_value_list = result_value_list

		self.body_text = text

		boundary = ['order by', 'group by', 'where']
		follows = [';']
		query_list = parser_get_query_list(text, boundary, follows)

		self.order_text = ''
		self.group_text = ''
		self.where_text = ''

		for q in query_list:
			if q.lower().startswith('select'):
				self.body_text =  q[len('select '):]
			if q.lower().startswith('order by'):
				self.order_text = q[len('order by '):].strip()
			if q.lower().startswith('group by'):
				self.group_text = q[len('group by '):].strip()
			if q.lower().startswith('where'):
				self.where_text = q[len('where '):]

	def parse(self):
		self.assign_list = list_strip(self.body_text.split(';'))
		self.where_list = list_strip(self.where_text.split(';'))
		self.where_list = [i for i in self.where_list if i !='']
		self.map_list = {}
		self.access_map_list = []
		self.assign_depend = []
		self.cond_depend = []
		self.var_depend = []
		self.value_list = []
		self.group_by_var = set()
		self.var_agg_map = {}
		self.value_depend = {}

		self.assign_list = [fix_default_format(i) for i in self.assign_list]
		self.where_list = [fix_default_format(i) for i in self.where_list]

		def _add_var_depend(new_dep):
			for i in self.var_depend:
				if set(new_dep) <= set(i):
						return
			self.var_depend.append(new_dep)

		def _startwith_agg(s, assign):
			for i in s:
				if assign.strip().lower().startswith(i):
					return i
			return None

		def _value_to_depend():
			self.value_depend = {}

			for i in range(len(self.value_list)):
				self.value_depend[self.value_list[i]] = self.assign_depend[i]

		def _get_depend_all(exprs, depend_list, group_by_var=set()):
			for expr in exprs:
				lexer = BodyLexer(self.fn, expr)
				tokens = lexer.make_tokens()

				for i in range(len(tokens)):
					if tokens[i].value in '[]':
						continue
					a_depend, var_depend, var_map = get_var_access(tokens[i:], self.var_list, self.value_list)
					self.map_list.update(var_map)
					if a_depend:
						self.depend = self.depend.union(a_depend)
					if var_depend:
						_add_var_depend(var_depend)
					a_depend, access_s_map = get_unit_access(tokens, self.var_list, self.value_list)
					if a_depend:
						self.depend = self.depend.union(a_depend)
					if access_s_map and access_s_map not in self.access_map_list:
						self.access_map_list.append(access_s_map)
			depend_list.append(self.depend|group_by_var)


		for assign in self.assign_list:
			self.depend = set()
			import re
			if str_in(' as ', assign):
				assign_ex, assign_value = list_strip(split(assign, ' as '))
				self.value_list.append(assign_value.strip())
			else:
				assign_ex = list_strip([assign])[0]
				assign_value = None

			s = ['collect list', 'collect set', 'count distinct', 'sum', 'min', 'max']

			agg_op = _startwith_agg(s, assign)

			if agg_op is None and str_in(' from ', assign_ex):
				assign_value, assign_ex = split(assign_ex, ' from ')
				self.value_list.append(assign_value.strip())

			group_by_var = set()
			if 	agg_op!= None:
				if str_in(' group by ', assign_ex):
					assign_ex, group_by = split(assign_ex, ' group by ')
					group_by_var = list_strip(group_by.split(','))
					group_by = ','.join(group_by_var)
					group_by_var = set(group_by_var)
					self.var_agg_map[assign_value] = {'op':agg_op, 'group_by': '('+group_by+')'}
				else:
					self.var_agg_map[assign_value] = {'op':agg_op, 'group_by': 'default_group_by'}
					group_by_var = self.group_by_var
				assign_ex = assign_ex.strip()
				assign_ex = strip_operator(assign_ex, s)
				assign_ex = assign_ex.strip()
			else:
				self.group_by_var.add(assign_value)

			assign_ex = assign_ex.replace(' where ', ' ').replace(' WHERE ', ' ')

			assign_expr = list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", assign_ex))
			_get_depend_all(assign_expr, self.assign_depend, group_by_var)

		print("self.assign_depend:", self.assign_depend)
		print("self.value_list:", self.value_list)

		for i in self.var_agg_map.keys():
			group_by = ','.join(list(self.group_by_var))
			if group_by == '':
				group_by = 'default_group_by'
				self.var_agg_map[i]['group_by'] = '('+group_by+')'			
			elif self.var_agg_map[i]['group_by'] == 'default_group_by':
				self.var_agg_map[i]['group_by'] = '('+group_by+')'

		for condition in self.where_list:
			self.depend = set()
			import re

			cond_expr = list_strip(re.split("[+,-,*,/,%,^,!,==,=,(,),' ',',']", condition))

			_get_depend_all(cond_expr, self.cond_depend)

		_value_to_depend()

		print("self.cond_depend:", self.cond_depend)
		print("self.var_depend:", self.var_depend)
		print("self.value_depend:", self.value_depend)
		print("self.map_list:", self.map_list)
		print("self.access_map_list", self.access_map_list)
		print("self.var_agg_map", self.var_agg_map)
		print("self.group_by_var", self.group_by_var)

	def gen_clause(self):
		tmp_var_loop_set = set()
		self.r_tuple = {}
		self.for_loop_list = [(0, """result_tuple = {}""")]
		for r, v_list in self.result_value_list.items():
			self.for_loop_list.append((0, f"""result_tuple['{r}'] = []"""))
		curr_assign_list = [i for i in range(len(self.assign_list))]
		curr_cond_list = [i for i in range(len(self.where_list))]
		offset = 0

		def _add_collect_to_for_loop_list(va, vu_list, offset):
			var_type = self.var_agg_map[va]['op']
			group_by = self.var_agg_map[va]['group_by']
			for vu in vu_list:
				if var_type == 'collect set':
					self.for_loop_list.append((offset, f"""if {vu} not in {va}.setdefault({group_by}, []):"""))
					self.for_loop_list.append((offset+4, f"""{va}[{group_by}].append({vu})"""))
				elif var_type == 'collect list':
					self.for_loop_list.append((offset, f"""{va}.setdefault({group_by}, []).append({vu})"""))
				elif var_type == 'sum':
					self.for_loop_list.append((offset, f"""{va}[{group_by}] = {va}.setdefault({group_by}, 0)+{vu}"""))
				elif var_type == 'min':
					self.for_loop_list.append((offset, f"""{va}[{group_by}] = min({va}.setdefault({group_by}, 0) , {vu})"""))
				elif var_type == 'max':
					self.for_loop_list.append((offset, f"""{va}[{group_by}] = max({va}.setdefault({group_by}, 0) , {vu})"""))
				elif var_type == 'count distinct': #collect list first
					self.for_loop_list.append((offset, f"""if {vu} not in {va}_.setdefault({group_by}, []):"""))
					self.for_loop_list.append((offset+4, f"""{va}_[{group_by}].append({vu})"""))
					self.for_loop_list.append((offset+4, f"""{va}[{group_by}] = {va}.setdefault({group_by}, 0)+1"""))
				else:
					print('error - not supported')


		def _check_group_by_repeat(va, tmp_var_loop_set, offset):
			for g_var, g_val in self.var_agg_map.items():
				if g_val['op'] not in ['sum',  'collect list']:
					continue
				group_by = g_val['group_by']
				group_by_var_list = group_by[1:-1].split(",")

				if va not in group_by_var_list or not set(group_by_var_list) < tmp_var_loop_set:
					continue
				
				group_by_var_depend = set()
				for i in group_by_var_list:
					group_by_var_depend |= self.value_depend[i] & set(self.var_list) 

				g_var_depend = self.value_depend[g_var] & set(self.var_list)
				loop_depend_var = group_by_var_depend & g_var_depend

				check_var = '('+','.join(group_by_var_list + list(loop_depend_var))+')'

				self.for_loop_list.append((offset, f"""if {check_var} in _{g_var}_check:"""))
				self.for_loop_list.append((offset+4, f"""_{g_var}_flag = False"""))
				self.for_loop_list.append((offset, f"""else:"""))
				self.for_loop_list.append((offset+4, f"""_{g_var}_check.append({check_var})"""))
				self.for_loop_list.append((offset+4, f"""_{g_var}_flag = True"""))


		def _put_assignment_clause(curr_assign_list, curr_cond_list, offset):
			new_assign_list = []
			curr_cond_list, offset = _put_where_clause(curr_cond_list, offset)
			for i in curr_assign_list:
				if set(self.assign_depend[i]) <= tmp_var_loop_set:
					if not str_in(' as ', self.assign_list[i]):
						if str_in(' from ', self.assign_list[i]):
							va, _ = split(self.assign_list[i], ' from ')
							vu = va
							for r, v_list in self.result_value_list.items():
								if va in v_list:
									self.r_tuple[r] = self.r_tuple.setdefault(r, '') + f"""'{va}':{va},"""
						continue
					tmp_collect = False
					vu, va = list_strip(split(self.assign_list[i], ' as '))
					vu_if = ''
					if va in self.var_agg_map.keys():
						if str_in(' group by ',vu):
							vu, c_vu = split(vu, ' group by ')
							c_vu = c_vu.split(',')
							for c_v in c_vu:
								c_v = c_v.strip()
								for r, v_list in self.result_value_list.items():
									if c_v not in self.value_list and c_v in v_list:
										self.r_tuple[r] = self.r_tuple.setdefault(r, '') + f"""'{c_v}':{c_v},"""
						vu = vu.strip()
						if str_in(' where ', vu):
							vu, vu_if = split(vu, ' where ')

						vu = strip_operator(vu, ['collect list', 'collect set', 'count distinct',
												 'min', 'max', 'sum'])
						if str_in(' from ', vu):
							vu, _ = split(vu, " from ")
						vu = vu.strip()
						tmp_collect = True
					else:
						if str_in(' where ', vu):
							vu, vu_if = split(vu, " where ")

					check_str, self.access_map_list = check_access_map(self.access_map_list, vu)
					if check_str:
						self.for_loop_list.append((offset, check_str))
						offset += 4

					if tmp_collect:
						if vu_if:
							self.for_loop_list.append((offset, f"""if _{va}_flag == True and {vu_if}:"""))
						else:
							self.for_loop_list.append((offset, f"""if _{va}_flag == True:"""))
						
						_add_collect_to_for_loop_list(va, vu.split('|'), offset+4)
						group_by = self.var_agg_map[va]['group_by']
						self.for_loop_list.append((offset, f"""{va}_group_by_str=str({group_by})"""))
						if ',' in group_by:
							tmp = '{%s_group_by_str}'%va
						else:
							tmp = '"{%s_group_by_str}"'%va
						for r, v_list in self.result_value_list.items():
							if va in v_list:
								if self.var_agg_map[va]['op'] in ['collect set', 'collect list']:
									self.r_tuple[r] = self.r_tuple.setdefault(r, '') + f"""'{va}':f'{va}.get({tmp}, [])',"""
								else:
									self.r_tuple[r] = self.r_tuple.setdefault(r, '') + f"""'{va}':f'{va}.get({tmp}, 0)',"""
					else:
						if vu_if:
							self.for_loop_list.append((offset, f"""if {vu_if}:"""))
							offset += 4
						self.for_loop_list.append((offset, f"""{va} = {vu}"""))
						for r, v_list in self.result_value_list.items():
							if va in v_list:
								self.r_tuple[r] = self.r_tuple.setdefault(r, '') + f"""'{va}':{va},"""
					tmp_var_loop_set.add(va)

					_check_group_by_repeat(va, tmp_var_loop_set, offset)

					curr_cond_list, offset = _put_where_clause(curr_cond_list, offset)
				else:
					new_assign_list.append(i)
			return new_assign_list, curr_cond_list, offset

		def _put_where_clause(curr_cond_list, offset):
			new_cond_list = []
			for i in curr_cond_list:
				if set(self.cond_depend[i]) <= tmp_var_loop_set:
					self.for_loop_list.append((offset, f'if {self.where_list[i]}:'))
					offset += 4
				else:
					new_cond_list.append(i)
			return new_cond_list, offset

		curr_assign_list, curr_cond_list, offset = _put_assignment_clause(curr_assign_list, curr_cond_list, offset)
		for top in self.var_depend:
			for v_key in top:
				v_value = self.map_list[v_key]
				if v_key not in tmp_var_loop_set:
					check_str, self.access_map_list = check_access_map(self.access_map_list, v_value)
					if check_str:
						self.for_loop_list.append((offset, check_str))
						offset += 4
					if v_value.startswith('range'):
						r_value = v_value.replace('[', '(').replace(']', ')')
						self.for_loop_list.append((offset , f'for {v_key} in {r_value}:'))
						offset += 4
					else:
						self.for_loop_list.append((offset, f'for {v_key} in {v_value}.keys() if isinstance({v_value}, dict) else range(len({v_value})):'))
						offset += 4
					for r, v_list in self.result_value_list.items():
						if v_key in v_list:
								self.r_tuple[r] = self.r_tuple.setdefault(r, '') + f"""'{v_key}':{v_key},"""
					tmp_var_loop_set.add(v_key)

					curr_assign_list, curr_cond_list, offset = _put_assignment_clause(curr_assign_list, curr_cond_list, offset)
		for r, v in self.r_tuple.items():
			self.r_tuple[r] = self.r_tuple[r].strip(',')
			self.for_loop_list.append((offset, 'if {'+self.r_tuple[r]+'} not in' + f" result_tuple['{r}']:"))
			self.for_loop_list.append((offset+4, f"result_tuple['{r}']"+'.append({'+self.r_tuple[r]+'})'))
		print("self.for_loop_list:", self.for_loop_list)

		return self.for_loop_list

class UpdateBodyParser:
	def __init__(self, fn, text, var_list):
		i = 1

		while '[_]' in text:
			text = text.replace('[_]', f"[v_{str(i)}]", 1)
			var_list.append("v_"+str(i))
			i+=1
		self.fn = fn
		self.var_list =  var_list

		self.body_text = text[len('set'):]


		boundary = ['where']
		follows = [';']
		query_list = parser_get_query_list(text, boundary, follows)

		self.where_text = ''

		for q in query_list:
			if q.lower().startswith('where'):
				self.where_text = q[len('where '):]

	def parse(self):
		self.assign_list = list_strip(self.body_text.split(';'))
		self.where_list = list_strip(self.where_text.split(';'))
		self.where_list = [i for i in self.where_list if i !='']
		self.map_list = {}
		self.access_map_list = []
		self.assign_depend = []
		self.cond_depend = []
		self.var_depend = []

		self.assign_list = [fix_default_format(i) for i in self.assign_list]
		self.where_list = [fix_default_format(i) for i in self.where_list]

		def _add_var_depend(new_dep):
			for i in self.var_depend:
				if set(new_dep) <= set(i):
						return
			self.var_depend.append(new_dep)

		for assign_val in self.assign_list:
			depend = set()
			import re
			if str_in(' as ', assign_val):
				vu, va = split(assign_val, ' as ')
				assign_expr = list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", vu)) \
							+ list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", va))
			elif str_in(' order by ',assign_val):
				vu, va = split(assign_val,' order by ')
				assign_expr = list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", vu))

			for expr in assign_expr:
				lexer = BodyLexer(self.fn, expr)
				tokens = lexer.make_tokens()

				for i in range(len(tokens)):
					if tokens[i].value in '[]':
						continue
					a_depend, var_depend, var_map = get_var_access(tokens[i:], self.var_list, [])
					self.map_list.update(var_map)
					if a_depend and var_depend:
						depend = depend.union(a_depend)
						_add_var_depend(var_depend)
					a_depend, access_s_map = get_unit_access(tokens, self.var_list, [])
					if a_depend:
						depend = depend.union(a_depend)
					if access_s_map and access_s_map not in self.access_map_list:
						self.access_map_list.append(access_s_map)
			self.assign_depend.append(depend)

		print('self.assign_depend:', self.assign_depend)

		for condition in self.where_list:
			depend = set()
			import re

			cond_expr = list_strip(re.split("[+,-,*,/,%,^,!,==,=,(,),' ',',']", condition))

			for expr in cond_expr:
				lexer = BodyLexer(self.fn, expr)
				tokens = lexer.make_tokens()

				for token in tokens:
					if token.value in self.var_list:
						depend.add(token.value)

			self.cond_depend.append(depend)

		print('self.cond_depend:', self.cond_depend)
		print('self.var_depend:', self.var_depend)
		print('self.map_list:', self.map_list)
		print('self.access_map_list', self.access_map_list)

	def gen_clause(self):
		tmp_var_loop_set = set()
		self.for_loop_list = []
		curr_assign_list = [i for i in range(len(self.assign_list))]
		curr_cond_list = [i for i in range(len(self.where_list))]
		self.var_agg_map = {}

		def _put_assignment_clause(curr_assign_list):
			new_assign_list = []
			for i in curr_assign_list:
				if set(self.assign_depend[i]) <= tmp_var_loop_set:
					if str_in(' as ', self.assign_list[i]):
						vu, va = list_strip(split(self.assign_list[i],' as '))
						for v_i in [vu, va]:
							check_str, self.access_map_list = check_access_map(self.access_map_list, v_i)
							if check_str:
								self.for_loop_list.append(check_str)
						if '|' in va:
							va = vu.replace("|", "+")
						self.for_loop_list.append(f"""{vu} = {va}""")

					if str_in(' order by ', self.assign_list[i]):
						vu, va = list_strip(split(self.assign_list[i],' order by '))
						check_str, self.access_map_list = check_access_map(self.access_map_list, vu)
						k,_=va.strip('{}').split(':')
						if check_str:
							self.for_loop_list.append(check_str)
						self.for_loop_list.append(f"""sorted({vu}, key=lambda _i: _i[{k}])""")
				else:
					new_assign_list.append(i)
			return new_assign_list

		def _put_where_clause(curr_cond_list):
			new_cond_list = []
			for i in curr_cond_list:
				if set(self.cond_depend[i]) <= tmp_var_loop_set:
					self.for_loop_list.append(f'if {self.where_list[i]}:')
				else:
					new_cond_list.append(i)
			return new_cond_list

		curr_assign_list = _put_assignment_clause(curr_assign_list)
		for top in self.var_depend:
			for v_key in top:
				v_value = self.map_list[v_key]
				if v_key not in tmp_var_loop_set:
					curr_assign_list = _put_assignment_clause(curr_assign_list)
					check_str, self.access_map_list = check_access_map(self.access_map_list, v_value)
					if check_str:
						self.for_loop_list.append(check_str)
					if v_value.startswith('range'):
						r_value = v_value.replace('[', '(').replace(']', ')')
						self.for_loop_list.append(
							f'for {v_key} in {r_value}:')
					else:
						self.for_loop_list.append(f"for {v_key} in {v_value}.keys() if isinstance({v_value}, dict) else range(len({v_value})):")
					tmp_var_loop_set.add(v_key)

					curr_cond_list = _put_where_clause(curr_cond_list)

					curr_assign_list = _put_assignment_clause(curr_assign_list)

					curr_cond_list = _put_where_clause(curr_cond_list)

		print("self.var_agg_map", self.var_agg_map)
		print("self.for_loop_list:", self.for_loop_list)

		return self.for_loop_list

def list_strip(l):
	return [i.strip("' ', '\n', '\t'") for i in l]

def FromPaser(fn, text):
	text = strip_prefix(text, ['read'])
	l = list_strip(text.split(","))
	r = ''
	for fl in l:
		f, s = split(fl, ' as ')
		r += f'{s} = read_json_file("{f}");'
	return r

def ToPaser(fn, text):
	text = strip_prefix(text, ['write'])
	text_list = text.split(',')
	r = ''
	for text_t in text_list:
		f, d = split(text_t, ' from ')
		f = f.strip()
		d = d.strip()
		r += f'\nwrite_json_file("{f}", {d});'
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
	r_code = ''
	for l in body_loop:
		r_code += offset_space + f'{l}\n'
		if l.startswith('for') or l.startswith('if'):
			offset_space += '    '

	return r_code,result_var

def find_boundary(text, boundary, follows):
	tmp_text = text.strip("' ', '\n', '\t'")[1:]
	body_end = -1
	for b in boundary:
		next = tmp_text.find(b)
		if next == -1:
			next = tmp_text.find(b.upper())
		if next != -1 and tmp_text[next-1] in [' ', '\n', '\t', ';'] \
			and tmp_text[next+len(b)] in [' ', '\n', '\t', ';']:
			if not follows or tmp_text[:next-1].strip("' ', '\n', '\t'")[-1] in follows:
				if (body_end == -1 or next < body_end):
					body_end = next
	return body_end

def parser_get_query_list(text, boundary, follows=[]):
	text = text.strip("' ', '\n', '\t'")

	query_list = []
	while text:
		body_end = find_boundary(text,boundary, follows)
		if body_end == -1:
			query_list.append(text.strip("' ', '\n', '\t', ';'"))
			text = ''
		else:
			body_end += 1
			query_list.append(text[0:body_end].strip("' ', '\n', '\t', ';'"))
			text = text[body_end:].strip("' ', '\n', '\t', ';'")
	return query_list

def QueryParser(fn, text):
	boundary = ['create', 'with', 'read', 'write', 'update']
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
	exec(result, globals())
	if result_v:
		return globals()[result_v]


def startswith_list(s, l):
	for i in l:
		if  s.strip().startswith(i):
			return i
	return ''

import sys

def main():

	def _startswith_list(s, l):
		for i in l:
			if  s.strip().lower().startswith(i):
				return i.lower()
		return ''
	
	def _pass_define(line):
		define_list = list_strip(line.split(','))
		for d in define_list:
			if not d:
				continue
			k, v = d.strip().split('=')
			path_define[k.strip()] = v.strip()
	
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
								for k,v in path_define.items():
									l = l.replace(k, v)		
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
						for k,v in path_define.items():
							l = l.replace(k, v)		
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
