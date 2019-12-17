"Post template parsing component to convert the input string to its tokenized represenation."

import json
import re
from collections import OrderedDict

from blogger_template_uploder.lib.template.common import TemplateError

class TemplateLexerError(TemplateError):
	pass

class token:
	def __init__(self, raw):
		self.raw = raw

class RawToken(token):
	pass

class EscapeToken(RawToken):
	pass

class OpenEscapeToken(EscapeToken):
	def __init__(self, value):
		EscapeToken.__init__(self, '[')

class ClosedEscapeToken(EscapeToken):
	def __init__(self, value):
		EscapeToken.__init__(self, ']')

class JsonToken(token):
	def _ParseJson(self)
		try:
			self.value = json.loads(self.raw, object_pairs_hook=OrderedDict)
		except json.decoder.JSONDecodeError as err:
			raise LexerError(''.join( ('Failed to decode template value JSON: "', self.raw, '" Reason: "', err.msg) ), self.line + err.lineno, self.col + err.colno)
	def __init__(self, raw, line, col):
		token.__init__(self, raw)
		self.line = line
		self.col = col
		self._ParseJson()

RE_NEWLINE_SINGLE = re.compile('[\n\r]')
class lexer:
	def _SetIdx(self, NewIdx):
		CurrentIdx = self._idx
		while True:
			m = RE_NEWLINE_SINGLE.search(self._input[CurrentIdx:])
			if m is not None:
				StartIdx = m.start(0)
				if StartIdx + CurrentIdx < NewIdx:
					self._line += 1
					self._col = 0
					CurrentIdx = CurrentIdx + StartIdx + len( m.group(0) )
				else:
					break
			else:
				break
		self._idx = NewIdx
		self._col = NewIdx - CurrentIdx
	def _scan(self, value, start=-1):
		if start == -1:
			TrueStart = self._idx
		else:
			TrueStart = start
		return self._raw.find(value, TrueStart)
	def _tokenize(self):
		self.tokens = []
		while True:
			DelimitIdx = self._scan('{') # Open
			if DelimitIdx == -1: # No more matches
				self.tokens.append( RawToken(self._raw[self._idx:]) )
				break
			if DelimitIdx > self._idx: # Preceeding raw values
				self.tokens.append( RawToken(self._raw[self._idx:DelimitIdx]) )
			self._SetIdx(DelimitIdx + 1)
			DelimitIdx = self._scan('}') # Closed
			if DelimitIdx == -1:
				raise LexerError("Unmatched '}', when parsing template value JSON.", self._line, self._col)
			value = self._raw[self._idx:DelimitIdx]
			if not value:
				self.tokens.append( ClosedEscapeToken() )
			elif value == '{':
				self.tokens.append( OpenEscapeToken() )
			else:
				self.tokens.append( JsonToken(value, self._line, self._col) )
			self._SetIdx(DelimitIdx + 1)
	def __init__(self, raw):
		self.raw = raw
		self._idx = 0
		self._line = 0
		self._col = 0
		self._tokenize()
