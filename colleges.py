import requests
import json
import re
import time
import atexit

s = requests.session()


def modify(courses, courses_to_change, change_to):
	if change_to in courses_to_change:
		courses_to_change.remove(change_to)
	for course in courses:
		re.sub('|'.join(courses_to_change), change_to, course)
	return courses

def fix_course_names(courses):
	new_course_list = []
	counter = {}
	for course in courses:
		pieces = re.findall(r'([A-Z][A-Z\/&+ ]*[A-Z])[ -]*?([A-Z]?[0-9]{1,5}[A-Z]?)', course)
		if not pieces or len(pieces[0]) != 2:
			courses.remove(course)
			continue
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
			print('Removing {}'.format(course))
			courses.remove(course)
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
		print("{} replacing {}".format(winner, str(d['ok'] + d['not'])))
		new_course_list += modify(courses, d['ok'] + d['not'], winner)
	new_course_list.sort()
	return list(set(new_course_list))

def save_checkpoints(school, index, queue):
	with open('course_catalog.json', 'r') as f:
		loaded_data = json.load(f)
	loaded_data[school]['checkpoints'] = [school, index, queue]
	with open('course_catalog.json', 'w') as f:
		json.dump(loaded_data, f, indent=4, sort_keys=True)

def save_entries(school, course_data):
	with open('course_catalog.json', 'r') as f:
		loaded_data = json.load(f)
	loaded_data[school]['courses'] = course_data
	loaded_data[school]['courses'].sort()
	with open('course_catalog.json', 'w') as f:
		json.dump(loaded_data, f, indent=4, sort_keys=True)

def reload():
	with open('course_catalog.json', 'r') as f:
		data = json.load(f)

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
url = "http://www.ratemyprofessors.com/search.jsp?queryBy=teacherName&queryoption=HEADER&facetSearch=true&schoolName={}&offset={}&max=20"
teacher = "http://www.ratemyprofessors.com/ShowRatings.jsp?tid={}"

with open('course_catalog.json', 'r') as f:
	data = json.load(f)
schools = list(data.keys())
schools = [school for school in schools if "University" in school]
checkpoints = data.get('checkpoints')
try:
	checkpoint_school = checkpoints[0]
	checkpoint_index = checkpoints[1]
	checkpoint_queue = checkpoints[2]
	print("Last checkpoint: {}, index {}.".format(checkpoint_school, checkpoint_index))
except TypeError:
	checkpoint_school = checkpoint_index = checkpoint_queue = None
	print("No checkpoint found.")

for school in schools:
	reload()
	if isinstance(data[school]['courses'], list) and data[school]['courses']:
		print('{} skipped'.format(school))
		continue
	checkpoint_school = school
	print('---\t{}\t---'.format(school))
	ue_name = re.sub(' |&', '+', school)
	search = s.get(url.format(ue_name, 0)).content
	nResults = re.findall(b'result-count\">Showing .*? of (\d+?) results<\/div>', search)
	try:
		r = int(nResults[0])
	except:
		continue
	res = set()
	if school == checkpoint_school and checkpoint_queue:
		res |= set(checkpoint_queue)
	if school == checkpoint_school and checkpoint_index:
		start = checkpoint_index
	else:
		start = 0
	for i in range(start, r, 20):
		reload()
		checkpoint_index = i
		search = s.get(url.format(ue_name, i)).content
		tids = re.findall(b'\/ShowRatings\.jsp\?tid=(\d+)', search)
		addq = []
		print('Page {} of {} in {} \n'.format(i // 20 + 1, r // 20 + 1, school))
		print('Page is finished when load bar is here ↴')
		for i, tid in enumerate(tids):
			print('░░', end='', flush=True)
			page = s.get(teacher.format(tid.decode('utf-8'))).content
			years = re.findall(b'div class=\"date\"> \d+\/\d+\/(\d{4})<\/div>', page)
			classes = re.findall(b'class=\"response\">([A-Z]+.{0,4}?\d+)', page)
			for i in range(len(classes)):
				if int(years[i]) < 2015:
					break;
				else:
					addq += [re.sub(r'([A-Z][A-Z\/&+ ]*[A-Z])[ -]*?([A-Z]?[0-9]{1,5}[A-Z]?)', r'\1 \2', classes[i].decode('utf-8').upper())]
			res |= set(addq)
		print(" 100%\n")
		print('Found on page: {}\n'.format(str(set(addq))))
		save_checkpoints(school, checkpoint_index, list(res))
	data[school]['courses'] = []
	save_entries(school, fix_course_names(list(res)))
