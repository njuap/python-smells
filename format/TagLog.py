import csv

subjects = ['django','numpy','ipython','boto','tornado','matplotlib','scipy','nltk','ansible']

for name in subjects:
    tags = []
    with open('C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\'+name+'\\tags_info') as f:
        for line in f:
            items = line.strip().split(";")
            s = items[1]
            l = s.find('refs/tags/')
            if (l == -1):
                print 'not find refs/tags/'
                exit()
            l = l + 10
            r = s[l:].find(',')
            if r == -1:
                r = s[l:].find(')')
            items[1] = s[l:r+l]
            items[3] = items[3][0:-6]
            # print items
            tags.append(items)
    with open('C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\'+name+'\\tags_info.csv', 'wb') as fp:
    	tagcsv = csv.writer(fp)
    	tagcsv.writerow(['hash','tag','author','date','title'])
        tags.sort
    	for item in tags:
    	    tagcsv.writerow(item)

    
