from mailbox import Error
import os
import shutil
import re
import random

from generator import generator_nosave
from convert import convert_nosave

class Synthesizer:

    @staticmethod
    def syn_pred(env, bool_expected, depth):
        if depth <= 0:
            return Synthesizer.syn_atom(env, bool_expected)

        rnd_int = random.randint(1, 4)
        if rnd_int == 1:
            return Synthesizer.syn_neg(env, bool_expected, depth)
        elif rnd_int == 2:
            return Synthesizer.syn_con(env, bool_expected, depth)
        elif rnd_int == 3:
            return Synthesizer.syn_dis(env, bool_expected, depth)
        elif rnd_int == 4:
            pred = Synthesizer.syn_atom(env, bool_expected)
            if pred.find('False') != -1 or pred.find('True') != -1:
                print('debug')
            return pred

    @staticmethod
    def syn_neg(env, bool_expected, depth):
        return '(!' + Synthesizer.syn_pred(env, bool(1-bool_expected), depth-1) + ')'

    @staticmethod
    def syn_con(env, bool_expected, depth):
        if bool_expected:
            left = True
            right = True
        elif random.random() > 0.5:
            left = False
            right = True
        elif random.random() > 0.5:
            left = True
            right = False
        else:
            left = False
            right = False
        return '(' + Synthesizer.syn_pred(env, left, depth-1) + '&' + Synthesizer.syn_pred(env, right, depth-1) + ')'

    @staticmethod
    def syn_dis(env, bool_expected, depth):
        if not bool_expected:
            left = False
            right = False
        elif random.random() > 0.5:
            left = False
            right = True
        elif random.random() > 0.5:
            left = True
            right = False
        else:
            left = True
            right = True
        return '(' + Synthesizer.syn_pred(env, left, depth-1) + '|' + Synthesizer.syn_pred(env, right, depth-1) + ')'

    @staticmethod
    def syn_atom(env, bool_expected, two_var=True):
        var_list = list(env.keys())
        if len(var_list) == 0:
            if bool_expected:
                return '(1)'
            else:
                return '(0)'

        if len(var_list) == 1 or (not two_var) or random.random() > 0.5:  # var and truth value
            var_name = random.choice(var_list)
            if len(list(env[var_name])) == 0:
                print(var_name, 'var set is empty')
                print('line', env.line_num)

            max_val = max(list(env[var_name]))
            min_val = min(list(env[var_name]))
            if min_val == 0 and bool_expected:
                return '(' + var_name + ' <= ##' + str(max_val) + '##)'
            elif min_val == 0 and not bool_expected:
                return '(' + var_name + ' > ##' + str(max_val) + '##)'
            elif max_val == 0 and bool_expected:
                return '(' + var_name + ' >= ##' + str(min_val) + '##)'
            elif max_val == 0 and not bool_expected:
                return '(' + var_name + ' < ##' + str(min_val) + '##)'

            rnd_int = random.randint(1, 4)
            if rnd_int == 1:  # <
                if bool_expected:  # < max+1
                    t_val = max_val + min(random.randint(1, 5), abs(max_val))
                else:  # < min
                    t_val = min_val
                ### preventing overflow
                print(t_val)
                if t_val > (2**31):
                    if bool_expected:
                        return '(' + var_name + ' <= ##' + str(max_val) + '##)'
                    else:
                        return '(' + var_name + ' > ##' + str(max_val) + '##)'
                else:
                    return '(' + var_name + ' < ##' + str(t_val) + '##)'
            elif rnd_int == 2:  # >
                if bool_expected:  # > min-1
                    t_val = min_val - min(random.randint(1, 5), abs(min_val))
                else:  # > max
                    t_val = max_val
                ### preventing overflow
                print(t_val)
                if t_val < -(2**31):
                    if bool_expected:
                        return '(' + var_name + ' >= ##' + str(min_val) + '##)'
                    else:
                        return '(' + var_name + ' < ##' + str(min_val) + '##)'
                else:
                    return '(' + var_name + ' > ##' + str(t_val) + '##)'
            elif rnd_int == 3:  # <=
                if bool_expected:  # <= max
                    t_val = max_val
                else:  # <= min-1
                    t_val = min_val - min(random.randint(1, 5), abs(min_val))
                ### preventing overflow
                print(t_val)
                if t_val < -(2**31):
                    if bool_expected:
                        return '(' + var_name + ' >= ##' + str(min_val) + '##)'
                    else:
                        return '(' + var_name + ' < ##' + str(min_val) + '##)'
                else:
                    return '(' + var_name + ' <= ##' + str(t_val) + '##)'
            elif rnd_int == 4:  # >=
                if bool_expected:  # >= min
                    t_val = min_val
                else:  # >= max+1
                    t_val = max_val + min(random.randint(1, 5), abs(max_val))
                print(t_val)
                if t_val > (2**31):
                    if bool_expected:
                        return '(' + var_name + ' <= ##' + str(max_val) + '##)'
                    else:
                        return '(' + var_name + ' > ##' + str(max_val) + '##)'
                else:
                    return '(' + var_name + ' >= ##' + str(t_val) + '##)'
        else:  # var and var
            for i in range(5):  # try 5 times at most
                # get two different var
                var_name1 = random.choice(var_list)
                var_name2 = random.choice(var_list)
                while var_name1 == var_name2:
                    var_name2 = random.choice(var_list)
                # analyze their relation
                val_list1 = list(env[var_name1])
                val_list2 = list(env[var_name2])
                # for debug
                if len(val_list1) == 0:
                    print(var_name1, 'var set is empty')
                    print('line', env.line_num)
                elif len(val_list2) == 0:
                    print(var_name2, 'var set is empty')
                    print('line', env.line_num)

                max1 = max(val_list1)
                min1 = min(val_list1)
                max2 = max(val_list2)
                min2 = min(val_list2)
                if max1 < min2 and ((max1 > 0 and min2 > 0) or (max1 < 0 and min2 < 0)):  # both plus or both minus
                    if bool_expected:
                        return '(' + var_name1 + ' < ' + var_name2 + ')'
                    else:
                        return '(' + var_name1 + ' > ' + var_name2 + ')'
                elif max2 < min1 and ((max2 > 0 and min1 > 0) or (max2 < 0 and min1 < 0)):
                    if bool_expected:
                        return '(' + var_name2 + ' < ' + var_name1 + ')'
                    else:
                        return '(' + var_name2 + ' > ' + var_name1 + ')'
            return Synthesizer.syn_atom(env, bool_expected, False)

