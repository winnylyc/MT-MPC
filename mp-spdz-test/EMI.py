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
        return '((' + Synthesizer.syn_pred(env, bool(1-bool_expected), depth-1) + ').bit_not())'

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
        return '(' + Synthesizer.syn_pred(env, left, depth-1) + '.bit_and(' + Synthesizer.syn_pred(env, right, depth-1) + '))'

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
        return '(' + Synthesizer.syn_pred(env, left, depth-1) + '.bit_or(' + Synthesizer.syn_pred(env, right, depth-1) + '))'

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
                return '(' + var_name + ' <= ' + str(max_val) + ')'
            elif min_val == 0 and not bool_expected:
                return '(' + var_name + ' > ' + str(max_val) + ')'
            elif max_val == 0 and bool_expected:
                return '(' + var_name + ' >= ' + str(min_val) + ')'
            elif max_val == 0 and not bool_expected:
                return '(' + var_name + ' < ' + str(min_val) + ')'

            rnd_int = random.randint(1, 4)
            if rnd_int == 1:  # <
                if bool_expected:  # < max+1
                    t_val = max_val + min(random.randint(1, 5), abs(max_val))
                else:  # < min
                    t_val = min_val
                return '(' + var_name + ' < ' + str(t_val) + ')'
            elif rnd_int == 2:  # >
                if bool_expected:  # > min-1
                    t_val = min_val - min(random.randint(1, 5), abs(min_val))
                else:  # > max
                    t_val = max_val
                return '(' + var_name + ' > ' + str(t_val) + ')'
            elif rnd_int == 3:  # <=
                if bool_expected:  # <= max
                    t_val = max_val
                else:  # <= min-1
                    t_val = min_val - min(random.randint(1, 5), abs(min_val))
                return '(' + var_name + ' <= ' + str(t_val) + ')'
            elif rnd_int == 4:  # >=
                if bool_expected:  # >= min
                    t_val = min_val
                else:  # >= max+1
                    t_val = max_val + min(random.randint(1, 5), abs(max_val))
                return '(' + var_name + ' >= ' + str(t_val) + ')'
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

def generate_block(env, exp_name, templete = 'gen_block_templete.mpc'):
    templete = open(templete)
    grammar_block = ''
    while True:
        line = templete.readline()
        if not line:
                    break
        if line.find('# Specify the special variabal') != -1:
            grammar_block += line
            for var_name in (env.keys()):
                if var_name == 'a' or 'b':
                    continue
                var_value = env[var_name]
                if isinstance(list(var_value)[0], int):
                    grammar_block += '<special_var> = ' + var_name + '\n'
                else:
                    grammar_block += '<special_var_fix> = ' + var_name + '\n'
                
        else:
            grammar_block += line
    templete.close()
    with open('gen_block_' + exp_name + '.mpc', 'w') as f:
        f.write(grammar_block)
    block_content = generator_nosave('gen_block_' + exp_name + '.mpc')
    block_content = convert_nosave(block_content)
    return block_content

def gen_fcb(env, exp_name, templete = 'gen_block_templete.mpc'):
    pred_depth = random.randint(1, 4)
    predicate = Synthesizer.syn_pred(env, False, pred_depth)
    block_txt = '# False Condition Block\n'
    block_txt += '@if_(' + predicate + '.reveal())\n'
    block_txt += 'def _():\n'
    block_syn = generate_block(env, exp_name, templete)
    for line in block_syn.split('\n'):
        block_txt += ' ' * 4 + line + '\n'
    # print(block_txt)
    return block_txt

