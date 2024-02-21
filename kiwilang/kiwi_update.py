# Author: Hong Xiao
# This program translates code in KiwiSpec to python and executes the python code.

from util import *
from kiwi_util import *

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
			for _i in self.var_depend:
				if set(new_dep) <= set(_i):
						return
			self.var_depend.append(new_dep)

		for assign_val in self.assign_list:
			depend = set()
			import re
			if str_in(' as ', assign_val):
				vu, va = split(assign_val, ' as ')
				assign_expr = list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", vu)) \
							+ list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", va))
			elif str_in(' from ',assign_val):
				_, vu = split(assign_val,' from ')
				assign_expr = list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", vu))
			elif str_in(' order by ',assign_val):
				vu, va = split(assign_val,' order by ')
				assign_expr = list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", vu))

			for expr in assign_expr:
				lexer = BodyLexer(self.fn, expr)
				tokens = lexer.make_tokens()

				for _i in range(len(tokens)):
					if tokens[_i].value in '[]':
						continue
					a_depend, var_depend, var_map, access_s_map = get_access_maps(tokens, self.var_list, [])

					self.map_list.update(var_map)
					if a_depend:
						depend = depend.union(a_depend)
					if var_depend:
						_add_var_depend(var_depend)

					for access_map in access_s_map:
						if access_map and access_map not in self.access_map_list:
							self.access_map_list.append(access_map)
					
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
			for _i in curr_assign_list:
				if set(self.assign_depend[_i]) <= tmp_var_loop_set:
					if str_in(' as ', self.assign_list[_i]):
						vu, va = list_strip(split(self.assign_list[_i],' as '))
						for v_i in [va]:
							check_str, self.access_map_list = check_access_map(self.access_map_list, v_i)
							if check_str:
								self.for_loop_list.append(check_str)
						if '|' in va:
							va = vu.replace("|", "+")
						self.for_loop_list.append(f"""{vu} = {va}""")

					if str_in(' order by ', self.assign_list[_i]):
						vu, va = list_strip(split(self.assign_list[_i],' order by '))
						check_str, self.access_map_list = check_access_map(self.access_map_list, vu)
						_k,_=va.strip('{}').split(':')
						if check_str:
							self.for_loop_list.append(check_str)
						self.for_loop_list.append(f"""sorted({vu}, key=lambda _i: _i[{_k}])""")
				else:
					new_assign_list.append(_i)
			return new_assign_list

		def _put_where_clause(curr_cond_list):
			new_cond_list = []
			for _i in curr_cond_list:
				if set(self.cond_depend[_i]) <= tmp_var_loop_set:
					self.for_loop_list.append(f'if {self.where_list[_i]}:')
				else:
					new_cond_list.append(_i)
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