def generate_block(env, exp_name, templete = 'gen_block_templete.py', block_num = None, block_type = None):
    no_pint = True
    special_variables = ''
    for var_name in env:
        special_variables += '<special_var_bl> = ' + var_name + '\n'
    templete = open(templete)
    grammar_block = ''
    while True:
        line = templete.readline()
        if not line:
            break
        if line.find('# Specify the special variabal') != -1:
            grammar_block += line
            grammar_block += special_variables
        elif line.find('!varformat varblock%04d') != -1:
            grammar_block += line.split('%')[0] + str(block_num) + '%' + line.split('%')[1]
        else:
            grammar_block += line
    templete.close()
    with open('gen_block_' + exp_name + '.py', 'w') as f:
        f.write(grammar_block)
    block_content = generator_nosave('gen_block_' + exp_name + '.py')
    block_content = convert_nosave(block_content)
    return block_content

def gen_fcb(env, exp_name, templete = 'gen_block_templete.py', block_num = None):
    pred_depth = random.randint(1, 4)
    predicate = Synthesizer.syn_pred(env, False, pred_depth)
    # numbers = re.findall(r'(?<!var)-?\b\d+\b', predicate)
    numbers = re.findall(r'##-?\d+##', predicate)
    block_txt = '// False Condition Block\n'
    ### the constant number used in synthesized predicate are not allowed to calculate with secure integer, so use secure integer to carry their value
    for number in set(numbers):
        value = number[2: -2]
        if value[0] == '-':
            prevar = 'prevar' + str(block_num) + '_n' + value[1:]
        else:
            prevar = 'prevar' + str(block_num) + '_' + value
        block_txt += 'Integer ' + prevar + "(32, " + value + ", ALICE);\n"
        predicate = predicate.replace(number, prevar)
    block_txt += 'if((' + predicate + ').reveal<bool>())\n'
    block_txt += '{\n'
    block_syn = generate_block(env, exp_name, templete, block_num = block_num)
    for line in block_syn.split('\n'):
        block_txt += ' ' * 4 + line + '\n'
    block_txt += '};\n'
    # print(block_txt)
    return block_txt

