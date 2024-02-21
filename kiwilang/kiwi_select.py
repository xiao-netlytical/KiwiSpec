# Author: Hong Xiao
# This program translates code in KiwiSpec to python and executes the python code.

from util import *
from kiwi_util import *

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
		query_list = parser_get_query_list(text, boundary, follows, True)

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
		self.where_map_list = []
		self.access_map_list = []
		self.where_access_map_list = []
		self.assign_depend = []
		self.cond_depend = []
		self.var_depend = []
		self.where_var_depend = []
		self.value_list = []
		self.group_by_var = set()
		self.var_agg_map = {}
		self.value_depend = {}

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

		def _startwith_agg(s, assign):
			for _i in s:
				if assign.strip().lower().startswith(_i):
					return _i
			return None

		def _value_to_depend():
			self.value_depend = {}

			for _i in range(len(self.value_list)):
				self.value_depend[self.value_list[_i]] = self.assign_depend[_i]

		def _get_all_maps(exprs, depend_list, group_by_var=set(), exclude_list=[], access=''):
			t_map_list = {}
			t_depend = set()
			for expr in exprs:
				lexer = BodyLexer(self.fn, expr)
				tokens = lexer.make_tokens()

				all_depend, var_depend, var_map, access_s_map = get_access_maps(tokens, self.var_list, self.value_list, exclude_list)
				
				if 'where' == access:
					for _k, _v in var_map.items():
						if _k not in self.map_list.keys():
							t_map_list[_k] = _v
				else:
					self.map_list.update(var_map)
				
				if all_depend:
					if 'where' == access:
						for where_d in all_depend:
							if where_d in self.map_list.keys() or where_d in self.value_list:
								t_depend.add(where_d)
					else:
						t_depend = t_depend.union(all_depend)

				if var_depend:
					_add_var_depend(var_depend, access)

				for access_map in access_s_map:
					if 'where' == access:
						if access_map and access_map not in self.where_access_map_list:
							self.where_access_map_list.append(access_map)
					elif access != 'eval':
						if access_map and access_map not in self.access_map_list:
							self.access_map_list.append(access_map)
			
			if 'where' == access:
				self.where_map_list.append(t_map_list)

			depend_list.append(t_depend|group_by_var)

		for assign in self.assign_list:
			exclude_list = []
			access = ''
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
					if group_by.lower() == 'none':
						group_by_var = set()
						group_by = 'NONE'
					self.var_agg_map[assign_value] = {'op':agg_op, 
									   'group_by': '('+group_by+')',
									   'agg_op': 'aggregate'}

				elif str_in(' extend by ', assign_ex):
					assign_ex, group_by = split(assign_ex, ' extend by ')
					group_by_var = list_strip(group_by.strip( "')','('").split(','))
					group_by = group_by.strip()
					group_by_var = set(group_by_var)
					if group_by.lower() == 'none':
						group_by_var = set()
						group_by = 'NONE'
					self.var_agg_map[assign_value] = {'op':agg_op, 
									   'group_by': group_by,
									   'agg_op': 'extend'}

				else:
					self.var_agg_map[assign_value] = {'op':agg_op, 
									   'group_by': '_kiwi_default_group_by',
									   'agg_op': 'aggregate'}
					group_by_var = self.group_by_var
				assign_ex = strip_operator(assign_ex.strip(), s)
				assign_ex = assign_ex.strip()
			elif str_in('collect eval', assign_ex):
				access = 'eval'
				if str_in(' group by ', assign_ex):
					assign_ex, group_by = split(assign_ex, ' group by ')
					exclude_list = list_strip(group_by.split(','))
				assign_ex = strip_operator(assign_ex.strip(), ['collect eval'])
				assign_ex_list = assign_ex.split(':')
				local_assign_ex = assign_ex_list[1]
				local_assign_expr = list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", local_assign_ex))
				var_map_list = {}
				for expr in local_assign_expr:
					lexer = BodyLexer(self.fn, expr)
					tokens = lexer.make_tokens()
					_, _, var_map, _ = get_access_maps(tokens, self.var_list, self.value_list)
					for _k,_v in var_map.items():
						if _k in group_by:
							var_map_list[_k] = _v
				self.var_agg_map[assign_value] = {'op':'collect eval',
									'group_by': var_map_list,
									'agg_op': 'eval'}

				local_ex = assign_ex_list[0]
				local_expr = list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", local_ex))

				for expr in local_expr:
					lexer = BodyLexer(self.fn, expr)
					tokens = lexer.make_tokens()
				
					_, _, _,  access_s_map = get_access_maps(tokens, self.var_list, self.value_list)
					for access_map in access_s_map:
						if access_map and access_map not in self.access_map_list:
							self.access_map_list.append(access_map)

			else:
				self.group_by_var.add(assign_value)

			assign_ex = assign_ex.replace(' where ', ' ').replace(' WHERE ', ' ')

			assign_expr = list_strip(re.split("[+,-,*,/,%,^,!,=,(,),' ',',','{','}']", assign_ex))
			_get_all_maps(assign_expr, self.assign_depend, group_by_var, exclude_list, access)

		print("self.assign_depend:", self.assign_depend)
		print("self.value_list:", self.value_list)

		for _i in self.var_agg_map.keys():
			group_by = ','.join(list(self.group_by_var))
			if self.var_agg_map[_i]['group_by'] == '(NONE)' or group_by == '':
				group_by = '_kiwi_default_group_by'
				self.var_agg_map[_i]['group_by'] = '('+group_by+')'			
			elif self.var_agg_map[_i]['group_by'] == '_kiwi_default_group_by':
				self.var_agg_map[_i]['group_by'] = '('+group_by+')'

		self.negate_sub_logic = []
		for condition in self.where_list:
			cond_expr = list_strip(re.split("[+,-,*,/,%,^,!,==,=,(,),' ',',']", condition))
			_get_all_maps(cond_expr, self.cond_depend, access='where')

		# merge condition with 'and' in where_list if they share some local vars
		
		cond_depend = {}
		_c = 0
		for condition in self.where_list:
			cond_depend[condition] = set(self.where_map_list[_c].keys())
			_c+=1
		
		self.where_list = []
		def popup_first_item(cond):
			vr = list(cond.keys())[0]
			ex = cond[vr]
			del cond[vr]
			return vr, ex
		
		while (cond_depend):
			t_cong, t_vars = popup_first_item(cond_depend)

			first_c = t_cong
			first_vars = t_vars
			t_cond_depend = {}
			for d_c, d_set in cond_depend.items():
				if t_vars & d_set:
					first_c = first_c +' and '+ d_c
					first_vars = first_vars.union(d_set)
				else:
					t_cond_depend[d_c] = d_set
			
			cond_depend = t_cond_depend
			self.where_list.append(first_c)

		# recalculate where_map_list
		self.where_map_list = []
		self.where_access_map_list = []
		self.cond_depend = []
		self.where_var_depend = []

		for condition in self.where_list:
			cond_expr = list_strip(re.split("[+,-,*,/,%,^,!,==,=,(,),' ',',']", condition))
			_get_all_maps(cond_expr, self.cond_depend, access='where')
			self.negate_sub_logic.append(get_negate_var_depend(condition, self.where_map_list[-1].keys()))

		_value_to_depend()

		print("self.cond_depend:", self.cond_depend)
		print("self.var_depend:", self.var_depend)
		print("self.where_var_depend:", self.where_var_depend)
		print("self.value_depend:", self.value_depend)
		print("self.map_list:", self.map_list)
		print("self.where_map_list:", self.where_map_list)
		print("self.access_map_list", self.access_map_list)
		print("self.where_access_map_list", self.where_access_map_list)
		print("self.negate_sub_logic", self.negate_sub_logic)
		print("self.var_agg_map", self.var_agg_map)
		print("self.group_by_var", self.group_by_var, "\n\n")

	def gen_clause(self):
		tmp_var_loop_set = set()
		self.r_tuple = {}
		self.for_loop_list = [(0, """_kiwi_result_tuple = {}""")]
		for r, v_list in self.result_value_list.items():
			self.for_loop_list.append((0, f"""_kiwi_result_tuple['{r}'] = []"""))
		curr_assign_list = list(range(len(self.assign_list)))
		curr_cond_list = list(range(len(self.where_list)))
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

		def _add_extend_to_for_loop_list(va, vus, offset):
			var_type = self.var_agg_map[va]['op']
			group_by = self.var_agg_map[va]['group_by']
			vu_list = "["+vus.replace('|', ',')+"]"
			self.for_loop_list.append((offset, f"""extend_by = {group_by}"""))
			self.for_loop_list.append((offset, """collect_by = """+ vu_list))
			self.for_loop_list.append((offset, """collect_by.append(extend_by)"""))
			self.for_loop_list.append((offset,f"""for var in collect_by:"""))
			self.for_loop_list.append((offset,f"""    if var not in {va}.setdefault(var, []):"""))
			self.for_loop_list.append((offset,f"""         {va}[var].append(var)"""))
			self.for_loop_list.append((offset,f"""    if var != extend_by:"""))
			self.for_loop_list.append((offset,f"""        if var not in {va}.setdefault(extend_by, []):"""))
			self.for_loop_list.append((offset,f"""            {va}[extend_by].extend({va}[var])"""))
			self.for_loop_list.append((offset,f"""        for var_items in {va}[var]:"""))
			self.for_loop_list.append((offset,f"""            {va}[var_items] = {va}[extend_by]"""))
				
		def _check_group_by_repeat(va, tmp_var_loop_set, offset):
			for g_var, g_val in self.var_agg_map.items():
				if g_val['op'] not in ['sum',  'collect list']:
					continue
				group_by = g_val['group_by']
				group_by_var_list = group_by[1:-1].split(",")

				if va not in group_by_var_list or not set(group_by_var_list) < tmp_var_loop_set:
					continue
				
				group_by_var_depend = set()
				for _i in group_by_var_list:
					group_by_var_depend |= self.value_depend[_i] & set(self.var_list) 

				g_var_depend = self.value_depend[g_var] & set(self.var_list)
				loop_depend_var = group_by_var_depend & g_var_depend

				check_var = '('+','.join(group_by_var_list + list(loop_depend_var))+')'

				self.for_loop_list.append((offset, f"""if {check_var} in _{g_var}_kiwi_check:"""))
				self.for_loop_list.append((offset+4, f"""_{g_var}_kiwi_flag = False"""))
				self.for_loop_list.append((offset, f"""else:"""))
				self.for_loop_list.append((offset+4, f"""_{g_var}_kiwi_check.append({check_var})"""))
				self.for_loop_list.append((offset+4, f"""_{g_var}_kiwi_flag = True"""))


		def _put_assignment_clause(curr_assign_list, curr_cond_list, offset):
			new_assign_list = []
			curr_cond_list, offset = _put_where_clause(curr_cond_list, offset)
			for _i in curr_assign_list:
				if set(self.assign_depend[_i]) <= tmp_var_loop_set:
					if not str_in(' as ', self.assign_list[_i]):
						if str_in(' from ', self.assign_list[_i]):
							va, _ = split(self.assign_list[_i], ' from ')
							vu = va
							for r, v_list in self.result_value_list.items():
								if va in v_list:
									self.r_tuple[r] = self.r_tuple.setdefault(r, '') + f"""'{va}':{va},"""
						continue
					tmp_collect = False
					vu, va = list_strip(split(self.assign_list[_i], ' as '))
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
						if str_in(' extend by ',vu):
							vu, c_vu = split(vu, ' extend by ')
							c_vu = c_vu.strip( "')','('").split(',')
							for c_v in c_vu:
								c_v = c_v.strip()
								for r, v_list in self.result_value_list.items():
									if c_v not in self.value_list and c_v in v_list:
										self.r_tuple[r] = self.r_tuple.setdefault(r, '') + f"""'{c_v}':{c_v},"""
						vu = vu.strip()
						if str_in(' where ', vu):
							vu, vu_if = split(vu, ' where ')

						vu = strip_operator(vu.strip(), ['collect list', 'collect set', 'count distinct',
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
						def put_collect_aggregate():
							if vu_if:
								self.for_loop_list.append((offset, f"""if _{va}_kiwi_flag == True and {vu_if}:"""))
							else:
								self.for_loop_list.append((offset, f"""if _{va}_kiwi_flag == True:"""))
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

						def put_collect_extend():
							if vu_if:
								self.for_loop_list.append((offset, f"""if _{va}_kiwi_flag == True and {vu_if}:"""))
							else:
								self.for_loop_list.append((offset, f"""if _{va}_kiwi_flag == True:"""))
							_add_extend_to_for_loop_list(va, vu, offset+4)
							group_by = self.var_agg_map[va]['group_by']
							self.for_loop_list.append((offset, f"""{va}_group_by_str=str({group_by})"""))
							if ',' in group_by:
								tmp = '{%s_group_by_str}'%va
							else:
								tmp = '"{%s_group_by_str}"'%va
							for r, v_list in self.result_value_list.items():
								if va in v_list:
									eval_str =  f"""{va}[{tmp}] if {va}.get({tmp}, []) and {tmp} == {va}[{tmp}][0] else []"""
									self.r_tuple[r] = self.r_tuple.setdefault(r, '') + f"""'{va}':f'{eval_str}',"""

						def put_collect_eval():
							local_offset=offset
							self.for_loop_list.append((local_offset, f"{va} = False"))
							exs = strip_operator(vu.strip(), ['collect eval'])
							assign_ex_list = exs.split(':')
							logic_ex = assign_ex_list[0]
							input_p = assign_ex_list[1]
							logic_ex = logic_ex.replace('\n', ' ')
							input_p = input_p.replace('\n', ' ')
							if logic_ex.strip().startswith('"'):
								self.for_loop_list.append((local_offset, f"""_logic_ex = {logic_ex}"""))
							else:
								self.for_loop_list.append((local_offset, f"""_logic_ex = {logic_ex}"""))
								# self.for_loop_list.append((local_offset, f"""_logic_ex = f'{{{logic_ex}}}'"""))
							self.for_loop_list.append((local_offset, f"""{va} = collect_eval(_logic_ex, '{input_p}', {self.var_agg_map[va]['group_by']})"""))

						if self.var_agg_map[va]['agg_op'] == 'aggregate':
							put_collect_aggregate()
						elif self.var_agg_map[va]['agg_op'] == 'extend':
							put_collect_extend()
						elif self.var_agg_map[va]['agg_op'] == 'eval':
							put_collect_eval()
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
					new_assign_list.append(_i)
			return new_assign_list, curr_cond_list, offset

		def _put_where_clause(curr_cond_list, offset):
			new_cond_list = []
			for _i in curr_cond_list:
				if set(self.cond_depend[_i]) <= tmp_var_loop_set:
					t_map_list = self.where_map_list[_i]
					self.for_loop_list.append((offset, f'con_var_dep_input = {t_map_list}'))
					t_negate = self.negate_sub_logic[_i]
					self.for_loop_list.append((offset, f'negate_input = {t_negate}'))
					t_where_string = f'{self.where_list[_i]}'
					t_where_string = t_where_string.replace('\n', '')
					self.for_loop_list.append((offset, f"""if execute_logic('{t_where_string}', con_var_dep_input, '', negate_input):"""))
					offset += 4
				else:
					new_cond_list.append(_i)
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
			self.for_loop_list.append((offset, 'if {'+self.r_tuple[r]+'} not in' + f" _kiwi_result_tuple['{r}']:"))
			self.for_loop_list.append((offset+4, f"_kiwi_result_tuple['{r}']"+'.append({'+self.r_tuple[r]+'})'))
		print("self.for_loop_list:", self.for_loop_list)

		return self.for_loop_list