def gen_tcb(env, exp_name, templete = 'gen_block_templete.mpc'):
    pred_depth = random.randint(1, 4)
    predicate = Synthesizer.syn_pred(env, True, pred_depth)
    block_txt = '# True Condition Block\n'
    var_list = list(env.keys())
    ### randomly put the value backup inside or outside the block
    global_var = -1
    if random.random()<0.5:
        block_txt += '@if_(' + predicate + '.reveal())\n'
        block_txt += 'def _():\n'
        for var_name in var_list:
            ### use sint() to deepcopy
            block_txt += ' ' * 4 + var_name + '_back = sint(' + var_name + ')\n'
    else:
        for var_name in var_list:
            ### use sint() to deepcopy
            block_txt += var_name + '_back = sint(' + var_name + ')\n'
        block_txt += '@if_(' + predicate + '.reveal())\n'
        block_txt += 'def _():\n'
        global_var = 1
    block_syn = generate_block(env, exp_name, templete)
    for line in block_syn.split('\n'):
        block_txt += ' ' * 4 + line + '\n'

    ### randomly put the value backup inside or outside the block
    ### only perfom the value restore outside when the back variable is set outside the block
    if random.random()<0.5 and global_var == 1:
        for var_name in var_list:
            block_txt += var_name + '.update(' + var_name + '_back)' + '\n'
    else:
        for var_name in var_list:
            block_txt += ' ' * 4 + var_name + '.update(' + var_name + '_back)' + '\n'
        
    return block_txt

def dead_code_mutate(mutate_block, mutate_block_cov, indent, p):
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
                    res = dead_code_mutate(mutate_block_branch, mutate_block_cov_branch, indent, p)
                    if res == '':
                        # mutate_text += ' ' * (indent - 1) * 4 + 'a.update(a)\n'
                        mutate_text += ' ' * (indent - 1) * 4 + '0\n'
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
                    res = dead_code_mutate(mutate_block_branch, mutate_block_cov_branch, indent, p)
                    if res == '':
                        # mutate_text += ' ' * (indent - 1) * 4 + 'a.update(a)\n'
                        mutate_text += ' ' * (indent - 1) * 4 + '0\n'
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
            res = dead_code_mutate(mutate_block_branch, mutate_block_cov_branch, indent, p)
            if res == '':
                # mutate_text += ' ' * (indent - 1) * 4 + 'a.update(a)\n'
                mutate_text += ' ' * (indent - 1) * 4 + '0\n'
            else:
                mutate_text += res
        return mutate_text

