# Author: Hong Xiao
# This program translates code in KiwiSpec to python and executes the python code.

from util import *
from kiwi_lexer import *

def get_logic_define(input_string):
	import re
	# Regular expression pattern to match the first string in double quotes
	pattern = re.compile(r'"([^"]+)"')
	# Find the first match in the input string
	match = pattern.search(input_string)
	# Check if a match is found and get the first captured group
	if match:
		first_string = match.group(1)
		return (first_string)
	else:
		return ""

def strip_operator(s, pre_list):
	for ss in pre_list:
		if s.lower().startswith(ss):
			new_s = s[len(ss):].strip()
			if new_s.startswith('('):
				new_s = new_s[1:]
			if new_s.endswith(')'):
				new_s = new_s[:-1]
			return new_s
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

def startswith_list(s, l):
	for _i in l:
		if  s.strip().startswith(_i):
			return _i
	return ''

def list_strip(l):
	return [i.strip("' ', '\n', '\t'") for i in l]

def find_leading_seperator(text, seperator, trailor, start):
	for t in trailor:
		next = text.lower().find(seperator+t, start)
		if next != -1:
			return next
	return -1

def find_boundary(text, boundary, follows, multi):
	tmp_text = text.strip("' ', '\n', '\t'")[1:]
	body_end = -1
	for b in boundary:
		repeat_b = True
		start = 0
		while repeat_b:
			next = find_leading_seperator(tmp_text, b, [' ', '\n', '\t'], start)
			if next != -1 and \
				tmp_text[next-1] in [' ', '\n', '\t', ';']:
					if not follows or tmp_text[:next-1].strip("' ', '\n', '\t'")[-1] in follows:
						if (body_end == -1 or next < body_end):
							body_end = next
						repeat_b = False
					else:
						start = next+ +len(b)
						repeat_b = multi

			else:
				repeat_b = False
	return body_end

def parser_get_query_list(text, boundary, follows=[], multi=False):
	text = text.strip("' ', '\n', '\t'")

	query_list = []
	while text:
		body_end = find_boundary(text,boundary, follows, multi)
		if body_end == -1:
			query_list.append(text.strip("' ', '\n', '\t', ';'"))
			text = ''
		else:
			body_end += 1
			query_list.append(text[0:body_end].strip("' ', '\n', '\t', ';'"))
			text = text[body_end:].strip("' ', '\n', '\t', ';'")
	return query_list

def check_access_map(access_map_list, check_str):
	match_str_list = []
	tmp_access_map_list = []
	for _i in access_map_list:
		if f"{_i[0]}[{_i[1]}]" in check_str.replace(' ', ''):
			match_str_list.append(_i)
		else:
			tmp_access_map_list.append(_i)
	con_collect = ''
	if match_str_list:
		con_collect = 'if '
		for _i in match_str_list:
			con_collect += f""" ({_i[1]} in {_i[0]}.keys() if isinstance({_i[0]}, dict) else {_i[1]} in range(len({_i[0]}))) and """
		con_collect = con_collect[:-4] + ':'
	return con_collect, tmp_access_map_list

def get_access_maps(token, var_list, value_list, exclude_list=[]):
	all_depend = set()
	var_depend = []
	s_curr = ''
	s_stack = []
	var_flag = False
	var_map = {}
	access_map = []

	for i in token.value:
		if i == '[':
			if s_curr:
				s_stack.append((s_curr, var_flag))
			var_flag = False
			s_curr = i
		elif i == ']':
			s_curr += i
			pre_str = ''
			pre_i = ('', False)
			if s_stack:
				pre_i = s_stack.pop()
				pre_str = pre_i[0].strip('[')
				if pre_str in value_list:
					all_depend.add(pre_str)

			curr_v = s_curr[1:-1].strip()

			if (not curr_v) or (not pre_str) or (':' in curr_v) :
				continue

			if curr_v in value_list:
				all_depend.add(curr_v)
				var_flag = True

			if curr_v in var_list and curr_v not in exclude_list:
				var_depend.append(curr_v)
				all_depend.add(curr_v)
				var_flag = True
				var_map[curr_v] = pre_str

			if curr_v not in var_list:
				if pre_str.lower() != 'range':
					access_map.append([pre_str, curr_v])


			s_curr = pre_i[0]+s_curr
			var_flag |= pre_i[1]

		else:
			s_curr += i
	
	if s_curr in var_list and s_curr not in exclude_list:
		var_depend.append(s_curr)
		all_depend.add(s_curr)

	if s_curr in value_list:
		all_depend.add(s_curr)

	return all_depend, var_depend, var_map, access_map

def get_access_string(assign_a):

	lexer = BodyLexer(None, assign_a.strip())
	tokens = lexer.make_tokens()

	s_curr = ''
	s_stack = []
	c_str = ''
	for i in tokens[0].value:
		if i == '[':
			if s_curr:
				s_stack.append(s_curr)
			s_curr = i
		elif i == ']':
			s_curr += i
			if s_stack:
				pre_s = s_stack.pop()
				s_curr = pre_s+s_curr
				if not s_stack:
					c_str = s_curr
		else:
			s_curr += i

	if c_str == s_curr:
		return c_str
	else:
		return ''

def fix_default_format(assign_a):
#a[x|y] a[b[x|y]] a[i][j][x|y] a[i|k][j][x|y] a[b[x|y]|z] a[b[x]|c[y]]
#a[b[x]|c[y]] | a[b[x|y]|c[z]] | a[b[x]|c[y|z]]
	lexer = BodyLexer(None, assign_a)
	tokens = lexer.make_tokens()
	r_str = ''
	for token in tokens:
		s_curr = ''
		s_stack = []
		for i in token.value:
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
		r_str += s_curr
	return r_str

