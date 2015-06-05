import ast,_ast
import re
import customast
import astunparse
import yaml

stream = open("config",'r')
config = yaml.load(stream)

class MyAst(ast.NodeVisitor):
    def __init__(self):
        self.fileName = None
        self.defmagic = set()
        self.usedmagic = set()
        self.subscriptnode = None #avoid replicate node code smell reports
        self.messagenode = None #avoid replicate node code smell reports
        self.imports = set()
        self.result = []

    def visit_ClassDef(self,node):
        className = node.name
        baseClassesSize = len(node.bases)
        if baseClassesSize >= config['baseclass']:
            self.result.append((4,self.fileName,node.lineno,className))
        self.generic_visit(node) 

    def visit_Lambda(self,node):
        expr = astunparse.unparse(node)
        exprLength = len(expr.strip()) - expr.count(' ') - 2
        if exprLength >= config['lambdalength']:
          self.result.append((9,self.fileName,node.lineno,exprLength))
        self.generic_visit(node) 

    def visit_TryExcept(self,node):
        exceptions = ["BaseException","Exception","StandardError"]
        generalFlag = True
        for item in node.handlers:
            if astunparse.unparse(item.body[0]).strip() == "pass":
                # print "pass"
                self.result.append((7,self.fileName,node.lineno,-1))
                self.generic_visit(node) 
                return
            if item.type is not None:
                if isinstance(item.type,_ast.Tuple):
                    # print "a tuple exceptions"
                    for e in item.type.elts:
                        if hasattr(e,"id") and e.id in exceptions:
                            # print "general in tuple:",e.id
                            self.result.append((7,self.fileName,node.lineno,-1))
                            self.generic_visit(node) 
                            return
                    # print "not general in tuple"
                    generalFlag = False
                elif (hasattr(item.type,"id") and item.type.id in exceptions) is False:
                    generalFlag = False
        if generalFlag:
            # print "general"
            self.result.append((7,self.fileName,node.lineno,-1))
        self.generic_visit(node) 

    def visit_FunctionDef(self,node):
      def findCharacter(s,d):
        try:
          value = s.index(d)
        except ValueError:
          return -1
        else:
          return value
      funcName = node.name.strip()
      p = re.compile("^(__[a-zA-Z0-9]+__)$")
      if p.match(funcName.strip()) and funcName != "__import__" and funcName != "__all__":
        self.defmagic.add((funcName,self.fileName,node.lineno))
      stmt = astunparse.unparse(node.args)
      arguments = stmt.split(",")
      argsCount = 0
      for element in arguments:
        if findCharacter(element,'=') == -1:
          argsCount += 1
      if argsCount > config['parametersize']:
          self.result.append((1,self.fileName,node.lineno,funcName,argsCount))
      self.generic_visit(node) 

    def visit_Call(self,node):
      # stmt = astunparse.unparse(node)
      # regexone = re.compile('\(+.*\)+')
      # regextwo = re.compile('\"+.*\"+')
      # regexthree = re.compile('\'+.*\'+')
      # p = re.compile("(__[a-zA-Z0-9]+__)")
      # poststmt = regexone.sub('',stmt)
      # poststmt = regextwo.sub('',poststmt)
      # poststmt = regexthree.sub('',poststmt)
      funcName = astunparse.unparse(node.func).strip()
      p = re.compile("^(__[a-zA-Z0-9]+__)$")
      # if p.match(poststmt):
      if p.match(funcName) and funcName != "__import__" and funcName != "__all__":
        # print p.match(funcName).groups()
        # self.usedmagic.add((p.match(poststmt).groups()[0],self.fileName,str(node.lineno)))
        self.usedmagic.add((funcName,self.fileName,node.lineno))
      # chains = poststmt.count('.') + 1
      # if chains >= config['messagechain']:
      #   self.result.append((13,self.fileName,str(node.lineno),chains))
      self.generic_visit(node)

    def visit_ListComp(self,node):
        count = 0
        expr = astunparse.unparse(node)
        exprLength = len(expr.strip()) - expr.count(' ')
        # print exprLength
        if exprLength >= config['complength']:
            self.result.append((11,self.fileName,node.lineno,exprLength))
            self.generic_visit(node) 
            return
        for item in expr.split(" "):
            if item.strip() == "if" or item.strip() == "for":
                count += 1
        # print count 
        if count >= config['compcomplexity']:
            self.result.append((11,self.fileName,node.lineno,count))
        self.generic_visit(node)  
           
    def visit_SetComp(self,node):
        self.visit_ListComp(node)

    def visit_DictComp(self,node):
        self.visit_ListComp(node)

    def visit_GeneratorExp(self,node):
        self.visit_ListComp(node)

    def visit_IfExp(self,node):
      elseblock = node.orelse
      if elseblock:
        if elseblock.lineno == node.lineno:
            stmt = astunparse.unparse(node)
            exprLength = len(stmt.strip()) - stmt.count(' ') - 2
            if exprLength >= config['ifinrowexp']:
                self.result.append((10,self.fileName,node.lineno,exprLength))
      self.generic_visit(node) 

    def visit_Subscript(self,node):
      if self.subscriptnode is not None:
        repnode = list(ast.walk(self.subscriptnode))
        if node in repnode:
          self.generic_visit(node)
          return
      self.subscriptnode = node
      t = ast.iter_child_nodes(node)
      res = [[t,0]]
      maxcount = 1
      while len(res) >= 1:
        t = res[-1][0]
        for childnode in t:
          # print childnode
          if isinstance(childnode, _ast.Subscript) or isinstance(childnode, _ast.Tuple) or \
           isinstance(childnode, _ast.Dict) or isinstance(childnode, _ast.List) or isinstance(childnode, _ast.Set):
            res[-1][1] = 1
          else:
            res[-1][1] = 0
          res.append([ast.iter_child_nodes(childnode),0])
          break
        else:
          maxcount = max(maxcount,sum([flag for (item,flag) in res]) + 1)
          res.pop()
        continue
      # print maxcount
      if maxcount >= config['containerdepth']:
        self.result.append((6,self.fileName,node.lineno,maxcount))
      self.generic_visit(node) 

    def visit_List(self,node):
      self.visit_Subscript(node)

    def visit_Tuple(self,node):
      self.visit_Subscript(node)

    def visit_Dict(self,node):
      self.visit_Subscript(node)

    def visit_Set(self,node):
      self.visit_Subscript(node) 

    def visit_Attribute(self,node):
      if self.messagenode is not None:
        repnode = list(ast.walk(self.messagenode))
        if node in repnode:
          self.generic_visit(node)
          return
      self.messagenode = node
      t = ast.iter_child_nodes(node)
      res = [[t,0]]
      maxcount = 1
      while len(res) >= 1:
        t = res[-1][0]
        for childnode in t:
          # print childnode
          if isinstance(childnode, _ast.Attribute):
            res[-1][1] = 1
          else:
            res[-1][1] = 0
          res.append([ast.iter_child_nodes(childnode),0])
          break
        else:
          maxcount = max(maxcount,sum([flag for (item,flag) in res]) + 2)
          res.pop()
        continue
      # print maxcount
      if maxcount >= config['messagechain']:
        self.result.append((13,self.fileName,node.lineno,maxcount))
      self.generic_visit(node)

    def visit_Import(self,node):
      if self.fileName[-12:] == '\\__init__.py':
        self.generic_visit(node)
        return
      for alias in node.names:
        if len(alias.name)>4 and alias.name[0:2] == '__' and alias.name[-2:] == '__':
            continue
        if alias.asname is not None:
          for (name,file,lineno) in self.imports:
            if name==alias.asname and self.fileName==file:
              break
          else:
            self.imports.add((alias.asname,self.fileName,node.lineno))
        elif alias.name != '*':
          for (name,file,lineno) in self.imports:
            if name==alias.name and self.fileName==file:
              break
          else:
            self.imports.add((alias.name,self.fileName,node.lineno))
      self.generic_visit(node)

    def visit_ImportFrom(self,node):
      if self.fileName[-12:] == '\\__init__.py':
        self.generic_visit(node)
        return
      try:
        if node.module is not None and len(node.module)>4 and node.module[0:2] == '__' and node.module[-2:] == '__':
          self.generic_visit(node)
          return
      except:
        print astunparse.unparse(node)
      for alias in node.names:
        if len(alias.name)>4 and alias.name[0:2] == '__' and alias.name[-2:] == '__':
            continue
        if alias.asname is not None:
          for (name,file,lineno) in self.imports:
            if name==alias.asname and self.fileName==file:
              break
          else:
            self.imports.add((alias.asname,self.fileName,node.lineno))
        elif alias.name != '*':
          for (name,file,lineno) in self.imports:
            if name==alias.name and self.fileName==file:
              break
          else:
            self.imports.add((alias.name,self.fileName,node.lineno))
      self.generic_visit(node)

if __name__ == '__main__':
    myast = MyAst()
    astContent = customast.parse_file('C:\\Users\\JOJO\\Desktop\\pysmell\\detection\\test.py')
    myast.fileName = "C:\\Users\\JOJO\\Desktop\\pysmell\\detection\\test.py"
    myast.visit(astContent)
    print myast.imports
    # print myast.defmagic
    # print myast.usedmagic
    # for useitem in myast.usedmagic:
    #   for defitem in myast.defmagic:
    #     if useitem[0] == defitem[0]:
    #       break
    #   else:
    #     myast.result.append((12,useitem[1],useitem[2],useitem[0]))

    # print myast.result