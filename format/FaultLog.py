#git log --no-walk --tags --pretty="%h;%d;%an;%ai;%s" --decorate=full > ../tags_info
#git log --name-only --pretty="==================%n%h;%an;%ai;%s%n%b%n==" > ../log_info

import csv
import re

failttokens = {
'django':['Fixed #','fixes #','Refs #','refs #','Fixed settings docs to match list/tuple changes in #'],
# 'numpy':[],
# 'ipython':[],
# 'boto':[],
# 'tornado':['Fixes #'], #no bug id
# 'matplotlib':['Fix for issue #'],
# 'scipy':[],
# 'nltk':[],
# 'ansible':['fixes #','Fixes #','fix #','Fix #','fix for issue #','closes #','Fixes bug #','Workaround for #','Port fix for #'],
}

def getFaultID(str,name):
  for tokens in failttokens[name]:
    index = str.find(tokens)
    if index != -1:
      match = re.match(r'\d*',str[(index+len(tokens)):])
      if match:
        return match.group()
  return None

for name in failttokens.keys():
  bugids = []
  bugfile = csv.reader(file('C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\%s\\%s-issues.csv' % (name,name),'rb')) 
  for line in bugfile:
    if bugfile.line_num == 1:
      continue
    bugids.append(line[0])
  # with open('C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\%s\\%s-issues.csv' % (name,name)) as bugfile:
  #   for line in bugfile:
  #     if bugfile.line_num == 1:  
  #       continue
  #     bugids.append(line.split(",")[0])
  #   if len(bugids) != 0:
  #     del bugids[0]
  with open('C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\'+name+'\\log_info') as f:
    fp = open('C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\'+name+'\\fault_log.csv', 'wb') 
    logcsv = csv.writer(fp)
    logcsv.writerow(['hash','author','date','faultID','file'])
    logflag = True
    fileflag = False
    logitem = []
    files = []
    for line in f:
      line = line.strip()
      if line == '==================':
        if len(logitem) == 0 or logitem[3] is None:
          logflag = True
          fileflag = False
          logitem = []
          files = []
          continue
        if len(files) > 0:
          for i in files:
            logcsv.writerow(logitem+[i])
        else:
          logcsv.writerow(logitem)
        logflag = True
        fileflag = False
        logitem = []
        files = []
      elif logflag and not fileflag:
        commit = line.split(";")
        logitem = commit[0:3]
        logitem[2] = logitem[2][0:-6]
        logitem.append(None)
        foundid = getFaultID(commit[3],name)
        if foundid is not None and foundid in bugids:
          logitem[3] = foundid
        # if foundid is not None:
        #   if foundid not in bugids:
        #     print foundid
        #   else:
        #     logitem[3] = foundid
        logflag = False
        fileflag = False
      elif not fileflag and not logflag and logitem[3] is None:
        foundid = getFaultID(line,name)
        if foundid is not None and foundid in bugids:
          logitem[3] = foundid
        # if foundid is not None:
        #   if foundid not in bugids:
        #     print foundid
        #   else:
        #     logitem[3] = foundid
      elif line == '==':
        fileflag = True 
      elif fileflag and line != '' and line[-3:] == '.py':
        files.append(line)

