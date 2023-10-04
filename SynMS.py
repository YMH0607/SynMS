from utlis.gameInit import *
import time
import numpy
import xlrd
from xlwt import *
from xlrd import *
from xlrd import open_workbook
from utlis.getExpressSion import *
from func_timeout import func_set_timeout
from utlis.generate_WCNF import genetate_formula_wcnf
import copy
from xlutils.copy import copy as xlutcopy
from utlis.duplicationFeaturePool import duplicationFeaturePool
def ConstantInExpression(exp):
    temp=exp.replace('-','*').replace('+','*')
    temp = temp.split('*')
    for expression in temp :
        try:
            int(expression)
            return True
        except:
            continue
    return False
def generateFeaturePool(Exp):
    result = []
    t1=time.time()
    hashset = set()

    for constantTerm in Exp['constantTermSet']:
        for expression in Exp['expressionSet']:
            Atom = str(expression) + '==' + str(constantTerm)
            if Atom not in hashset:
                result.append(Atom)
                hashset.add(Atom)
            Atom = str(expression) + '>=' + str(constantTerm)
            if Atom not in hashset:
                result.append(Atom)
                hashset.add(Atom)

                # Atom = str(e1) +'%'+ str(e2)+'=='
            for constantTerm2 in range(0,constantTerm): 
                if ('+' in expression or '-' in expression):
                    Atom = '('+str(expression)+')' + '%' + str(constantTerm) +'=='+str(constantTerm2)
                else:
                    Atom = str(expression) + '%' + str(constantTerm) +'=='+str(constantTerm2)
                if Atom not in hashset:
                    result.append(Atom)
                    hashset.add(Atom)
    for expression1 in Exp['expressionSet']:
        if(len(expression1)<10):
            for expression2 in Exp['expressionSet']:
                if(len(expression2)<10):
                    if(not ConstantInExpression(expression1) and not ConstantInExpression(expression2)):
                        Atom = str(expression1) + '==' + str(expression2)
                        if Atom not in hashset:
                            result.append(Atom)
                            hashset.add(Atom)
                        Atom = str(expression1) + '>=' + str(expression2)
                        if Atom not in hashset:
                            result.append(Atom)
                            hashset.add(Atom)
                        Atom = str(expression1) + '<=' + str(expression2)
                        if Atom not in hashset:
                            result.append(Atom)
                            hashset.add(Atom)
    t2=time.time()
    print('特征生成耗时',t2-t1)
    print('特征数量',len(result))
    return result


def expandPool(Exp):
    result = copy.copy(Exp)
    constantTermSet=copy.copy(Exp['constantTermSet'])
    expressionSet=copy.copy(Exp['expressionSet'])
    for expression1 in Exp['expressionSet']:
        for expression2 in Exp['expressionSet']:
            newExpression = expression1+'+'+expression2
            if(len(newExpression)<10):
                if(newExpression not in expressionSet):
                    expressionSet.append(newExpression)
                if(expression1 != expression2):
                    newExpression = expression1+'-'+'('+expression2+')'
                    if(newExpression not in expressionSet):
                        expressionSet.append(newExpression)

    # for constantTerm in Exp['constantTermSet']:
    #     for expression in Exp['expressionSet']:
    #         newExpression = expression+'+'+str(constantTerm)
    #         if(newExpression not in expressionSet and constantTerm != 0):
    #             print(result)
    #             expressionSet.append(newExpression)

    for constantTerm1 in Exp['constantTermSet']:
        for constantTerm2 in Exp['constantTermSet']:
            newConstantTerm = constantTerm1+constantTerm2
            if(newConstantTerm not in constantTermSet):
                constantTermSet.append(newConstantTerm)
    
    result={
        'constantTermSet': constantTermSet,
        'expressionSet' : expressionSet
    }
    print('特征池扩充，当前特征变量',result)
    return result


