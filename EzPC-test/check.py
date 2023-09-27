import os
import shutil
import re
import random
import glob

def check(src_dir = 'src_2_convert', mutate_dir = 'src_2_convert_mutate', src_res_dir = 'tgt', mutate_res_dir = 'tgt_mutate', max_mutate = 5):
    ### input
    # max_mutate = 5

    # src_dir = 'src_1_convert'
    # src_dir = 'seed'
    # mutate_dir = src_dir + '_mutate'

    # src_res_dir = 'tgt_seed'
    # mutate_res_dir = 'tgt_mutate'

    # src_res_dir = 'tgt_seed_dce'
    # mutate_res_dir = 'tgt_mutate_dce'

    # src_res_dir = 'tgt_seed_fo'
    # mutate_res_dir = 'tgt_mutate_fo'

    # src_res_dir = 'tgt_src_1'
    # mutate_res_dir = 'tgt_src_1_mutate'

    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_bug'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    fail_dir = src_dir + '_fail'
    if os.path.exists(fail_dir):
        shutil.rmtree(fail_dir) 
    os.mkdir(fail_dir)
    check_dir = src_dir + '_check'
    if os.path.exists(check_dir):
        shutil.rmtree(check_dir) 
    os.mkdir(check_dir)
    check_mutate_dir = src_dir + '_check_mutate'
    if os.path.exists(check_mutate_dir):
        shutil.rmtree(check_mutate_dir) 
    os.mkdir(check_mutate_dir)
    for file in file_names:
        for i in range(max_mutate):
            mutate_file = os.path.join(mutate_dir, file.split('/')[-1][:-5] + '_mut' + str(i) + '.ezpc')
            coverage_file = os.path.join(src_dir, file.split('/')[-1][:-5] + '_cov.txt')
            result_file = os.path.join(src_res_dir, file.split('/')[-1][:-5] + '.txt')
            mutate_result_file = os.path.join(mutate_res_dir, mutate_file.split('/')[-1][:-5] + '.txt')
            ori_sum = -10000
            try:
                f = open(result_file)
            except:
                break
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('checksum') != -1:
                    line = f.readline()
                    ori_sum = int(line)
            f.close()
            mutate_sum = -10000
            mutate_fail = -1
            try:
                f = open(mutate_result_file)
            except:
                continue
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('error') != -1:
                    mutate_fail = 1
                    break
                if line.find('checksum') != -1:
                    line = f.readline()
                    mutate_sum = int(line)
            f.close()
            if mutate_fail != 1 and mutate_sum != ori_sum and mutate_sum != -10000 and mutate_sum != -10000:
                shutil.copy(file, out_dir)
                shutil.copy(mutate_file, out_dir)
                shutil.copy(coverage_file, out_dir)
                shutil.copy(result_file, out_dir)
                shutil.copy(mutate_result_file, out_dir)

                shutil.copy(file, check_dir)
                shutil.copy(mutate_file, check_mutate_dir)
            if mutate_fail == 1 or mutate_sum == -10000 or mutate_sum == -10000:
                shutil.copy(file, fail_dir)
                shutil.copy(mutate_file, fail_dir)
                shutil.copy(coverage_file, fail_dir)
                shutil.copy(result_file, fail_dir)
                shutil.copy(mutate_result_file, fail_dir)

def check_check(src_dir = 'src_2_convert', mutate_dir = 'src_2_convert_mutate', src_res_dir = 'tgt', mutate_res_dir = 'tgt_mutate'):
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_bug'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    fail_dir = src_dir + '_fail'
    if os.path.exists(fail_dir):
        shutil.rmtree(fail_dir) 
    os.mkdir(fail_dir)
    for file in file_names:
        ref_file = os.path.join(src_res_dir, file.split('/')[-1][:-5] + '.txt')
        ref_sum = -10000
        try:
            f = open(ref_file)
        except:
            continue
        while True:
            line = f.readline()
            if not line:
                break
            if line.find('error') != -1:
                break
            if line.find('checksum') != -1:
                    line = f.readline()
                    ref_sum = int(line)
        f.close()
        mut_files = glob.glob(os.path.join(mutate_res_dir, file.split('/')[-1][:-5])+'_mut*')
        for mut_file in mut_files:
            mut_sum = -10000
            try:
                f = open(mut_file)
            except:
                continue
            mutate_fail = -1
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('error') != -1:
                    mutate_fail = 1
                    break
                if line.find('checksum') != -1:
                    line = f.readline()
                    mut_sum = int(line)
            f.close()
            if mutate_fail != 1 and ref_sum != mut_sum and ref_sum != -10000 and mut_sum != -10000:
                shutil.copy(file, out_dir)
                shutil.copy(os.path.join(mutate_dir, mut_file.split('/')[-1][:-4] + '.ezpc'), out_dir)
                shutil.copy(ref_file, out_dir)
                shutil.copy(mut_file, out_dir)

            if mutate_fail == 1 or ref_sum == -10000 or mut_sum == -10000:
                shutil.copy(file, fail_dir)
                shutil.copy(os.path.join(mutate_dir, mut_file.split('/')[-1][:-4] + '.ezpc'), fail_dir)
                shutil.copy(ref_file, fail_dir)
                shutil.copy(mut_file, fail_dir)