def EMI(src_dir = 'src_2_convert', tgt_dir = 'tgt', max_mutate = 5, flipcoin = 0.5, exp_name = 'common', templete = 'gen_block_templete.mpc'):
    ### input
    # max_mutate = 5
    # flipcoin = 0.5

    # src_dir = 'src_1_convert'
    # src_dir = 'seed'
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    # file_names = ['src_2_convert/fuzz-00002.mpc']
    out_dir = src_dir + '_mutate'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    for file in file_names:
        # print(file)
        ### check whether the seed file cannot be conducted successfull. If not, skip the EMI ###
        result_file = os.path.join(tgt_dir, file.split('/')[-1][:-4] + '.txt')
        error = False
        try:
            f_result = open(result_file)
            while True:
                result_line = f_result.readline()
                if not result_line:
                    break
                if result_line.find('Traceback') != -1:
                    error = True
                    break
            f_result.close()
        except:
            error = True
        if error == True:
            continue
        cov_file = file[:-4] + '_cov.txt'
        ### Check whether the first line of the coverage result file shows the error
        f_cov = open(cov_file)
        result_line = f_cov.readline()
        if result_line.find('error') != -1:
            error = True
        f_cov.close()
        if error == True:
            continue
        for i in range(max_mutate):
            # print('new')
            txt_mutate = ''
            mutate_file = os.path.join(out_dir, file.split('/')[-1][:-4] + '_mut' + str(i) + '.mpc')
            cov_file = file[:-4] + '_cov.txt'
            f_cov = open(cov_file)
            f_code = open(file)
            mutate_block_flag = -1
            # block_txt = ''
            mutate_block = []
            mutate_block_cov = []
            tg_flag = -1
            env_tg = {}
            while True:
                cov_env_inf = f_cov.readline().split('||')
                line = f_code.readline()
                        
                cov_inf = cov_env_inf[0]
                inf_detail = cov_inf.split(' ')
                if not line:
                    break
                if mutate_block_flag == -1 and inf_detail[1] == '!':
                    mutate_block_flag = 1
                    coverage_flag = -1
                    mutate_block.append(line)
                    # block_txt += line
                    mutate_block_cov.append(cov_inf)
                    continue
                if mutate_block_flag == 1:
                    # print(line)
                    if line[0] != ' ' and line.find('def') == -1:
                        # print(coverage_flag)
                        # print(mutate_block)
                        if coverage_flag == 1:
                            if tg_flag == 1:
                                txt_mutate += '# True Guard\n'
                                pred_depth = random.randint(1, 4)
                                predicate = Synthesizer.syn_pred(env_tg, True, pred_depth)
                                txt_mutate += '@if_(' + predicate + '.reveal())\n'
                                txt_mutate += 'def _():\n'
                                for mutate_line in mutate_block:
                                    txt_mutate += ' ' * 4 + mutate_line + '\n'
                                tg_flag = -1
                            else:
                                txt_mutate += ('').join(mutate_block)
                        else:
                            mutate_text = dead_code_mutate(mutate_block, mutate_block_cov, 1, flipcoin)
                            if tg_flag == 1:
                                txt_mutate += '# True Guard\n'
                                pred_depth = random.randint(1, 4)
                                predicate = Synthesizer.syn_pred(env_tg, True, pred_depth)
                                txt_mutate += '@if_(' + predicate + '.reveal())\n'
                                txt_mutate += 'def _():\n'
                                for mutate_index, mutate_line in enumerate(mutate_text.split('\n')):
                                    if mutate_index == 0 and mutate_line == '':
                                        txt_mutate += ' ' * 4 + '0\n'
                                    else:
                                        txt_mutate += ' ' * 4 + mutate_line + '\n'
                                tg_flag = -1
                            else:
                                txt_mutate += mutate_text
                        mutate_block_flag = -1
                        # block_txt = ''
                        mutate_block = []
                        mutate_block_cov = []
                        # print(inf_detail)
                        if inf_detail[1] == '!':
                            mutate_block_flag = 1
                            coverage_flag = -1
                            mutate_block.append(line)
                            mutate_block_cov.append(cov_inf)
                        else:
                            if tg_flag == 1:
                                if line.find('=') == -1: ### variable defining should not be done in if/for block
                                    txt_mutate += '# True Guard\n'
                                    pred_depth = random.randint(1, 4)
                                    predicate = Synthesizer.syn_pred(env_tg, True, pred_depth)
                                    txt_mutate += '@if_(' + predicate + '.reveal())\n'
                                    txt_mutate += 'def _():\n'
                                    txt_mutate += ' ' * 4 + line + '\n'
                                    tg_flag = -1
                                else:
                                    txt_mutate += line
                                    tg_flag = -1
                            else:
                                txt_mutate += line
                    else:
                        mutate_block.append(line)
                        # block_txt += line
                        mutate_block_cov.append(cov_inf)
                        # print(inf_detail[1], inf_detail[3])
                        if inf_detail[1].isdigit():
                            coverage_flag = 1
                else:
                    if tg_flag == 1:
                        if line.find('=') == -1: ### variable defining should not be done in if/for block
                            txt_mutate += '# True Guard\n'
                            pred_depth = random.randint(1, 4)
                            predicate = Synthesizer.syn_pred(env_tg, True, pred_depth)
                            txt_mutate += '@if_(' + predicate + '.reveal())\n'
                            txt_mutate += 'def _():\n'
                            txt_mutate += ' ' * 4 + line + '\n'
                            tg_flag = -1
                        else:
                            txt_mutate += line
                            tg_flag = -1
                    else:
                        txt_mutate += line
                if len(cov_env_inf) == 3:
                    env_inf = cov_env_inf[2].split('?')
                    env = {}
                    for i in env_inf:
                        if i == '':
                            continue
                        i_inf = i.split('=')
                        env[i_inf[0]] = eval(i_inf[1])
                    type_choice = random.randint(1, 5)
                    # type_choice = random.randint(1, 4)
                    if mutate_block_flag != 1:
                        if type_choice <= 2: 
                            generate_txt = gen_fcb(env, exp_name, templete)
                        elif type_choice <= 4: 
                            generate_txt = gen_tcb(env, exp_name, templete)
                        else:
                            if tg_flag == 1:
                                ### tg_flag should not be 1 if the statement is not in if/for block
                                print('debug')
                                print(file)
                            else:
                                tg_flag = 1
                                env_tg = env
                        if type_choice <= 4: 
                            for generate_line in generate_txt.split('\n'):
                                txt_mutate += ' ' * int(inf_detail[-1]) * 4 + generate_line + '\n'
                    else:
                        if type_choice <= 2: 
                            generate_txt = gen_fcb(env, exp_name, templete)
                        elif type_choice <= 4: 
                            generate_txt = gen_tcb(env, exp_name, templete)
                        else:
                            pass ### now I will not trigger Ture gurad in if/for block
                            # if tg_flag == 1:
                            #     ### if the if/for block has been in true guard, the branch should not be in true guard (temp)
                            #     pass
                            # else:
                            #     tg_flag = 1
                            #     env_tg = env
                        if type_choice <= 4:
                            for generate_line in generate_txt.split('\n'):
                                mutate_block.append(' ' * int(inf_detail[-1]) * 4 + generate_line + '\n')
                                mutate_block_cov.append(cov_inf)
            f_cov.close()
            f_code.close()
            f = open(mutate_file, 'w')
            f.write(txt_mutate)
            f.close

