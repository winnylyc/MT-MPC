import os
import shutil
import re

def splitline(txt_convert, line_split, indent):
    # print(line_split)
    if line_split[0].find('if') != -1:
        txt_convert += 4*indent*' ' + '@if_' + line_split[0][2:] + '\n'
        txt_convert += 4*indent*' ' + 'def _():' '\n'
    else:
        txt_convert += 4*indent*' ' + '@for_range' + line_split[0][4:] + '\n'
        txt_convert += 4*indent*' ' + 'def _(i):' '\n'
    i = 1
    inner_count = -10
    while i < len(line_split):
        temp = line_split[i]
        if temp.find('for') != -1 or temp.find('if') != -1:
            if inner_count == -10:
                inner = [temp]
                inner_count = 1
            else:
                inner.append(temp)
                inner_count += 1
        else:
            find_end = len(temp.split('}'))
            if find_end > 1:
                inner_count -= (find_end - 1)
            if inner_count == 0:
                inner.append(temp)
                txt_convert = splitline(txt_convert, inner, indent+1)
                inner_count = -10
            elif inner_count > 0:
                inner.append(temp)
            elif inner_count <= -1 and inner_count > -10:
                inner.append(temp)
                txt_convert = splitline(txt_convert, inner, indent+1)
                inner_count = -10
            else:
                if temp.find(' = ') != -1:
                    temp_split = temp.split(' = ')
                    # print(temp_split)
                    if temp_split[1].find(temp_split[0]) != -1:
                        temp = temp_split[0] + '.update('
                        if temp_split[1].find('}') != -1:
                            temp += temp_split[1].split('}')[0] + ')' + temp_split[1].split('}')[1]
                        else:
                            temp += temp_split[1] + ')'
                if i == len(line_split) - 1:
                    txt_convert += 4*(indent+1)*' ' + temp.split('}')[0] + '\n'
                else:
                    txt_convert += 4*(indent+1)*' ' + temp + '\n'
        i += 1
    return txt_convert

    # if len(line_split) > 2:
    #     splitline(txt_convert, ('{').join(line_split[1,-1]))

def convert_nosave(text):
    txt_convert = ''
    for i in text.split('\n'):
        line = i + '\n'
        if not line:
            break
        if line.find('#') != -1 or not line.split():
            continue
        if line.find('for') != -1 or line.find('if') != -1:
            line_split = re.split('[{;]',line)
            txt_convert = splitline(txt_convert, line_split, 0)
        else:
            txt_convert += line
    return txt_convert
        # break
    
def convert(src_dir = 'src_2'):
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
    mpc_dir = os.path.abspath(os.path.join("..", "mp-spdz"))
    out_dir = src_dir + '_convert'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    else:
        shutil.rmtree(out_dir) 
        os.mkdir(out_dir)
    for file in file_names:
        txt_convert = ''
        convert_file = os.path.join(out_dir, file.split('/')[-1])
        # print(cov_file)
        var_dic = {}
        f = open(file)
        while True:
            line = f.readline()
            if not line:
                break
            if line.find('#') != -1 or not line.split():
                continue
            if line.find('for') != -1 or line.find('if') != -1:
                line_split = re.split('[{;]',line)
                txt_convert = splitline(txt_convert, line_split, 0)
            else:
                txt_convert += line
                if line.find(' = ') != -1:
                    ### 目前只看考虑了sint和sint的array
                    temp_split = line.split(' = ')
                    if temp_split[1].find('Array') != -1:
                        var_dic[temp_split[0]] = 'sintarray'
                    else:
                        var_dic[temp_split[0]] = 'sint'

        f.close()
        checksum = 'checksum ='
        for var in var_dic:
            if var_dic[var] == 'sint':
                checksum += ' ' + var + ' +'
            else:
                ###目前array的固定设置是长度为10
                for i in range(10):
                    checksum += ' ' + var + '[' + str(i) + ']' + ' +'
        txt_convert += checksum[:-2] + '\n'
        txt_convert += "print_ln('checksum: %s', checksum.reveal())\n"
        f = open(convert_file, 'w')
        f.write(txt_convert)
        f.close()
        # break

if __name__ == '__main__':
    convert()  