import os
import shutil
import re

def splitline(txt_convert, line_split, indent):
    # print(line_split)
    if line_split[0].find('if') != -1:
        txt_convert += 4*indent*' ' + 'if' + line_split[0][2:] + '\n'
    else:
        txt_convert += 4*indent*' ' + 'for i in range' + line_split[0][4:-1] + ':\n'
    txt_convert += 4*indent*' ' + '{\n'
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
                if i == len(line_split) - 1:
                    txt_convert += 4*(indent+1)*' ' + temp.split('}')[0] + '\n'
                else:
                    txt_convert += 4*(indent+1)*' ' + temp + '\n'
        i += 1
    txt_convert += 4*indent*' ' + '};\n'
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
            line_split = re.split('[{$]',line)
            txt_convert = splitline(txt_convert, line_split, 0)
        else:
            txt_convert += line
    return txt_convert
        # break
    
def convert(src_dir = 'src'):
    file_names = [os.path.join(src_dir, file) for file in os.listdir(src_dir) if file.find('cov') == -1 and file.find('convert') == -1]
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
                line_split = re.split('[{$]',line)
                txt_convert = splitline(txt_convert, line_split, 0)
            else:
                txt_convert += line
                if line.find(' = ') != -1:
                    temp_split = line.split(' = ')
                    if temp_split[0] in var_dic:
                        continue
                    if temp_split[0].find('uint32')!= -1:
                        var_dic[temp_split[0].split(' ')[1]] = 'int'
                    elif temp_split[0].find('bool_bl')!= -1:
                        var_dic[temp_split[0].split(' ')[1]] = 'bool'
                    else:
                        var_dic[temp_split[0]] = 'int'

        f.close()
        # for i, var in enumerate(var_dic):
        #     if i == 0:
        #         var_last = var
        #         continue
        #     if i == 1:
        #         txt_convert += 'checksum = circ->PutADDGate(' + var + ',' +  var_last  + ');\n'
        #     else:
        #         txt_convert += 'checksum = circ->PutADDGate(checksum,' +  var_last  + ');\n'
        checksum = 'uint32_bl checksum ='
        for var in var_dic:
            if var_dic[var] == 'int':
                checksum += ' ' + var + ' +'
        txt_convert += checksum[:-2] + ';\n'
        txt_convert += "output(CLIENT, checksum);\n"
                
        txt_convert_final = ""
        txt_convert_final += 'def void main(){\n'
        for txt in txt_convert.split('\n'):
            txt_convert_final += ' ' * 4 + txt + '\n'
        txt_convert_final += '}'
        f = open(convert_file, 'w')
        f.write(txt_convert_final)
        f.close()
        # break

if __name__ == '__main__':
    convert()  