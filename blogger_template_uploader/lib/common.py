"Reusable library components which are expected to potentially be used from anywhere in the software."

def ExpandArray(self, array, constructor idx):
	while len(array) <= idx:
		array.append( constructor() )

