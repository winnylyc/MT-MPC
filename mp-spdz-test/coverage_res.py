import os
import shutil

def coverageRes(src_dir = 'src', tgt_dir = 'tgt'):
    # src_dir = 'src_1_convert'
    # tgt_dir = 'tgt_src_1'

    # src_dir = 'seed'
    # tgt_dir = 'tgt_seed'

    # src_dir = 'src_2_convert'
    # tgt_dir = 'tgt'
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 ]
    mpc_dir = os.path.abspath(os.path.join("..", "mp-spdz"))
    for file in file_names:
        txt_cov_inf = ''
        cov_file = file[:-4] + '_cov.txt'
        cov_result_file = os.path.join(tgt_dir, file.split('/')[-1][:-4] + '_cov.txt')
        dict_run = {}
        overflow = -1
        try:
            f = open(cov_result_file)
            while True:
                res = f.readline()
                if not res:
                    break
                if res.find('run code line') != -1:
                    if res.find('|') != -1:
                        res_split = res.split('|')
                        num = res_split[0].split(' ')[-1]
                        env = res_split[1][1:-1].split(' ')
                        # print(num)
                        # print(dict_run)
                        # print(env)
                        if num in dict_run:
                            dict_run[num][0] += 1
                            for var_env in env:
                                var, value = var_env.split(':')
                                if value.find('.') != -1:
                                    value = float(value)
                                else:
                                    value = int(value)
                                if value >= 2**63 or value < -2**63:
                                    overflow = 1
                                dict_run[num][1][var].add(value)
                        else:
                            env_record = {}
                            for var_env in env:
                                var, value = var_env.split(':')
                                if value.find('.') != -1:
                                    value = float(value)
                                else:
                                    value = int(value)
                                if value >= 2**63 or value < -2**63:
                                    overflow = 1
                                env_record[var] = {value}
                            dict_run[num] = [1,env_record]
                    else:
                        num = res.split(' ')[-1][:-1]
                        if num in dict_run:
                            dict_run[num][0] += 1
                        else:
                            dict_run[num] = [1, None]
            f.close()
        except:
            f = open(cov_file, 'w')
            f.write('error occurs')
            f.close()
            continue

        counter = 0
        f = open(file)
        while True:
            line = f.readline()
            if not line:
                break
            counter += 1
            if line.find('#') != -1 or not line.split():
                txt_cov_inf += line
                continue
            if line.find('def') != -1 or line.find('for') != -1 or line.find('if') != -1:
                indent = len(line) - len(line.lstrip())
                txt_cov_inf += 'cov ! indent %d|| '%(int(indent/4)+1)
                txt_cov_inf += line
                continue
            indent = len(line) - len(line.lstrip())
            if str(counter) in dict_run:
                if dict_run[str(counter)][1] == None:
                    txt_cov_inf += 'cov %d indent %d|| '%(dict_run[str(counter)][0], int(indent/4))
                    txt_cov_inf += line
                else:
                    txt_cov_inf += 'cov %d indent %d|| '%(dict_run[str(counter)][0], int(indent/4))
                    txt_cov_inf += line[:-1] + ' '
                    txt_cov_inf += '||'
                    env_record = dict_run[str(counter)][1]
                    for var_env in env_record:
                        txt_cov_inf += '?' + var_env + '=' + str(env_record[var_env]) # ? is used for split in EMI, since the string converted from set also contains space
                    txt_cov_inf += '\n'
            else:
                txt_cov_inf += 'cov # indent %d|| '%int(indent/4)
                txt_cov_inf += line
            # print(line)
        if overflow == 1:
            txt_cov_inf += "#### there is a overflow" 
        f.close()
        # print(txt_cov)
        f = open(cov_file, 'w')
        f.write(txt_cov_inf)
        f.close()

if __name__ == '__main__':
    coverageRes()