def gen_tcb(env, exp_name, templete = 'gen_block_templete.py', block_num = None):
    pred_depth = random.randint(1, 4)
    predicate = Synthesizer.syn_pred(env, True, pred_depth)
    block_txt = '// True Condition Block\n'
    var_list = list(env.keys())
    ### randomly put the value backup inside or outside the block
    global_var = -1
    if random.random()<0.5:
        ### the constant number used in synthesized predicate are not allowed to calculate with secure integer, so use secure integer to carry their value
        numbers = re.findall(r'##-?\d+##', predicate)
        for number in set(numbers):
            value = number[2: -2]
            if value[0] == '-':
                prevar = 'prevar' + str(block_num) + '_n' + value[1:]
            else:
                prevar = 'prevar' + str(block_num) + '_' + value
            block_txt += 'Integer ' + prevar + "(32, " + value + ", ALICE);\n"
            predicate = predicate.replace(number, prevar)
        block_txt += 'if((' + predicate + ').reveal<bool>())\n'
        block_txt += '{\n'
        for var_name in var_list:
            block_txt += ' ' * 4 + 'Integer ' + var_name + '_back'+ str(block_num) + ' = ' + var_name + ';\n'
    else:
        for var_name in var_list:
            block_txt += 'Integer ' + var_name + '_back'+ str(block_num) + ' = ' + var_name + ';\n'
        ### the constant number used in synthesized predicate are not allowed to calculate with secure integer, so use secure integer to carry their value
        numbers = re.findall(r'##-?\d+##', predicate)
        for number in set(numbers):
            value = number[2: -2]
            if value[0] == '-':
                prevar = 'prevar' + str(block_num) + '_n' + value[1:]
            else:
                prevar = 'prevar' + str(block_num) + '_' + value
            block_txt += 'Integer ' + prevar + "(32, " + value + ", ALICE);\n"
            predicate = predicate.replace(number, prevar)
        block_txt += 'if((' + predicate + ').reveal<bool>())\n'
        block_txt += '{\n'
        global_var = 1
    block_syn = generate_block(env, exp_name, templete, block_num = block_num)
    for line in block_syn.split('\n'):
        block_txt += ' ' * 4 + line + '\n'

    ### randomly put the value backup inside or outside the block
    ### only perfom the value restore outside when the back variable is set outside the block
    if random.random()<0.5 and global_var == 1:
        block_txt += '};\n'
        for var_name in var_list:
            block_txt += var_name + '= ' + var_name + '_back' + str(block_num) + ';\n'
    else:
        for var_name in var_list:
            block_txt += ' ' * 4 + var_name + '=' + var_name + '_back' + str(block_num) + ';\n'
        block_txt += '};\n'
        
    return block_txt

