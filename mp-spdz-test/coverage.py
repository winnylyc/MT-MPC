import os
import shutil
import random

def coverage(src_dir = 'src_2_convert', flipcoin = 0.5):
    # src_dir = 'src_1_convert'
    # src_dir = 'src_2_convert'
    # src_dir = 'seed'
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 ]
    # print(file_names)
    mpc_dir = os.path.abspath(os.path.join("..", "mp-spdz"))
    for file in file_names:
        txt_cov = ''
        cov_file = file[:-4] + '_cov' + file[-4:]
        # print(cov_file)
        counter = 0
        var_dic = {}
        f = open(file)
        while True:
            line = f.readline()
            if not line:
                break
            counter += 1
            if line.find('#') != -1 or not line.split():
                continue
            txt_cov += line
            if line.find('def') != -1 or line.find('for') != -1 or line.find('if') != -1:
                continue
            if line.find(' = ') != -1:
                temp_split = line.split(' = ')
                var_name = temp_split[0]
                if var_name[0] == ' ':
                    pass
                else:
                    var_name = var_name.lstrip()

                    ### 目前没有考虑输出array的值
                    # if temp_split[1].find('Array') != -1:
                    #     var_dic[temp_split[0]] = 'sintarray'
                    # else:
                    if temp_split[1].find('Array') == -1:
                        var_dic[var_name] = 'sint'
            if random.random()<flipcoin and line.find('sum')==-1 and line.find('sint.get_input_from(0)')==-1 and line.find('set_precision')==-1:
                print_text = "print_ln('run code line %s|"
                print_value = ", " + str(counter)
                for var in var_dic:
                    print_text += " " + var + ":%s"
                    print_value += ", " + var + '.reveal()'
                if line[0] == ' ':
                    indent = len(line) - len(line.lstrip())
                    txt_cov += " " * indent + print_text + "'" + print_value + ")\n"
                else:
                    txt_cov += print_text + "'" + print_value + ")\n"
            else:
                if line[0] == ' ':
                    indent = len(line) - len(line.lstrip())
                    txt_cov += " " * indent + "print_ln('run code line %s', " + str(counter) + ")\n"
                else:
                    txt_cov += "print_ln('run code line %s', " + str(counter) + ")\n"
            # print(line)
        f.close()
        # print(txt_cov)
        f = open(cov_file, 'w')
        f.write(txt_cov)
        f.close()
        # break  

if __name__ == '__main__':
    coverage()  