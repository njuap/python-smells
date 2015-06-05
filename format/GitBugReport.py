"""
Exports Issues from a specified repository to a CSV file

Uses basic authentication (Github username + password) to retrieve Issues
from a repository that username has access to. Supports Github API v3.
"""
import csv
import requests

#the bug report of django is not available from github issues. I got it from django website.
directory = {
             # 'numpy':['Easy Fix','Defect','Patch','Critical Defect'],
             # 'ipython':['bug','quickfix'],
             # 'boto':['Bug'],
             # 'tornado':[''], #all labels
             # 'matplotlib':['can\'t fix','confirmed bug','needs_patch'],
             # 'scipy':['defect','easy-fix'],
             # 'nltk':['bug','goodfirstbug'],
             # 'ansible':['bug_report']
}
 
def write_issues(response,name,csvout):
  '''output a list of issues to csv'''
  if not response.status_code == 200:
    raise Exception(response.status_code)
  for issue in response.json():
    labels = issue['labels']
    if name == 'tornado' and 'pull_request' not in issue:
      csvout.writerow([issue['number'], issue['title'].encode('utf-8'), issue['created_at'], issue['closed_at']])
    else:
      for label in labels:
        if label['name'] in directory[name]:
          # print issue['number']
          csvout.writerow([issue['number'], issue['title'].encode('utf-8'), issue['created_at'], issue['closed_at']])
          break
 
for name in directory.keys():
  GITHUB_USER = '' #usename
  GITHUB_PASSWORD = '' #passport
  REPO = name+'/'+name  # format is username/repo
  if name=='tornado':
    ISSUES_FOR_REPO_URL = 'https://api.github.com/repos/tornadoweb/tornado/issues?state=all'
  else:
    ISSUES_FOR_REPO_URL = 'https://api.github.com/repos/%s/issues?state=all' % REPO
  AUTH = (GITHUB_USER, GITHUB_PASSWORD)

  csvfile = 'C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\%s\\%s-issues.csv' % (name,name)
  csvout = csv.writer(open(csvfile, 'wb'))
  csvout.writerow(('ID', 'Title', 'Created At', 'Closed At'))
  r = requests.get(ISSUES_FOR_REPO_URL, auth=AUTH)
  write_issues(r,name,csvout)
 
  #more pages? examine the 'link' header returned
  if 'link' in r.headers:
    pages = dict(
      [(rel[6:-1], url[url.index('<')+1:-1]) for url, rel in
        [link.split(';') for link in
          r.headers['link'].split(',')]])
    # print "***"
    # print pages
    while 'last' in pages and 'next' in pages:
      # print pages['next']
      r = requests.get(pages['next'], auth=AUTH)
      write_issues(r,name,csvout)
      if pages['next'] == pages['last']:
          break
      pages = dict(
        [(rel[6:-1], url[url.index('<')+1:-1]) for url, rel in
          [link.split(';') for link in
            r.headers['link'].split(',')]])
