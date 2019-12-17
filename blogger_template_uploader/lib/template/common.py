"Common code used throughout the template component."

class TemplateError(Exception):
	def __init__(self, message, line, col):
		super().__init__( ''.join( ( message, ' Line: ', str(line), ' Col: ', str(col) ) ) )

class unfound: # A type to differentiate from null (translated to None) when searching inside a JSON-derived object.
	pass

def GetJsonTypeName(item):
	"Return a string containing the equivalent JSON type of the variable."
	if isinstance(item, dict):
		return 'object'
	elif isinstance(item, list) or isinstance(item, tuple):
		return 'array'
	elif isinstance(item, str):
		return 'string'
	elif isinstance(item, int) or isinstance(item, float):
		return 'number'
	elif item is True:
		return 'true'
	elif item is False:
		return 'false'
	elif isinstance(item, unfound):
		return 'unfound'
	else: # item is None:
		return 'null'
