# -*- coding: utf-8 -*-
import re
import json
import requests
import time
def modify(school, courses_to_change, change_to):
	if change_to in courses_to_change:
		courses_to_change.remove(change_to)
	if "COM" in change_to:
		print(school)
	for course in data[school]['courses']:
		re.sub('|'.join(courses_to_change), change_to, course)

abbr = [{'ok': ['HIST', 'HISTO', 'HIS'], 'not': ['HISTORY', 'H']}, 
		{'ok': ['ENGL', 'ENG'], 'not': ['ENGLISH', 'E']},
		{'ok': ['ACCT', 'ACC', 'ACCTN', 'ACCTG'], 'not': ['ACCOUNTING', 'ACCOUTING', 'A']},
		{'ok': ['BIO', 'BIOL'], 'not': ['BIOLOGY', 'B']},
		{'ok': ['ANAT', 'ANA'], 'not': ['ANATOMY']},
		{'ok': ['PSYCH', 'PSYC', 'PSY'], 'not': ['PSYCHOLOGY', 'P', 'PSYCC']},
		{'ok': ['CHEM', 'CHM'], 'not': ['CHEMISTRY', 'CHEMM']},
		{'ok': ['ANTHR', 'ANTHRO', 'ANTH', 'ANT', 'ANTRO', 'ANTR'], 'not': ['ANTHROPOLOGY']},
		{'ok': ['SOC', 'SOCI', 'SOCIO'], 'not': ['SOCIOLOGY']},
		{'ok': ['MATH', 'MAT', 'MTH'], 'not': ['MATHEMATICS']},
		{'ok': ['CALC'], 'not': ['CALCULAS', 'CALCU', 'CALCULUS']},
		{'ok': ['PHIL'], 'not': ['PHILOSOPHY']},
		{'ok': ['STAT', 'STATS'], 'not': ['STATISTICS']},
		{'ok': ['PLSC', 'PLSCI', 'POLSC', 'POLSCI', 'POLISCI'], 'not': ['POLITICALSCIENCE', 'POLITICAL SCIENCE']},
		{'ok': ['FIN'], 'not': ['FINANCE']},
		{'ok': ['FREN', 'FRE'], 'not': ['FRENCH']},
		{'ok': ['SPAN', 'SP', 'SPA', 'SPN'], 'not': ['SPANISH', 'S']},
		{'ok': ['MUS', 'MUSI', 'MUSC'], 'not': ['M']},
		{'ok': ['HUM', 'HUMN', 'HUMAN', 'HUMT'], 'not': ['HUMANITIES', 'H']},
		{'ok': ['JOUR', 'JOURN', 'JRN'], 'not': ['JOURNALISM', 'J']},
		{'ok': ['COMM', 'COM', 'COMMUN', 'COMMS', 'COMMU', 'COMS'], 'not': ['COMMUNICATION', 'COMMUNICATIONS', 'C']}
]

with open('course_catalog.json', 'r') as f:
	data = json.load(f)
for school, info in data.items():
	if "University of California" in school or "San Diego" in school or "Diablo Valley" in school:
		print("{} SKIPPED\n\n".format(school))
		continue
	counter = {}
	try:
		if not isinstance(data[school]['courses'], list):
			continue
	except:
		continue
	for i, course in enumerate(data[school]['courses']):
		pieces = re.findall(r'([A-Z &\/]*[A-Z]).{0,4}?(\d+)', course)
		subj = pieces[0][0]
		num = int(pieces[0][1])
		added = False
		for d in abbr:
			if added:
				break
			if any(subj == rsubj for rsubj in d['ok']):
				if counter.get(subj):
					counter[subj] += 1
				else:
					counter[subj] = 1
		if len(str(num)) > 4:
			print(course)
			data[school]['courses'].remove(course)
	for d in abbr:
		winner = d['ok'][0]
		if counter.get(winner):
			mx = counter[winner]
		else:
			mx = 0
		for subj in d['ok']:
			if counter.get(subj) and counter[subj] >= mx:
				mx = counter[subj]
				winner = subj
		if any(winner in c for c in data[school]['courses']):
			modify(school, d['ok'] + d['not'], winner)
	"""	keysystem = []
	for l in queue:
		if len(l) > 1:
			notok = max(l)
			l.remove(notok)
		keysystem += [{'ok': list(l), 'not': [notok]}]
	for entry in keysystem:
		pass"""

	


with open('course_catalog.json', 'w') as f:
	json.dump(data, f, indent=4, sort_keys=True)