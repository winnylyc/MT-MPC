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
            if not line.split():
                continue
            txt_cov += line
            if line.find('include') != -1 or line.find('using') != -1 or line.find('main') != -1 or line.find('party') != -1 or line.find('for') != -1 or line.find('if') != -1 or line.find('{') != -1 or line.find('}') != -1 or line.find('checksum') != -1:
                continue
            if len(line) - len(line.lstrip()) < 5:
                if line.find(' = ') != -1:
                    temp_split = line.split(' = ')
                    var_name = temp_split[0]
                    var_name = var_name.lstrip()

                    if var_name not in var_dic:
                        if var_name.find('Integer')!= -1:
                            var_dic[var_name.split(' ')[1]] = 'sint'
                        elif var_name.find('Bit')!= -1:
                            var_dic[var_name.split(' ')[1]] = 'bool'
                        else:
                            var_dic[var_name] = 'sint'
                elif line.find('Integer') != -1:
                    var_name = line.split('(')[0].split(' ')[-1]
                    var_dic[var_name] = 'sint'
                elif line.find('Bit') != -1:
                    var_name = line.split('(')[0].split(' ')[-1]
                    var_dic[var_name] = 'bool'
            indent = len(line) - len(line.lstrip())
            if random.random()<flipcoin:
            # if random.random()< -1:
                txt_cov += ' ' * indent + 'cout<< "run code line ' + str(counter) + '|'
                for var in var_dic:
                    if var_dic[var] == 'sint':
                        txt_cov += ' ' + var + ':"<<' + var + '.reveal<int32_t>()' + '<<",sint'
                    elif var_dic[var] == 'bool':
                        txt_cov += ' ' + var + ':"<<' + var + '.reveal<bool>()' + '<<",bool'
                txt_cov += '"<<endl;\n'
            else:
                txt_cov += " " * indent + 'cout<< "run code line ' + str(counter) + '"<<endl;\n'
            # if random.random()<flipcoin and line.find('sum')==-1 and line.find('sint.get_input_from(0)')==-1 and line.find('set_precision')==-1:
            #     indent = len(line) - len(line.lstrip())
            #     print_text = " " * indent + "uint32_pl l" + str(counter) + " = " + str(counter) + "u;\n"
            #     print_text += " " * indent + "output(CLIENT, l" + str(counter) + ");\n"
            #     for var in var_dic:
            #         if var_dic[var] == 'pint':
            #             print_text += " " * indent + "output(CLIENT, pint);\n"
            #             print_text += " " * indent + "output(CLIENT, " + var + ");\n"
            #     txt_cov += print_text
            # else:
            #     indent = len(line) - len(line.lstrip())
            #     txt_cov += " " * indent + "uint32_pl l" + str(counter) + " = " + str(counter) + "u;\n"
            #     txt_cov += " " * indent + "output(CLIENT, l" + str(counter) + ");\n"
            # print(line)
        f.close()
        # print(txt_cov)
        f = open(cov_file, 'w')
        f.write(txt_cov)
        f.close()

if __name__ == '__main__':
    coverage()  