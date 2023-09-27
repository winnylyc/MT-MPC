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
    for file in file_names:
        for i in range(max_mutate):
            mutate_file = os.path.join(mutate_dir, file.split('/')[-1][:-4] + '_mut' + str(i) + '.mpc')
            coverage_file = os.path.join(src_dir, file.split('/')[-1][:-4] + '_cov.txt')
            result_file = os.path.join(src_res_dir, file.split('/')[-1][:-4] + '.txt')
            mutate_result_file = os.path.join(mutate_res_dir, mutate_file.split('/')[-1][:-4] + '.txt')
            org_fail = -1
            ori_sum = -10000
            f = open(result_file)
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('Traceback') != -1:
                    org_fail = 1
                    break
                if line.find('checksum:') != -1:
                    ori_sum = float(line.split(' ')[1])
                    break
            f.close()
            mutate_sum = -10000
            mutate_fail = -1
            try:
                f = open(mutate_result_file)
            except:
                break
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('Traceback') != -1:
                    mutate_fail = 1
                    break
                if line.find('checksum:') != -1:
                    mutate_sum = float(line.split(' ')[1])
                    break
            f.close()
            if mutate_sum != ori_sum and mutate_sum != -10000 and mutate_sum != -10000:
                shutil.copy(file, out_dir)
                shutil.copy(mutate_file, out_dir)
                shutil.copy(coverage_file, out_dir)
                shutil.copy(result_file, out_dir)
                shutil.copy(mutate_result_file, out_dir)
            if org_fail == -1 and mutate_fail == 1:
                shutil.copy(file, fail_dir)
                shutil.copy(mutate_file, fail_dir)
                shutil.copy(coverage_file, fail_dir)
                shutil.copy(result_file, fail_dir)
                shutil.copy(mutate_result_file, fail_dir)

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
    # test_protocals = ['spdz2k.sh', 'semi2k.sh', 'semi-bin.sh', 'tinier.sh']
    test_protocals = ['semi-bin.sh']

    file_names = [file for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_bug_dt'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    fail_dir = src_dir + '_fail_dt'
    if os.path.exists(fail_dir):
        shutil.rmtree(fail_dir) 
    os.mkdir(fail_dir)
    mut_out_dir = src_dir + '_bug_mutdt'
    if os.path.exists(mut_out_dir):
        shutil.rmtree(mut_out_dir) 
    os.mkdir(mut_out_dir)
    mut_fail_dir = src_dir + '_fail_mutdt'
    if os.path.exists(mut_fail_dir):
        shutil.rmtree(mut_fail_dir) 
    os.mkdir(mut_fail_dir)
    ###The result from mascot is used as reference###
    for file in file_names:
        ref_file = os.path.join(src_res_dir, file.split('/')[-1][:-4] + '.txt')
        org_fail = -1
        ref_sum = -10000
        try:
            f = open(ref_file)
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('Traceback') != -1:
                    org_fail = 1
                    break
                if line.find('checksum:') != -1:
                    ref_sum = float(line.split(' ')[1])
                    break
            f.close()
        except:
            continue
        if org_fail == 1:
            continue
        
        for protocal in test_protocals:
            dt_file = os.path.join(src_res_dir + '_' + protocal.split('.')[0], file.split('/')[-1][:-4] + '.txt')
            dt_sum = -10000
            mutate_fail = -1
            try:
                f = open(dt_file)
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if line.find('Traceback') != -1:
                        mutate_fail = 1
                        break
                    if line.find('checksum:') != -1:
                        dt_sum = float(line.split(' ')[1])
                        break
                f.close()
            except:
                continue
            if ref_sum != dt_sum and ref_sum != -10000 and dt_sum != -10000:
                shutil.copy(os.path.join(src_dir, file), out_dir)
                shutil.copy(ref_file, out_dir)
                shutil.copy(dt_file, os.path.join(out_dir, file.split('/')[-1][:-4] + '_' + protocal.split('.')[0] + '.txt'))
            elif (org_fail == -1 and mutate_fail == 1) or (ref_sum != -10000 and dt_sum == -10000):
                shutil.copy(os.path.join(src_dir, file), fail_dir)
                shutil.copy(ref_file, fail_dir)
                shutil.copy(dt_file, os.path.join(fail_dir, file.split('/')[-1][:-4] + '_' + protocal.split('.')[0] + '.txt'))
            for i in range(max_mutate):
                mutate_file = os.path.join(mutate_dir, file.split('/')[-1][:-4] + '_mut' + str(i) + '.mpc')
                ref_file_mut = os.path.join(mutate_res_dir + '_mascot', mutate_file.split('/')[-1][:-4] + '.txt')
                dt_file_mut = os.path.join(mutate_res_dir + '_' + protocal.split('.')[0], mutate_file.split('/')[-1][:-4] + '.txt')
                org_fail = -1
                ref_sum_mut = -10000
                try:
                    f = open(ref_file_mut)
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        if line.find('Traceback') != -1:
                            org_fail = 1
                            break
                        if line.find('checksum:') != -1:
                            ref_sum_mut = float(line.split(' ')[1])
                            break
                    f.close()
                except:
                    continue
                
                dt_sum_mut = -10000
                mutate_fail = -1
                try:
                    f = open(dt_file_mut)
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        if line.find('Traceback') != -1:
                            mutate_fail = 1
                            break
                        if line.find('checksum:') != -1:
                            dt_sum_mut = float(line.split(' ')[1])
                            break
                    f.close()
                except:
                    continue
                
                if ref_sum_mut != dt_sum_mut and ref_sum_mut != -10000 and dt_sum_mut != -10000:
                    shutil.copy(mutate_file, mut_out_dir)
                    shutil.copy(ref_file_mut, mut_out_dir)
                    shutil.copy(dt_file_mut, os.path.join(mut_out_dir, mutate_file.split('/')[-1][:-4] + '_' + protocal.split('.')[0] + '.txt'))
                elif (org_fail == -1 and mutate_fail == 1) or (ref_sum_mut != -10000 and dt_sum_mut == -10000):
                    shutil.copy(mutate_file, mut_fail_dir)
                    shutil.copy(ref_file_mut, mut_fail_dir)
                    shutil.copy(dt_file_mut, os.path.join(mut_fail_dir, mutate_file.split('/')[-1][:-4] + '_' + protocal.split('.')[0] + '.txt'))
                

def check_mutplayer(src_dir = 'exp2_0/seed_convert_mutate', src_res_dir = 'exp2_0/tgt_mutate'):

    file_names = [file for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_bug_player'
    mutplayer_dir = src_dir + '_mutplayer'
    mutplayer_src_dir = src_res_dir + '_mutplayer'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    ###The result from mascot is used as reference###
    for file in file_names:
        ref_file = os.path.join(src_res_dir, file.split('/')[-1][:-4] + '.txt')
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
        mutplayer_file = os.path.join(mutplayer_src_dir, file.split('/')[-1][:-4] + '.txt')
        mutplayer_sum = -10000
        try:
            f = open(mutplayer_file)
        except:
            continue
        while True:
            line = f.readline()
            if not line:
                break
            if line.find('checksum:') != -1:
                mutplayer_sum = float(line.split(' ')[1])
                break
        f.close()
        if ref_sum != mutplayer_sum and ref_sum != -10000 and mutplayer_sum != -10000:
            shutil.copy(os.path.join(src_dir, file), out_dir)
            shutil.copy(os.path.join(mutplayer_dir, file), os.path.join(out_dir, file.split('/')[-1][:-4] + '_mutplayer.mpc'))
            shutil.copy(ref_file, out_dir)
            shutil.copy(mutplayer_file, os.path.join(out_dir, file.split('/')[-1][:-4] + '_mutplayer.txt'))

def check_mutprivate(src_dir = 'exp2_0/seed_convert_mutate', src_res_dir = 'exp2_0/tgt_mutate'):

    file_names = [file for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    out_dir = src_dir + '_bug_private'
    mutplayer_dir = src_dir + '_mutprivate'
    mutplayer_res_dir = src_res_dir + '_mutprivate'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir) 
    os.mkdir(out_dir)
    fail_dir = src_dir + '_fail_private'
    if os.path.exists(fail_dir):
        shutil.rmtree(fail_dir) 
    os.mkdir(fail_dir)
    ###The result from mascot is used as reference###
    for file in file_names:
        ref_file = os.path.join(src_res_dir, file.split('/')[-1][:-4] + '.txt')
        org_fail = -1
        ref_sum = -10000
        try:
            f = open(ref_file)
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('Traceback') != -1:
                    org_fail = 1
                    break
                if line.find('checksum:') != -1:
                    ref_sum = float(line.split(' ')[1])
                    break
            f.close()
        except:
            continue
        if org_fail == 1:
            continue
        mutprivate_files = glob.glob(os.path.join(mutplayer_res_dir, file.split('/')[-1][:-4])+'_p*')
        for mutprivate_file in mutprivate_files:
            mutprivate_sum = -10000
            try:
                f = open(mutprivate_file)
            except:
                continue
            mutate_fail = -1
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('Traceback') != -1:
                    mutate_fail = 1
                    break
                if line.find('checksum:') != -1:
                    mutprivate_sum = float(line.split(' ')[1])
                    break
            f.close()
            if ref_sum != mutprivate_sum and ref_sum != -10000 and mutprivate_sum != -10000:
                shutil.copy(os.path.join(src_dir, file), out_dir)
                shutil.copy(os.path.join(mutplayer_dir, mutprivate_file.split('/')[-1][:-4] + '.mpc'), os.path.join(out_dir, mutprivate_file.split('/')[-1][:-4] + '_mutprivate.mpc'))
                shutil.copy(ref_file, out_dir)
                shutil.copy(mutprivate_file, os.path.join(out_dir, mutprivate_file.split('/')[-1][:-4] + '_mutprivate.txt'))
            elif (org_fail == -1 and mutate_fail == 1) or (ref_sum != -10000 and mutprivate_sum == -10000):
                shutil.copy(os.path.join(src_dir, file), fail_dir)
                shutil.copy(os.path.join(mutplayer_dir, mutprivate_file.split('/')[-1][:-4] + '.mpc'), os.path.join(fail_dir, mutprivate_file.split('/')[-1][:-4] + '_mutprivate.mpc'))
                shutil.copy(ref_file, fail_dir)
                shutil.copy(mutprivate_file, os.path.join(fail_dir, mutprivate_file.split('/')[-1][:-4] + '_mutprivate.txt'))
            

if __name__ == '__main__':
    # check('exp4_0/seed_convert', 'exp4_0/seed_convert_mutate', 'exp4_0/tgt', 'exp4_0/tgt_mutate')  

    # check(src_dir = 'src_2_convert', mutate_dir = 'src_2_convert_mutate', src_res_dir = 'tgt', mutate_res_dir = 'tgt_mutate', max_mutate = 5)
    
    # check_dt()

    # check_mutplayer()
    # check_mutprivate(src_dir = 'exp40_0/seed_convert_mutate', src_res_dir = 'exp40_0/tgt_mutate')
    # check('exp12_0/seed_convert', 'exp12_0/seed_convert_mutate', # 'exp12_0/tgt', 'exp12_0/tgt_mutate_mascot', 5)
    check_dt('exp12_0/seed_convert', 'exp12_0/seed_convert_mutate', 'exp12_0/tgt', 'exp12_0/tgt_mutate', 5)
    
    