# 返回值 为真 验证成功
def ValidationPolicy(e):
    e1 = eval(e.replace("X1", "Y1").replace("X2", "Y2").replace("X", "Y"))
    e=eval(e)
    # print(e1,'e1')
    if Game["type"] == "normal":
        # e is losing formula
        # 取定义中的取反 unsat 就是我们想要的
        con1 = And(Game["Constraint"],Game["Terminal_Condition"], Not(e))
        # con1 = Not(Implies(Game['Terminal_Condition'],e))
        con2 = Not(Implies(And(Game["Constraint"], Not(e)), Exists(
            Game['varListY'], And(game.global_transition_formula, e1))))
        # 必胜态情况
        # con2 = And(Game["Constraint"], Not(e), ForAll(
        #     varListY, Or(Not(global_transition_formula), Not(e1))))
        # 必败态
        con3 = And(Game["Constraint"], e, Not(Game["Terminal_Condition"]), Exists(
            Game['varListY'], And(game.global_transition_formula, e1)))

        # con3 =Not(Implies(And(Game["Constraint"],e),ForAll(
        #     varListY, Implies(global_transition_formula, Not(e1)))))
    else:
        con1 = And(Game["Constraint"],Game["Terminal_Condition"], e)
        # con2 = And(Game["Constraint"], Not(e), Not(Game["Terminal_Condition"]), ForAll(varListY, Implies(global_transition_formula, Not(e1))))
        con3 = And(Game["Constraint"], e), Exists(
            Game['varListY'], And(game.global_transition_formula, e1))
        # con1 = Not(Implies(Game['Terminal_Condition'],Not(e)))
        con2 = Not(Implies(And(Game["Constraint"], Not(e), Not(Game["Terminal_Condition"])), Exists(
            Game['varListY'], And(game.global_transition_formula, e1))))

    s = Solver()
    s.set('timeout', 60000)
    s.add(con1)
    check1 = s.check()
    if check1 == sat:
        print("unsat con1")
        return False
    else:
        print("sat con1")

        s = Solver()
        s.set('timeout', 60000)
        s.add(con2)
        check2 = s.check()
        print("con2 check:", check2)
        if check2 == sat:
            print("unsat con2")
            m = s.model()
            if(Game['var_num']==1):
                return [m[X].as_long()]
            if(Game['var_num']==2):
                return [m[X].as_long(), m[X1].as_long()]
            if(Game['var_num']==3):
                return [m[X].as_long(), m[X1].as_long(),m[X2].as_long()]
        else:
            print("sat con2")

            s = Solver()
            s.set('timeout', 60000)
            s.add(con3)
            check3 = s.check()
            if check3 == sat:
                print("unsat con3")
                m = s.model()
                if(Game['var_num']==1):
                    return [m[X].as_long()]
                if(Game['var_num']==2):
                    return [m[X].as_long(), m[X1].as_long()]
                if(Game['var_num']==3):
                    return [m[X].as_long(), m[X1].as_long(),m[X2].as_long()]
            else:
                print("sat con3")
                print('con3:', check3)

                return True


WinningFormulaStart = time.time()
time_out1 = 400

pddlFile =sys.argv[1] #由文件main.py输入路径
resultFile =sys.argv[2]
game_type=sys.argv[3]

# pddlFile = r"domain/4.Wythoff/4.6/(l,m)-1st-Odd-Odd-wythoff(l-3,m-4)v2-1.pddl" 
# pddlFile = r"domain/4.Wythoff/4.2/Odd-Even-l(1)-wythoff-v2-le-4.pddl" 
# pddlFile = r"domain/3.Welter/3.1 Welter Game/Welter(n=2).pddl" 
# pddlFile = r"domain/2.Nim/2.8 l-Slow Nim/Two-piled-22-slow-nim.pddl" 
# pddlFile = r"domain/2.Nim/2.17 Staircase Nim/Three-staircase.pddl" 


#  # 执行单个pddl
# pddlFile = r"domain/2.Nim/2.1 Nim/Two-piled-nim.pddl"  # 执行单个pddl
# domain/1.Sub/1.3S,D-MarkGame/t,d-i-Mark-Game{2,2}.pddl
# pddlFile = r"domain\1.Sub\1.2 Subtraction\Subtraction-(1,2,4,5).pddl"  # 执行单个pddl
# pddlFile = r"domain/1.Sub/1.3S,D-MarkGame/T,d-I-Mark-Game{2,2}.pddl"  # 执行单个pddl
# pddlFile = r"domain/1.Sub/1.2Subtraction/Subtraction-(2,4,6,10).pddl"  #两个参数游戏
# pddlFile = r"domain/domain/4.Wythoff/4.9/Even-Even-Wyt[1,2]v2-4.pddl"  # 执行单个pddl

# game_type = 'normal'
# resultFile='result.txt'

