import os
import shutil
import subprocess
import multiprocessing
import time

def run_termial(num, mpc_dir, no_ext, tgt_file, compile_inf, log):
    current_attempt = 0 
    while current_attempt < 3:
        current_attempt += 1
        try:
            p1 = subprocess.run(['./bin/test_' + no_ext, str(num), '12345', '32'], cwd=mpc_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=60)
            try:
                p1.check_returncode()
                if num == 1:
                    with open(tgt_file, 'w') as f:
                        for inf in compile_inf:
                            f.write(inf)
                        f.write(p1.stdout)
                        if log == True:
                            print(p1.stdout)
            except:
                if num == 1:
                    with open(tgt_file, 'w') as f:
                        for inf in compile_inf:
                            f.write(inf)
                        f.write(p1.stdout)
                        if log == True:
                            print(p1.stdout)
            break
        except:
            print('Attempt times:', str(current_attempt))

def compile(src_dir = 'src_convert', tgt_dir = 'tgt', testdir = 'fuzzing', no_cov = False, log = False):
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    source_file = 'emp-sh2pc'
    if os.path.exists(tgt_dir):
        shutil.rmtree(tgt_dir)
    os.makedirs(tgt_dir, exist_ok=True)
    if no_cov == False:
        file_names = [file for file in os.listdir(src_dir) if file[-3:]=='cpp']
    else:
        file_names = [file for file in os.listdir(src_dir) if file[-3:]=='cpp' and file.find('cov') == -1]
    ### craate the directory and add the directory into the cmakelist
    mpc_dir = os.path.abspath(os.path.join("..", source_file))
    # if os.path.exists(os.path.join(mpc_dir, testdir)):
    #     shutil.rmtree(os.path.join(mpc_dir, testdir))
    # os.makedirs(os.path.join(mpc_dir, testdir), exist_ok=True)
    ### currently the file will not be deleted to avoid cmake to have problem
    if os.path.exists(os.path.join(mpc_dir, testdir)) != True:
        os.makedirs(os.path.join(mpc_dir, testdir), exist_ok=True)
    text_modified = ''
    added = False
    add_text = 'ADD_SUBDIRECTORY(test)'.replace('test', testdir)
    f = open(os.path.join(mpc_dir, 'CMakeLists.txt'))
    while True:
        line = f.readline()
        if not line:
            break
        if line.find("# end of directory list") != -1:
            if added == False:
                text_modified += add_text + '\n'
            text_modified += line
        else:
            text_modified += line
            if line.find(add_text) != -1 and added == False:
                added = True

    f.close()
    f = open(os.path.join(mpc_dir, 'CMakeLists.txt'), 'w')
    f.write(text_modified)
    f.close()

    for file in file_names:
        shutil.copyfile(os.path.join(src_dir, file),
                        os.path.join(mpc_dir, testdir, file))
    shutil.copyfile("prototype/CMakeLists.txt", os.path.join(mpc_dir, testdir, 'CMakeLists.txt'))
    text_modified = ''
    f = open(os.path.join(mpc_dir, testdir, 'CMakeLists.txt'))
    while True:
        line = f.readline()
        if not line:
            break
        text_modified += line
        if line.find('# Test cases') != -1:
            for file in file_names:
                no_ext = file.split('.')[0]
                text_modified += 'add_test_case_with_run(initialtest)\n'.replace('initialtest', no_ext)
    f.close()
    f = open(os.path.join(mpc_dir, testdir, 'CMakeLists.txt'), 'w')
    f.write(text_modified)
    f.close()
    p1 = subprocess.run(['cmake', '.'], cwd = '../emp-sh2pc',
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True)
    try:
        p1.check_returncode()
        if log == True:
            print(p1.stdout)
    except:
        print('cmake wrong')
        return

    compile_time = 0
    compile_success_num = 0
    run_time = 0
    run_sucess_num = 0
    for file in file_names:
        if log == True:
            print(file)
        no_ext = os.path.splitext(file)[0]
        tgt_file = os.path.join(tgt_dir, f"{no_ext}.txt")
        start_time = time.time()
        p2 = subprocess.run(['make', 'test_' + no_ext], cwd = '../emp-sh2pc',
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True)
        try:
            p2.check_returncode()
            if log == True:
                print(p2.stdout)
        except:
            with open(tgt_file, 'w') as f:
                f.write(p1.stdout)
                f.write(p2.stdout)
            continue
        end_time = time.time()
        compile_time += end_time - start_time
        compile_success_num += 1
        start_time = time.time()
        processes = []
        for num in range(2):
            process = multiprocessing.Process(target = run_termial, args=(num, mpc_dir, no_ext, tgt_file, [p1.stdout, p2.stdout], log))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()
        end_time = time.time()
        run_time += end_time - start_time
        run_sucess_num += 1
        if log == True:
            print('complete compilation:' + file)
    return compile_time, compile_success_num, run_time, run_sucess_num

if __name__ == '__main__':
    # compile(src_dir = 'src_convert', tgt_dir = 'tgt', testdir = 'fuzzing', no_cov = False, log = True)
    # compile(src_dir = 'src_convert_mutate', tgt_dir = 'tgt_mutate', testdir = 'fuzzingmutate', no_cov = False, log = True)
    # compile(src_dir = 'src_convert_mutprivate', tgt_dir = 'tgt_mutprivate', testdir = 'fuzzingmutprivate', no_cov = False)

    compile(src_dir = 'src_test', tgt_dir = 'tgt_test', testdir = 'fuzzingtest', no_cov = False)