def dead_code_mutate(mutate_block, mutate_block_cov, indent, p, placeholder_variable):
    if random.random()<p:
        return ''
    else:
        subbranch = -1
        branch_start = -1
        # have_branch = -1
        indent = indent + 1
        mutate_text = ''
        mutate_block_branch = []
        mutate_block_cov_branch = []
        for i in range(len(mutate_block)):
            inf_detail = mutate_block_cov[i].split(' ')
            if subbranch == -1 and int(inf_detail[-1]) == indent:
                subbranch = 1
                coverage_flag = -1
                mutate_block_branch.append(mutate_block[i])
                mutate_block_cov_branch.append(mutate_block_cov[i])
            elif subbranch == 1 and int(inf_detail[-1]) >= indent:
                if inf_detail[1].isdigit():
                    coverage_flag = 1
                mutate_block_branch.append(mutate_block[i])
                mutate_block_cov_branch.append(mutate_block_cov[i])
            elif subbranch == 1 and int(inf_detail[-1]) < indent:
                if coverage_flag == 1:
                    mutate_text += ('').join(mutate_block_branch)
                else:
                    res = dead_code_mutate(mutate_block_branch, mutate_block_cov_branch, indent, p, placeholder_variable)
                    if res == '':
                        # mutate_text += ' ' * (indent - 1) * 4 + 'a.update(a)\n'
                        mutate_text += ' ' * (indent - 1) * 4 + placeholder_variable + ' = ' + placeholder_variable + ';\n'
                    else:
                        mutate_text += res
                subbranch = -1
                mutate_block_branch = []
                mutate_block_cov_branch = []
                mutate_text += mutate_block[i]
            elif subbranch == 1 and int(inf_detail[-1]) == indent and inf_detail[1] == '!':
                if coverage_flag == 1:
                    mutate_text += ('').join(mutate_block_branch)
                else:
                    res = dead_code_mutate(mutate_block_branch, mutate_block_cov_branch, indent, p, placeholder_variable)
                    if res == '':
                        # mutate_text += ' ' * (indent - 1) * 4 + 'a.update(a)\n'
                        mutate_text += ' ' * (indent - 1) * 4 + placeholder_variable + ' = ' + placeholder_variable + ';\n'
                    else:
                        mutate_text += res
                subbranch = -1
                mutate_block_branch = []
                mutate_block_cov_branch = []
                subbranch = 1
                coverage_flag = -1
                mutate_block_branch.append(mutate_block[i])
                mutate_block_cov_branch.append(mutate_block_cov[i])
            elif subbranch == -1 and int(inf_detail[-1]) < indent:
                mutate_text += mutate_block[i]
            else:
                print(mutate_block)
                print(mutate_block_cov)
                print('erereirererere')
        if subbranch == 1:
            res = dead_code_mutate(mutate_block_branch, mutate_block_cov_branch, indent, p, placeholder_variable)
            if res == '':
                # mutate_text += ' ' * (indent - 1) * 4 + 'a.update(a)\n'
                mutate_text += ' ' * (indent - 1) * 4 + placeholder_variable + ' = ' + placeholder_variable + ';\n'
            else:
                mutate_text += res
        return mutate_text

