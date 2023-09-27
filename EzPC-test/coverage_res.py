import os
import shutil

def coverageRes(src_dir = 'src_convert', tgt_dir = 'tgt'):
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 ]
    for file in file_names:
        txt_cov_inf = ''
        cov_file = file[:-5] + '_cov.txt'
        cov_result_file = os.path.join(tgt_dir, file.split('/')[-1][:-5] + '_cov.txt')
        cov_result_file2 = os.path.join(tgt_dir, file.split('/')[-1][:-5] + '_cov2.txt')
        ### The coverage output file should not ouput the value of varaible first
        error_found = False
        dict_run = {}
        # overflow = -1
        bug = 0
        try:
            f = open(cov_result_file)
            while True:
                res = f.readline()
                if not res:
                    break
                if res.find('error') != -1:
                    bug = 1
                    break
                if res.find('Value of') != -1:
                    if res.find('pint') != -1:
                        f.readline()
                        res = f.readline()
                        var = res.split(' ')[-1].split(':')[0]
                        vtype = 'pint'
                        value = int(f.readline())
                        try:
                            if var in dict_run[num][1]:
                                dict_run[num][1][var][1].add(value)
                            else:
                                dict_run[num][1][var] = [vtype,{value}]
                        except KeyError:
                            bug = 1
                            break

                    else:
                        if res.find('checksum') == -1:
                            num = f.readline().strip()
                            # sometimes there is bug when coverage information is added, the number will be random number
                            if int(num) > 1000:
                                bug = 1
                                break
                            if num in dict_run:
                                dict_run[num][0] += 1
                            else:
                                env_record = {}
                                dict_run[num] = [1,env_record]
            f.close()
        except:
            f = open(cov_file, 'w')
            f.write('error occurs')
            f.close()
            continue
        if bug == 1:
            f = open(cov_file, 'w')
            f.write('error occurs')
            f.close()
            continue
        try:
            f = open(cov_result_file2)
            while True:
                res = f.readline()
                if not res:
                    break
                if res.find('error') != -1:
                    bug = 1
                    break
                if res.find('Value of') != -1:
                    if res.find('var') != -1:
                        var = res.split(' ')[-1].split(':')[0]
                        vtype = 'sint'
                        value = int(f.readline())
                        try:
                            if var in dict_run[num][1]:
                                dict_run[num][1][var][1].add(value)
                            else:
                                dict_run[num][1][var] = [vtype,{value}]
                        except KeyError:
                            bug = 1
                            break
                    else:
                        if res.find('checksum') == -1:
                            num = f.readline().strip()
                            # sometimes there is bug when coverage information is added, the number will be random number
                            if int(num) > 1000:
                                bug = 1
                                break
            f.close()
        except:
            f = open(cov_file, 'w')
            f.write('error occurs')
            f.close()
            continue
        if bug == 1:
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
            if line.find('def') != -1 or line.find('for') != -1 or line.find('if') != -1 or line.find('{') != -1 or line.find('}') != -1:
                indent = len(line) - len(line.lstrip())
                txt_cov_inf += 'cov ! indent %d|-| '%(int(indent/4)+1)
                txt_cov_inf += line
                continue
            indent = len(line) - len(line.lstrip())
            if str(counter) in dict_run:
                if dict_run[str(counter)][1] == {}:
                    txt_cov_inf += 'cov %d indent %d|-| '%(dict_run[str(counter)][0], int(indent/4))
                    txt_cov_inf += line
                else:
                    txt_cov_inf += 'cov %d indent %d|-| '%(dict_run[str(counter)][0], int(indent/4))
                    txt_cov_inf += line[:-1] + ' '
                    txt_cov_inf += '|-|'
                    env_record = dict_run[str(counter)][1]
                    for var_env in env_record:
                        txt_cov_inf += '?' + var_env + '=' + str(env_record[var_env]) # ? is used for split in EMI, since the string converted from set also contains space
                    txt_cov_inf += '\n'
            else:
                txt_cov_inf += 'cov # indent %d|-| '%int(indent/4)
                txt_cov_inf += line
            # print(line)
        # if overflow == 1:
        #     txt_cov_inf += "#### there is a overflow" 
        f.close()
        # print(txt_cov)
        f = open(cov_file, 'w')
        f.write(txt_cov_inf)
        f.close()

if __name__ == '__main__':
    coverageRes()