# wb = open_workbook(resultFile, encoding_override='utf-8')
# new_workbook = xlutcopy(wb) 
# new_worksheet = new_workbook.get_sheet(0)
# sheet1 = wb.sheet_by_index(0)
# row = sheet1.nrows
frequency = 2
game_name = pddlFile.split('\\')[-1].split('.pddl')[0]
print(game_name)
# 打开文件夹
rb = xlrd.open_workbook(resultFile, encoding_override='utf-8')
r_sheet = rb.sheet_by_index(0)
cur_row = r_sheet.nrows
wb = xlutcopy(rb)
f = wb.get_sheet(0)
f.write(cur_row, 0, game_name)
wb.save(resultFile)
game = GameClass(pddlFile, game_type, frequency)
# f = open(resultFile, 'a')

# sys.exit('exit')
Game = game.Game

print(Game)
winSet = game.winSet
loseSet = game.loseSet
featurePool = []
expression={
    'constantTermSet':[0,1],
    'expressionSet':[]
}
for constant in Game['appeal_constants']:
    if(constant not in expression['constantTermSet']):
        expression['constantTermSet'].append(int(constant))
    if(int(constant)+1 not in expression['constantTermSet']):
        expression['constantTermSet'].append(int(constant)+1)
    for constant2 in Game['appeal_constants']:
        if(int(constant)+int(constant2) not in expression['constantTermSet']):
            expression['constantTermSet'].append(int(constant)+int(constant2) )

if Game['var_num'] == 1:
    expression['expressionSet']=['X']
if Game['var_num'] == 2:
    expression['expressionSet']=['X','X1']
if Game['var_num'] == 3:
    expression['constantTermSet']=[0,1,2,3,4,5,6,7,8,9]
    expression['expressionSet']=['X', 'X1', 'X2', 'X+X1', 'X+X2', 'X1+X2', 'X2-(X1)', 'X2-(X)', 'X1-(X)', 'X1-(X2)', 'X-(X1)', 'X-(X2)', 'X+X', 'X+X+X1', 'X-(X+X1)', 'X+X+X2', 'X-(X+X2)', 'X+X1+X2', 'X-(X1+X2)', 'X+X2-(X1)', 'X-(X2-(X1))', 'X-(X2-(X))', 'X-(X1-(X))', 'X1+X1', 'X1+X+X1', 'X1-(X+X1)', 'X1-(X+X2)', 'X1+X1+X2', 'X1+X2-(X)', 'X1+X1-(X)', 'X2+X2', 'X2-(X+X1)', 'X2+X+X2', 'X2+X1+X2', 'X2+X2-(X)', 'X+X1+X+X1', 'X+X1+X+X2', 'X+X2+X+X2', 'X2-(X)-(X)', 'X1-(X)-(X)', 'X-(X1)-(X1)', 'X-(X2)-(X2)']

            