def EMI(src_dir = 'src_convert', tgt_dir = 'tgt', max_mutate = 5, flipcoin = 0.5, exp_name = 'common', templete = 'gen_block_templete.py'):
    ### input
    # max_mutate = 5
    # flipcoin = 0.5

    # src_dir = 'src_1_convert'
    # src_dir = 'seed'
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_mutate'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    for file in file_names:
        print(file)
        # print(file)
        ### check whether the seed file cannot be conducted successfull. If not, skip the EMI ###
        result_file = os.path.join(tgt_dir, file.split('/')[-1][:-4] + '.txt')
        error = False
        ### since there is timeout limitation for compilation, there is sometimes no result file
        try:
            f_result = open(result_file)
            while True:
                result_line = f_result.readline()
                if not result_line:
                    break
                if result_line.find('error') != -1:
                    error = True
                    break
            f_result.close()
        except:
            error = True
        if error == True:
            continue
        cov_file = file[:-4] + '_cov.txt'
        ### Check whether the first line of the coverage result file shows the error
        try:
            f_cov = open(cov_file)
            while True:
                result_line = f_cov.readline()
                if not result_line:
                    break
                if result_line.find('error') != -1:
                    error = True
                    break
            f_cov.close()
        except:
            error = True
        if error == True:
            continue
        for i in range(max_mutate):
            # print('new')
            txt_mutate = ''
            mutate_file = os.path.join(out_dir, file.split('/')[-1][:-4] + '_mut' + str(i) + '.cpp')
            cov_file = file[:-4] + '_cov.txt'
            f_cov = open(cov_file)
            f_code = open(file)
            mutate_block_flag = -1
            # block_txt = ''
            mutate_block = []
            mutate_block_cov = []
            tg_flag = -1
            env_tg = {}
            placeholder_variable = None
            ### used for different block, since the declaration of variables cannot be repeated
            block_num = 0
            while True:
                cov_env_inf = f_cov.readline().split('||')
                line = f_code.readline()
                cov_inf = cov_env_inf[0]
                inf_detail = cov_inf.split(' ')
                if not line:
                    break
                if placeholder_variable == None and (line.find('Integer') != -1 or line.find('Bit') != -1):
                    if line.find(' = ') != -1:
                        placeholder_variable = line.split(' = ')[0].split(' ')[-1]
                    else:
                        placeholder_variable = line.split('(')[0].split(' ')[-1]
                if mutate_block_flag == -1 and inf_detail[1] == '!' and line.find('main') == -1:
                    mutate_block_flag = 1
                    coverage_flag = -1
                    mutate_block.append(line)
                    # block_txt += line
                    mutate_block_cov.append(cov_inf)
                    continue
                if mutate_block_flag == 1:
                    ### there are one indent for default
                    if len(line) - len(line.lstrip())==4 and line.find('};') != -1:
                        mutate_block.append(line)
                        mutate_block_cov.append(cov_inf)
                        # print(coverage_flag)
                        # print(mutate_block)
                        ### currently, true guard will not contain if blocks
                        if coverage_flag == 1:
                            if tg_flag == 1:
                                txt_mutate += ' ' * (len(line) - len(line.lstrip())) + '// True Guard\n'
                                pred_depth = random.randint(1, 4)
                                predicate = Synthesizer.syn_pred(env_tg, True, pred_depth)
                                ### the constant number used in synthesized predicate are not allowed to calculate with secure integer, so use secure integer to carry their value
                                numbers = re.findall(r'##-?\d+##', predicate)
                                for number in set(numbers):
                                    value = number[2: -2]
                                    if value[0] == '-':
                                        prevar = 'prevar' + str(block_num) + '_n' + value[1:]
                                    else:
                                        prevar = 'prevar' + str(block_num) + '_' + value
                                    txt_mutate += ' ' * (len(line) - len(line.lstrip())) + 'Integer ' + prevar + "(32, " + value + ", ALICE);\n"
                                    predicate = predicate.replace(number, prevar)
                                txt_mutate += ' ' * (len(line) - len(line.lstrip())) + 'if((' + predicate + ').reveal<bool>())\n'
                                txt_mutate += ' ' * (len(line) - len(line.lstrip())) + '{\n'
                                for mutate_line in mutate_block:
                                    txt_mutate += ' ' * (len(line) - len(line.lstrip()) + 4) + mutate_line + '\n'
                                txt_mutate += ' ' * (len(line) - len(line.lstrip())) + '};\n'
                                tg_flag = -1
                            else:
                                txt_mutate += ('').join(mutate_block)
                        else:
                            mutate_text = dead_code_mutate(mutate_block, mutate_block_cov, 2, flipcoin, placeholder_variable)
                            if tg_flag == 1:
                                txt_mutate += ' ' * (len(line) - len(line.lstrip())) + '// True Guard\n'
                                pred_depth = random.randint(1, 4)
                                predicate = Synthesizer.syn_pred(env_tg, True, pred_depth)
                                ### the constant number used in synthesized predicate are not allowed to calculate with secure integer, so use secure integer to carry their value
                                numbers = re.findall(r'##-?\d+##', predicate)
                                for number in set(numbers):
                                    value = number[2: -2]
                                    if value[0] == '-':
                                        prevar = 'prevar' + str(block_num) + '_n' + value[1:]
                                    else:
                                        prevar = 'prevar' + str(block_num) + '_' + value
                                    txt_mutate += ' ' * (len(line) - len(line.lstrip())) + 'Integer ' + prevar + "(32, " + value + ", ALICE);\n"
                                    predicate = predicate.replace(number, prevar)
                                txt_mutate += ' ' * (len(line) - len(line.lstrip())) + 'if((' + predicate + ').reveal<bool>())\n'
                                txt_mutate += ' ' * (len(line) - len(line.lstrip())) + '{\n'
                                for mutate_line in mutate_block:
                                    txt_mutate += ' ' * (len(line) - len(line.lstrip()) + 4) + mutate_line + '\n'
                                txt_mutate += ' ' * (len(line) - len(line.lstrip())) + '};\n'
                                tg_flag = -1
                            else:
                                txt_mutate += mutate_text
                        mutate_block_flag = -1
                        # block_txt = ''
                        mutate_block = []
                        mutate_block_cov = []
                        # print(inf_detail)
                    else:
                        mutate_block.append(line)
                        # block_txt += line
                        mutate_block_cov.append(cov_inf)
                        # print(inf_detail[1], inf_detail[3])
                        if inf_detail[1].isdigit():
                            coverage_flag = 1
                else:
                    if tg_flag == 1:
                        if line.find('check') == -1 and line.find('Integer') == -1 and line.find('Bit') == -1:
                            block_num += 1
                            txt_mutate += ' ' * (len(line) - len(line.lstrip())) + '// True Guard\n'
                            pred_depth = random.randint(1, 4)
                            predicate = Synthesizer.syn_pred(env_tg, True, pred_depth)
                            ### the constant number used in synthesized predicate are not allowed to calculate with secure integer, so use secure integer to carry their value
                            numbers = re.findall(r'##-?\d+##', predicate)
                            for number in set(numbers):
                                value = number[2: -2]
                                if value[0] == '-':
                                    prevar = 'prevar' + str(block_num) + '_n' + value[1:]
                                else:
                                    prevar = 'prevar' + str(block_num) + '_' + value
                                txt_mutate += ' ' * (len(line) - len(line.lstrip())) + 'Integer ' + prevar + "(32, " + value + ", ALICE);\n"
                                predicate = predicate.replace(number, prevar)
                            txt_mutate += ' ' * (len(line) - len(line.lstrip())) + 'if((' + predicate + ').reveal<bool>())\n'
                            txt_mutate += ' ' * (len(line) - len(line.lstrip())) + '{\n'
                            txt_mutate += ' ' * 4 + line
                            txt_mutate += ' ' * (len(line) - len(line.lstrip())) + '};\n'
                            tg_flag = -1
                        else:
                            txt_mutate += line
                            tg_flag = -1
                    else:
                        txt_mutate += line
                if len(cov_env_inf) == 3:
                    env_inf = cov_env_inf[2].split('?')
                    ### the format is changed for easy to use, since env with only value can be read by Synthesizer
                    env = {}
                    env_type = {}
                    for i in env_inf:
                        if i == '':
                            continue
                        i_inf = i.split('=')
                        ### currently, only sint are recorded here
                        var_inf = eval(i_inf[1])
                        if var_inf[0] == 'sint':
                            env[i_inf[0]] = var_inf[1]
                            env_type[i_inf[0]] = 'sint'
                        ### currently bool is not used in any synthesized block or predicate
                        # else:
                        #     env[i_inf[0]] = var_inf[1]
                        #     env_type[i_inf[0]] = 'bool'
                    ########################################################## for test ################################################
                    type_choice = random.randint(1, 5)
                    ########################################################## for test ################################################
                    ### fcb and tcb must be conducted on a secret integer variable
                    # no_sint = True
                    # for var_name in (env_type.keys()):
                    #     var_type = env_type[var_name]
                    #     if no_sint == True and var_type == 'sint':
                    #         no_sint = False
                    if len(env) == 0:
                        no_sint = True
                    else:
                        no_sint = False
                    if no_sint == False:
                        if mutate_block_flag != 1:
                            if type_choice <= 2:
                                block_num += 1
                                generate_txt = gen_fcb(env, exp_name, templete, block_num = block_num)
                            elif type_choice <= 4: 
                                block_num += 1
                                generate_txt = gen_tcb(env, exp_name, templete, block_num = block_num)
                            else:
                                if tg_flag == 1:
                                    ### tg_flag should not be 1 if the statement is not in if/for block
                                    print('debug')
                                    print(file)
                                else:
                                    tg_flag = 1
                                    env_tg = env
                                    # env_type_tg = env_type
                            if type_choice <= 4: 
                                for generate_line in generate_txt.split('\n'):
                                    txt_mutate += ' ' * int(inf_detail[-1]) * 4 + generate_line + '\n'
                        else:
                            if type_choice <= 2: 
                                block_num += 1
                                generate_txt = gen_fcb(env, exp_name, templete, block_num = block_num)
                            elif type_choice <= 4: 
                                block_num += 1
                                generate_txt = gen_tcb(env, exp_name, templete, block_num = block_num)
                            else:
                                pass ### now I will not trigger Ture gurad in if/for block
                                # if tg_flag == 1:
                                #     ### if the if/for block has been in true guard, the branch should not be in true guard (temp)
                                #     pass
                                # else:
                                #     tg_flag = 1
                                #     env_tg = env
                                #     env_type_tg = env_type
                            if type_choice <= 4:
                                for generate_line in generate_txt.split('\n'):
                                    mutate_block.append(' ' * int(inf_detail[-1]) * 4 + generate_line + '\n')
                                    mutate_block_cov.append(cov_inf)
            txt_mutate += '}'
            f_cov.close()
            f_code.close()
            f = open(mutate_file, 'w')
            f.write(txt_mutate)
            f.close

