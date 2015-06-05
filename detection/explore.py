import astChecker
import util
import customast
import os
import time
import csv

directory = [
             # ('django','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\django\\django','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\django\\result\\'),
             # ('numpy','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\numpy\\numpy','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\numpy\\result\\'),
             # ('ipython','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\ipython\\ipython','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\ipython\\result\\'),
             # ('boto','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\boto\\boto','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\boto\\result\\'),
             # ('tornado','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\tornado\\tornado','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\tornado\\result\\'),
             ('matplotlib','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\matplotlib\\matplotlib','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\matplotlib\\result\\'),
             # ('scipy','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\scipy\\scipy','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\scipy\\result\\'),
             # ('nltk','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\nltk\\nltk','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\nltk\\result\\'),
             # ('ansible','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\ansible\\ansible','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\ansible\\result\\')
]

# directory = [('matplotlib','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\matplotlib\\matplotlib','C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\matplotlib\\result\\'),]

for name,sourcedir,currentdir in directory:
    tags = []
    with open('C:\\Users\\JOJO\\Desktop\\pysmell\\subject\\'+name+'\\tags') as f:
        for line in f:
            tags.append(line.strip())
    tags = tags[17:]
    for tag in tags:
        resultdir = currentdir + tag + "\\"
        if not os.path.exists(resultdir):
            os.makedirs(resultdir)
        smell_info = csv.writer(file(resultdir+'smell_info.csv','wb'))
        logfile = open(resultdir+'accountlog.txt',mode='w')
        LongParameterList = open(resultdir+"LongParameterList.txt",mode="w")
        LongMethod = open(resultdir+"LongMethod.txt",mode="w")
        LongScopeChaining = open(resultdir+"LongScopeChaining.txt",mode="w")
        LongBaseClassList = open(resultdir+"LongBaseClassList.txt",mode="w")
        LargeClass = open(resultdir+"LargeClass.txt",mode="w")
        UselessExceptionHandling = open(resultdir+"UselessExceptionHandling.txt",mode="w")
        ComplexLambdaExpression = open(resultdir+"ComplexLambdaExpression.txt",mode="w")
        LongTernaryConditionalExpression = open(resultdir+"LongTernaryConditionalExpression.txt",mode="w")
        ComplexContainerComprehension = open(resultdir+"ComplexContainerComprehension.txt",mode="w")
        LongMessageChain = open(resultdir+"LongMessageChain.txt",mode="w")
        MultiplyNestedContainer = open(resultdir+"MultiplyNestedContainer.txt",mode="w")
        ViolatedMagicMethod = open(resultdir+"ViolatedMagicMethod.txt",mode="w")
        UnusedImport = open(resultdir+"UnusedImport.txt",mode="w")

        h = {1: LongParameterList, 2: LongMethod, 3: LongScopeChaining, 4: LongBaseClassList, 5: LargeClass, 6:MultiplyNestedContainer,7: UselessExceptionHandling,
        8:UnusedImport, 9: ComplexLambdaExpression, 10: LongTernaryConditionalExpression, 11: ComplexContainerComprehension, 12: ViolatedMagicMethod,
        13: LongMessageChain}

        name = {1: 'LongParameterList', 2: 'LongMethod', 3: 'LongScopeChaining', 4: 'LongBaseClassList', 5: 'LargeClass', 6:'MultiplyNestedContainer', 7: 'UselessExceptionHandling',
        8:'UnusedImport', 9: 'ComplexLambdaExpression', 10: 'LongTernaryConditionalExpression', 11: 'ComplexContainerComprehension', 12: 'ViolatedMagicMethod',
        13: 'LongMessageChain'}

        count = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0}

        myast = astChecker.MyAst()
        # time.sleep(3)
        util.changegittag(sourcedir,tag)
        time.sleep(3)
        filenum = 0
        for currentFileName in util.walkDirectory(sourcedir):
            filenum = filenum + 1
            try:
                astContent = customast.parse_file(currentFileName)
            except:
                logfile.write(currentFileName+"\n")
                continue
            myast.fileName = currentFileName
            myast.visit(astContent)
            res = util.execute(currentFileName)
            if len(res) > 0:
                myast.result = myast.result + res
            usedImports = util.usedImports(currentFileName,myast.imports)
            for defitem in myast.imports:
                for useitem in usedImports:
                    if useitem == defitem[0]:
                        break
                else:
                    myast.result.append((8,defitem[1],defitem[2],defitem[0]))
            myast.imports = set()

        for useitem in myast.usedmagic:
            for defitem in myast.defmagic:
                if useitem[0] == defitem[0]:
                    break
            else:
                myast.result.append((12,useitem[1],useitem[2],useitem[0]))
        
        smell_info.writerow(['file','LongParameterList', 'LongMethod', 'LongScopeChaining', 'LongBaseClassList', 'LargeClass', 'UselessExceptionHandling',
        'ComplexLambdaExpression', 'LongTernaryConditionalExpression', 'ComplexContainerComprehension', 'ViolatedMagicMethod',
        'LongMessageChain', 'MultiplyNestedContainer', 'UnusedImport','total','file numbers:'+str(filenum)])

        filesmell = {}#file:[smell1,smell2,]
        for item in myast.result:
            h[item[0]].write(item[1] + "," + str(item[2]) + "," + str(item[3]) + "\n")
            count[item[0]] = count[item[0]] + 1

            if item[1] in filesmell.keys():
                filesmell[item[1]][item[0]-1] = filesmell[item[1]][item[0]-1]+1
            else:
                filesmell[item[1]] = [0,0,0,0,0,0,0,0,0,0,0,0,0]
                filesmell[item[1]][item[0]-1] = 1

        for k in filesmell:
            smell_info.writerow([k[(len(sourcedir)+1):]]+filesmell[k]+[sum(filesmell[k])])

        logfile.write("LongParameterList: "+ str(count[1]) + "\n")
        logfile.write("LongMethod: "+ str(count[2]) + "\n")
        logfile.write("LongScopeChaining: "+ str(count[3]) + "\n")
        logfile.write("LongBaseClassList: "+ str(count[4]) + "\n")
        logfile.write("LargeClass: "+ str(count[5]) + "\n")
        logfile.write("UselessExceptionHandling: "+ str(count[7]) + "\n")
        logfile.write("ComplexLambdaExpression: "+ str(count[9]) + "\n")
        logfile.write("LongTernaryConditionalExpression: "+ str(count[10]) + "\n")
        logfile.write("ComplexContainerComprehension: "+ str(count[11]) + "\n")
        logfile.write("ViolatedMagicMethod: "+ str(count[12]) + "\n")
        logfile.write("LongMessageChain: "+ str(count[13]) + "\n")
        logfile.write("MultiplyNestedContainer: "+ str(count[6]) + "\n")
        logfile.write("UnusedImport: "+ str(count[8]) + "\n")
        logfile.write("total: "+ str(len(myast.result)) + "\n")

        logfile.close()
        LongParameterList.close()
        LongMethod.close()
        LongScopeChaining.close()
        LongBaseClassList.close()
        LargeClass.close()
        UselessExceptionHandling.close()
        ComplexLambdaExpression.close()
        LongTernaryConditionalExpression.close()
        ComplexContainerComprehension.close()
        LongMessageChain.close()
        MultiplyNestedContainer.close()
        ViolatedMagicMethod.close()
        UnusedImport.close()