winning_formula_of_game=''
while(frequency < 4):
    print(expression,'expression')
    featurePool= generateFeaturePool(expression)
    # print(featurePool)

    featurePool = duplicationFeaturePool(featurePool,winSet,loseSet)
    print('去除无效特征后数量',len(featurePool))
    # print(featurePool)

    if(len(winSet)==0):
        winning_formula, losing_fomula='False','True'
    else:
        try:
            winning_formula, losing_fomula = genetate_formula_wcnf(winSet,loseSet,featurePool)
            if(winning_formula=='timeout'):
                f.write(cur_row, 1, "time out")
                # f.close()
                wb.save(resultFile)
                sys.exit('time out')
        except:
            f.write(cur_row, 1, "time out")
            # f.close()
            wb.save(resultFile)
            sys.exit('time out')
    if(winning_formula==''):
        expression=expandPool(expression)
        continue
    result_of_win = ValidationPolicy('Not('+winning_formula+')')
    if (result_of_win == True):
        print("winnig_formula验证成功")
        print(featurePool)
        winning_formula_of_game=winning_formula
        WinningFormulaTime_cost = round((time.time() - WinningFormulaStart), 3)
        # f.write(game_name + '\t' +winning_formula + '\t' +str(WinningFormulaTime_cost)+'\n')
        # f.close()

        f.write(cur_row, 1, winning_formula)
        f.write(cur_row, 2, str(WinningFormulaTime_cost))
        wb.save(resultFile)


        print('winning formula generate time cost', WinningFormulaTime_cost)
        break
    print(result_of_win)
    result_of_lose = ValidationPolicy(losing_fomula)
    if (result_of_lose == True):
        winning_formula='Not('+losing_fomula+')'
        winning_formula_of_game=winning_formula
        print("losing_fomula_验证成功")
        WinningFormulaTime_cost = round((time.time() - WinningFormulaStart), 3)
        # f.write(game_name + '\t' +winning_formula + '\t' +str(WinningFormulaTime_cost)+'\t' +'\n')
        # f.close()
        f.write(cur_row, 1, winning_formula)
        f.write(cur_row, 2, str(WinningFormulaTime_cost))
        wb.save(resultFile)
        break
    else:
        print('Winning formula验证失败，添加反例',result_of_win,result_of_lose)
        # expression=expandPool(expression)
        if(Game['var_num']==1):
            if(game.isLossingState(result_of_win[0])):
                loseSet.append(result_of_win[0])
            else:
                winSet.append(result_of_win[0])
            if(game.isLossingState(result_of_lose[0])):
                loseSet.append(result_of_lose[0])
            else:
                winSet.append(result_of_lose[0])
        if(Game['var_num']==2):
            if(game.isLossingState(result_of_win[0], result_of_win[1])):
                loseSet.append([result_of_win[0], result_of_win[1]])
            else:
                winSet.append([result_of_win[0], result_of_win[1]])
            if(game.isLossingState(result_of_lose[0], result_of_lose[1])):
                loseSet.append([result_of_lose[0], result_of_lose[1]])
            else:
                winSet.append([result_of_lose[0], result_of_lose[1]])
        if(Game['var_num']==3):
            if(game.isLossingState(result_of_win[0], result_of_win[1], result_of_win[2])):
                loseSet.append([result_of_win[0], result_of_win[1], result_of_win[2]])
            else:
                winSet.append([result_of_win[0], result_of_win[1], result_of_win[2]])
            if(game.isLossingState(result_of_lose[0], result_of_lose[1], result_of_lose[2])):
                loseSet.append([result_of_lose[0], result_of_lose[1], result_of_lose[2]])
            else:
                winSet.append([result_of_lose[0], result_of_lose[1], result_of_lose[2]])
        print(winSet)


# new_workbook.save(resultFile)
strategy_start = time.time()
strategy_start_wormap = time.time()

