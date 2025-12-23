import os
import re
import xml.etree.ElementTree as ET
from udmurt_translit import UdmurtTransliterator


class TlexXMLProcessor:
    """
    Contains methods for transliterating examples and entries
    in a TLEX-generated XML file in the Beserman Dictionary project
    format.
    """
    rxDir = re.compile('[/\\\\][^/\\\\]+$')

    def __init__(self, transliterator):
        self.transliterator = transliterator

    def xml2txt(self, tree, fnameTxtOut):
        text = ''
        for el in tree.findall('.//Lemma'):
            text += '\n\n\n***  ' + el.attrib['LemmaSign'] + '  ***\n'
            for val in el.findall('.//Value'):
                if ('ValTr' not in val.attrib and 'ValNeed' not in val.attrib) or val.attrib['ValNeed'] != '584':
                    continue
                text += '\n'
                if 'ValTr' in val.attrib:
                    text += ' -> ' + val.attrib['ValTr']
                if 'ValTolk' in val.attrib:
                    text += ' :: ' + val.attrib['ValTolk']
                if 'ValPometa' in val.attrib:
                    if '205' in val.attrib['ValPometa']:
                        text += ' (удм.)'
                    if '206' in val.attrib['ValPometa']:
                        text += ' (устар.)'
                    if '203' in val.attrib['ValPometa']:
                        text += ' (редк.)'
                text += '\n'
                for ex in val.findall('.//Example'):
                    if 'ExText' not in ex.attrib or 'ExTrans' not in ex.attrib or 'ExGoesToDict' not in ex.attrib or ex.attrib['ExGoesToDict'] != '584':
                        continue
                    text += '  ~ ' + ex.attrib['ExText'] + ' --- ' + ex.attrib['ExTrans'] + '\n'

            for idiom in el.findall('.//Idiom'):
                if 'IdiomText' not in idiom.attrib or 'IdiomTr' not in idiom.attrib or 'IdiomNeed' not in idiom.attrib or idiom.attrib['IdiomNeed'] != '584':
                    continue
                text += '\n ♢ ' + idiom.attrib['IdiomText'] + ' • ' + idiom.attrib['IdiomTr']
                if 'IdiomPometa' in idiom.attrib:
                    if '205' in idiom.attrib['IdiomPometa']:
                        text += ' (удм.)'
                    if '206' in idiom.attrib['IdiomPometa']:
                        text += ' (устар.)'
                    if '203' in idiom.attrib['IdiomPometa']:
                        text += ' (редк.)'
                text += '\n'
                for ex in idiom.findall('.//Example'):
                    if 'ExText' not in ex.attrib or 'ExTrans' not in ex.attrib or 'ExGoesToDict' not in ex.attrib or ex.attrib['ExGoesToDict'] != '584':
                        continue
                    text += '  ~ ' + ex.attrib['ExText'] + ' --- ' + ex.attrib['ExTrans'] + '\n'

            for subel in el.findall('.//SubLemma'):
                text += '\n\n  ** ' + subel.attrib['SubLeSign'] + ' **\n'
                for val in subel.findall('.//Value'):
                    if 'ValTr' not in val.attrib or 'ValNeed' not in val.attrib or val.attrib['ValNeed'] != '584':
                        continue
                    text += '\n -> ' + val.attrib['ValTr']
                    if 'ValTolk' in val.attrib:
                        text += ' :: ' + val.attrib['ValTolk']
                    text += '\n'
                    for ex in val.findall('.//Example'):
                        if 'ExText' not in ex.attrib or 'ExTrans' not in ex.attrib or 'ExGoesToDict' not in ex.attrib or \
                                ex.attrib['ExGoesToDict'] != '584':
                            continue
                        text += '  ~ ' + ex.attrib['ExText'] + ' --- ' + ex.attrib['ExTrans'] + '\n'
        with open(fnameTxtOut, 'w', encoding='utf-8') as fOut:
            fOut.write(text)

    def process_file(self, fnameXml, fnameXmlOut, fnameTxtOut=''):
        """
        Process one XML file.
        """
        if not fnameXml.lower().endswith(('.xml', '.xhtml')):
            return
        tree = ET.parse(fnameXml)
        for nodeName in ('Lemma', 'SubLemma', 'Example', 'Idiom'):
            for el in tree.findall('.//' + nodeName):
                for a in ('Text', 'ExText', 'IdiomText', 'LemmaSign', 'SubLeSign'):
                    if a in el.attrib:
                        el.attrib[a] = self.transliterator.transliterate(el.attrib[a])
        tree.write(fnameXmlOut, encoding='unicode')
        if len(fnameTxtOut) > 0:
            self.xml2txt(tree, fnameTxtOut)

    def process_corpus(self):
        if not os.path.exists('xml'):
            print('All XML files should be located in the xml folder.')
            return
        if not os.path.exists('xml_transliterated'):
            os.makedirs('xml_transliterated')

        nDocs = 0
        for root, dirs, files in os.walk('xml'):
            for fname in files:
                if not fname.lower().endswith(('.xml', '.xhtml')):
                    continue
                fnameXml = os.path.join(root, fname)
                fnameXmlOut = 'xml_transliterated' + fnameXml[3:]
                fnameTxtOut = re.sub('\\.[^.]+$', '.txt', fnameXmlOut)
                outDirName = TlexXMLProcessor.rxDir.sub('', fnameXmlOut)
                if len(outDirName) > 0 and not os.path.exists(outDirName):
                    os.makedirs(outDirName)
                nDocs += 1
                self.process_file(fnameXml, fnameXmlOut, fnameTxtOut)
        print(str(nDocs) + ' documents processed.')


if __name__ == '__main__':
    transliterator = UdmurtTransliterator(src='beserman_lat', target='beserman_cyr',
                                          eafCleanup=False)
    xmlp = TlexXMLProcessor(transliterator)
    xmlp.process_corpus()

