import re
import xlrd
from xlwt import *
from xlrd import *
from xlutils.copy import copy
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

def countSize(var, varpool):
    if is_number(var):
        var = float(var)
    if type(var) != type(1.0):
        return 1
    elif var in varpool:
        return 1
    else:
        return 1 + countSize(var, expandpool(varpool))

def expandpool(varpool):
    p = []
    for i in varpool:
        p.append(i)
    i = 0
    j = 0

    while i < len(varpool):

        while j < len(varpool):

            if varpool[i] + varpool[j] not in p:
                p.append(varpool[i] + varpool[j])
            j += 1
        i += 1
        j = i
    return p

def Size(expression, varpool=[0, 1]):
    count1 = 0
    str1 = expression.replace(' ', '').replace('\n', '')
    while str1.find('Not') >= 0:
        count1 += 1
        str1 = str1.replace('Not', '', 1)
    while str1.find('Or') >= 0:
        count1 += 1
        str1 = str1.replace('Or', '', 1)
    while str1.find('And') >= 0:
        count1 += 1
        str1 = str1.replace('And', '', 1)
    while str1.find('*') >= 0:
        count1 += 1
        str1 = str1.replace('*', '-', 1)
    while str1.find('+') >= 0:
        count1 += 1
        str1 = str1.replace('+', '-', 1)
    while str1.find('<=') >= 0:
        count1 += 1
        str1 = str1.replace('<=', '-', 1)
    while str1.find('>=') >= 0:
        count1 += 1
        str1 = str1.replace('>=', '-', 1)
    while str1.find('>') >= 0:
        count1 += 1
        str1 = str1.replace('>', '-', 1)
    while str1.find('<') >= 0:
        count1 += 1
        str1 = str1.replace('<', '-', 1)
    while str1.find('==') >= 0:
        count1 += 1
        str1 = str1.replace('==', '-', 1)
    while str1.find('%') >= 0:
        count1 += 1
        str1 = str1.replace('%', '-', 1)
    pattern = r"'(.*?)'"
    matches = re.findall(pattern, str1)
    for mat in matches:
        content = re.search(r'\((.*?)\)', mat).group(1)
        num = Size(content, varpool)
        count1 = count1 + num - 1
    tmpC = re.sub(r"['].*?[']", 'T',str1, 1)
    while (tmpC == str1) == 0:
        str1 = tmpC
        tmpC = re.sub(r"['].*?[']", 'T',str1, 1)
    str1 = str1.replace(',', '-').replace('(', '').replace(')', '').replace('[', '').replace(']', '')
    while True:
        if len(str1) == 0:
            break
        if len(str1) == 1:
            count1 += countSize(str1, varpool)
            break
        if len(str1) == 2 and is_number(str1[0]):
            count1 += countSize(str1, varpool)
            break
        if len(str1) == 2:
            count1 += countSize(str1, varpool)
            break
        tempvar = str1[0:str1.find('-')]
        count1 += countSize(str1[0:str1.find('-')], varpool)
        
        str1 = str1[str1.find('-') + 1:len(str1)]
    return count1


def Getvarpool(pddl):
    num = re.findall('\d+', pddl)
    num = list(set(num))
    num = list(map(int, num))
    if not (0 in num):
        num.append(0)
    if not (1 in num):
        num.append(1)
    if not (2 in num):
        num.append(2)
    return num


def GetSize(gamename, winningformula):
    if winningformula == "False" or winningformula == "True" or winningformula == "true":
        return 1
    varpool = Getvarpool(gamename)
    size = Size(winningformula, varpool)
    return size

# it is a function of preprocesing the winning strategy.
def pretreat(str_pre):
    quotes_content = re.findall(r"'(.*?)'", str_pre)
    new_quotes_content = []
    for idx, content in enumerate(quotes_content):
        if (idx + 1) % 2 == 1:  # 去除偶数对单引号
            new_quotes_content.append(content)
    new_str = str_pre
    for content in new_quotes_content:
        new_str = new_str.replace("'" + content + "'", content)
    return new_str

''' 
    "gameName" is the name of Game.
    "winning" is the winning formula or strategy that will be calculated in size. For example,
    sizeWS = GetSize(gameName,winning_formula_pred)
    (If calculating the size of the winning strategy of SynMS, it is necessary to preprocess the winning strategy first.)
'''
