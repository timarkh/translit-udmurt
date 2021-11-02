import re
import json


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
               'y': 'ы', 'f': 'ф', 'ɨ': 'ы'}
    cyr2dic = {v: k for k, v in dic2cyr.items()}
    cyr2dic.update({'я': 'ʼa', 'е': 'ʼe', 'и': 'ʼi', 'ӝ': 'ǯ', 'ӵ': 'č', 'щ': 'šʼ',
                    'ё': 'ʼo', 'ю': 'ʼu', 'ь': 'ʼ', 'ы': 'ɨ', 'у': 'u'})
    dic2cyr.update({'ŋ': 'н', 'ä': 'а', 'h': 'х',
                    'ö': 'ӧ'})
    cyrHard2Soft = {'а': 'я', 'э': 'е', 'е': 'е', 'ӥ': 'и', 'о': 'ё', 'у': 'ю'}
    rxSoften = re.compile('(?<![чӟ])ʼ([аэӥоу])', flags=re.I)
    rxCyrSoften = re.compile('([čǯ])(?!ʼ)', flags=re.I)
    rxCyrMultSoften = re.compile('ʼ{2,}')
    rxNeutral1 = re.compile('(?<=[бвгжкмпрфхцчшщйʼ])([эӥ])', re.I)
    rxNeutral2 = re.compile('([бвгжкмпрфхцчʼаоэӥуўяёеиюө]|\\b)(ӥ)', re.I)
    rxCyrNeutral = re.compile('(?<=[bvgzkmprfxcwj])ʼ', re.I)
    rxCJV = re.compile('(?<=[бвгджзӟклмнпрстўфхцчшщ])й([аяэеӥоёую])', re.I)
    rxSh = re.compile('ш(?=[ʼяёюиеЯЁЮИЕ])')
    rxZh = re.compile('ж(?=[ʼяёюиеЯЁЮИЕ])')
    rxShCapital = re.compile('Ш(?=[ʼяёюиеЯЁЮИЕ])')
    rxZhCapital = re.compile('Ж(?=[ʼяёюиеЯЁЮИЕ])')
    rxVJV = re.compile('(?<=[аеёиӥоӧөуыэюяʼ])й([аэоу])', flags=re.I)
    rxJV = re.compile('\\bй([аэоу])')
    rxJVCapital = re.compile('\\bЙ([аэоуАЭОУ])')
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
    rxOe = re.compile('ȯ')
    rxOeCapital = re.compile('Ȯ')
    rxGlottalStop = re.compile('ˀ')
    rxSchwa = re.compile('ə̈|ə̑')
    rxSchwaCapital = re.compile('Ə̈|Ə̑')
    rxY = re.compile('i̮')
    rxYCapital = re.compile('I̮')
    rxCyrSchwa = re.compile('ө')
    rxCyrSchwaCapital = re.compile('Ө')

    rxCyrillic = re.compile('^[а-яёӟӥӧўөА-ЯЁӞӤӦЎӨ.,;:!?\-()\\[\\]{}<>]*$')

    rxWords = re.compile("[\\wʼ̑̈'̯̮̇-]+|[^\\wʼ̑̈'̯̮̇-]+", flags=re.DOTALL)

    def __init__(self, src, target, eafCleanup=False):
        self.cyrReplacements = {}
        self.srcReplacements = {}
        self.cyr2dicReplacements = {}
        self.rxCyrReplacements = re.compile('^$')
        self.src = src
        self.target = target
        self.eafCleanup = eafCleanup
        self.load_replacements('data/cyr_replacements_rx.csv')
        self.freqDict = self.load_freq_list()
        print('Initialization complete.')

    def load_replacements(self, filename):
        cyrRx = []
        with open(filename, 'r', encoding='utf-8') as fIn:
            for line in fIn:
                if len(line) <= 3:
                    return
                cyrSrc, cyrCorrect = line.strip('\r\n').split('\t')
                if len(cyrCorrect) > 0 and len(cyrSrc) > 0:
                    cyrSrc = cyrSrc.strip('^$')
                    cyrRx.append(cyrSrc)
                    self.cyrReplacements[re.compile('^' + cyrSrc + '$')] = cyrCorrect
                    self.cyrReplacements[re.compile('^' + cyrSrc.upper() + '$')] = cyrCorrect.upper()
                    self.cyrReplacements[re.compile('^' + cyrSrc.capitalize() + '$')] = cyrCorrect.capitalize()
        self.rxCyrReplacements = re.compile('|'.join(r for r in sorted(cyrRx, key=lambda x: -len(x))),
                                            flags=re.I)

    def load_freq_list(self):
        """
        Load Standard Udmurt frequency list.
        """
        freqDict = {}
        with open('data/std_freq_dict.json', 'r', encoding='utf-8') as fIn:
            freqDict = json.load(fIn)
        return freqDict

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

    def expand_glottal_stop_variants(self, wordVariants):
        """
        Try replacing glottal stop with different vowels.
        """
        wordVariantsUpdated = []
        prevListLen = -1
        while len(wordVariantsUpdated) != prevListLen:
            wordVariantsUpdated = []
            prevListLen = len(wordVariants)
            for word in wordVariants:
                if self.rxGlottalStop.search(word) is None:
                    wordVariantsUpdated.append(word)
                else:
                    for consonant in 'дтгк':
                        wordVariantsUpdated.append(self.rxGlottalStop.sub(consonant, word, count=1))
            wordVariants = wordVariantsUpdated[:]
        return wordVariants

    def expand_shwa_variants(self, wordVariants):
        """
        Try replacing schwa with different vowels.
        """
        wordVariantsUpdated = []
        prevListLen = -1
        while len(wordVariantsUpdated) != prevListLen:
            wordVariantsUpdated = []
            prevListLen = len(wordVariants)
            for word in wordVariants:
                if self.rxCyrSchwa.search(word) is None:
                    wordVariantsUpdated.append(word)
                else:
                    for vowel in 'ыиуӧ':
                        wordVariantsUpdated.append(self.rxCyrSchwa.sub(vowel, word, count=1))
            wordVariants = wordVariantsUpdated[:]
        return wordVariants

    def pick_best(self, words):
        """
        Choose the most probable replacement out of several options
        based on frequency.
        """
        if len(words) <= 0:
            return ''
        bestWord = words[0]
        maxFreq = -1
        for word in words:
            wordLower = word.lower()
            if wordLower in self.freqDict:
                curFreq = self.freqDict[wordLower]
                if curFreq > maxFreq:
                    bestWord = word
                    maxFreq = curFreq
        return bestWord

    def transliterate_word_tatyshly_standard(self, word):
        if self.rxCyrillic.search(word) is not None:
            return word
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
        if 'ü' in word.lower():
            wordVariants = [word.replace('ü', 'у').replace('Ü', 'У'), word.replace('ü', 'уи').replace('Ü', 'УИ')]
        wordVariants = self.expand_glottal_stop_variants(wordVariants)
        wordVariants = self.expand_shwa_variants(wordVariants)

        for i in range(len(wordVariants)):
            w = wordVariants[i]
            w = self.rxSoften.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxSh.sub('с', w)
            w = self.rxZh.sub('з', w)
            w = self.rxShCapital.sub('С', w)
            w = self.rxZhCapital.sub('З', w)
            w = self.rxVJV.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxVJV.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxJV.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxJVCapital.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()].upper(), w)
            w = self.rxNeutral1.sub(lambda m: self.cyrHard2Soft[m.group(1).lower()], w)
            w = self.rxNeutral2.sub('\\1и', w)
            w = self.rxCJV.sub(lambda m: 'ъ' + self.cyrHard2Soft[m.group(1).lower()], w)
            w = w.replace('ӟʼ', 'ӟ')
            w = w.replace('Ӟʼ', 'Ӟ')
            w = w.replace('чʼ', 'ч')
            w = w.replace('Чʼ', 'Ч')
            w = w.replace('ʼ', 'ь')
            w = self.rxExtraSoft.sub('\\1\\1', w)

            if self.rxCyrReplacements.search(w) is not None:
                for rxSrc, replacement in self.cyrReplacements.items():
                    w = rxSrc.sub(replacement, w)

            wordVariants[i] = w

        return self.pick_best(wordVariants)

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
    print(bt.transliterate("nə̑lə̑ uže magn'itə̑n d'irektor lu̇sa."))
    print(bt.transliterate("van'ze verasa bə̑dti mon tileˀlə̑, van' istori asles'tə̑m."))
    # print(bt.beserman_translit_cyrillic('walʼlʼo no soje tuləs pɤžʼtəlizə, štobɨ gužem užan dərja.... marəmen...'))
    # print(bt.beserman_translit_upa('walʼlʼo no soje tuləs pɤžʼtəlizə, štobɨ gužem užan dərja.... marəmen...'))
