"Post template parsing component to convert the input string to usable entry objects."

from blogger_template_uploder.lib.common import ExpandArray
from blogger_template_uploder.lib.template.common import unfound, TemplateError
from blogger_template_uploder.lib.template.parser import parser

class RenderError(TemplateError):
	pass

class RenderItem:
	pass

class RenderStaticItem(RenderItem):
	def render(self):
		return self.item.token.raw
	def __init__(self, item):
		self.item = item

class RenderEntry(RenderItem):
	def __init__(self, entry):
		self.entry = entry
		self.clear()

class RenderListEntry(RenderEntry):
	def clear(self):
		self.value = []
	def _GetRendered(self):
		if isinstance(v, unfound):
			if self.entry.required:
				raise RenderError()
			else:
				return (self.entry.EntryPreString, self.entry.DefaultEntry, self.entry.EntryPostString)
		else:
			return (self.entry.EntryPreString, v, self.entry.EntryPostString)

class RenderOneLineEntry(RenderListEntry):
	def AddEntry(self, idx):
		if not (self.entry.MinEntryAmount == 0 and self.entry.MaxEntryAmount == 0) and idx >= self.entry.MaxEntryAmount:
			raise RenderError()
		ExpandArray(self.value, unfound, idx)
	def SetEntry(self, idx, value):
		self.AddEntry(idx)
		self.value[idx] = value
	def DeleteEntry(self, idx):
		if not (self.entry.MinEntryAmount == 0 and self.entry.MaxEntryAmount == 0) and len(self.value) - 1 < self.entry.MinEntryAmount:
			raise RenderError()
		if idx < len(self.value):
			del self.value[idx]
	def render(self):
		output = []
		if not (self.entry.MinEntryAmount == 0 and self.entry.MaxEntryAmount == 0)
		   and (len(self.value) < self.MinEntryAmount or len(self.value) > self.MaxEntryAmount):
			raise RenderError()
		output.append(self.entry.PreString)
		for v in self.value:
			output.extend( self._GetRendered(v) )
		output.append(self.entry.PostString)
		return tuple(output)
	def __init__(self, entry):
		RenderEntry.__init__(self, entry)
		self.AddEntry(self.entry.MinEntryAmount - 1)

class RenderMultiLineEntry(RenderEntry):
	def _GetRenderable(self):
		if self.value == '':
			if self.entry.required:
				raise RenderError()
			else:
				return self.entry.DefaultEntry
		else:
			return self.value
	def clear(self):
		self.value = ''
	def set(self, value):
		lines = len( value.splitlines() )
		if not (self.entry.MinEntryAmount == 0 and self.entry.MaxEntryAmount == 0) and lines > self.entry.MaxEntryAmount:
			raise RenderError()
		self.value = value
	def render(self):
		output = []
		value = self._GetRenderable()
		ValueLines = value.splitlines()
		if not (self.entry.MinEntryAmount == 0 and self.entry.MaxEntryAmount == 0)
		   and (len(ValueLines) < self.MinEntryAmount or len(ValueLines) > self.MaxEntryAmount):
			raise RenderError()
		output.append(self.entry.PreString)
		for v in ValueLines:
			output.extend( (self.entry.EntryPreString, v, self.entry.EntryPostString) )
		output.append(self.entry.PostString)
		return tuple(output)

class RenderImagesEntry(RenderListEntry):
	def _CountEntries(self):
		output = 0
		for r in self.value:
			output += len(r)
		return output
	def AddEntry(self, row=-1, col=-1):
		CurrentEntries = self._CountEntries()
		ExpandedEntries = len(self.value[row])
		if col >= ExpandedEntries:
			ExpandedEntries = ExpandedEntries + (col - ExpandedEntries) + 1
		if not (self.entry.MinEntryAmount == 0 and self.entry.MaxEntryAmount == 0) and ExpandedEntries > self.entry.MaxEntryAmount:
			raise RenderError()
		ExpandArray(self.value, list, row)
		ExpandArray(self.value[row], unfound, col)
	def SetEntry(self, row, col, value):
		self.AddEntry(row, col)
		self.value[row][col] = value
	def DeleteEntry(self, row, col):
		CurrentEntries = self._CountEntries()
		if not (self.entry.MinEntryAmount == 0 and self.entry.MaxEntryAmount == 0) and CurrentEntries - 1 < self.entry.MinEntryAmount:
			raise RenderError()
		if row < len(self.value) and col < len(self.value[row]):
			del self.value[row][col]
	def render(self):
		output = []
		NumEntries = self._CountEntries()
		if not (self.entry.MinEntryAmount == 0 and self.entry.MaxEntryAmount == 0)
		   and (NumEntries < self.MinEntryAmount or NumEntries > self.MaxEntryAmount):
			raise RenderError()
		output.append(self.entry.PreString)
		for r in self.value:
			output.append(self.entry.RowPreString)
			for v in r:
				output.extend( self._GetRendered(v) )
			output.append(self.entry.RowPostString)
		output.append(self.entry.PostString)
		return tuple(output)

class renderer:
	def _GenerateEntries(self):
		self.entries = []
		for e in self.parser.entries:
			if isinstance(e, TemplateStaticItem):
				self.entries.append( RenderStaticItem(e) )
			elif isinstance(e, TemplateOneLineEntry):
				self.entries.append( RenderOneLineEntry(e) )
			elif isinstance(e, TemplateMultiLineEntry):
				self.entries.append( RenderMultiLineEntry(e) )
			elif isinstance(e, TemplateImagesEntry):
				self.entries.append( RenderImagesEntry(e) )
	def render(self):
		output = []
		for e in self.entries:
			output.extend( e.render() )
		return ''.join(output)
	def __init__(self, TemplateParser):
		self.parser = TemplateParser
		self._GenerateEntries()