tryTimes=0
WinnigStrategy=[]
workMap=[]
while(tryTimes<6):
    workMap = game.generateActionWorkMap(workMap)
    # sys.exit('22')
    for actionMap in workMap:
        # actionClass = ExpressionClass(Game,featurePool,actionMap,winning_formula_of_game) 
        if not actionMap["isWinning"]:

            actionMap["winning_formula"],actionMap["losing_fomula"] = genetate_formula_wcnf(actionMap["workSet"],actionMap['notWorkSet'],featurePool)
        if actionMap["winning_formula"] == '':
            actionMap['Valid'] = False
        else:
            actionMap['Valid'] = True

    WinnigStrategy=[]
    print(workMap)
    for actionMap in workMap:
        print(actionMap)
        if(actionMap['Valid']):
            #检查是否有状态无法执行此动作
            s = Solver()
            s.add(Game['Constraint'])
            s.add(Not(Game['Terminal_Condition']))
            s.add(Not(actionMap['precondition']))
            if(actionMap['paramNumber']==1):
                s.add(actionMap['paramName']==actionMap['actionParam'])
            if(actionMap['paramNumber']==2):
                s.add(actionMap['paramName'][0]==actionMap['actionParam'][0])
                s.add(actionMap['paramName'][1]==actionMap['actionParam'][1])

            
            s.add(eval(actionMap['winning_formula'])) 
            if (s.check() == sat):
                m = s.model()
                print('当前状态无法执行：',m)
                if(Game['var_num']==1):
                    actionMap['notWorkSet'].append(m[X].as_long())
                if(Game['var_num']==2):
                    actionMap['notWorkSet'].append([m[X].as_long(),m[X1].as_long()])
                if(Game['var_num']==3):
                    actionMap['notWorkSet'].append([m[X].as_long(),m[X1].as_long(),m[X2].as_long()])
                continue
            
            

            



            #验证规则是否Winning
            winning_formula_of_game_Y = (winning_formula_of_game.replace("X1", "Y1").replace("X2", "Y2").replace("X", "Y"))
            s = Solver()
            s.add(Game['Constraint'])
            s.add(Not(Game['Terminal_Condition']))
            if(actionMap['paramNumber']==1):
                s.add(actionMap['paramName']==actionMap['actionParam'])
            if(actionMap['paramNumber']==2):
                s.add(actionMap['paramName'][0]==actionMap['actionParam'][0])
                s.add(actionMap['paramName'][1]==actionMap['actionParam'][1])
            s.add(actionMap['transition_formula'])
            s.add(actionMap['precondition'])
            s.add(eval(actionMap['winning_formula']))  
            s.add(eval(winning_formula_of_game_Y))
            if (s.check() == sat):
                m = s.model()
                print('当前子策略不完备，以下状态无法获胜：',m)
                if(Game['var_num']==1):
                    actionMap['notWorkSet'].append(m[X].as_long())
                if(Game['var_num']==2):
                    actionMap['notWorkSet'].append([m[X].as_long(),m[X1].as_long()])
                if(Game['var_num']==3):
                    actionMap['notWorkSet'].append([m[X].as_long(),m[X1].as_long(),m[X2].as_long()])
            # s.add(actionMap["transition_formula"])
            else:
                print('当前子策略验证完备')
                actionMap["isWinning"]=True
        elif(not actionMap['Valid']):
            s = Solver()
            s.add(Game['Constraint'])
            s.add(Not(Game['Terminal_Condition']))
            s.add(eval(winning_formula_of_game))
            if(actionMap['paramNumber']==1):
                s.add(actionMap['paramName']==actionMap['actionParam'])
            if(actionMap['paramNumber']==2):
                s.add(actionMap['paramName'][0]==actionMap['actionParam'][0])
                s.add(actionMap['paramName'][1]==actionMap['actionParam'][1])
            s.add(actionMap['precondition'])
            if (s.check() == sat):
                m = s.model()
                print('当前状态可以执行：',m)
                if(Game['var_num']==1):
                    game.winSet.append(m[X].as_long())
                if(Game['var_num']==2):
                    game.winSet.append([m[X].as_long(),m[X1].as_long()])
                if(Game['var_num']==3):
                    game.winSet.append([m[X].as_long(),m[X1].as_long(),m[X2].as_long()])
        
        
        if(actionMap["isWinning"]):
            WinnigStrategy.append(actionMap["actionName"]+'('+str(actionMap['actionParam'])+')'+':'+actionMap['winning_formula'])


    valid_strategy_start = time.time()     

    s = Solver()
    s.add(eval(winning_formula_of_game))
    s.add(Game['Constraint'])
    s.add(Not(Game['Terminal_Condition']))
    for actionMap in workMap:
        if(actionMap['Valid'] and actionMap['isWinning']):
            s.add(eval('Not('+actionMap['winning_formula']+')'))
    if (s.check() == sat):
        m = s.model()
        print('当前策略不完备，以下状态不存在：',m)
        if(Game['var_num']==1):
            game.winSet.append(m[X].as_long())
        if(Game['var_num']==2):
            game.winSet.append([m[X].as_long(),m[X1].as_long()])
        if(Game['var_num']==3):
            game.winSet.append([m[X].as_long(),m[X1].as_long(),m[X2].as_long()])
        tryTimes+=1
        if(tryTimes==6):
            # f = open(resultFile, 'a')
            # f.write(str(WinnigStrategy) + '\t' +str('Failed to verify policy ,timeout') + '\n')
            # f.close()
            f.write(cur_row, 4, str(WinnigStrategy))
            f.write(cur_row, 5, "time out")
            wb.save(resultFile)
            break
            # new_worksheet.write(row,3,str(WinnigStrategy))
            # new_worksheet.write(row,4,str('策略验证失败，超时'))
        continue


    else:
        print('策略验证成功，包含所有必胜点')
        strategy_time_cost = round((time.time() - strategy_start), 3)
        # f = open(resultFile, 'a')
        # f.write(str(WinnigStrategy) + '\t' +str(strategy_time_cost) + '\n')
        # f.close()
        f.write(cur_row, 4, str(WinnigStrategy))
        f.write(cur_row, 5, str(strategy_time_cost))
        wb.save(resultFile)

        # new_worksheet.write(row,3,str(WinnigStrategy))
        # new_worksheet.write(row,4,str(strategy_time_cost))
        break