def EMI_player(src_dir = 'src_2_convert', tgt_dir = 'tgt'):
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_mutplayer'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    for file in file_names:
        ### check whether the seed file cannot be conducted successfull. If not, skip the EMI ###
        result_file = os.path.join(tgt_dir, file.split('/')[-1][:-4] + '.txt')
        error = False
        f_result = open(result_file)
        while True:
            result_line = f_result.readline()
            if not result_line:
                break
            if result_line.find('Traceback') != -1:
                error = True
                break
        f_result.close()
        if error == True:
            continue
        txt_mutate = ''
        mutate_file = os.path.join(out_dir, file.split('/')[-1])
        f_code = open(file)
        while True:
            line = f_code.readline()
            if not line:
                break
            if line.find('sint.get_input_from(1)') != -1:
                txt_mutate += line.split('1')[0] + '0' + line.split('1')[-1]
            else:
                txt_mutate += line
        f_code.close()
        f = open(mutate_file, 'w')
        f.write(txt_mutate)
        f.close

def EMI_private_ori(src_dir = 'src_2_convert', tgt_dir = 'tgt'):
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_mutprivate'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    for file in file_names:
        ### check whether the seed file cannot be conducted successfull. If not, skip the EMI ###
        result_file = os.path.join(tgt_dir, file.split('/')[-1][:-4] + '.txt')
        error = False
        f_result = open(result_file)
        while True:
            result_line = f_result.readline()
            if not result_line:
                break
            if result_line.find('Traceback') != -1:
                error = True
                break
        f_result.close()
        if error == True:
            continue
        txt_mutate = ''
        mutate_file = os.path.join(out_dir, file.split('/')[-1])
        revealed_list = []
        array_list = []
        f_code = open(file)
        while True:
            line = f_code.readline()
            if not line:
                break
            if line.find(' = ') != -1 or line.find('update') != -1 and line.find('def') == -1 and line.find('@') == -1:
                if line.find('update') != -1:
                    variable = line.strip().split('.')[0]
                else:
                    variable = line.strip().split(' = ')[0]
                if variable.find('[') != -1:
                    variable = variable.split('[')[0]
                # print(variable)
                # print(revealed_list)
                if line.find('Array') != -1:
                    if variable not in array_list:
                        array_list.append(variable)
                if variable not in revealed_list:
                    if (variable not in array_list) and random.random()<0.5 and variable.find('varblock') == -1:
                        # if line.find('update') != -1:
                        #     # line_split = line.split('.update(')
                        #     # txt_mutate += line_split[0] + ' = ' + line_split[1][:-2] + '.reveal()\n'
                        #     txt_mutate += line
                        #     indent = len(line) - len(line.lstrip())
                        # else:
                        txt_mutate += line
                        indent = len(line) - len(line.lstrip())
                        txt_mutate += (indent * ' ') + variable + ' = ' + variable + '.reveal()\n'
                        revealed_list.append(variable)
                    else:
                        txt_mutate += line
                else:
                    if line.find('update') != -1:
                        line_split = line.split('.update(')
                        txt_mutate += line_split[0] + ' = ' + line_split[1][:-2] + '.reveal()\n'
                    else:
                        txt_mutate += line
                        indent = len(line) - len(line.lstrip())
                        txt_mutate += (indent * ' ') + variable + ' = ' + variable + '.reveal()\n'
            else:
                txt_mutate += line
        f_code.close()

        f = open(mutate_file, 'w')
        f.write(txt_mutate)
        f.close

