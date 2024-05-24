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

		boundary = ['set', 'where']
		follows = [';']
		query_list = parser_get_query_list(text, boundary, follows)

		self.where_text = ''

		for q in query_list:
			if q.lower().startswith('set'):
				self.body_text =  q[len('set '):]

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

		self.assign_list = [fix_default_format(i).replace('\n', ' ') for i in self.assign_list]
		self.where_list = ['('+fix_default_format(i).replace('\n', ' ')+')' for i in self.where_list]
		
		def _add_var_depend(new_dep, access):
			if 'where' == access:
				t_new_dep = set(new_dep)
				for _i in new_dep:
					t_new_dep = t_new_dep - set(_i)
				f_new_dep = []
				for _i in new_dep:
					if _i in t_new_dep:
						f_new_dep.append(_i)	
				self.where_var_depend.append(f_new_dep)
			else:
				for _i in self.var_depend:
					if set(new_dep) <= set(_i):
							return
				self.var_depend.append(new_dep)


		def _get_all_maps(exprs, depend_list, access=''):
			t_map_list = {}
			t_depend = set()

			lexer = BodyLexer(self.fn, exprs)
			tokens = lexer.make_tokens()
			for token in tokens:
				all_depend, var_depend, var_map, access_s_map = get_access_maps(token, self.var_list, [], [])
				
				if 'where' == access:
					for _k, _v in var_map.items():
						if _k not in self.map_list.keys():
							t_map_list[_k] = _v
				else:
					for _k, _v in var_map.items():
						if _k not in self.map_list.keys():
							self.map_list[_k] = _v
				
				if all_depend:
					if 'where' == access:
						for where_d in all_depend:
							if where_d in self.map_list.keys():
								t_depend.add(where_d)
					else:
						t_depend = t_depend.union(all_depend)

				if var_depend:
					_add_var_depend(var_depend, access)

				for access_map in access_s_map:
					if access_map and access_map not in self.access_map_list:
						self.access_map_list.append(access_map)
			
			if 'where' == access:
				self.where_map_list.append(t_map_list)

			depend_list.append(t_depend)

		for assign_val in self.assign_list:
			depend = set()
			import re
			match_c = 0
			if str_in(' as ', assign_val):
				assign_expr =assign_val
				match_c += 1
			if str_in(' from ',assign_val):
				_, vu = split(assign_val,' from ')
				assign_expr = vu
				match_c += 1
			if str_in(' order by ',assign_val):
				vu, va = split(assign_val,' order by ')
				assign_expr = vu
				match_c += 1
			if str_in(' delete',assign_val):
				i_d = assign_val.find(' delete', 0)
				assign_expr = assign_val[:i_d]
				match_c += 1

			if match_c == 0 or match_c > 1:
				print(f'\nError: {assign_val}\n')
				print('The right clause for UPDATE is:')
				print('v1 AS v2;')
				print('v1 ORDER BY v2:DESC;')
				print('v1 DELETE;\n')
				print('And separated by ";"\n')
				raise
			_get_all_maps(assign_expr, self.assign_depend)

		print('self.assign_depend:', self.assign_depend)


		self.where_map_list = []
		self.where_access_map_list = []
		self.cond_depend = []
		self.where_var_depend = []

		for condition in self.where_list:
			_get_all_maps(condition, self.cond_depend, access='where')

		print("self.cond_depend:", self.cond_depend)
		print("self.var_depend:", self.var_depend)
		print("self.where_var_depend:", self.where_var_depend)
		print("self.map_list:", self.map_list)
		print("self.where_map_list:", self.where_map_list)
		print("self.access_map_list", self.access_map_list)
		print("self.where_access_map_list", self.where_access_map_list)


	def gen_clause(self):
		tmp_var_loop_set = set()
		self.for_loop_list = []
		curr_assign_list = [i for i in range(len(self.assign_list))]
		curr_cond_list = [i for i in range(len(self.where_list))]
		self.var_agg_map = {}

		def _put_assignment_clause(curr_assign_list, curr_cond_list):
			new_assign_list = []
			curr_cond_list = _put_where_clause(curr_cond_list)
			for _i in curr_assign_list:
				if set(self.assign_depend[_i]) <= tmp_var_loop_set:
					i_d = self.assign_list[_i].find(' delete', 0)
					if i_d != -1:
						va = self.assign_list[_i][:i_d]
						check_str, self.access_map_list = check_access_map(self.access_map_list, va)
						if check_str:
							self.for_loop_list.append(check_str)
						self.for_loop_list.append(f"""del {va}""")

					if str_in(' as ', self.assign_list[_i]):
						vu, va = list_strip(split(self.assign_list[_i],' as '))

						check_str, self.access_map_list = check_access_map(self.access_map_list, va)
						if check_str:
							self.for_loop_list.append(check_str)
						if '|' in va:
							va = vu.replace("|", "+")
						self.for_loop_list.append(f"""{vu} = {va}""")

					if str_in(' order by ', self.assign_list[_i]):
						vu, va = list_strip(split(self.assign_list[_i],' order by '))
						check_str, self.access_map_list = check_access_map(self.access_map_list, vu)
						if ':' in va:
							_k, _o=va.strip('{}').split(':')
							order_s = "reverse=False"
							if _o == 'DESC':
								order_s = "reverse=True"
						else:
							order_s = "reverse=False"
						if check_str:
							self.for_loop_list.append(check_str)
						self.for_loop_list.append(f"""{vu} = sorted({vu}, key=lambda _i: _i[{_k}], {order_s})""")
				else:
					new_assign_list.append(_i)
			return new_assign_list, curr_cond_list

		def _put_where_clause(curr_cond_list):
			new_cond_list = []
			for _i in curr_cond_list:
				if set(self.cond_depend[_i]) <= tmp_var_loop_set:
					check_str, self.access_map_list = check_access_map(self.access_map_list, self.where_list[_i])
					if check_str:
						t_check_str =  check_str.strip(':')
						self.for_loop_list.append(f"""{t_check_str} and {self.where_list[_i]}:""")
					else:
						self.for_loop_list.append(f'if {self.where_list[_i]}:')
				else:
					new_cond_list.append(_i)
			return new_cond_list

		curr_assign_list, curr_cond_list = _put_assignment_clause(curr_assign_list, curr_cond_list)
		for top in self.var_depend:
			for v_key in top:
				v_value = self.map_list[v_key]
				if v_key not in tmp_var_loop_set:
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

					curr_assign_list, curr_cond_list = _put_assignment_clause(curr_assign_list, curr_cond_list)
					
		print("self.var_agg_map", self.var_agg_map)
		print("self.for_loop_list:", self.for_loop_list)

		return self.for_loop_list
