import os
import shutil
import random

def coverage(src_dir = 'src_convert', flipcoin = 0.5):
    # src_dir = 'src_1_convert'
    # src_dir = 'src_2_convert'
    # src_dir = 'seed'
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 ]
    # print(file_names)
    for file in file_names:
        txt_cov = ''
        txt_cov2 = ''
        cov_file = file[:-5] + '_cov' + file[-5:]
        cov_file2 = file[:-5] + '_cov2' + file[-5:]
        # print(cov_file)
        counter = 0
        var_dic = {}
        f = open(file)
        while True:
            line = f.readline()
            if not line:
                break
            counter += 1
            if counter == 2:
                txt_cov += " " * 4 + "uint32_pl pint = 0u;\n"
            if line.find('#') != -1 or not line.split():
                continue
            txt_cov += line
            txt_cov2 += line
            if line.find('def') != -1 or line.find('for') != -1 or line.find('if') != -1 or line.find('{') != -1 or line.find('}') != -1 or line.find('checksum') != -1:
                continue
            if line.find(' = ') != -1:
                temp_split = line.split(' = ')
                var_name = temp_split[0]
                if len(var_name) - len(var_name.lstrip()) >= 5:
                    pass
                else:
                    var_name = var_name.lstrip()
                    if var_name not in var_dic:
                        if var_name.find('uint32')!= -1:
                            if var_name.find('uint32_pl')!= -1:
                                var_dic[var_name.split(' ')[1]] = 'pint'
                            else:
                                var_dic[var_name.split(' ')[1]] = 'sint'
                        elif var_name.find('bool_bl')!= -1:
                            var_dic[var_name.split(' ')[1]] = 'bool'
                        else:
                            var_dic[var_name] = 'sint'
            if random.random()<flipcoin and line.find('sum')==-1 and line.find('sint.get_input_from(0)')==-1 and line.find('set_precision')==-1:
                indent = len(line) - len(line.lstrip())
                print_text = " " * indent + "uint32_pl l" + str(counter) + " = " + str(counter) + "u;\n"
                print_text += " " * indent + "output(CLIENT, l" + str(counter) + ");\n"
                for var in var_dic:
                    if var_dic[var] == 'pint':
                        print_text += " " * indent + "output(CLIENT, pint);\n"
                        print_text += " " * indent + "output(CLIENT, " + var + ");\n"
                txt_cov += print_text

                print_text2 = " " * indent + "uint32_bl l" + str(counter) + " = " + str(counter) + "u;\n"
                print_text2 += " " * indent + "output(CLIENT, l" + str(counter) + ");\n"
                for var in var_dic:
                    if var_dic[var] == 'sint':
                        print_text2 += " " * indent + "output(CLIENT, " + var + ");\n"
                txt_cov2 += print_text2
            else:
                indent = len(line) - len(line.lstrip())
                txt_cov += " " * indent + "uint32_pl l" + str(counter) + " = " + str(counter) + "u;\n"
                txt_cov += " " * indent + "output(CLIENT, l" + str(counter) + ");\n"

                txt_cov2 += " " * indent + "uint32_bl l" + str(counter) + " = " + str(counter) + "u;\n"
                txt_cov2 += " " * indent + "output(CLIENT, l" + str(counter) + ");\n"
            # print(line)
        f.close()
        # print(txt_cov)
        f = open(cov_file, 'w')
        f.write(txt_cov)
        f.close()
        f = open(cov_file2, 'w')
        f.write(txt_cov2)
        f.close()
        # break  

if __name__ == '__main__':
    coverage()  