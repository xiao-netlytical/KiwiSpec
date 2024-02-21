# Author: Hong Xiao
# This program translates code in KiwiSpec to python and executes the python code.

from util import *

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

def find_boundary(text, boundary, follows, multi):
	tmp_text = text.strip("' ', '\n', '\t'")[1:]
	body_end = -1
	for b in boundary:
		repeat_b = True
		start = 0
		while repeat_b:
			next = tmp_text.lower().find(b, start)
			if next != -1 and \
				tmp_text[next-1] in [' ', '\n', '\t', ';'] and \
				tmp_text[next+len(b)] in [' ', '\n', '\t', ';']:
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

def get_access_maps(tokens, var_list, value_list, exclude_list=[]):
	all_depend = set()
	var_depend = []
	s_curr = ''
	s_stack = []
	var_flag = False
	var_map = {}
	access_map = []

	for token in tokens:
		i = token.value
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