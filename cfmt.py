# -*- encoding:utf-8 -*-
"""
C语言自动缩进

"""

import os
import re
filelist = os.listdir()

#C语言关键字，如果没有括号下一行缩进处理
expbra=("for","while","if","else","do","switch")

def strexpbar(s):
    """
    检查下一行是否需要缩进
    """
    if s:
        if ";" == s[-1]:
            return False
        s = re.findall(r"[\w#]+",s)
        for w in s:
            if w in expbra:
                return True
    return False


def checkcomment(line):
    """
    判断代码是否是注释，以及注释起始结束位置
    """
    global comt,comol,comtst,linecounter
    findcomtindex = 0
    while True:
        if comtst == False:
            comst = line.find("/*",findcomtindex)
            if comst >= 0:
                comt[0] = linecounter
                comt[1].append(comst)
                comtst = True
                findcomtindex = comst
            if comst == -1:
                break
        else:
            comed = line.find("*/",findcomtindex) + 2
            if comed >= 2:
                comt[2] = linecounter
                comt[3].append(comed)
                comtst = False
                findcomtindex = comed
            else:
                break
    comol = line.find("//")
    if comol > 0:
        if comt[0] == linecounter:
            if comol < comt[1][0]:
                comtst = False
                comt[0] = 0
                comt[1] = []
                if comt[2]:
                    comt[2] = 0
                    comt[3] = []

def chgfile(fname,newfiledir):
    """
    转换文件
    """
    global comt,comol,comtst,linecounter
    #默认gbk编码
    frp = open(fname,encoding = 'gbk',errors = 'ignore')
    print(fname)
    fwp = open(newfiledir+fname,"w")
    #记录缩进空格数量
    csp = 0
    #行号
    linecounter = 0
    #多行注释的起始和结束位置
    comt = [0,[],0,[]]
    #当前行是否注释部分
    comtst = False
    exp = 0
    while True:

        try:
            line = frp.readline()
        except:
            print(line)
            print("encode error:file=%s,line=%d"%(fname,linecounter))
            break
        linecounter += 1
        if not line:
            break
        line = line.strip()
        #判断当前行是否有注释，以及注释位置
        checkcomment(line)

        while not comtst:
            indexl = -1
            indexr = -1
            # '#' 后面的内容不能换行
            if '#' in line:
                notnewline = True
            else:
                notnewline = False
            # '/*' 多行注释开始
            if comt[0] == linecounter:
                lstend = 0
                for i in range(len(comt[1])):
                    indexl = line.find("{",lstend,comt[1][i])+1
                    indexr = line.find("}",lstend,comt[1][i])+1
                    lstend = comt[3][i]
                    if indexl > 0 or indexr > 0:
                        comt[1] = comt[1][i+1:]
                        comt[3] = comt[3][i+1:]
                        break
                else:
                    comt[0] = 0
                    comt[2] = 0
                    comt[1] = []
                    comt[3] = []

            # '*/' 多行注释结束
            elif comt[2] == linecounter:
                if(len(comt[3]) != 1):
                    frp.close()
                    fwp.close()
                    raise TabError(fname + "line:" + str(linecounter) + "  kks")
                indexl = line.find("{",0,)+1
                indexr = line.find("}",0,)+1
                if(indexl < comt[3][0]):
                    indexl = 0
                if(indexr < comt[3][0]):
                    indexr = 0
                comt[0] = 0
                comt[2] = 0
                comt[1] = []
                comt[3] = []
            # '//' 注释
            elif comol >= 0:
                indexl = line.find("{",0,comol)+1
                indexr = line.find("}",0,comol)+1
            else:
                indexl = line.find("{")+1
                indexr = line.find("}")+1
            if indexl > 0:
                if ('=' in line[:indexl] and indexr > 0) or notnewline:
                    lwite = " "*(csp+exp) + line
                else:
                    exp = 0
                    lwite = " "*csp + line[:indexl]
                    csp += 4
                    if len(line) > indexl:
                        line = line[indexl:].strip()
                        if line:
                            fwp.write(lwite + '\n')
                            checkcomment(line)
                            continue
            elif indexr > 0:
                if indexr > 1:
                    lwite = " "*csp + line[:indexr-1]
                    fwp.write(lwite + '\n')
                    line = line[indexr-1:]
                    indexr = 1
                exp = 0
                csp -= 4
                if csp < 0:
                    frp.close()
                    fwp.close()
                    raise TabError(fname + ",line:" + str(linecounter) + "  sj")
                lwite = " "*csp + line[:indexr]
                if (len(line) > indexr) and (not notnewline):
                    #line = line[indexr:].strip()
                    #if line:
                    #    line = line.strip()
                        if line[0:2] == "};":
                            lwite = lwite + ';'
                            line =line[indexr+1:]
                        else:
                            line =line[indexr:]
                        if line:
                            fwp.write(lwite + '\n')
                            checkcomment(line)
                            continue

            else:
                if exp:
                    lwite = " "*(csp+exp) + line
                else:
                    lwite = " "*csp + line
            if(strexpbar(line)):
                if indexl == 0:
                    exp += 4
            else:
                exp = 0
            break
        if comtst:
            fwp.write(line + '\n')
        else:
            fwp.write(lwite + '\n')
    frp.close()
    fwp.close()
if __name__ == "__main__":

    for fname in filelist:
        index = fname.rfind(".")
        if index > 0:
            suffix = fname[index:]
            if suffix == ".c" or suffix == ".h":
                chgfile(fname,"new\\")
    input()