import difflib
from operator import itemgetter

def search(searchTerm, list, keyName : str = None, numMatches : int = 3):
	"""Searches the provided list for the searchTerm - using a keyName if provided for dicts."""
	if len(list) < 1:
		return None
	searchList = []
	for item in list:
		if keyName:
			testName = item[keyName]
		else:
			testName = item
		matchRatio = difflib.SequenceMatcher(None, searchTerm.lower(), testName.lower()).ratio()
		searchList.append({ 'Item' : item, 'Ratio' : matchRatio })
	searchList = sorted(searchList, key=lambda x:x['Ratio'], reverse=True)
	if numMatches > len(searchList):
		numMatches = len(searchList)
	return searchList[:numMatches]
