import os
import re
import pandas as pd
import numpy as np
import html
from udmurt_translit import UdmurtTransliterator


class CsvProcessor:
    """
    Contains methods for adding transliterated columns to a CSV file.
    """
    rxDir = re.compile('[/\\\\][^/\\\\]+$')

    def __init__(self, transliterator, sep='\t',
                 srcCol=0,
                 tgtCol=1,
                 startLine=1):
        self.transliterator = transliterator
        self.sep = sep
        self.srcCol = srcCol
        self.tgtCol = tgtCol
        self.startLine = startLine

    def process_file(self, fnameCsv, fnameCsvOut):
        """
        Process one CSV file.
        """
        lines = []
        # Read lines from XLSX or CSV
        if fnameCsv.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(fnameCsv, sheet_name=0, header=None)
            colList = df.columns.values
            for row in range(len(df)):
                lines.append([])
                for col in range(len(colList)):
                    lines[-1].append(df[colList[col]][row])
                    if lines[-1][-1] in (np.nan, None, 'nan'):
                        lines[-1][-1] = ''
                    else:
                        lines[-1][-1] = str(lines[-1][-1])
        elif fnameCsv.lower().endswith(('.csv', '.tsv')):
            with open(fnameCsv, 'r', encoding='utf-8-sig') as fIn:
                lines = [list(line.strip('\r\n').split(self.sep)) for line in fIn.readlines()]

        # Process data and write CSV
        for i in range(self.startLine, len(lines)):
            if len(lines[i]) <= self.srcCol:
                continue
            srcText = lines[i][self.srcCol]
            tgtText = self.transliterator.transliterate(srcText)
            if len(lines[i]) <= self.tgtCol:
                lines[i] += [''] * (self.tgtCol - len(lines) + 1)
            lines[i][self.tgtCol] = tgtText
        lines = [self.sep.join(line) for line in lines]
        with open(fnameCsvOut, 'w', encoding='utf-8-sig') as fOut:
            fOut.write('\n'.join(lines))

    def process_corpus(self):
        if not os.path.exists('csv'):
            print('All CSV files should be located in the csv folder.')
            return
        if not os.path.exists('csv_transliterated'):
            os.makedirs('csv_transliterated')

        nDocs = 0
        for root, dirs, files in os.walk('csv'):
            for fname in files:
                if not fname.lower().endswith(('.csv', '.tsv', '.xlsx', '.xls')):
                    continue
                fnameCsv = os.path.join(root, fname)
                fnameCsvOut = 'csv_transliterated' + re.sub('\\.xlsx?$', '.csv', fnameCsv[3:])
                outDirName = CsvProcessor.rxDir.sub('', fnameCsvOut)
                if len(outDirName) > 0 and not os.path.exists(outDirName):
                    os.makedirs(outDirName)
                nDocs += 1
                self.process_file(fnameCsv, fnameCsvOut)
        print(str(nDocs) + ' documents processed.')


if __name__ == '__main__':
    transliterator = UdmurtTransliterator(src='tatyshly_cyr', target='standard',
                                          eafCleanup=True)
    cp = CsvProcessor(transliterator, sep='\t', srcCol=1, tgtCol=0, startLine=1)
    cp.process_corpus()

