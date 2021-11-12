import os
import re
import html
from lxml import etree
from udmurt_translit import UdmurtTransliterator


EAF_TIME_MULTIPLIER = 1000  # time stamps are in milliseconds


class EafProcessor:
    """
    Contains methods for adding transliterated tiers to an ELAN file.
    """
    rxDir = re.compile('[/\\\\][^/\\\\]+$')
    rxSpeakerCode = re.compile('^\\[[^\\[\\]]+\\]$')

    def __init__(self, transliterator, tiers,
                 replaceSegments=False,
                 translitType='transcription_st',
                 translitTierPfx='tx_st',
                 csTier=None,
                 csTurnOffRegex=''):
        self.transliterator = transliterator
        self.eafTree = None
        self.replaceSegments = replaceSegments  # Whether segment text should be
                                                # with the transliteration
        self.translitType = translitType        # Tier type to be added, if replaceSegments is false
        self.translitTierPfx = translitTierPfx
        self.csTier = ''            # Tier where code switching is annotated
                                    # (must be associated with the transcription)
        self.rxCSTier = ''
        if csTier is not None:
            self.csTier = csTier
            self.csTurnOffRegex = re.compile(csTurnOffRegex)
            # Do not transliterate transcription segments
            # if the associated CS segment matches this regex
            if not self.csTier.startswith('^'):
                self.csTier = '^' + self.csTier
            if not self.csTier.endswith('$'):
                self.csTier += '$'
            self.rxCSTier = re.compile(self.csTier)
        self.csTranscriptionSegments = []
        if not tiers.startswith('^'):
            tiers = '^' + tiers
        if not tiers.endswith('$'):
            tiers += '$'
        self.rxTiers = re.compile(tiers)    # regex for names or types of tiers to be transliterated
        self.lastID = 0

    def check_tier_types(self):
        """
        Check if ELAN tier type(s) needed for the transliteration
        already exist in the ELAN file. If not, add them.
        """
        if self.replaceSegments:
            return
        tierAttrs = [
            ('Symbolic_Association', self.translitType)
        ]
        for constraint, tierType in tierAttrs:
            tierTypeTxt = '<LINGUISTIC_TYPE CONSTRAINTS="' + constraint + '"' \
                          ' GRAPHIC_REFERENCES="false" LINGUISTIC_TYPE_ID="' + tierType + '"' \
                          ' TIME_ALIGNABLE="false"/>\n'
            tierEl = self.eafTree.xpath(
                '/ANNOTATION_DOCUMENT/LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID=\'' + tierType + '\']')
            lastTier = self.eafTree.xpath('/ANNOTATION_DOCUMENT/TIER')[-1]
            tierParent = lastTier.getparent()
            if len(tierEl) <= 0:
                tierParent.insert(tierParent.index(lastTier) + 1, etree.XML(tierTypeTxt))

    def collectCSData(self):
        """
        If there are code switching tiers, collect IDs of
        transcription segments corresponding to the code
        switching instances.
        """
        if self.csTier is None or len(self.csTier) <= 0:
            return
        self.csTranscriptionSegments = []
        for tierNode in self.eafTree.xpath('/ANNOTATION_DOCUMENT/TIER'):
            if 'TIER_ID' not in tierNode.attrib:
                continue
            tierID = tierNode.attrib['TIER_ID']
            if (self.rxCSTier.search(tierID) is not None
                    or self.rxCSTier.search(tierNode.attrib['LINGUISTIC_TYPE_REF']) is not None):
                for segNode in tierNode.xpath('ANNOTATION/REF_ANNOTATION'):
                    if 'ANNOTATION_REF' not in segNode.attrib:
                        continue
                    try:
                        segText = segNode.xpath('ANNOTATION_VALUE')[0].text.strip().lower()
                    except AttributeError:
                        continue
                    if self.csTurnOffRegex.search(segText) is not None:
                        self.csTranscriptionSegments.append(segNode.attrib['ANNOTATION_REF'])

    def write_output(self, fnameEafOut):
        """
        Write current (transliterated) EAF tree to the output file.
        """
        if self.eafTree is None:
            return
        self.eafTree.write(fnameEafOut,
                           pretty_print=True,
                           xml_declaration=True,
                           encoding="utf-8")

    def create_dependent_annotation(self, curID, parentID, text, prevID=''):
        """
        Create an XML element representing one annotation in transliteration tiers.
        """
        if prevID == '':
            annoTxt = '<ANNOTATION>\n\t\t\t<REF_ANNOTATION ANNOTATION_ID="' + curID \
                      + '" ANNOTATION_REF="' + parentID + '">\n'
        else:
            annoTxt = '<ANNOTATION>\n\t\t\t<REF_ANNOTATION ANNOTATION_ID="' + curID \
                      + '" ANNOTATION_REF="' + parentID + '" PREVIOUS_ANNOTATION="' + prevID + '">\n'
        annoTxt += '\t\t\t\t<ANNOTATION_VALUE>' + html.escape(text) \
                   + '</ANNOTATION_VALUE>\n\t\t\t</REF_ANNOTATION>\n\t\t</ANNOTATION>'
        return etree.XML(annoTxt)

    def process_tier(self, tierNode, participant):
        """
        Transliterate one transcription tier.
        """
        tierID = tierNode.attrib['TIER_ID']
        translitTierTxt = '<TIER LINGUISTIC_TYPE_REF="' + self.translitType + \
                          '" PARENT_REF="' + tierID + '" PARTICIPANT="' + participant + \
                          '" TIER_ID="' + self.translitTierPfx + '@' + participant + '"/>\n'
        translitTier = etree.XML(translitTierTxt)
        tierParent = tierNode.getparent()

        for segNode in tierNode.xpath('ANNOTATION/ALIGNABLE_ANNOTATION'):
            if 'ANNOTATION_ID' not in segNode.attrib:
                continue
            segID = segNode.attrib['ANNOTATION_ID']
            if segID in self.csTranscriptionSegments:
                # Do not transliterate code switches
                continue
            try:
                segText = segNode.xpath('ANNOTATION_VALUE')[0].text.strip().lower()
            except AttributeError:
                continue
            transText = self.transliterator.transliterate(segText)
            if self.replaceSegments:
                segNode.xpath('ANNOTATION_VALUE')[0].text = transText
                continue
            else:
                curWordID = 'a' + str(self.lastID)
                self.lastID += 1
                translitEl = self.create_dependent_annotation(curWordID, segID, transText)
                translitTier.insert(len(translitTier), translitEl)
        if not self.replaceSegments:
            tierParent.insert(tierParent.index(tierNode) + 1, translitTier)

    def transliterate(self):
        """
        Transliterate self.eafTree.
        """
        self.check_tier_types()
        participantID = 1
        self.collectCSData()
        for tierNode in self.eafTree.xpath('/ANNOTATION_DOCUMENT/TIER'):
            if 'TIER_ID' not in tierNode.attrib:
                continue
            tierID = tierNode.attrib['TIER_ID']
            if (self.rxTiers.search(tierID) is not None
                    or self.rxTiers.search(tierNode.attrib['LINGUISTIC_TYPE_REF']) is not None):
                if 'PARTICIPANT' not in tierNode.attrib:
                    participant = ''
                else:
                    participant = tierNode.attrib['PARTICIPANT']
                if len(participant) <= 0:
                    participant = 'SP' + str(participantID)
                    participantID += 1
                self.process_tier(tierNode, participant)
        self.eafTree.xpath('/ANNOTATION_DOCUMENT/HEADER/'
                           'PROPERTY[@NAME=\'lastUsedAnnotationId\']')[0].text = str(self.lastID - 1)

    def process_corpus(self):
        if not os.path.exists('eaf'):
            print('All ELAN files should be located in the eaf folder.')
            return
        if not os.path.exists('eaf_transliterated'):
            os.makedirs('eaf_transliterated')

        nDocs = 0
        for root, dirs, files in os.walk('eaf'):
            for fname in files:
                if not fname.lower().endswith('.eaf'):
                    continue
                fnameEaf = os.path.join(root, fname)
                fnameEafOut = 'eaf_transliterated' + fnameEaf[3:]
                self.eafTree = etree.parse(fnameEaf)
                outDirName = EafProcessor.rxDir.sub('', fnameEafOut)
                if len(outDirName) > 0 and not os.path.exists(outDirName):
                    os.makedirs(outDirName)
                nDocs += 1
                self.lastID = int(self.eafTree.xpath('/ANNOTATION_DOCUMENT/HEADER/'
                                                     'PROPERTY[@NAME=\'lastUsedAnnotationId\']')[0].text) + 1
                self.transliterate()
                self.write_output(fnameEafOut)
        print(str(nDocs) + ' documents processed.')


if __name__ == '__main__':
    transliterator = UdmurtTransliterator(src='tatyshly_lat', target='standard',
                                          eafCleanup=True)
    ep = EafProcessor(transliterator, 'transcription')
    ep.process_corpus()
