#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections.abc
from collections import defaultdict
import sys

import os 
os.chdir(os.path.dirname(os.path.realpath(__file__)))

"""
Examples:
    pron['ligt'] gives 'l I x t'
    English: pronounciation of the Dutch word 'lays'
    
    lemmaDict['hebben'] gives:
    {
     'regular': False,
     'PRS': {'SG': {1:'heb', 2:'hebt',3:'heeft'}, 'PL': 'liggen'},
     'PST': {'SG': {1:'had', 2:'had',3:'had'}, 'PL': 'hadden'}
    }
    - lemmaDict['hebben']['PST']['SG']['2'] gives 'had'
      English: past tense 2sg of 'to have' is 'had'
    
    orthoDict['zwijgt'] gives
    {'pron': 'z w K x t', 'regular': False, 'past': {'pron': 'z w e x', 'ortho': 'zweeg'}}
    - orthoDict['zwijgt']['past']['ortho'] gives 'zweeg'
      English: the past tense of 'keeps silence' is 'kept silence'
    - 'Merken' is a regular verb, so orthoDict['merkt']['regular'] gives 'True'

@author: Arjan
"""
# from https://stackoverflow.com/a/3233356
def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


### read pronounciation of all verbs into pronDict
pron = {}
freq = defaultdict(lambda:-1)
with open('NL-pron-freq.txt') as reader:
    for line in reader:
        currentWord = line.split('\t')
        pron[currentWord[0]] = currentWord[2].strip('\n')
        freq[currentWord[0]] = int(currentWord[1])

# we need a temporary dictionairy for the lemma's
lemmaDict = {} # or defaultdict(lambda:{'PRS': {'SG': {1:'<unk>', 2:'<unk>',3:'<unk>'}, 'PL': '<unk>'},'PST': {'SG': {1:'<unk>', 2:'<unk>',3:'<unk>'}, 'PL': '<unk>'}})
'''
example of lemmaDict, key 'hebben':
{
 'freq': 15
 'regular': False,
 'PRS': {'SG': {1:'heb', 2:'hebt',3:'heeft'}, 'PL': 'liggen'},
 'PST': {'SG': {1:'had', 2:'had',3:'had'}, 'PL': 'hadden'}
}

V;IND;PRS;1;SG  heb
V;IND;PRS;2;SG  hebt
V;IND;PRS;3;SG  heeft

V;IND;PRS;PL    hebben

V;IND;PST;1;SG  had
V;IND;PST;2;SG  had
V;IND;PST;3;SG  had

V;IND;PST;PL    hadden
'''
with open('unimorph-wordforms.txt') as reader:
    for line in reader:
        currentWordForm = line.split('\t')
        lemma = currentWordForm[0].strip()  # abonneren
        word = currentWordForm[1].strip()   # abonneert
        pos = currentWordForm[2].split(';') # V;IND;PRS;3;SG
        if pos[0] == 'V' and pos[1] == 'IND':
            tense = pos[2]
            number = pos[-1].strip()
            if number == 'SG':
                person = pos[3]
                if tense == 'PST':
                    if word[-2:] == 'te' or word[-2:] == 'de':
                        regular = 'reg'
                    else:
                        regular = 'irreg'
                    newEntry = {lemma : {'regular': regular, tense: {'SG': {person : word}}}}
                else:
                    newEntry = {lemma : {tense: {'SG': {person : word}}}}
                update(lemmaDict, newEntry)
            elif number == 'PL':
                newEntry = {lemma : {'freq': freq[lemma], tense: {'PL': {'1': word}}}}
                update(lemmaDict, newEntry)

allLines = []
def getWriteLine(mergedFile, lemma, person, number=None):
    try:
        phon = '\t' + pron[lemmaDict[lemma]['PRS'][person][number]] + ';' + pron[lemmaDict[lemma]['PST'][person][number]]
        orth = '\t' + lemmaDict[lemma]['PRS'][person][number] + ';' + lemmaDict[lemma]['PST'][person][number]
        if orth in allLines:
            phon = ''
            orth = ''
        else:
            allLines.append(orth)
            mergedFile.write(lemmaDict[lemma]['PRS'][person][number] + '\t' + lemmaDict[lemma]['PST'][person][number]
                             + '\t' + pron[lemmaDict[lemma]['PRS'][person][number]]  + '\t' + pron[lemmaDict[lemma]['PST'][person][number]]
                             + '\t' + lemmaDict[lemma]['regular'] + '\n')
    except KeyError:
        phon = ''
        orth = ''
    return (phon, orth)


