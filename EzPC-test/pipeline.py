import os
import shutil
from generator import generator
from convert import convert
from coverage_run import coverage
from coverage_res import coverageRes
from compile import compile
from EMI import EMI, EMI_private, EMI_circuit
from check import check, check_dt, check_mutprivate, check_check, check_mutcircuit

from optparse import OptionParser
from glob import glob
import sys
from datetime import datetime

### Used for multiprocess ###
def modify_name(experiment_all, seed_dir):
    file_names = [file for file in os.listdir(seed_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    for file_name in file_names:
        split_name = file_name.split('-')
        new_file_name = split_name[0]+experiment_all + '-' + '-'.join(split_name[1:])
        os.rename(os.path.join(seed_dir, file_name), os.path.join(seed_dir, new_file_name))

### Used for clear source code, bytecode and schedule generated during pipeline in mp-spdz file ###
def clear(experiment_all):
    source_dir = "../EzPC/EzPC/EzPC/test_fuzz"
    byte_dir = "../EzPC/EzPC/EzPC"
    # source_files = glob.glob(source_dir+"/fuzz"+experiment_all + '*')
    # print(source_files)
    os.system("rm -rf " + source_dir+"/fuzz"+experiment_all + '*')
    os.system("rm -rf " + byte_dir+"/fuzz"+experiment_all + '*')

def main(experiment_all = 'exp35', log = False):
    if log == True:
        original_stdout = sys.stdout
    sample_number = 500
    batch_number = 100
    # max_mutation = 20
    max_mutation = 10
    for i in range(int(sample_number/batch_number)):
        experiment = experiment_all + '_' + str(i)
        if os.path.exists(experiment):
            shutil.rmtree(experiment)
        os.makedirs(experiment)
        if log == True:
            f = open(os.path.join(experiment, 'log.txt'), 'w')
            sys.stdout = f
        start_time = datetime.now()
        print('start_time:',start_time)
        seed_dir = os.path.join(experiment, 'seed')
        seedout_dir = os.path.join(experiment, 'tgt')
        generator(seed_dir, batch_number, grammertxt='gen.py')
        modify_name(experiment_all, seed_dir)
        convert(seed_dir)
        seed_dir = seed_dir + '_convert'
        coverage(seed_dir, flipcoin = 0.5)
        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile(seed_dir, seedout_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration = compilatin_end_time - compilatin_start_time
        coverageRes(seed_dir, seedout_dir)
        # EMI(seed_dir, seedout_dir, max_mutation, 0.5, experiment_all, templete = 'gen_block_templete.py')
        EMI(seed_dir, seedout_dir, max_mutation, 0.5, experiment_all, templete = 'gen_block_templete.py')
        mutate_dir = seed_dir + '_mutate'
        mutateout_dir = os.path.join(experiment, 'tgt_mutate')
        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile(mutate_dir, mutateout_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        check(seed_dir, mutate_dir, seedout_dir, mutateout_dir, max_mutation)

        check_dir = seed_dir + '_check'
        checkout_dir = seedout_dir + '_check'
        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile(check_dir, checkout_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        check_mutate_dir = check_dir + '_mutate'
        checkout_mutate_dir = checkout_dir + '_mutate'
        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile(check_mutate_dir, checkout_mutate_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        check_check(check_dir, check_mutate_dir, checkout_dir, checkout_mutate_dir)
        end_time = datetime.now()
        print('end_time:',end_time)
        print('Duration: {}'.format(end_time - start_time))
        print('Compilation Duration: {}'.format(compilation_duration))
        if log == True:
            f.close()
            sys.stdout = original_stdout
    clear(experiment_all)

def main_circuit(experiment_all = 'exp20', log = False):
    if log == True:
        original_stdout = sys.stdout
    sample_number = 500
    batch_number = 50
    # max_mutation = 20
    max_mutation = 10
    for i in range(int(sample_number/batch_number)):
        experiment = experiment_all + '_' + str(i)
        if os.path.exists(experiment):
            shutil.rmtree(experiment)
        os.makedirs(experiment)
        if log == True:
            f = open(os.path.join(experiment, 'log.txt'), 'w')
            sys.stdout = f
        compile_time_total, compile_success_num_total, run_time_total, run_sucess_num_total = 0, 0, 0, 0
        start_time = datetime.now()
        print('start_time:',start_time)
        seed_dir = os.path.join(experiment, 'seed')
        seedout_dir = os.path.join(experiment, 'tgt')
        generator(seed_dir, batch_number, grammertxt='gen_reveal.py')
        modify_name(experiment_all, seed_dir)
        convert(seed_dir)
        seed_dir = seed_dir + '_convert'
        coverage(seed_dir)

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(seed_dir, seedout_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration = compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num

        coverageRes(seed_dir, seedout_dir)
        EMI(seed_dir, seedout_dir, max_mutation, 0.5, experiment_all, templete = 'gen_block_templete.py')
        mutate_dir = seed_dir + '_mutate'
        mutateout_dir = os.path.join(experiment, 'tgt_mutate')

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(mutate_dir, mutateout_dir)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num


        EMI_circuit(seed_dir, seedout_dir)
        EMI_circuit(mutate_dir, mutateout_dir)

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(seed_dir+'_mutcircuit', seedout_dir+'_mutcircuit', log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num


        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(mutate_dir+'_mutcircuit', mutateout_dir+'_mutcircuit')
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num


        check(seed_dir, mutate_dir, seedout_dir, mutateout_dir, max_mutation)
        check_dir = seed_dir + '_check'
        checkout_dir = seedout_dir + '_check'

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(check_dir, checkout_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num

        check_mutate_dir = check_dir + '_mutate'
        checkout_mutate_dir = checkout_dir + '_mutate'

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(check_mutate_dir, checkout_mutate_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num

        check_check(check_dir, check_mutate_dir, checkout_dir, checkout_mutate_dir)

        check_mutcircuit(src_dir = seed_dir, src_res_dir = seedout_dir, recheck = True)

        check_dir = seed_dir + '_check'
        checkout_dir = seedout_dir + '_check'

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(check_dir, checkout_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num

        check_mutate_dir = check_dir + '_mutcircuit'
        checkout_mutate_dir = checkout_dir + '_mutcircuit'

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(check_mutate_dir, checkout_mutate_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num

        check_mutcircuit(check_dir, checkout_dir)

        check_mutcircuit(src_dir = mutate_dir, src_res_dir = mutateout_dir, recheck = True)

        check_dir = mutate_dir + '_check'
        checkout_dir = mutateout_dir + '_check'

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(check_dir, checkout_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num

        check_mutate_dir = check_dir + '_mutcircuit'
        checkout_mutate_dir = checkout_dir + '_mutcircuit'

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(check_mutate_dir, checkout_mutate_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num

        check_mutcircuit(check_dir, checkout_dir)


        end_time = datetime.now()
        print('end_time:',end_time)
        print('Duration: {}'.format(end_time - start_time))
        print('Compilation Duration: {}'.format(compilation_duration))
        print('All Compilation Time:', compile_time_total)
        print('Average Compilation Time:', compile_time_total/compile_success_num_total)
        print('All Execution Time:', run_time_total)
        print('Average Execution Time:', run_time_total/run_sucess_num_total)
        if log == True:
            f.close()
            sys.stdout = original_stdout
    clear(experiment_all)

def main_mutprivate(experiment_all = 'exp20', log = False):
    if log == True:
        original_stdout = sys.stdout
    sample_number = 500
    batch_number = 50
    # max_mutation = 20
    max_mutation = 5
    for i in range(int(sample_number/batch_number)):
        experiment = experiment_all + '_' + str(i)
        if os.path.exists(experiment):
            shutil.rmtree(experiment)
        os.makedirs(experiment)
        if log == True:
            f = open(os.path.join(experiment, 'log.txt'), 'w')
            sys.stdout = f
        compile_time_total, compile_success_num_total, run_time_total, run_sucess_num_total = 0, 0, 0, 0
        start_time = datetime.now()
        print('start_time:',start_time)
        seed_dir = os.path.join(experiment, 'seed')
        seedout_dir = os.path.join(experiment, 'tgt')
        generator(seed_dir, batch_number, grammertxt='gen_reveal.py')
        modify_name(experiment_all, seed_dir)
        convert(seed_dir)
        seed_dir = seed_dir + '_convert'
        # coverage(seed_dir)

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(seed_dir, seedout_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration = compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num
        
        # coverageRes(seed_dir, seedout_dir)
        # EMI(seed_dir, seedout_dir, max_mutation, 0.5, experiment_all, templete = 'gen_block_templete.py')
        # mutate_dir = seed_dir + '_mutate'
        # mutateout_dir = os.path.join(experiment, 'tgt_mutate')
        # compile(mutate_dir, mutateout_dir)
        EMI_private(seed_dir, seedout_dir)
        # EMI_private(mutate_dir, mutateout_dir)

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(seed_dir+'_mutprivate', seedout_dir+'_mutprivate', log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num

        # compile(mutate_dir+'_mutprivate', mutateout_dir+'_mutprivate')
        # check(seed_dir, mutate_dir, seedout_dir, mutateout_dir, max_mutation)
        check_mutprivate(src_dir = seed_dir, src_res_dir = seedout_dir, recheck = True)
        # check_mutprivate(src_dir = mutate_dir, src_res_dir = mutateout_dir)

        check_dir = seed_dir + '_check'
        checkout_dir = seedout_dir + '_check'

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(check_dir, checkout_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num
        

        check_mutate_dir = check_dir + '_mutprivate'
        checkout_mutate_dir = checkout_dir + '_mutprivate'

        compilatin_start_time = datetime.now()
        print('compilatin_start_time:',compilatin_start_time)
        compile_time, compile_success_num, run_time, run_sucess_num = compile(check_mutate_dir, checkout_mutate_dir, log = log)
        compilatin_end_time = datetime.now()
        print('compilatin_end_time:',compilatin_end_time)
        compilation_duration += compilatin_end_time - compilatin_start_time
        compile_time_total += compile_time
        compile_success_num_total += compile_success_num
        run_time_total += run_time
        run_sucess_num_total += run_sucess_num

        check_mutprivate(check_dir, checkout_dir)

        end_time = datetime.now()
        print('end_time:',end_time)
        print('Duration: {}'.format(end_time - start_time))
        print('Compilation Duration: {}'.format(compilation_duration))
        print('All Compilation Time:', compile_time_total)
        print('Average Compilation Time:', compile_time_total/compile_success_num_total)
        print('All Execution Time:', run_time_total)
        print('Average Execution Time:', run_time_total/run_sucess_num_total)
        if log == True:
            f.close()
            sys.stdout = original_stdout
    clear(experiment_all)


if __name__ == '__main__':
    # clear('')
    # exit()
    parser = OptionParser() 
    parser.add_option("-e", "--exp", dest="experiment_all", help="expriment name")
    parser.add_option("-p", "--private", dest="private", action="store_true", help="whether conduct EMI on private")
    parser.add_option("-a", "--party", dest="party", action="store_true", help="whether conduct EMI on party")
    parser.add_option("-c", "--circuit", dest="circuit", action="store_true", help="whether conduct MT on circuit")
    parser.add_option("-l", "--log", dest="log", action="store_true", help="whether keep the log")
    (options, args) = parser.parse_args()
    experiment_all = options.experiment_all
    private = options.private
    circuit = options.circuit
    log = options.log
    if private == True:
        main_mutprivate(experiment_all, log = log)
    elif circuit == True:
        main_circuit(experiment_all, log = log)
    else:
        main(experiment_all, log = log)
    # main(experiment_all)
    # clear('')
    # main_mutplayer(experiment_all)
    # main_mutprivate(experiment_all)