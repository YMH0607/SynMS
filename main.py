import os
import sys
import subprocess
import xlrd
from xlwt import *
from xlrd import *
from xlutils.copy import copy
import pandas as pd
import re

approach = sys.argv[1]

PDDLFolder =sys.argv[2]

resultFile =sys.argv[3]

gameType = sys.argv[4]


# the fourth method: python main.py SynMS.py "domain-拆开\1.Sub" "result\SynMS_misere_sub_welter_chomp.xls" "misere"
# the fourth method: python main.py SynMS.py "domain-拆开\4.Wythoff-1" "result\SynMS_misere_wythoff1.xls" "misere"
# the fourth method: python main.py SynMS.py "domain-拆开\4.Wythoff-2" "result\SynMS_misere_wythoff2.xls" "misere"
# the fourth method: python main.py SynMS.py "domain-拆开\4.Wythoff-3" "result\SynMS_misere_wythoff3.xls" "misere"
# the fourth method: python main.py SynMS.py "domain-拆开\4.Wythoff-4" "result\SynMS_misere_wythoff4.xls" "misere"


PDDLlist = os.listdir(PDDLFolder)
PDDLlist = sorted(PDDLlist,key=None)

def needJump(pddl) :
    name = pddl[:-5]
    oldwb = xlrd.open_workbook(resultFile, encoding_override='utf-8')
    sheet1 = oldwb.sheet_by_index(0)
    row = sheet1.nrows - 1                          
    # print(row)
    if row == -1:
        return False  
    df = pd.read_excel(resultFile, header=None)
    if name in df.iloc[:,0].values:
        return True
    timeString = "" if len(sheet1.row_values(row)) <= 2 else sheet1.row_values(row)[2]
    if re.match(r'^-?\d+\.?\d*$', str(timeString)) and 0 < float(timeString)  < 1200:
        return False
    else:
        fail_game_name = sheet1.row_values(row)[0]
       
        if  is_one_char_diff(fail_game_name, pddl[:-5]) and "Sub" not in pddl[:-5]:
            
            newwb = copy(oldwb)
            sheet1 = newwb.get_sheet(0)
            sheet1.write(row + 1, 0, pddl[:-5])
            sheet1.write(row + 1, 6, "J-C")
            newwb.save(resultFile)
            
            return True
        else:
            
            return False

def is_one_char_diff(str1, str2):
    if len(str1) == len(str2) - 1:
       
        for i in range(len(str1)):
            if str1[i] != str2[i]:
                return str1 == str2[:i] + str2[i+1:]  
        return True
    elif len(str2) == len(str1) - 1:
        
        for i in range(len(str2)):
            if str2[i] != str1[i]:
                return str2 == str1[:i] + str1[i+1:]  
        return True
    elif len(str1) == len(str2):
       
        count_diff = 0  
        for i in range(len(str1)):
            if str1[i] != str2[i]:
                count_diff += 1
                if count_diff > 1:
                    return False 
        return count_diff == 1  
    else:
        return False

for pddl in PDDLlist:
    print(pddl)
    try:
        if 'pddl' not in pddl:    
            continue
        print("test case：", pddl)
        if needJump(pddl) == False:
            pddl = PDDLFolder+'\\'+pddl
            subprocess.call("python \"%s\" \"%s\" \"%s\" \"%s\" "%(approach, pddl, resultFile, gameType), timeout = 2400)
    except subprocess.TimeoutExpired as e:
        print('Error: Subprocess execution timed out:', e)
        continue
    except subprocess.CalledProcessError as e:
        print("Error executing subprocess:", e)
        continue
    except:
        print("other error")
        continue

