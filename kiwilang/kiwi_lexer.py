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
			if self.current_char in '\t\n .+-*/%^!=(){}:,;[]':
				tokens.append(Token('SYM', self.current_char))
				self.advance()
			else:
				tokens.append(self.make_expr())
		return tokens

	def make_expr(self):
		id_str = ''
		index_c = 0
		index_e = 0
		while self.current_char != None and \
			(index_c != 0 or self.current_char not in '\t\n .+-*/%^!={}():,;'):

			if index_c == 0 and self.current_char == ']':
				break

			if self.current_char == '[':
				index_e = 1
				index_c += 1

			elif self.current_char == ']':
				index_c -= 1

			else:
				if index_e and index_c == 0:
					print("index_expression error:", id_str, "/", self.text[self.pos.idx:])
					raise

			id_str += self.current_char
			self.advance()

		tok_type = 'EXPR'
		return Token(tok_type, id_str)