def check_dt(src_dir = 'exp9_0/seed_convert', mutate_dir = 'exp9_0/seed_convert_mutate', src_res_dir = 'exp9_0/tgt', mutate_res_dir = 'exp9_0/tgt_mutate', max_mutate = 5):
    ### input
    # max_mutate = 5

    # src_dir = 'src_1_convert'
    # src_dir = 'seed'
    # mutate_dir = src_dir + '_mutate'

    # src_res_dir = 'tgt_seed'
    # mutate_res_dir = 'tgt_mutate'

    # src_res_dir = 'tgt_seed_dce'
    # mutate_res_dir = 'tgt_mutate_dce'

    # src_res_dir = 'tgt_seed_fo'
    # mutate_res_dir = 'tgt_mutate_fo'

    # src_res_dir = 'tgt_src_1'
    # mutate_res_dir = 'tgt_src_1_mutate'
    # test_protocals = ['lowgear.sh', 'highgear.sh', 'cowgear.sh', 'chaigear.sh']
    # test_protocals = ['spdz2k.sh', 'semi2k.sh']
    # test_protocals = ['mama.sh', 'semi.sh', 'hemi.sh', 'temi.sh', 'soho.sh']
    # test_protocals = ['mama.sh', 'lowgear.sh', 'highgear.sh']
    test_protocals = ['spdz2k.sh', 'semi2k.sh', 'semi-bin.sh', 'tinier.sh']

    file_names = [file for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_bug_dt'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    ###The result from mascot is used as reference###
    for file in file_names:
        ref_file = os.path.join(src_res_dir, file.split('/')[-1][:-5] + '.txt')
        ref_sum = -10000
        try:
            f = open(ref_file)
        except:
            continue
        while True:
            line = f.readline()
            if not line:
                break
            if line.find('checksum:') != -1:
                ref_sum = float(line.split(' ')[1])
                break
        f.close()
        for protocal in test_protocals:
            dt_file = os.path.join(src_res_dir + '_' + protocal.split('.')[0], file.split('/')[-1][:-5] + '.txt')
            dt_sum = -10000
            try:
                f = open(dt_file)
            except:
                continue
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('error') != -1:
                    break
                if line.find('checksum:') != -1:
                    dt_sum = float(line.split(' ')[1])
                    break
            f.close()
            if ref_sum != dt_sum and ref_sum != -10000 and dt_sum != -10000:
                shutil.copy(os.path.join(src_dir, file), out_dir)
                shutil.copy(ref_file, out_dir)
                shutil.copy(dt_file, os.path.join(out_dir, file.split('/')[-1][:-5] + '_' + protocal.split('.')[0] + '.txt'))
            for i in range(max_mutate):
                mutate_file = os.path.join(mutate_dir, file.split('/')[-1][:-5] + '_mut' + str(i) + '.ezpc')
                ref_file_mut = os.path.join(mutate_res_dir + '_mascot', mutate_file.split('/')[-1][:-5] + '.txt')
                dt_file_mut = os.path.join(mutate_res_dir + '_' + protocal.split('.')[0], mutate_file.split('/')[-1][:-5] + '.txt')
                ref_sum_mut = -10000
                try:
                    f = open(ref_file_mut)
                except:
                    continue
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if line.find('checksum:') != -1:
                        ref_sum_mut = float(line.split(' ')[1])
                        break
                f.close()
                dt_sum_mut = -10000
                mutate_fail = -1
                try:
                    f = open(dt_file_mut)
                except:
                    continue
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if line.find('error') != -1:
                        mutate_fail = 1
                        break
                    if line.find('checksum:') != -1:
                        dt_sum_mut = float(line.split(' ')[1])
                        break
                f.close()
                if mutate_fail == 1 or (ref_sum_mut != dt_sum_mut and ref_sum_mut != -10000 and dt_sum_mut != -10000):
                    shutil.copy(mutate_file, out_dir)
                    shutil.copy(ref_file_mut, out_dir)
                    shutil.copy(dt_file_mut, os.path.join(out_dir, mutate_file.split('/')[-1][:-5] + '_' + protocal.split('.')[0] + '.txt'))

def check_mutcircuit(src_dir = 'exp2_0/seed_convert_mutate', src_res_dir = 'exp2_0/tgt_mutate', recheck = False):

    file_names = [file for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_bug_circuit'
    mutplayer_dir = src_dir + '_mutcircuit'
    mutplayer_res_dir = src_res_dir + '_mutcircuit'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    fail_dir = src_dir + '_fail'
    if os.path.exists(fail_dir) != True:
        os.mkdir(fail_dir)
    check_dir = src_dir + '_check'
    if recheck == True:
        if os.path.exists(check_dir):
            shutil.rmtree(check_dir) 
        os.mkdir(check_dir)
        check_mutate_dir = src_dir + '_check_mutcircuit'
        if os.path.exists(check_mutate_dir):
            shutil.rmtree(check_mutate_dir) 
        os.mkdir(check_mutate_dir)
    ###The result from mascot is used as reference###
    for file in file_names:
        ref_file = os.path.join(src_res_dir, file.split('/')[-1][:-5] + '.txt')
        ref_sum = -10000
        org_fail = -1
        try:
            f = open(ref_file)
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('error') != -1:
                    org_fail = 1
                    break
                if line.find('checksum') != -1:
                        line = f.readline()
                        ref_sum = int(line)
            f.close()
        except:
            org_fail = 1
            continue
        mutcircuit_files = glob.glob(os.path.join(mutplayer_res_dir, file.split('/')[-1][:-5])+'_c*')
        for mutcircuit_file in mutcircuit_files:
            mutcircuit_sum = -10000
            mutate_fail = -1
            try:
                f = open(mutcircuit_file)
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if line.find('error') != -1:
                        mutate_fail = 1
                        break
                    if line.find('checksum') != -1:
                        line = f.readline()
                        mutcircuit_sum = int(line)
                f.close()
            except:
                mutate_fail = 1
                continue
            print(ref_sum, mutcircuit_sum)
            if mutate_fail != 1 and ref_sum != mutcircuit_sum and ref_sum != -10000 and mutcircuit_sum != -10000:
                shutil.copy(os.path.join(src_dir, file), out_dir)
                shutil.copy(os.path.join(mutplayer_dir, mutcircuit_file.split('/')[-1][:-4] + '.ezpc'), os.path.join(out_dir, mutcircuit_file.split('/')[-1][:-4] + '_mutcircuit.ezpc'))
                shutil.copy(ref_file, out_dir)
                shutil.copy(mutcircuit_file, os.path.join(out_dir, mutcircuit_file.split('/')[-1][:-4] + '_mutcircuit.txt'))

                if recheck == True:
                    shutil.copy(os.path.join(src_dir, file), check_dir)
                    shutil.copy(os.path.join(mutplayer_dir, mutcircuit_file.split('/')[-1][:-4] + '.ezpc'), os.path.join(check_mutate_dir, mutcircuit_file.split('/')[-1][:-4] + '_mutcircuit.ezpc'))
            if (mutate_fail == 1 and org_fail == -1) or (ref_sum == -10000 and mutcircuit_sum != -10000):
                shutil.copy(os.path.join(src_dir, file), fail_dir)
                shutil.copy(os.path.join(mutplayer_dir, mutcircuit_file.split('/')[-1][:-4] + '.ezpc'), os.path.join(fail_dir, mutcircuit_file.split('/')[-1][:-4] + '_mutcircuit.ezpc'))
                shutil.copy(ref_file, fail_dir)
                shutil.copy(mutcircuit_file, os.path.join(fail_dir, mutcircuit_file.split('/')[-1][:-4] + '_mutcircuit.txt'))

def check_mutprivate(src_dir = 'exp2_0/seed_convert_mutate', src_res_dir = 'exp2_0/tgt_mutate', recheck = False):

    file_names = [file for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_bug_private'
    mutplayer_dir = src_dir + '_mutprivate'
    mutplayer_res_dir = src_res_dir + '_mutprivate'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    fail_dir = src_dir + '_fail_private'
    if os.path.exists(fail_dir) != True:
        os.mkdir(fail_dir)
    check_dir = src_dir + '_check'
    if recheck == True:
        if os.path.exists(check_dir):
            shutil.rmtree(check_dir) 
        os.mkdir(check_dir)
        check_mutate_dir = src_dir + '_check_mutprivate'
        if os.path.exists(check_mutate_dir):
            shutil.rmtree(check_mutate_dir) 
        os.mkdir(check_mutate_dir)
   
    ###The result from mascot is used as reference###
    for file in file_names:
        ref_file = os.path.join(src_res_dir, file.split('/')[-1][:-5] + '.txt')
        ref_sum = -10000
        org_fail = -1
        try:
            f = open(ref_file)
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('error') != -1:
                    org_fail = 1
                    break
                if line.find('checksum') != -1:
                        line = f.readline()
                        ref_sum = int(line)
            f.close()
        except:
            org_fail = 1
            continue
        mutprivate_files = glob.glob(os.path.join(mutplayer_res_dir, file.split('/')[-1][:-5])+'_p*')
        for mutprivate_file in mutprivate_files:
            mutprivate_sum = -10000
            mutate_fail = -1
            try:
                f = open(mutprivate_file)
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if line.find('error') != -1:
                        mutate_fail = 1
                        break
                    if line.find('checksum') != -1:
                        line = f.readline()
                        mutprivate_sum = int(line)
                f.close()
            except:
                mutate_fail = 1
                continue
            
            if mutate_fail != 1 and ref_sum != mutprivate_sum and ref_sum != -10000 and mutprivate_sum != -10000:
                shutil.copy(os.path.join(src_dir, file), out_dir)
                shutil.copy(os.path.join(mutplayer_dir, mutprivate_file.split('/')[-1][:-4] + '.ezpc'), os.path.join(out_dir, mutprivate_file.split('/')[-1][:-4] + '_mutprivate.ezpc'))
                shutil.copy(ref_file, out_dir)
                shutil.copy(mutprivate_file, os.path.join(out_dir, mutprivate_file.split('/')[-1][:-4] + '_mutprivate.txt'))

                if recheck == True:
                    shutil.copy(os.path.join(src_dir, file), check_dir)
                    shutil.copy(os.path.join(mutplayer_dir, mutprivate_file.split('/')[-1][:-4] + '.ezpc'), os.path.join(check_mutate_dir, mutprivate_file.split('/')[-1][:-4] + '_mutprivate.ezpc'))
            if (mutate_fail == 1 and org_fail == -1) or (ref_sum == -10000 and mutprivate_sum != -10000):
                shutil.copy(os.path.join(src_dir, file), fail_dir)
                shutil.copy(os.path.join(mutplayer_dir, mutprivate_file.split('/')[-1][:-4] + '.ezpc'), os.path.join(fail_dir, mutprivate_file.split('/')[-1][:-4] + '_mutprivate.ezpc'))
                shutil.copy(ref_file, fail_dir)
                shutil.copy(mutprivate_file, os.path.join(fail_dir, mutprivate_file.split('/')[-1][:-4] + '_mutprivate.txt'))
            

if __name__ == '__main__':
    # check('exp23_c0/seed_convert', 'exp23_c0/seed_convert_mutate', 'exp23_c0/tgt', 'exp23_c0/tgt_mutate', max_mutate = 20)  
    # check('exp3_0/seed_convert', 'exp3_0/seed_convert_mutate', 'exp3_0/tgt', 'exp3_0/tgt_mutate', max_mutate = 10)  
    # check('exp1_9/seed_convert', 'exp1_9/seed_convert_mutate', 'exp1_9/tgt', 'exp1_9/tgt_mutate', max_mutate = 10)

    # check_mutprivate(src_dir = 'exp11_4/seed_convert', src_res_dir = 'exp11_4/tgt')
    # check_mutprivate('exp14_0/seed_convert_check', 'exp14_0/tgt_check')
    check_mutcircuit(src_dir = 'exp21_0/seed_convert', src_res_dir = 'exp21_0/tgt')

