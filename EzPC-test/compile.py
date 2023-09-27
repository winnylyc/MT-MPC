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
            p1 = subprocess.run(['./' + no_ext + '0', '-r', str(num)], cwd=mpc_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=60)
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

def compile(src_dir = 'src_convert', tgt_dir = 'tgt', dt = False, no_cov = False, log = False):
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    source_file = 'EzPC/EzPC/EzPC/'
    if os.path.exists(tgt_dir) and dt == False:
        shutil.rmtree(tgt_dir)
    os.makedirs(tgt_dir, exist_ok=True)
    if no_cov == False:
        file_names = [file for file in os.listdir(src_dir) if file[-4:]=='ezpc']
    else:
        file_names = [file for file in os.listdir(src_dir) if file[-4:]=='ezpc' and file.find('cov') == -1]
    # mpc_dir = os.path.abspath(os.path.join("..", "..", "mp-spdz"))
    mpc_dir = os.path.abspath(os.path.join("..", source_file))
    for file in file_names:
        shutil.copyfile(os.path.join(src_dir, file),
                        os.path.join(mpc_dir, 'test_fuzz', file))
    
    compile_time = 0
    compile_success_num = 0
    run_time = 0
    run_sucess_num = 0
    
    for file in file_names:
        if log == True:
            print(file)
        no_ext = os.path.splitext(file)[0]
        start_time = time.time()
        p1 = subprocess.run(['./ezpc.sh', 'test_fuzz/' + no_ext + '.ezpc', '--bitlen', '32'], cwd=mpc_dir,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True)
        try:
            p1.check_returncode()
            if log == True:
                print(p1.stdout)
        # except subprocess.CalledProcessError as e:
        except:
            with open(os.path.join(cur_dir, tgt_dir, f"{no_ext}.txt"), 'w') as f:
                f.write(p1.stdout)
            continue
        p2 = subprocess.run(['./compile_aby.sh', 'test_fuzz/' + no_ext + '0.cpp'], cwd=mpc_dir,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, timeout=180)
        try:
            p2.check_returncode()
            if log == True:
                print(p2.stdout)
        # except subprocess.CalledProcessError as e:
        except:
            with open(os.path.join(cur_dir, tgt_dir, f"{no_ext}.txt"), 'w') as f:
                f.write(p1.stdout)
                f.write(p2.stdout)
            continue
        end_time = time.time()
        compile_time += end_time - start_time
        compile_success_num += 1
        tgt_file = os.path.join(tgt_dir, f"{no_ext}.txt")
        processes = []
        start_time = time.time()
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
    # compile(src_dir = 'src_convert', tgt_dir = 'tgt', dt = False, no_cov = False)
    # compile(src_dir = 'src_convert_mutate', tgt_dir = 'tgt_mutate', dt = False, no_cov = False)

    compile(src_dir = 'src_test', tgt_dir = 'tgt_test', dt = False, no_cov = False)
