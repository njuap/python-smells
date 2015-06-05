import csv
import datetime
from scipy import stats
import os
import subprocess
import time

directory = {
             # ('django','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\django\\django'),
             # ('numpy','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\numpy\\numpy'),
             # ('ipython','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\ipython\\ipython'),
             # ('boto','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\boto\\boto'),
             # ('tornado','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\tornado\\tornado'),
             # ('matplotlib','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\matplotlib\\matplotlib'),
             # ('scipy','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\scipy\\scipy'),
             # ('nltk','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\nltk\\nltk'),
             'ansible':'C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\ansible\\'
}

visions = {
 'ansible':['v1.2.2','v1.4.0','v1.5.0','v1.6.0','v1.7.0','v1.8.0','v1.8.4','v1.9.2-0.1.rc1']

}

def walkDirectory(rootdir):
	sourcedirs = set()
	for root, dirs, files in os.walk(rootdir):
		for name in files:
			if (os.path.splitext(name)[1][1:] == 'py'):
				sourcedirs.add(os.path.join(root,name)[(len(rootdir)+1):].replace("\\", "/"))
	return sourcedirs

def changegittag(directory,tag):
  os.chdir(directory)
  p = subprocess.Popen('git checkout '+tag,shell=True,stdout=subprocess.PIPE)

def fisher_exact(smell,maint,sourcedir):
	currentfiles = walkDirectory(sourcedir)
	smell_maint = set(smell.keys()).intersection(set(maint.keys()))
	smell_maint = smell_maint.intersection(currentfiles)
	smell_nonmaint = set(smell.keys()).difference(set(maint.keys()))
	smell_nonmaint = smell_nonmaint.intersection(currentfiles)
	nonsmell_maint = set(maint.keys()).difference(set(smell.keys()))
	nonsmell_maint = nonsmell_maint.intersection(currentfiles)
	smell_or_maint = set(smell.keys()).union(set(maint.keys()))
	smell_or_maint = smell_or_maint.intersection(currentfiles)
	nonsmell_nonmaint = currentfiles.difference(smell_or_maint)
	xx = smell_or_maint.difference(set(walkDirectory(sourcedir)))
	# print len(smell_maint),len(smell_nonmaint),len(nonsmell_maint),len(nonsmell_nonmaint),len(smell_or_maint),len(currentfiles)
	oddsratio, pvalue = stats.fisher_exact([[len(smell_maint), len(smell_nonmaint)], [len(nonsmell_maint), len(nonsmell_nonmaint)]])
	return oddsratio, pvalue


for name in directory.keys():
	tagtime = {} #vision:time
	tagfile = csv.reader(file(directory[name]+'tags_info.csv','rb')) 
	for line in tagfile:
		if tagfile.line_num == 1:
			continue
		v = line[1]
		t = line[3]
		if v in visions[name]:
			tagtime[v] = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
	# print tagtime
	for i in range(len(visions[name])-1):
		tag = visions[name][i]
		nexttagtime = tagtime[visions[name][i+1]]
		changegittag(directory[name]+name,tag)
		time.sleep(3)

		#code smell {filename:[#smell1,#smell2,#smell3]}
		smell_info = {}
		smellnum = csv.reader(file(directory[name]+'\\result\\'+tag+'\\smell_info.csv','rb'))		
		for line in smellnum:
			if smellnum.line_num == 1:
				continue
			filename = line[0][:]
			filename = filename.replace("\\", "/")
			smell_info[filename] = line[1:14]
		# print smell_info

		#change {filename:count}
		change_info = {}
		changenum = csv.reader(file(directory[name]+'change_log.csv','rb'))	
		for line in changenum:
			# print tagtime[tag],line[2]
			if changenum.line_num == 1:
				continue
			currenttime = datetime.datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S')
			if tagtime[tag] >= currenttime or nexttagtime < currenttime:
				continue
			elif currenttime > tagtime[tag] and currenttime<=nexttagtime and len(line)==4:
				if line[3] in change_info.keys():
					change_info[line[3]] = change_info[line[3]] + 1
				else:
					change_info[line[3]] = 1
		# print tag
		# print change_info

		#fault {filename:count}
		fault_info = {}
		faultnum = csv.reader(file(directory[name]+'fault_log.csv','rb'))
		for line in faultnum:
			# print tagtime[tag],line[2]
			if faultnum.line_num == 1:
				continue
			currenttime = datetime.datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S')
			if tagtime[tag] >= currenttime or nexttagtime < currenttime:
				continue
			elif currenttime > tagtime[tag] and currenttime<=nexttagtime and len(line)==5:
				# print currenttime,tagtime[tag],nexttagtime
				if line[4] in fault_info.keys():
					fault_info[line[4]] = fault_info[line[4]] + 1
				else:
					fault_info[line[4]] = 1
		# print tag
		# print fault_info
		print 'tag:', tag
		print fisher_exact(smell_info,change_info,directory[name]+name)
		print fisher_exact(smell_info,fault_info,directory[name]+name)