def saveDataset():
    with open('dutch_bylemma_orth.txt', 'w') as orthFile, open('dutch_bylemma_phon.txt', 'w') as phonFile, open('dutch_merged.txt', 'w') as mergedFile:
        # {
        #  'freq': 15
        #  'regular': False,
        #  'PRS': {'SG': {1:'heb', 2:'hebt',3:'heeft'}, 'PL': 'liggen'},
        #  'PST': {'SG': {1:'had', 2:'had',3:'had'}, 'PL': 'hadden'}
        # }

        for lemma in lemmaDict:
            sg1pron, sg1orth = getWriteLine(mergedFile, lemma, 'SG', '1')
            sg2pron, sg2orth = getWriteLine(mergedFile, lemma, 'SG', '2')
            sg3pron, sg3orth = getWriteLine(mergedFile, lemma, 'SG', '3')
            plpron, plorth = getWriteLine(mergedFile, lemma, 'PL', '1')
            
            if sg1pron + sg2pron + sg3pron + plpron != '':
                try:
                    phonFile.write(pron[lemma] + '\t' + str(lemmaDict[lemma]['freq']) + '\t' + lemmaDict[lemma]['regular'] +
                               sg1pron + sg2pron + sg3pron + plpron + '\n')
                    orthFile.write(lemma + '\t' + str(lemmaDict[lemma]['freq']) + '\t' + lemmaDict[lemma]['regular'] +
                               sg1orth + sg2orth + sg3orth + plorth + '\n')
                except KeyError:
                    pass
            
    print("All wordforms saved to dutch_bylemma_orth.txt, to dutch_bylemma_phon.txt and to dutch_merged.txt")

def examples():
    print("Let me show you some examples")
    
    print("\nGet the pronouncation of the Dutch word 'lays':")
    print("pron['ligt'] -", pron['ligt']) # 'l I x t'


    print("\n\n\nShow the LEMMA 'hebben' (to have)")
    print("lemmaDict['hebben'] -", lemmaDict['hebben'])
    # {
    #  'regular': False,
    #  'PRS': {'SG': {1:'heb', 2:'hebt',3:'heeft'}, 'PL': 'liggen'},
    #  'PST': {'SG': {1:'had', 2:'had',3:'had'}, 'PL': 'hadden'}
    # }

    print("\nShow me the past tense 2sg of the LEMMA 'hebben' (to have)") # = 'had'
    print("lemmaDict['hebben']['PST']['SG'][2] -", lemmaDict['hebben']['PST']['SG']['2']) # 'had'

    
    '''
    print("\n\n\nShow the WORDFORM 'zwijgt' (to be silence):")
    print("orthoDict['zwijgt'] -", orthoDict['zwijgt'])
    
    print("\nShow me the past tense 'zwijgT' (keeps silence)")  # = 'zweeg' (kept silence)
    print("orthoDict['zwijgt']['past']['ortho'] - ", orthoDict['zwijgt']['past']['ortho']) # 'zweeg' (kept silence)

    print("\nShow me the past tense 'zwijgEN' (keep silence)")  # = 'zweeg' (kept silence)
    print("orthoDict['zwijgen']['past']['ortho'] - ", orthoDict['zwijgen']['past']['ortho']) # 'zwegen' (kept silence)

    print("\n'Merkt' belongs to the REGULAR verb 'merken', so orthoDict['merkt']['regular'] is", orthoDict['merkt']['regular']) # True
    print("'Slapen' belongs to the IRREGULAR verb 'slapen', so orthoDict['slapen']['regular'] is", orthoDict['slapen']['regular']) # False
    '''    


if __name__ == "__main__":
    saveDataset()
