import re
import json
from uniparser_udmurt import UdmurtAnalyzer
import random


class UdmurtTransliterator:
    rxSpaces = re.compile('[ \t]+')
    rxLetters = re.compile('\w+')
    rxDots = re.compile(' *\\.\\.+ *')
    rxNrzb = re.compile('[(<\\[]?(?:нрзб|nrzb)\\.?[)>\\]]?')
    rxSentEnd = re.compile('[.?!,;:][)"]?$')
    rxTwoPartWords = re.compile('\\b(olo|оло|kin\\w*|кин\\w*|mar\\w*|мар\\w*|'
                                'kət\\w*|кыт\\w*|kud\\w*|куд\\w*|malə|малы)[ -]*'
                                '(ke|ке|kinʼ\\w*|кин\\w*|mar\\w*|мар\\w*|'
                                'kət\\w*|кыт\\w*|kud\\w*|куд\\w*|malə|малы)\\b')
    rxQ = re.compile('-[aа]\\b')

    dic2cyr = {'a': 'а', 'b': 'б', 'v': 'в',
               'g': 'г', 'd': 'д', 'e': 'э',
               'ž': 'ж', 'š': 'ш', 'ɤ': 'ӧ',
               'ə': 'ө', 'ǯ': 'ӟ', 'č': 'ч',
               'z': 'з', 'i': 'ӥ', 'j': 'й', 'k': 'к',
               'l': 'л', 'm': 'м', 'n': 'н',
               'o': 'о', 'p': 'п', 'r': 'р',
               's': 'с', 't': 'т', 'u': 'у',
               'c': 'ц', 'w': 'ў', 'x': 'х',
               'y': 'ы', 'f': 'ф', 'ɨ': 'ы',
               'ü': 'ӱ', 'ŋ': 'ң'}
    cyr2dic = {v: k for k, v in dic2cyr.items()}
    cyr2dic.update({'я': 'ʼa', 'е': 'ʼe', 'и': 'ʼi', 'ӝ': 'ǯ', 'ӵ': 'č', 'щ': 'šʼ',
                    'ё': 'ʼo', 'ю': 'ʼu', 'ь': 'ʼ', 'ы': 'ɨ', 'у': 'u'})
    dic2cyr.update({'ä': 'а', 'h': 'х',
                    'ö': 'ӧ'})
    cyr2upa = {'а': 'a', 'б': 'b', 'в': 'v',
               'г': 'g', 'д': 'd', 'э': 'e',
               'ж': 'ž', 'ш': 'š', 'ӧ': 'ö',
               'ө': 'ə̑', 'ъ': 'ə̑', 'ӹ': 'ə̈', 'ч': 'č\'', 'ӟ': 'ǯ\'',
               'з': 'z', 'и': 'i', 'ӥ': 'i', 'й': 'j', 'к': 'k',
               'л': 'l', 'м': 'm', 'н': 'n',
               'о': 'o', 'п': 'p', 'р': 'r',
               'с': 's', 'т': 't', 'у': 'u',
               'ц': 'c', 'ў': 'u̯', 'х': 'x',
               'ф': 'f', 'ы': 'i̮', 'ӓ': 'ä',
               'ӱ': 'u̇', 'ң': 'ŋ', 'ӝ': 'ǯ', 'ӵ': 'č'}
    cyrHard2Soft = {'а': 'я', 'э': 'е', 'е': 'е', 'ӥ': 'и', 'о': 'ё', 'у': 'ю'}
    rxSoften = re.compile('(?<![чӟ])ʼ([аэӥоу])', flags=re.I)
    rxCyrSoften = re.compile('([čǯ])(?!ʼ)', flags=re.I)
    rxCyrMultSoften = re.compile('ʼ{2,}')
    rxNeutral1 = re.compile('(?<=[бвгжӝкмпрфхцчӵшщйʼ])([эӥ])', re.I)
    rxNeutral2 = re.compile('([бвгжӝкмпрфхцчӵʼаоэӥуўяёеиюө]|\\b)(ӥ)', re.I)
    rxCyrNeutral = re.compile('(?<=[bvgzkmprfxcwj])ʼ', re.I)
    rxCJV = re.compile('(?<=[бвгджзӟклмнпрстўфхцчшщ])й([аяэеӥоёую])', re.I)
    rxCSoftJV = re.compile('(?<=[ӟчщ]ʼ)й([аяэеӥоёую])', re.I)
    rxSh = re.compile('ш(?=[ʼяёюиеЯЁЮИЕ])')
    rxZh = re.compile('ж(?=[ʼяёюиеЯЁЮИЕ])')
    rxShCapital = re.compile('Ш(?=[ʼяёюиеЯЁЮИЕ])')
    rxZhCapital = re.compile('Ж(?=[ʼяёюиеЯЁЮИЕ])')
    rxVJV = re.compile('(?<=[аеёиӥоӧөуыэюя])й([аэоу])', flags=re.I)
    rxSoftJV = re.compile('(?<=[^ӟчщ]ʼ)й([аэоу])', flags=re.I)
    rxJV = re.compile('\\b(?<!ʼ)й([аэоу])')
    rxJVCapital = re.compile('\\b(?<!ʼ)Й([аэоуАЭОУ])')
    rxCyrVJV = re.compile('([aeiouɨəɤ])ʼ([aeouɨəɤ])')
    rxCyrVSoft = re.compile('([aeiouɨəɤ]|\\b)ʼ')
    rxCyrJV = re.compile('\\bʼ([aeouɨəɤ])')
    rxExtraSoft = re.compile('([дзлнст])ь\\1(?=[ьяеёию])')
    rxCyrExtraSoft = re.compile('([džlnšt])\\1(?=ʼ)')
    rxCyrW = re.compile('(\\b|[кр])у(?=[аоэи])')

    rxWDiacritic = re.compile('u̯')
    rxWDiacriticCapital = re.compile('U̯')
    rxUe = re.compile('u̇')
    rxUeCapital = re.compile('U̇')
    rxUeCyr = re.compile('ӱ')
    rxUeCyrCapital = re.compile('Ӱ')
    rxUeFinalCyr = re.compile('ӱ$')
    rxUeFinalCyrCapital = re.compile('Ӱ$')
    rxWCyr = re.compile('ў')
    rxWCyrCapital = re.compile('Ў')
    rxOe = re.compile('ȯ')
    rxOeCapital = re.compile('Ȯ')
    rxGlottalStop = re.compile('ˀ')
    rxSchwa = re.compile('ə̈|ə̑')
    rxSchwaCapital = re.compile('Ə̈|Ə̑')
    rxY = re.compile('i̮')
    rxYCapital = re.compile('I̮')
    rxCyrFinalT = re.compile('т(ь?$|ь?[кпстфхцчшщ])')
    rxCyrFinalK = re.compile('к(ь?$|ь?[кпстфхцчшщ])$')
    rxCyrFinalP = re.compile('г(ь?$|ь?[кпстфхцчшщ])$')

    rxCyrSchwa = re.compile('ө')
    rxCyrSchwaCapital = re.compile('Ө')
    rxCyrJeStart = re.compile('^йэ')
    rxCyrJeStartCapital = re.compile('^Йэ')
    rxCyrDZjVStart = re.compile('^(?:дʼзʼ|ӟʼ)(?=[аеёиӥоӧуӱыэюяө])')
    rxCyrDZjVStartCapital = re.compile('^(?:ДʼЗʼ|Ӟʼ)(?=[аеёиӥоӧуӱыэюяө])')
    rxCyrChV = re.compile('(?:тʼсʼ|чʼ)(?=[аеёиӥоӧуӱыэюяө])')
    rxCyrChVCapital = re.compile('(?:ТʼСʼ|Чʼ)(?=[аеёиӥоӧуӱыэюяө])')
    rxCyrDZjVMiddle = re.compile('(?<=\\w)(?:дʼзʼ|ӟʼ)(?=[аеёиӥоӧуӱыэюяө])')
    rxCyrCDZjos = re.compile('(?<=\\w[тдкгбпʼ])(?:дʼзʼос|[дӟ]ʼос)')
    rxCyrGlottalStopDZjos = re.compile('(?<=\\w)ˀ(?:дʼзʼос|[ӟд]ʼос)')
    rxCyrNg = re.compile('ң')
    rxCyrJYEnd = re.compile('(?<=[аеёиӥоӧуӱыэюяө])й([өы]н$|[өы]с[ьʼ])')
    rxCyrZh = re.compile('ж')
    rxCyrZhCapital = re.compile('Ж')
    rxCyrSh = re.compile('ш')
    rxCyrShCapital = re.compile('Ш')
    rxCyrCh = re.compile('чʼ?')
    rxCyrChCapital = re.compile('Чʼ?')
    rxCyrMM = re.compile('мм')
    rxCyrTT = re.compile('тт')
    rxCyrChCh = re.compile('чʼ?чʼ?')
    rxCyrDzjDzj = re.compile('ӟʼ?ӟʼ?')
    rxCyrConsCluster = re.compile('([бпдт])([рл])')
    rxOeCyr = re.compile('ӧ⁰')
    rxOeCapitalCyr = re.compile('Ӧ⁰')

    rxUPAApos = re.compile('([źśń])', flags=re.I)
    dicUPAApos2Tatyshly = {'ź': 'z\'', 'ś': 's\'', 'ń': 'n\'',
                           'Ź': 'Z\'', 'Ś': 'S\'', 'Ń': 'N\''}

    rxCyrillic = re.compile('^[а-яёӟӥӧўөА-ЯЁӞӤӦЎӨ.,;:!?\-()\\[\\]{}<>]*$')

    rxWords = re.compile("[\\wʼ´́̑̈'··̯̮̇-]+|[^\\wʼ´́̑̈'··̯̮̇-]+", flags=re.DOTALL)
    rxGoodHyphenatedWord = re.compile('^\\w{3,}[^ъ.()-]-[^ьъ()-]')

    def __init__(self, src, target, eafCleanup=False):
        self.cyrReplacements = {}
        self.srcReplacements = {}
        self.cyr2dicReplacements = {}
        self.rxCyrReplacements = re.compile('^$')
        self.src = src
        self.target = target
        self.eafCleanup = eafCleanup
        self.analyzableWords = set()
        self.a = UdmurtAnalyzer(mode='strict')

        # Basic replacements that always have to take place
        # with Cyrillic output:
        self.cyrReplacementsBasic, self.rxCyrReplacementsBasic = self.load_replacements('data/cyr_replacements_basic_rx.csv')
        # Additional replacements that should only be applied
        # if complete standardization is required:
        self.cyrReplacementsStd, self.rxCyrReplacementsStd = self.load_replacements('data/cyr_replacements_std_rx.csv')

        self.freqDict = self.load_freq_list()
        print('Initialization complete.')

    def load_replacements(self, filename):
        cyrRx = []
        cyrReplacements = {}
        with open(filename, 'r', encoding='utf-8') as fIn:
            for line in fIn:
                if len(line) <= 3:
                    return
                cyrSrc, cyrCorrect = line.strip('\r\n').split('\t')
                if len(cyrCorrect) > 0 and len(cyrSrc) > 0:
                    cyrSrc = cyrSrc.strip('^$')
                    cyrRx.append(cyrSrc)
                    cyrReplacements[re.compile('^' + cyrSrc + '$')] = cyrCorrect
                    cyrReplacements[re.compile('^' + cyrSrc.upper() + '$')] = cyrCorrect.upper()
                    cyrReplacements[re.compile('^' + cyrSrc.capitalize() + '$')] = cyrCorrect.capitalize()
        return cyrReplacements, re.compile('|'.join(r for r in sorted(cyrRx, key=lambda x: -len(x))), flags=re.I)

    def load_freq_list(self):
        """
        Load Standard Udmurt frequency list.
        """
        freqDict = {}
        with open('data/std_freq_dict.json', 'r', encoding='utf-8') as fIn:
            freqDict = json.load(fIn)
        return freqDict

    def analyzable(self, word):
        """
        Return True iff the word can be analyzed by the Udmurt analyzer.
        """
        if word in self.analyzableWords:
            # Cache
            return True
        analyses = self.a.analyze_words(word)
        if len(analyses) <= 0 or (len(analyses) == 1 and len(analyses[0].lemma) <= 0):
            if self.rxGoodHyphenatedWord.search(word) is not None:
                if all(self.analyzable(part) for part in word.split('-')):
                    self.analyzableWords.add(word)
                    return True
            return False
        if all(',missp' in ana.gramm for ana in analyses):
            return False
        self.analyzableWords.add(word)
        return True

    def beserman_translit_cyrillic(self, text):
        """
        Transliterate Beserman text from dictionary Latin script to the Cyrillics.
        """
        parts = self.rxWords.findall(text)
        return ''.join(self.beserman_translit_cyrillic_word(part) for part in parts)

    def beserman_translit_cyrillic_word(self, text):
        """
        Transliterate a single Beserman word from dictionary Latin script to the Cyrillics.
        """
        if self.rxCyrillic.search(text) is not None:
            return text

        letters = []
        for letter in text:
            if letter.lower() in self.dic2cyr:
                if letter.islower():
                    letters.append(self.dic2cyr[letter.lower()])
                else:
                    letters.append(self.dic2cyr[letter.lower()].upper())
            else:
                letters.append(letter)
        res = ''.join(letters)
        res = res.replace('h', 'х')
        res = res.replace('H', 'Х')
        res = self.rxSoften.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], res)
        res = self.rxSh.sub('с', res)
        res = self.rxZh.sub('з', res)
        res = self.rxShCapital.sub('С', res)
        res = self.rxZhCapital.sub('З', res)
        res = self.rxVJV.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], res)
        res = self.rxVJV.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], res)
        res = self.rxJV.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], res)
        res = self.rxJVCapital.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()].upper(), res)
        res = self.rxNeutral1.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], res)
        res = self.rxNeutral2.sub('\\1и', res)
        res = self.rxCJV.sub(lambda m: 'ъ' + self.cyrHard2Soft[m.group(1).lower()], res)
        res = res.replace('ӟʼ', 'ӟ')
        res = res.replace('Ӟʼ', 'Ӟ')
        res = res.replace('чʼ', 'ч')
        res = res.replace('Чʼ', 'Ч')
        res = res.replace('ʼ', 'ь')
        res = self.rxExtraSoft.sub('\\1\\1', res)

        if res in self.cyrReplacements:
            res = self.cyrReplacements[res]
        return res

    def beserman_translit_upa(self, text):
        if text in self.srcReplacements:
            text = self.srcReplacements[text]
        text = text.replace("'", 'ʼ')
        text = text.replace('ə', 'ə̑')
        text = text.replace('Ə', 'Ə̑')
        text = text.replace('ɤ', 'e̮')
        text = text.replace('ɨ', 'i̮')
        text = text.replace('Ɨ', 'I̮')
        # text = text.replace('w', 'u̯')
        # text = text.replace('W', 'u̯')
        text = text.replace('čʼ', 'č́')
        text = text.replace('Čʼ', 'Č́')
        text = text.replace('ǯʼ', 'ǯ́')
        text = text.replace('Ǯʼ', 'Ǯ́')
        text = text.replace('šʼ', 'ś')
        text = text.replace('Šʼ', 'Ś')
        text = text.replace('žʼ', 'ź')
        text = text.replace('Žʼ', 'Ź')
        text = text.replace('dʼ', 'd́')
        text = text.replace('Dʼ', 'D́')
        text = text.replace('tʼ', 't́')
        text = text.replace('Tʼ', 'T́')
        text = text.replace('lʼ', 'ĺ')
        text = text.replace('Lʼ', 'Ĺ')
        text = text.replace('nʼ', 'ń')
        text = text.replace('Nʼ', 'Ń')
        text = text.replace('ʼ', '̓')
        return text

    def beserman_translit_cyr2dic(self, text):
        """
        Transliterate Beserman text from dictionary Latin script to the Cyrillics.
        """
        parts = self.rxWords.findall(text)
        return ''.join(self.beserman_translit_cyr2dic_word(part) for part in parts)
    
    def beserman_translit_cyr2dic_word(self, text):
        if text in self.cyr2dicReplacements:
            text = self.cyr2dicReplacements[text]
        text = self.rxCyrW.sub('\\1w', text)
        text = text.replace('жи', 'жӥ')
        text = text.replace('ши', 'шӥ')
        text = text.replace('же', 'жэ')
        text = text.replace('ше', 'шэ')
        text = text.replace('Жи', 'Жӥ')
        text = text.replace('Ши', 'Шӥ')
        text = text.replace('Же', 'Жэ')
        text = text.replace('Ше', 'Шэ')
        letters = []
        for letter in text:
            try:
                letters.append(self.cyr2dic[letter.lower()])
            except KeyError:
                letters.append(letter)
        text = ''.join(letters)
        text = self.rxCyrVJV.sub('\\1j\\2', text)
        text = self.rxCyrJV.sub('j\\1', text)
        text = text.replace('ъʼ', 'j')
        text = text.replace('sʼ', 'šʼ')
        text = text.replace('zʼ', 'žʼ')
        text = self.rxCyrSoften.sub('\\1ʼ', text)
        text = self.rxCyrNeutral.sub('', text)
        text = self.rxCyrExtraSoft.sub('\\1ʼ\\1', text)
        text = text.replace('sšʼ', 'šʼšʼ')
        text = text.replace('zžʼ', 'žʼžʼ')
        text = self.rxCyrMultSoften.sub('ʼ', text)
        text = self.rxCyrVSoft.sub('\\1', text)
        return text

    def upa_to_tatyshly(self, word):
        word = word.replace('·', '')    # Remove stress marks
        word = word.replace('·', '')    # Remove stress marks
        word = word.replace('͕', "'")
        word = self.rxUPAApos.sub(lambda m: self.dicUPAApos2Tatyshly[m.group(1)], word)
        word = word.replace('´', "'")
        word = word.replace('́', "'")
        return word

    def join_digraphs(self, word):
        word = self.rxWDiacritic.sub('w', word)
        word = self.rxWDiacriticCapital.sub('W', word)
        word = self.rxUe.sub('ü', word)
        word = self.rxUeCapital.sub('Ü', word)
        word = self.rxOe.sub('ö', word)
        word = self.rxOeCapital.sub('Ö', word)
        word = self.rxSchwa.sub('ə', word)
        word = self.rxSchwaCapital.sub('Ə', word)
        word = self.rxY.sub('ɨ', word)
        word = self.rxYCapital.sub('Ɨ', word)
        return word

    def join_digraphs_cyr(self, word):
        word = self.rxOeCyr.sub('ȯ', word)
        word = self.rxOeCapitalCyr.sub('Ȯ', word)
        return word

    def expand_variants(self, wordVariants, rxWhat, replacements, depth=-1):
        """
        Replace each occurrence of rxWhat within each of the words
        stored in wordVariants with all options listed in replacements.
        If depth > 0, it limits the number of iterations.
        Return updated word list.
        """
        wordVariantsUpdated = []
        prevListLen = -1
        iStep = 0
        while len(wordVariantsUpdated) != prevListLen and (depth <= 0 or iStep < depth):
            wordVariantsUpdated = []
            prevListLen = len(wordVariants)
            for word in wordVariants:
                if rxWhat.search(word) is None:
                    if word not in wordVariantsUpdated:
                        wordVariantsUpdated.append(word)
                else:
                    for replacement in replacements:
                        wordNew = rxWhat.sub(replacement, word, count=1)
                        if wordNew not in wordVariantsUpdated:
                            wordVariantsUpdated.append(wordNew)
            wordVariants = wordVariantsUpdated[:]
            iStep += 1
        return wordVariants

    def expand_ue_variants(self, wordVariants):
        """
        Try replacing ü with u or wi.
        """
        for i in range(len(wordVariants)):
            wordVariants[i] = self.rxUeFinalCyr.sub('у', wordVariants[i])
            wordVariants[i] = self.rxUeFinalCyrCapital.sub('У', wordVariants[i])
        wordVariants = self.expand_variants(wordVariants, self.rxUeCyr, ('у', 'уи'))
        return self.expand_variants(wordVariants, self.rxUeCyrCapital, ('У', 'Уи'))

    def expand_w_variants(self, wordVariants):
        """
        Try replacing w with u or v.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxWCyr, ('у', 'в'))
        return self.expand_variants(wordVariants, self.rxWCyrCapital, ('У', 'В'))

    def expand_ye_variants(self, wordVariants):
        """
        Try replacing je at the start with e, je or ö.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrJeStart, ('йэ', 'э', 'ӧ'))
        return self.expand_variants(wordVariants, self.rxCyrJeStartCapital, ('Йэ', 'Э', 'Ӧ'))

    def expand_dzjV_variants_start(self, wordVariants):
        """
        Try replacing dzjV at the start with dzjV, djV or jV.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrDZjVStart, ('ӟʼ', 'дʼ', 'й'))
        return self.expand_variants(wordVariants, self.rxCyrDZjVStartCapital, ('Ӟʼ', 'Дʼ', 'Й'))

    def expand_dzjV_variants_middle(self, wordVariants):
        """
        Try replacing dzja with dzja or dja.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrDZjVMiddle, ('ӟʼ', 'дʼ'))
        return wordVariants

    def expand_CDzjos_variants(self, wordVariants):
        """
        Try replacing Cdzjos with Cjos.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrCDZjos, ('ӟʼос', 'йос'), depth=1)
        return wordVariants

    def expand_GlottalStopDzjos_variants(self, wordVariants):
        """
        Try replacing glottal stop + dzjos with different Cjos.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrGlottalStopDZjos, ('ˀӟʼос', 'тйос', 'дйос',
                                                                                       'кйос', 'гйос'), depth=1)
        return wordVariants

    def expand_chV_variants(self, wordVariants):
        """
        Try replacing cha at the start with cha or tja.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrChV, ('чʼ', 'тʼ'))
        return self.expand_variants(wordVariants, self.rxCyrChVCapital, ('Чʼ', 'Тʼ'))

    def expand_ng_variants(self, wordVariants):
        """
        Try replacing ŋ with n, nj or m.
        """
        return self.expand_variants(wordVariants, self.rxCyrNg, ('н', 'нʼ', 'м'))

    def expand_cons_cluster_variants(self, wordVariants):
        """
        Try inserting y in certain consonant clusters.
        """
        return self.expand_variants(wordVariants, self.rxCyrConsCluster, ('\\1\\2', '\\1ы\\2'))

    def expand_sh_variants(self, wordVariants):
        """
        Try replacing sh with sh or tsh.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrSh, ('ш', 'ӵ'))
        return self.expand_variants(wordVariants, self.rxCyrShCapital, ('Ш', 'Ӵ'))

    def expand_ch_variants(self, wordVariants):
        """
        Try replacing ch with ch or tsh.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrCh, ('чʼ', 'ӵ'))
        return self.expand_variants(wordVariants, self.rxCyrChCapital, ('Чʼ', 'Ӵ'))

    def expand_zh_variants(self, wordVariants):
        """
        Try replacing zh with zh or dzh.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrZh, ('ж', 'ӝ'))
        return self.expand_variants(wordVariants, self.rxCyrZhCapital, ('Ж', 'Ӝ'))

    def expand_Vjy_variants(self, wordVariants):
        """
        Try removing the j between a vowel and y at the end of the word.
        """
        return self.expand_variants(wordVariants, self.rxCyrJYEnd, ('\\1', 'й\\1'))

    def expand_glottal_stop_variants(self, wordVariants):
        """
        Try replacing glottal stop with different consonants.
        """
        return self.expand_variants(wordVariants, self.rxGlottalStop, ('д', 'т', 'г', 'к'))

    def expand_shwa_variants(self, wordVariants):
        """
        Try replacing schwa with different vowels.
        """
        return self.expand_variants(wordVariants, self.rxCyrSchwa, ('ы', 'ӥ', 'у', 'ӧ'))

    def expand_consonant_assimilation_variants(self, wordVariants):
        """
        Try double consonants that may have been the result of an assimilation.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrMM, ('мм', 'нм'))
        wordVariants = self.expand_variants(wordVariants, self.rxCyrTT, ('тт', 'дт'))
        wordVariants = self.expand_variants(wordVariants, self.rxCyrChCh, ('чч', 'тч', 'дч'))
        wordVariants = self.expand_variants(wordVariants, self.rxCyrDzjDzj, ('ӟӟ', 'дӟ', 'тӟ'))
        return wordVariants

    def expand_final_devoicing_variants(self, wordVariants):
        """
        Try voicing final consonants if they are voiceless.
        """
        wordVariants = self.expand_variants(wordVariants, self.rxCyrFinalT, ('т\\1', 'д\\1'))
        wordVariants = self.expand_variants(wordVariants, self.rxCyrFinalK, ('к\\1', 'г\\1'))
        return self.expand_variants(wordVariants, self.rxCyrFinalP, ('п\\1', 'б\\1'))

    def pick_best(self, words):
        """
        Choose the most probable replacement out of several options
        based on frequency.
        """
        if len(words) <= 0:
            return ''
        elif len(words) == 1:
            return words[0]
        bestWord = words[0]
        maxFreq = -1
        for word in words:
            wordLower = word.lower()
            if wordLower in self.freqDict:
                curFreq = self.freqDict[wordLower]
                if curFreq > maxFreq:
                    bestWord = word
                    maxFreq = curFreq
        if maxFreq == -1:
            # Couldn't find any word in the frequency dictionary
            random.shuffle(words)
            for word in words:
                if self.analyzable(word):
                    return word
        return bestWord

    def transliterate_word_tatyshly_standard(self, word, finalDevoicing=True):
        if self.rxCyrillic.search(word) is not None:
            return word
        word = self.upa_to_tatyshly(word)
        word = self.join_digraphs(word)

        letters = []
        for letter in word:
            if letter.lower() in self.dic2cyr:
                if letter.islower():
                    letters.append(self.dic2cyr[letter.lower()])
                else:
                    letters.append(self.dic2cyr[letter.lower()].upper())
            else:
                letters.append(letter)
        word = ''.join(letters)
        word = word.replace("'", 'ʼ')

        # Some replacements are ambiguous
        wordVariants = [word]
        wordVariants = self.expand_ye_variants(wordVariants)
        wordVariants = self.expand_dzjV_variants_start(wordVariants)
        wordVariants = self.expand_chV_variants(wordVariants)
        wordVariants = self.expand_dzjV_variants_middle(wordVariants)
        wordVariants = self.expand_CDzjos_variants(wordVariants)
        wordVariants = self.expand_GlottalStopDzjos_variants(wordVariants)
        wordVariants = self.expand_Vjy_variants(wordVariants)
        wordVariants = self.expand_ng_variants(wordVariants)
        wordVariants = self.expand_sh_variants(wordVariants)
        wordVariants = self.expand_ch_variants(wordVariants)
        wordVariants = self.expand_zh_variants(wordVariants)
        wordVariants = self.expand_cons_cluster_variants(wordVariants)
        wordVariants = self.expand_ue_variants(wordVariants)
        wordVariants = self.expand_w_variants(wordVariants)
        wordVariants = self.expand_glottal_stop_variants(wordVariants)
        wordVariants = self.expand_shwa_variants(wordVariants)
        wordVariants = self.expand_consonant_assimilation_variants(wordVariants)
        if finalDevoicing:
            wordVariants = self.expand_final_devoicing_variants(wordVariants)
        # print(wordVariants)

        for i in range(len(wordVariants)):
            w = wordVariants[i]
            w = self.rxSoften.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxSh.sub('с', w)
            w = self.rxZh.sub('з', w)
            w = self.rxShCapital.sub('С', w)
            w = self.rxZhCapital.sub('З', w)
            w = self.rxVJV.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxVJV.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxSoftJV.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxJV.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxJVCapital.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()].upper(), w)
            w = self.rxNeutral1.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxNeutral2.sub('\\1и', w)
            w = self.rxCJV.sub(lambda m: 'ъ' + self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxCSoftJV.sub(lambda m: 'ъ' + self.cyrHard2Soft[m.group(1).lower()], w)
            w = w.replace('ӟʼ', 'ӟ')
            w = w.replace('Ӟʼ', 'Ӟ')
            w = w.replace('чʼ', 'ч')
            w = w.replace('Чʼ', 'Ч')
            w = w.replace('ʼ', 'ь')
            w = self.rxExtraSoft.sub('\\1\\1', w)

            if self.rxCyrReplacementsBasic.search(w) is not None:
                for rxSrc, replacement in self.cyrReplacementsBasic.items():
                    w = rxSrc.sub(replacement, w)
            if self.rxCyrReplacementsStd.search(w) is not None:
                for rxSrc, replacement in self.cyrReplacementsStd.items():
                    w = rxSrc.sub(replacement, w)

            wordVariants[i] = w

        # print(wordVariants)
        return self.pick_best(wordVariants)

    def transliterate_word_cyrtrans_upa(self, word):
        """
        Transliterate Cyrillic transcription into UPA.
        """
        # if self.rxCyrillic.search(word) is None:
        #     return word
        word = self.join_digraphs_cyr(word)

        letters = []
        for letter in word:
            if letter.lower() in self.cyr2upa:
                if letter.islower():
                    letters.append(self.cyr2upa[letter.lower()])
                else:
                    letters.append(self.cyr2upa[letter.lower()].upper())
            else:
                letters.append(letter)
        word = ''.join(letters)
        return word

    def transliterate_word(self, word, src='', target='', eafCleanup=None):
        """
        Return transliterated word, taking into account
        src, target and other parameters.
        """
        # Use default values if none are provided
        if len(src) <= 0:
            src = self.src
        if len(target) <= 0:
            target = self.target
        if eafCleanup is None:
            eafCleanup = self.eafCleanup

        # Lots of cases
        if src == 'tatyshly_lat':
            if target == 'standard':
                return self.transliterate_word_tatyshly_standard(word)
        if src == 'tatyshly_cyr':
            if target == 'standard':
                wordUpa = self.transliterate_word_cyrtrans_upa(word)
                return self.transliterate_word_tatyshly_standard(wordUpa, finalDevoicing=True)

        return word

    def transliterate(self, text, src='', target='', eafCleanup=None):
        """
        Return transliterated string, taking into account
        src, target and other parameters.
        """
        # Use default values if none are provided
        if len(src) <= 0:
            src = self.src
        if len(target) <= 0:
            target = self.target
        if eafCleanup is None:
            eafCleanup = self.eafCleanup

        if eafCleanup:
            text = self.rxDots.sub('... ', text)
            text = self.rxSpaces.sub(' ', text).strip()

        parts = self.rxWords.findall(text)
        text = ''.join(self.transliterate_word(part,
                                               src=src,
                                               target=target,
                                               eafCleanup=eafCleanup)
                       for part in parts)

        if eafCleanup:
            text = self.rxNrzb.sub('[нрзб]', text)
            # if target == 'standard':
            #     text = self.rxTwoPartWords.sub('\\1 \\2', text)
            # else:
            #     text = self.rxTwoPartWords.sub('\\1\\2', text)
            # if target == 'standard':
            #     text = self.rxQ.sub('-а', text)
            # else:
            #     text = self.rxQ.sub(' a', text)
        return text


if __name__ == '__main__':
    bt = UdmurtTransliterator(src='tatyshly_lat',
                              target='standard',
                              eafCleanup=True)
    print(bt.transliterate("no uˀmort s'äin polnost'ju kə̑ljosə̑z vala."))
    print(bt.transliterate("van' odiˀ vnuke."))
    print(bt.transliterate("jen pitra."))
    print(bt.transliterate("nə̑lə̑, baˀǯ'ə̑ŋez, d'iana."))
    print(bt.transliterate("nə̑lə̑lə̑ ku̯amə̑n ares."))
    print(bt.transliterate("nə̑lə̑ uže magn'itə̑n d'irektor lu̇sa."))
    print(bt.transliterate("kuzpale, karte mə̑nam uža das ku̇n' ar uže sverlovskə̑n."))
    print(bt.transliterate("van'ze verasa bə̑dti mon tileˀlə̑, van' istori asles'tə̑m."))
    print(bt.transliterate("otə̑n al'i uks'o tə̑ro ke no, užas's'os tə̑ros jevə̑l ni."))
    print(bt.transliterate("užaj školajə̑n ku̯amə̑n ar, biologi= biologija no ximija nu̇i."))
    print(bt.transliterate("i udmurtjos kazanskij xanstvolen udmurtjosə̑z lu̇em bere ǯ'u̇č'josə̑n gožto dogovor."))
    # print(bt.beserman_translit_cyrillic('walʼlʼo no soje tuləs pɤžʼtəlizə, štobɨ gužem užan dərja.... marəmen...'))
    # print(bt.beserman_translit_upa('walʼlʼo no soje tuləs pɤžʼtəlizə, štobɨ gužem užan dərja.... marəmen...'))
    bt = UdmurtTransliterator(src='tatyshly_cyr',
                              target='standard',
                              eafCleanup=True)
    print(bt.transliterate("одик пол иммӓр ас дораз тылобурдоосъз ӧ⁰т'ътэм."))
    print(bt.transliterate("со вӱэн мис'тӓс'кэм но сӹбӹрэ гӹнэ иммӓр доръ мънэм."))
    print(bt.transliterate("— тон ачит вӱ шӧттид-а ма? — шӱэм но иммӓр, пэззъкэз шур доръ лэз'ъмтэ ни."))
    print(bt.transliterate("тӥн'и сойин кўака вӱо интъйън, пэ, улэ, а пэззък ўан' гӱмӹрзэ вӱ уччаса орччътэ."))