def EMI_private(src_dir = 'src_2_convert', tgt_dir = 'tgt'):
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_mutprivate'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    for file in file_names:
        ### check whether the seed file cannot be conducted successfull. If not, skip the EMI ###
        result_file = os.path.join(tgt_dir, file.split('/')[-1][:-4] + '.txt')
        error = False
        try:
            f_result = open(result_file)
            while True:
                result_line = f_result.readline()
                if not result_line:
                    break
                if result_line.find('Traceback') != -1:
                    error = True
                    break
            f_result.close()
        except:
            error = True
        if error == True:
            continue
        reveal_list = []
        f_code = open(file)
        while True:
            line = f_code.readline()
            if not line:
                break
            if line.find(' = ') != -1 or line.find('update') != -1 and line.find('def') == -1 and line.find('@') == -1:
                if line.find('update') != -1:
                    variable = line.strip().split('.')[0]
                else:
                    variable = line.strip().split(' = ')[0]
                if variable.find('[') != -1:
                    variable = variable.split('[')[0]
                if (variable not in reveal_list)  and variable.find('varblock') == -1:
                    reveal_list.append(variable)
        f_code.close()
        random.shuffle(reveal_list)
        for i in range(0, len(reveal_list), 2):
            txt_mutate = ''
            file_name = file.split('/')[-1]
            mutate_file = os.path.join(out_dir, file_name[:-4] + '_p' + str(i) + '.mpc')
            # print(mutate_file)
            toreveal_list = reveal_list[:(i+1)]
            f_code = open(file)
            while True:
                line = f_code.readline()
                if not line:
                    break
                if line.find(' = ') != -1 or line.find('update') != -1 and line.find('def') == -1 and line.find('@') == -1:
                    if line.find('update') != -1:
                        variable = line.strip().split('.')[0]
                    else:
                        variable = line.strip().split(' = ')[0]
                    if variable.find('[') != -1:
                        variable = variable.split('[')[0]
                    if variable in toreveal_list:
                        if line.find('update') != -1:
                            txt_mutate += line[:-2] + '.reveal())\n'
                        else:
                            txt_mutate += line
                            indent = len(line) - len(line.lstrip())
                            txt_mutate += (indent * ' ') + variable + ' = ' + variable + '.reveal()\n'
                    else:
                        txt_mutate += line
                else:
                    txt_mutate += line
            f_code.close()
            f = open(mutate_file, 'w')
            f.write(txt_mutate)
            f.close
        # for i in range(0, 1):
        #     txt_mutate = ''
        #     file_name = file.split('/')[-1]
        #     mutate_file = os.path.join(out_dir, file_name[:-4] + '_p' + str(i) + '.mpc')
        #     # print(mutate_file)
        #     toreveal_list = reveal_list
        #     f_code = open(file)
        #     while True:
        #         line = f_code.readline()
        #         if not line:
        #             break
        #         if line.find(' = ') != -1 or line.find('update') != -1 and line.find('def') == -1 and line.find('@') == -1:
        #             if line.find('update') != -1:
        #                 variable = line.strip().split('.')[0]
        #             else:
        #                 variable = line.strip().split(' = ')[0]
        #             if variable.find('[') != -1:
        #                 variable = variable.split('[')[0]
        #             if variable in toreveal_list:
        #                 if line.find('update') != -1:
        #                     txt_mutate += line[:-2] + '.reveal())\n'
        #                 else:
        #                     txt_mutate += line
        #                     indent = len(line) - len(line.lstrip())
        #                     txt_mutate += (indent * ' ') + variable + ' = ' + variable + '.reveal()\n'
        #             else:
        #                 txt_mutate += line
        #         else:
        #             txt_mutate += line
        #     f_code.close()
        #     f = open(mutate_file, 'w')
        #     f.write(txt_mutate)
        #     f.close


if __name__ == '__main__':
    # EMI(src_dir = 'exp40_0/seed_convert', tgt_dir = 'exp40_0/tgt')
    EMI_private(src_dir = 'exp21_0/seed_convert', tgt_dir = 'exp21_0/tgt')