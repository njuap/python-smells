#git log --no-walk --tags --pretty="%h;%d;%an;%ai;%s" --decorate=full > ../tags_info
#git log --name-only --pretty="==================%n%h;%an;%ai;%s%n%b%n==" > ../log_info
#cannot find some tag logs in log-info

import csv

subjects = [
              'django',
              'numpy',
              'ipython',
              'boto',
              'tornado',
              'matplotlib',
              'scipy',
              'nltk',
              'ansible'
]


for name in subjects:
  with open('C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\'+name+'\\log_info') as f:
    fp = open('C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\'+name+'\\change_log.csv', 'wb') 
    logcsv = csv.writer(fp)
    logcsv.writerow(['hash','author','date','file'])
    logflag = True
    fileflag = False
    logitem = []
    files = []
    for line in f:
      line = line.strip()
      if line == '==================':
        if len(logitem) == 0:
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
        logitem = line.split(";")[0:3]
        # print logitem
        logitem[2] = logitem[2][0:-6]
        logflag = False
        fileflag = False
      elif line == '==':
        fileflag = True 
      elif fileflag and line != '' and line[-3:] == '.py':
        files.append(line)
