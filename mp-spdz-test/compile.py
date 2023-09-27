import os
import shutil
import subprocess
import time

def compile(src_dir = 'src_test', tgt_dir = 'tgt_test', dt = False, no_cov = False, skipprime = False):
    compiler_file = 'mp-spdz'
    # src_dir = 'seed'
    # src_dir = 'seed_mutate'
    # src_dir = 'src_1_convert'
    # src_dir = 'src_1_convert_mutate'
    # src_dir = 'src_2_convert'
    # src_dir = 'src_2_convert_mutate'
    # src_dir = 'src_bug'
    # src_dir = 'src_test'
    # src_dir = 'src_debug'
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    # tgt_dir = 'tgt'
    # tgt_dir = 'tgt_seed'
    # tgt_dir = 'tgt_mutate'

    # tgt_dir = 'tgt_seed_dce'
    # tgt_dir = 'tgt_mutate_dce'

    # tgt_dir = 'tgt_seed_fo'
    # tgt_dir = 'tgt_mutate_fo'

    # tgt_dir = 'tgt_src_1'
    # tgt_dir = 'tgt_src_1_mutate'
    if dt == True:
        # Dishonest_Prime = ['mascot.sh', 'mama.sh', 'semi.sh', 'lowgear.sh', 'highgear.sh', 'cowgear.sh', 'chaigear.sh', 'hemi.sh', 'temi.sh', 'soho.sh']
        # Dishonest_Prime = ['mascot.sh', 'mama.sh', 'semi.sh', 'hemi.sh', 'temi.sh', 'soho.sh']
        # Dishonest_Prime = ['mama.sh', 'lowgear.sh', 'highgear.sh']
        # Dishonest_Prime = ['mascot.sh', 'lowgear.sh', 'highgear.sh', 'cowgear.sh', 'chaigear.sh']
        # Dishonest_Prime = ['mascot.sh']
        Dishonest_2k = ['spdz2k.sh', 'semi2k.sh']
        # Dishonest_Binary = ['semi-bin.sh', 'tiny.sh', 'tinier.sh']
        # Dishonest_Binary = ['semi-bin.sh', 'tinier.sh']
        # Honest_Prime = ['rep-field.sh', 'ps-rep-field.sh', 'sy-rep-field.sh', 'mal-rep-field.sh', 'atlas.sh', 'shamir.sh', 'mal-shamir.sh', 'sy-shamir.sh']
        # Honest_2k = ['ring.sh', 'brain.sh', 'ps-rep-ring.sh', '	mal-rep-ring.sh', 'sy-rep-ring.sh', 'rep4-ring.sh']
        # Honest_Binary = ['replicated.sh', 'mal-rep-bin.sh', 'ps-rep-bin.sh', 'ccd.sh', 'mal-ccd.sh']
        # test_protocals_dir = Dishonest_Prime + Dishonest_2k + Dishonest_Binary
        Dishonest_Prime = ['mascot.sh']
        Dishonest_Binary = ['semi-bin.sh']
        test_protocals_dir = Dishonest_Prime + Dishonest_Binary
        for protocal in test_protocals_dir:
            tgt_protocal_dir = os.path.join(cur_dir, tgt_dir+ '_' + protocal.split('.')[0])
            if os.path.exists(tgt_protocal_dir) and dt == False:
                shutil.rmtree(tgt_protocal_dir)
            os.makedirs(tgt_protocal_dir, exist_ok=True)

    # if dt == False:
    if os.path.exists(tgt_dir) and dt == False:
        shutil.rmtree(tgt_dir)
    os.makedirs(tgt_dir, exist_ok=True)
    if no_cov == False:
        file_names = [file for file in os.listdir(src_dir) if file[-3:]=='mpc']
    else:
        file_names = [file for file in os.listdir(src_dir) if file[-3:]=='mpc' and file.find('cov') == -1]
    # mpc_dir = os.path.abspath(os.path.join("..", "..", "mp-spdz"))
    mpc_dir = os.path.abspath(os.path.join("..", compiler_file))
    for file in file_names:
        shutil.copyfile(os.path.join(src_dir, file),
                        os.path.join(mpc_dir, "Programs", "Source", file))
    compile_time = 0
    compile_success_num = 0
    run_time = 0
    run_sucess_num = 0

    for file in file_names:
        no_ext = os.path.splitext(file)[0]
        if dt == True:
            ###Three compilation mode###
            for i in range(3):
                ### currently test on prime just including mascot, so directly copy the result from tgt
                if i == 0 and skipprime == True:
                    ### some source code are not compiled/executed successfully
                    try:
                        shutil.copyfile(os.path.join(cur_dir, tgt_dir, f"{no_ext}.txt"), os.path.join(cur_dir, tgt_dir + '_mascot', f"{no_ext}.txt"))
                        continue
                    except:
                        continue
                ### currently not test on 2k
                if i == 1:
                    continue
                # p1 = subprocess.run(['python', 'compile.py', no_ext], cwd=mpc_dir,
                #                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                #                     text=True)
                if i == 0:
                    test_protocals = Dishonest_Prime
                elif i == 1:
                    test_protocals = Dishonest_2k
                else:
                    test_protocals = Dishonest_Binary
                print("p1:", no_ext, "================================")
                compile_fail = False
                start_time = time.time()
                for attempt in range(3):
                    try:
                        if i == 0:
                            p1 = subprocess.run(['python', 'compile.py', no_ext], cwd=mpc_dir,
                                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                universal_newlines=True, timeout=180)
                        elif i == 1:
                            p1 = subprocess.run(['python', 'compile.py', '-R', '64', no_ext], cwd=mpc_dir,
                                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                universal_newlines=True, timeout=180)
                        else:
                            p1 = subprocess.run(['python', 'compile.py', '-B', '64', no_ext], cwd=mpc_dir,
                                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                universal_newlines=True, timeout=180)
                        try:
                            p1.check_returncode()
                            for protocal in test_protocals:
                                with open(os.path.join(cur_dir, tgt_dir+ '_' + protocal.split('.')[0], f"{no_ext}.txt"), 'w') as f:
                                    f.write(p1.stdout)
                            break
                        except subprocess.CalledProcessError as e:
                            for protocal in test_protocals:
                                with open(os.path.join(cur_dir, tgt_dir+ '_' + protocal.split('.')[0], f"{no_ext}.txt"), 'w') as f:
                                    f.write(p1.stdout)
                            print(f"Attempt {attempt + 1} failed")
                            print(p1.stdout)
                            compile_fail = True
                            break
                    except subprocess.TimeoutExpired:
                        print(f"Attempt {attempt + 1} timed out")
                        time.sleep(1)
                else:
                    print("All attempts failed")
                    continue
                if compile_fail == True:
                    continue
                end_time = time.time()
                compile_time += end_time - start_time
                compile_success_num += 1
                print("Success")
                
                                
                for protocal in test_protocals:
                    print("p2:", no_ext, protocal, "================================")
                    start_time = time.time()
                    for attempt in range(3):
                        try:
                            p2 = subprocess.run([os.path.join('./Scripts', protocal), no_ext], cwd=mpc_dir,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                universal_newlines=True, timeout=180)
                            try:
                                p2.check_returncode()
                                with open(os.path.join(cur_dir, tgt_dir+ '_' + protocal.split('.')[0], f"{no_ext}.txt"), 'w') as f:
                                    f.write(p1.stdout)
                                    f.write(p2.stdout)
                                break
                            except subprocess.CalledProcessError as e:
                                with open(os.path.join(cur_dir, tgt_dir+ '_' + protocal.split('.')[0], f"{no_ext}.txt"), 'w') as f:
                                    f.write(p1.stdout)
                                    f.write(p2.stdout)
                                print(f"Attempt {attempt + 1} failed")
                                print(p2.stdout)
                                break
                        except subprocess.TimeoutExpired:
                            print(f"Attempt {attempt + 1} timed out")
                            time.sleep(1)
                    else:
                        print("All attempts failed")
                        continue
                    end_time = time.time()
                    run_time += end_time - start_time
                    run_sucess_num += 1
                    print("Success")
        else:
            print("p1:", no_ext, "================================")
            compile_fail = False
            start_time = time.time()
            for attempt in range(3):
                try:
                    p1 = subprocess.run(['python', 'compile.py', no_ext], cwd=mpc_dir,
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            universal_newlines=True, timeout=180)
                    try:
                        p1.check_returncode()
                        with open(os.path.join(cur_dir, tgt_dir, f"{no_ext}.txt"), 'w') as f:
                            f.write(p1.stdout)
                        break
                    
                    except subprocess.CalledProcessError as e:
                        with open(os.path.join(cur_dir, tgt_dir, f"{no_ext}.txt"), 'w') as f:
                            f.write(p1.stdout)
                        print(f"Attempt {attempt + 1} failed")
                        print(p1.stdout)
                        compile_fail = True
                        break
                except subprocess.TimeoutExpired:
                    print(f"Attempt {attempt + 1} timed out")
                    time.sleep(1)
            else:
                print("All attempts failed")
                continue
            if compile_fail == True:
                continue
            end_time = time.time()
            compile_time += end_time - start_time
            compile_success_num += 1
            print("Success")
            print("p2:", no_ext, "================================")
            start_time = time.time()
            for attempt in range(3):
                try:
                    p2 = subprocess.run(['./Scripts/mascot.sh', no_ext], cwd=mpc_dir,
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            universal_newlines=True, timeout=180)
                    try:
                        p2.check_returncode()
                        with open(os.path.join(cur_dir, tgt_dir, f"{no_ext}.txt"), 'w') as f:
                            f.write(p1.stdout)
                            f.write(p2.stdout)
                        break
                    except subprocess.CalledProcessError as e:
                        with open(os.path.join(cur_dir, tgt_dir, f"{no_ext}.txt"), 'w') as f:
                            f.write(p1.stdout)
                            f.write(p2.stdout)
                        print(f"Attempt {attempt + 1} failed")
                        print(p2.stdout)
                        break
                except subprocess.TimeoutExpired:
                    print(f"Attempt {attempt + 1} timed out")
                    time.sleep(1)
            else:
                print("All attempts failed")
                continue
            end_time = time.time()
            run_time += end_time - start_time
            run_sucess_num += 1
            print("Success")
    return compile_time, compile_success_num, run_time, run_sucess_num
            

if __name__ == '__main__':
    compile()  
