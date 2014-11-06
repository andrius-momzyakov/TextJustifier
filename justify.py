# coding: UTF-8

import sys

__author__ = 'andrius'


# parsing parameters

import argparse
import re
import math

parser = argparse.ArgumentParser()
parser.add_argument('inf', help='input text file')
parser.add_argument('outf', help='output text file')
parser.add_argument('N', help='width of text in characters', type=int)


args = parser.parse_args()

if args.N<20 or args.N>120:
    print u'Ширина текста не может быть меньше 20 и больше 120 символов.'
    sys.exit()

norm = args.N - 4 # ширина строки с учётом отступа

try:
    input_file = open(args.inf, 'r')
    output_file = open(args.outf, 'w')
except IOError:
    print u'Ошибка: Невозможно открыть входной или создать выходной файл.'
    sys.exit()

def clear_line(line):
    """
    очистка от переносов строк и пробелов
    возвращает очищенную строку
    """
    # убираем лишние пробелы
    l = re.sub('[ ]+', ' ', line)
    # убираем все управляющие символы и переносы
    l = re.sub('[\t\n\r\f\v]+', '', l)
    return l

def split_into_para(pdelimiter, line):
    """
    разбивка строки из файла на абзацы
    возвращает остаток абзаца с разделителем, массив абзацев из середины
    и остаток после последнего в строке разделителя
    """
    m = re.search(pdelimiter, line)
    if m:
        return line[:m.end()], line[m.end():]
    return line, ''

def justify(para, limit, offset=4):
    """
    разбивает собранный абзац в виде строки с пробелами на массив выровненных строк
    возвращает массив выровненных строк
    """
    def add_spaces(words, lengths, limit, add_offset=False, offset=4):
        '''
        добавляет пробелы
        возвращает выровненную строку
        :param words: список слов
        :param limit: ограничение по длине строки
        :return: выровненная строка
        '''
        rez = ''
        if len(words)==0: return ''
        spaces_to_insert =  limit - sum(lengths)

        if spaces_to_insert>0:

            x=len(words) - 1
            add_to_each_gap = 0
            rest_to_insert = 0
            if x>0:
                add_to_each_gap = int(math.floor(spaces_to_insert / x))
                rest_to_insert = int(spaces_to_insert % x)

            # выравниваем
            for m in reversed(range(len(words)-1)):
                lengths[m] += add_to_each_gap
                if rest_to_insert>0:
                    lengths[m] += 1
                    rest_to_insert -= 1

        for i in range(len(words)):
            if i==0:
                if add_offset:
                    rez = ' ' * offset
                    rez += words[i] + ' ' * (lengths[i] - offset - len(words[i]))
                else:
                    rez += words[i] + ' ' * (lengths[i] - len(words[i]))
            else:
                rez += words[i] + ' ' * (lengths[i] - len(words[i]))

        return rez + '\n'

    rez = []

    if len(para)==0: return []

    if len(para)<math.ceil(args.N/2):
        return [para]

    # массив слов в абзаце
    words = para.split()
    # массив длин слов в абзаце c учетом пробелов и отступов
    lengths = map(lambda word: len(word)+1, words)
    lengths[len(lengths)-1] -= 1 #убираем пробел от последнего слова
    lengths[0] += offset # добавляем отступ к первому слову

    k = 0
    while True:
        if not len(words)>0: break
        accum = 0
        words_tmp = []
        lengths_tmp = []
        i=0
        while accum<limit and len(words)>0:
            accum += lengths[0]
            if accum<=limit and len(words)>0:
                w = words.pop(0)
                l = lengths.pop(0)
                words_tmp.append(w) #words.pop(0))
                lengths_tmp.append(l) #lengths.pop(0))
                i += 1
            else:
                break
        k += 1
        add_offset = False
        if k==1: add_offset = True
        rez.append(add_spaces(words=words_tmp, lengths=lengths_tmp,  limit=limit, add_offset=add_offset))

    return rez

delimiter = '[\.?!:]' # метка конца абзаца
para = ''  # буфер абзаца
tail = ''  # остаток строки после метки абзаца
line = ''  # строка из файла
m = None # match object
is_first_line = True

# цикл чтения строк из файла
while True:
    # читаем строку из файла
    line = input_file.readline()
    if not line: # достигнут конец файла
        # хвост пишем как абзац
        if tail:
            for line in justify(para=tail, limit=args.N):
                output_file.write(line)
        break

    line = clear_line(line)
    if len(line)>0: line = line + ' '
    if len(line)< args.N/2 and not tail:
        output_file.write(line + '\n')
        continue
    line_tmp = tail + line
    tail = ''
    para = ''
    m = re.search(delimiter, line_tmp)
    if not m:
        tail = line_tmp
        continue
    # цикл разбора строки на абзацы
    while m:
        para = line_tmp[:m.end()]
        line_tmp = line_tmp[m.end():]
        # выравниваем и пишем в файл строки
        for line in justify(para=para, limit=args.N):
            output_file.write(line)
        m=re.search(delimiter, line_tmp)
    else:
        tail = line_tmp

input_file.close()
output_file.close()
