"""
Parse MCE errors coming from the kernel.
"""

import argparse
import datetime
import re
import sys

import pandas as pd

def main(argv) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('mce_log')
    args = parser.parse_args(argv)

    mces = []
    with open(args.mce_log, 'r', encoding='utf8') as log_file:
        mce_lines = []
        for line in log_file:
            line = line.rstrip(' ')
            if line == '\n':
                mces.append(''.join(mce_lines))
                mce_lines = []
            else:
                mce_lines.append(line)

    pattern = re.compile(r'^.*mce: \[Hardware Error\]: Machine check events logged$\n'
                         r'^.*mce: \[Hardware Error\]: CPU (\d+): Machine Check: (\d+) Bank (\d+): ([\d\w]+)$\n'
                         r'^.*mce: \[Hardware Error\]: TSC (\d+) ADDR ([\d\w]+) MISC ([\d\w]+) SYND ([\d\w]+) IPID ([\d\w]+)$\n'
                         r'^.*mce: \[Hardware Error\]: PROCESSOR (\d:[\d\w]+) TIME (\d+) SOCKET (\d) APIC ([\d\w]) microcode (\d+)$',
                         re.MULTILINE)

    data = []
    for mce in mces:
        if match := pattern.match(mce):
            data.append(match.groups())
        else:
            print(f'no match for "{mce}"', file=sys.stderr)

    frame = pd.DataFrame(data, columns=['CPU', 'MC', 'Bank', 'BankCode', 'TSC',
                                        'ADDR', 'MISC', 'SYND', 'IPID', 'PROC',
                                        'TIME', 'SOCKET', 'APIC', 'microcode'])
    print(frame)

    frame['CPU'] = frame['CPU'].apply(int)
    frame['MC'] = frame['MC'].apply(int)
    frame['TIME'] = frame['TIME'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)))
    frame['APIC'] = frame['APIC'].apply(lambda x: int(x, 16))

    print(frame['microcode'].apply(int).value_counts(normalize=True))
    print('BankCode:', frame['BankCode'].value_counts(normalize=True))
    print('MISC:', frame['MISC'].value_counts(normalize=True))
    print('SYND:', frame['SYND'].value_counts(normalize=True))
    print('IPID:', frame['IPID'].value_counts(normalize=True))
    print('PROC:', frame['PROC'].value_counts(normalize=True))

    print(frame)

if __name__ == '__main__':
    main(sys.argv[1:])
