# Author: Hong Xiao
# This program translates code in KiwiSpec to python and executes the python code.

from util import *
from kiwi_util import *

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


	def parse_disc(self, head, r_tail):
		self.advance()
		tmp_string = ''
		while self.tok_idx < len(self.tokens) and self.current_tok.value != '}':
			if self.current_tok.type == 'STR':
				tmp_string += self.current_tok.value
				self.advance()
			elif self.current_tok.type == 'EXPR':
				if self.current_tok.value in self.var_agg_map.keys():
					tmp_string += f"""eval(_kiwi_r_tuple['{self.current_tok.value}'])"""
				else:
					tmp_string += f"""_kiwi_r_tuple['{self.current_tok.value}']"""
				self.advance()
			else:
				tmp_string += self.current_tok.value
				self.advance()

			if self.current_tok.value == ':':
				tmp_string += self.current_tok.value
				self.advance()
				if self.current_tok.type == 'EXPR':
					if self.current_tok.value in self.var_agg_map.keys():
						tmp_string += f"""eval(_kiwi_r_tuple['{self.current_tok.value}'])"""
					else:
						tmp_string += f"""_kiwi_r_tuple['{self.current_tok.value}']"""
				self.advance()

		return  tmp_string

	def get_limit(self):
		cur_tidx = self.tok_idx
		limit = -1
		while cur_tidx < len(self.tokens) and self.tokens[cur_tidx].value != ']':
			if self.tokens[cur_tidx].value.lower() == 'limited':
				limit = self.tokens[cur_tidx+1].value
			cur_tidx +=1
		return int(limit)
	
	def parse_result_list(self, head, offset=''):
		r_tail = ''
		self.advance()
		limit = self.get_limit()

		if self.current_tok.value == '{':
			tmp_string = self.parse_disc(head, r_tail)
			tmp_string = '{' + tmp_string + '}'
			if limit > 0:
				r_tail += offset + f"""if len({head}) < {limit}: {head}.append({tmp_string})\n"""
			else:
				r_tail += offset + f"""{head}.append({tmp_string})\n"""

		elif self.current_tok.type == 'EXPR':
			if self.current_tok.value in self.var_agg_map.keys():
				r_tail += offset + f"""_{head} = eval(_kiwi_r_tuple['{self.current_tok.value}'])\n"""
				if limit > 0:
					r_tail += offset + f"""if _{head} and len({head}) < {limit}:{head}.append(_{head})"""
				else:
					r_tail += offset + f"""if _{head}: {head}.append(_{head})"""
			else:
				r_tail += offset + f"""_{head} = _kiwi_r_tuple['{self.current_tok.value}']\n"""
				if limit > 0:
					r_tail += offset + f"""if _{head} and len({head}) < {limit}:{head}.append(_{head})"""
				else:
					r_tail += offset + f"""if _{head}: {head}.append(_{head})"""
			self.advance()
		return r_tail

	def parse_result_dict(self, head):
		self.advance()
		tmp_values = {}
		if self.current_tok.type == 'STR':
			tmp_values["key"]=self.current_tok.value
		elif self.current_tok.type == 'EXPR':
			if self.current_tok.value in self.var_agg_map.keys():
				tmp_values["key"]=f"""eval(_kiwi_r_tuple['{self.current_tok.value}'])"""
			else:
				tmp_values["key"]=f"""_kiwi_r_tuple['{self.current_tok.value}']"""

		self.advance()
		r_tail = ''
		if self.current_tok.value == ':':
			self.advance()
			if self.current_tok.type == 'EXPR':
				if self.current_tok.value in self.var_agg_map.keys():
					val = f"""eval(_kiwi_r_tuple['{self.current_tok.value}'])"""
				else:
					val =  f"""_kiwi_r_tuple['{self.current_tok.value}']"""
				tmp_values["val"] = val
				self.advance()
				r_tail+=f"""{head}[{tmp_values["key"]}]={tmp_values["val"]}"""
			elif self.current_tok.value == '[':
				tmp_result = self.parse_result_list(f"""{head}.setdefault({tmp_values["key"]}, [])""")
				# r_tail+=f"""{head}[{tmp_values["key"]}]={tmp_result}"""   
				r_tail+=f"""{tmp_result}"""          
			elif self.current_tok.value == '{':
				# if the key inside "{"" is expr 
				# e.g self.advance() if self.current_tok.type == 'EXPR':
				# tmp = '{}'
				# r_tail = self.parse_result_dict(f"""{head}.setdefault({tmp_values["key"]}, {tmp})""")
				# if the key inside "{"" is str
				# e.g self.advance() if self.current_tok.type == 'STR':
				tmp_string = self.parse_disc(head, r_tail)
				tmp_string = '{' + tmp_string + '}'
				r_tail = f"""{head}[{tmp_values["key"]}] = {tmp_string}"""
			else:
				print("error - format")

		return r_tail

	def preparse(self):
		r_head ="init_util()\n"
		r_head += '_kiwi_default_group_by="_kiwi_default_group_by"\n'
		for _k in self.var_agg_map.keys():
			if self.var_agg_map[_k]["op"] in ['collect list', 'collect set', 'count distinct', 'sum', 'min', 'max']:
				tmp = '{}'
				r_head += f"""{_k} = {tmp}\n"""
				r_head += f"""_{_k}_kiwi_check = []\n"""
				r_head += f"""_{_k}_kiwi_flag = True\n"""
			if self.var_agg_map[_k]["op"] == 'count distinct':
				tmp = '{}'
				r_head += f"""{_k}_ = {tmp}\n"""
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
					r_tail += f"""_kiwi_result_tuple['{self.result_var}'] = sorted(_kiwi_result_tuple['{self.result_var}'], key=lambda l: eval(l['{order_t}']), reverse={reversed})[:{limit_v}]\n"""
				else:
					r_tail += f"""_kiwi_result_tuple['{self.result_var}'] = sorted(_kiwi_result_tuple['{self.result_var}'], key=lambda l: l['{order_t}'], reverse={reversed})[:{limit_v}]\n"""

		if self.current_tok.type == 'STR' or self.current_tok.type == 'EXPR':
			tmp_expr = self.current_tok.value
			if tmp_expr in self.var_agg_map.keys():
				r_tail += f"""if _kiwi_result_tuple['{self.result_var}']: \n"""
				r_tail += f"""    {self.result_var} = eval(_kiwi_result_tuple['{self.result_var}'][0]['{tmp_expr}']) \n"""
				r_tail += f"""else: \n"""
				r_tail += f"""    {self.result_var} = [] \n"""
			else:
				r_tail += f"""if _kiwi_result_tuple['{self.result_var}']: \n"""
				r_tail += f"""    {self.result_var} = _kiwi_result_tuple['{self.result_var}'][0]['{tmp_expr}'] \n"""
				r_tail += f"""else: \n"""
				r_tail += f"""    {self.result_var} = [] \n"""
		else:
			r_tail += f"""for _kiwi_r_tuple in _kiwi_result_tuple['{self.result_var}']:\n"""
			if self.current_tok.value == '{':
				tmp = '{}'
				r_head += f"""{self.result_var} = {tmp}\n"""
				r_tail += "    " + self.parse_result_dict(self.result_var)+"\n"

			if self.current_tok.value == '[':
				r_head += f"""{self.result_var} = []\n"""
				r_tail += self.parse_result_list(self.result_var, "    ")+"\n"
		return r_head, r_tail

	def get_result_value_set(self): 

		self.result_value_set = set()

		if self.current_tok.type == 'STR' or self.current_tok.type == 'EXPR':
			self.result_value_set.add(self.current_tok.value)
		else:
			self.advance()
			while self.tok_idx < len(self.tokens):
				if self.current_tok.type == 'EXPR':
						self.result_value_set.add(self.current_tok.value)
				self.advance()

		return self.result_value_set		