def EMI_private(src_dir = 'src_convert', tgt_dir = 'tgt'):
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_mutprivate'
    # out_dir = src_dir + '_mutate'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    for file in file_names:
        ### check whether the seed file cannot be conducted successfull. If not, skip the EMI ###
        result_file = os.path.join(tgt_dir, file.split('/')[-1][:-4] + '.txt')
        error = False
        ### since there is timeout limitation for compilation, there is sometimes no result file
        try:
            f_result = open(result_file)
            while True:
                result_line = f_result.readline()
                if not result_line:
                    break
                if result_line.find('error') != -1:
                    error = True
                    break
            f_result.close()
        except:
            error = True
        if error == True:
            continue
        f_result.close()

        for i in range(0, 1):
            txt_mutate = ''
            file_name = file.split('/')[-1]
            mutate_file = os.path.join(out_dir, file_name[:-4] + '_p' + str(i) + '.cpp')
            # print(mutate_file)
            f_code = open(file)
            while True:
                line = f_code.readline()
                if not line:
                    break
                ### the code that do not need change
                if line.find('include') != -1 or line.find('using') != -1 or line.find('main') != -1 or line.find('party') != -1:
                    txt_mutate += line
                    continue
                if line.find('Integer') != -1:
                    if line.find(' = ') == -1:
                        varname = line.split('(')[0].split(' ')[-1]
                        value = line.split(',')[-2]
                        indent = len(line) - len(line.lstrip())
                        line = indent * ' ' + 'int ' + varname + ' =' + value + ';\n'
                    else:
                        line = line.replace('Integer', 'int')
                if line.find('Bit') != -1:
                    line = line.replace('Bit', 'bool')
                if line.find('.reveal<bool>()') != -1:
                    line = line.replace('.reveal<bool>()', '')
                if line.find('.reveal<int32_t>()') != -1:
                    line = line.replace('.reveal<int32_t>()', '')
                txt_mutate += line
            f_code.close()
            f = open(mutate_file, 'w')
            f.write(txt_mutate)
            f.close

