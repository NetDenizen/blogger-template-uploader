"Post template parsing component to convert the input string to usable entry objects."

from blogger_template_uploder.lib.template.common import TemplateError, unfound, GetJsonTypeName
from blogger_template_uploder.lib.template.lexer import lexer, token

class TemplateEntryError(TemplateError):
	pass

class TemplateItem:
	def __init__(self, ThisToken):
		self.token = ThisToken

class TemplateStaticItem(TemplateItem):
	pass

class TemplateEntry(TemplateItem): # This should never be constructed alone.
	def _GetTyped(self, key, default, required=False):
		value = self.token.value.get( key, unfound() )
		# TODO: Reduce duplication
		if isinstance( value, type(default) ):
			pass
		elif isinstance(value, unfound) or value is None:
			if required:
				raise TemplateEntryError( ''.join( ("'", key, "' field is '", GetJsonTypeName(value), "' but must be a ", GetJsonTypeName(value), ".") ) )
			else:
				value = default
		else:
			if required:
				raise TemplateEntryError( ''.join( ("'", key, "' field is '", GetJsonTypeName(value), "' but must be a ", GetJsonTypeName(value), ".") ) )
			else:
				raise TemplateEntryError( ''.join( ("'", key, "' field is '", GetJsonTypeName(value), "' but must be a ", GetJsonTypeName(value), ", null, or not included.") ) )
	def _GetIntString(self, key, default):
		raw = self._GetTyped( key, str(default) )
		try:
			return int(raw)
		except ValueError:
			raise TemplateEntryError( ''.join( ("'", key, "' field must be a string representing a valid integer.") ) )
	def _SetName(self):
		self.name = self._GetTyped('name', '', True)
	def _SetRequired(self):
		self.required = self._GetTyped('required', False)
	def _SetDefaultEntry(self):
		self.DefaultEntry = self._GetTyped('DefaultEntry', '')
	def _SetEntryAmountRange(self):
		self.MinEntryAmount = self._GetIntString('MinEntryAmount', 0)
		self.MaxEntryAmount = self._GetIntString('MaxEntryAmount', 0)
		if self.MinEntryAmount < 0:
			raise TemplateEntryError( ''.join( ("A minimum entry amount of '", str(self.MinEntryAmount), "' must be greater than '0'.") ) )
		elif self.MaxEntryAmount < 0:
			raise TemplateEntryError( ''.join( ("A maximum entry amount of '", str(self.MaxEntryAmount), "' must be greater than '0'.") ) )
		elif self.MinEntryAmount > self.MaxEntryAmount:
			raise TemplateEntryError( ''.join( ("A minimum entry amount of '", str(self.MinEntryAmount), "' must be less than a maximum entry amount of '", str(self.MaxEntryAmount), "'.") ) )
	def _SetPreString(self):
		self.PreString = self._GetTyped('PreString', '')
	def _SetPostString(self):
		self.PostString = self._GetTyped('PostString', '')
	def _SetEntryPreString(self):
		self.EntryPreString = self._GetTyped('EntryPreString', '')
	def _SetEntryPostString(self):
		self.EntryPostString = self._GetTyped('EntryPostString', '')
	def __init__(self, ThisToken):
		TemplateItem.__init__(self, ThisToken)
		self._SetName()
		self._SetRequired()
		self._SetDefaultEntry()
		self._SetEntryAmountRange()
		self._SetPreString()
		self._SetPostString()
		self._SetEntryPreString()
		self._SetEntryPostString()

class TemplateOneLineEntry(TemplateEntry):
	pass

class TemplateMultiLineEntry(TemplateEntry):
	pass

class TemplateImagesEntry(TemplateEntry):
	def _SetDefaultEntry(self):
		self.DefaultEntry = ''
	def _SetRowPreString(self):
		self.RowPreString = self._GetTyped('RowPreString', '')
	def _SetRowPostString(self):
		self.RowPostString = self._GetTyped('RowPostString', '')
	def __init__(self, ThisToken):
		TemplateEntry.__init__(self, ThisToken)
		self._SetRowPreString()
		self._SetRowPostString()

class parser:
	def _GenerateJsonEntry(self, t):
		EntryType = t.value.get( 'type', unfound() )
		if EntryType == 'OneLineEntry':
			self.entries.append( TemplateOneLineEntry(t) )
		elif EntryType == 'MultiLineEntry'
			self.entries.append( TemplateMultiLineEntry(t) )
		elif EntryType == 'ImagesEntry':
			self.entries.append( TemplateImagesEntry(t) )
		else:
			raise TemplateEntryError( ''.join( ("'type' field is '", str(EntryType), "' but must be 'OneLineEntry', 'MultiLineEntry', or 'ImagesEntry'.") ) )
	def _GenerateEntries(self):
		self.entries = []
		for t in self.lexer.tokens:
			if isinstance(t, JsonToken):
				self._GenerateJsonEntry(t)
			else:
				self.entries.append( TemplateStaticItem(t) )
	def __init__(self, raw):
		self.raw = raw
		self.lexer = lexer(self.raw)
		self._GenerateEntries()
