import glob
import os
import re
import csv

from textblob_de import TextBlobDE as TextBlob
from textblob_de.packages import pattern_de as pd

idioms='short_list5.csv' # мини-список из 21 идиомы,
# с указанием на порядок и меняющийся компонент
name='test_it'
name_txt=name+'.txt'
name_out='outfile_'+name+'.txt'

'''открыть файл с текстом,'''
file = open(name_txt,'r',encoding='utf-8')
outfile= open(name_out,'w',encoding='utf-8')
file_idioms=open(idioms,'r',encoding='utf-8')

text=file.read().strip()
print(len(text))
list_idioms=file_idioms.read().strip().split('\n')
print(len(list_idioms))

'''В outfile записывается номер найденной идиомы (по csv-таблице),
сама идиома, номер предложения (по делению TextBlob), само предложение.
Для теста результаты в outfile_test_it.txt'''
def write_outfile(num_idiom,idiom,num,sentence):
    outfile.write('idiom '+str(num_idiom)+': '+str(idiom)+'\n')
    outfile.write('sentence '+str(num)+': '+str(sentence)+'\n\n')

'''Экспорт функции для спряжения глаголов.
Используется модуль pattern.de. С его помощью
строятся словари, содержащие все допустимые формы
для данного глагола'''
from fr_conjugate import conjugate_verb

'''С помощью модуля TextBlob текст делится на предложения'''
blob = TextBlob(text)
sentences=blob.sentences
num=0

'''В каждом предложении осуществляется поиск идиом из списка'''
for sentence in sentences:
    num_idiom=1
    '''Перед разбиением предложения на токены осуществляется
    их очистка'''
    senten=re.sub(r"[«»„”“/./(/)/']","",str(sentence).lower())
    senten=re.sub(r'["]','',str(senten))
    blob2 = TextBlob(str(senten))
    tokens=blob2.tokens

    for item in list_idioms[1:]:
        items=item.split('\t')
        idiom=str(items[0]).strip()
        idiom_low=idiom.lower()
        if items[1]=='0': # т.е. порядок слов не меняется
            if items[2]=='': # т.е. нет меняющегося компонента
                if idiom_low in str(senten):
                    # проверяется наличие всей подстроки
                    # в предложении в нижнем регистре
                    write_outfile(num_idiom,idiom,num,sentence)
        if items[2]!='': # т.е. есть меняющийся компонент
            variables=items[2].split('|') # на случай, если их несколько
            # таковой еще не попадался
            for it in variables:
                it=it.split(':')
                word=it[0].lower()
                # сам компонент
                pos=it[1]
                # его часть речи
                if pos=='a': # если это прилагательное
                    if items[1]=='0': # порядок слов не меняется
                        if word in senten:
                            # слово и предложение в нижнем регистре
                            id_word=senten.index(word)
                            id2=id_word+30
                            new_senten=senten[id_word:id2]
                            # случаи предшествования прилагательного
                            new_idiom=re.sub(word,'',str(items[0]))
                            new_idiom=new_idiom.lower()
                            if new_idiom in new_senten:
                                write_outfile(num_idiom,idiom,num,sentence)
                if pos=='v':
                    # меняющийся глагол и меняющийся порядок слов
                    new_idiom=re.sub(word,'',str(items[0]))
                    new_idiom=new_idiom.lower().split()
                    value=True
                    # проверка на наличие всех остальных компонентов
                    # идиомы в предложении
                    for component in new_idiom:
                        if component not in tokens:
                            value=False
                    if value is True:
                        # если все компоненты в наличии,
                        # проверить, есть ли требуемая глагольная форма
                        verb_forms={}
                        conjugate_verb(word, verb_forms)
                        # далее корректировка полученного списка
                        # потом для удобоваримости можно перенести
                        verb_inf=verb_forms['present_1_pl_imperative']
                        verb_pl=verb_forms['present_1_pl_indicative']
                        if ' ' in verb_pl:
                            elems=verb_pl.split()
                            infinitiv=elems[1]+'zu'+elems[0]
                            if infinitiv=='aufzureissen':
                                infinitiv='aufzureißen'
                        if ' ' in verb_inf:
                            elems=verb_inf.split()
                            verb_inf=elems[1]+elems[0]
                        if ' ' not in verb_inf:
                            infinitiv='zu '+verb_inf
                        verb_forms['infinitiv']=infinitiv
                        verb_forms['verb_inf']=verb_inf
                        verbs=[]
                        # создать список глагольных форм без повторов
                        for verb in verb_forms:
                            if verb_forms[verb] not in verbs:
                                verbs.append(verb_forms[verb])
                        # еще немного залечивания ошибок
                        if word=='zucken':
                            verbs=[]
                            verbs=['zucke','zuckst','zuckt',
                                        'zucken','zuckte','zuckten',
                                        'zucktest','zucktet','gezuckt',
                                        'zu zucken']
                        for elem in verbs:
                            if value is True:
                                if elem in tokens:
                                    value=False
                                    # если хотя бы одна форма найдена,
                                    # запись и переход к другой идиоме
                                    write_outfile(num_idiom,idiom,num,sentence)
                                    
                    
        num_idiom+=1
    num+=1
        

file.close()
outfile.close()