def EMI_party(src_dir = 'src_convert', tgt_dir = 'tgt'):
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_mutparty'
    # out_dir = src_dir + '_mutate'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    for file in file_names:
        ### check whether the seed file cannot be conducted successfull. If not, skip the EMI ###
        result_file = os.path.join(tgt_dir, file.split('/')[-1][:-4] + '.txt')
        error = False
        ### since there is timeout limitation for compilation, there is sometimes no result file
        try:
            f_result = open(result_file)
            while True:
                result_line = f_result.readline()
                if not result_line:
                    break
                if result_line.find('error') != -1:
                    error = True
                    break
            f_result.close()
        except:
            error = True
        if error == True:
            continue
        f_result.close()

        for i in range(0, 5):
            txt_mutate = ''
            file_name = file.split('/')[-1]
            mutate_file = os.path.join(out_dir, file_name[:-4] + '_p' + str(i) + '.cpp')
            # print(mutate_file)
            f_code = open(file)
            while True:
                line = f_code.readline()
                if not line:
                    break
                ### the code that do not need change
                if line.find('include') != -1 or line.find('using') != -1 or line.find('main') != -1 or line.find('party') != -1:
                    txt_mutate += line
                    continue
                if line.find('ALICE') != -1 and random.random()<0.5:
                    line = line.replace('ALICE', 'BOB')
                txt_mutate += line
                    
            f_code.close()
            f = open(mutate_file, 'w')
            f.write(txt_mutate)
            f.close
            



if __name__ == '__main__':

    # EMI('src_convert', 'tgt', max_mutate = 5)
    # EMI_private('src_convert', 'tgt')
    EMI('exp10_2/seed_convert', 'exp10_2/tgt', max_mutate = 5)