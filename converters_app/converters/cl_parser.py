import argparse

class Parser:
    def __init__(self):
        self.input = None
        self.output = None

        self.format = None

        self.exclude = False
        self.verbose = False

    def run(self):
        parser = argparse.ArgumentParser(prog = 'secon',
                                         description = 'Nucleic acid sequence files batch converter.\
                                            Supports FASTA, GenBank and EMBL formats.',
                                         epilog='For more info go to: https://github.com/Silbena/SeCon')

        parser.add_argument('input',
                            type = str,
                            help = 'path to input file/folder')
        parser.add_argument('format',
                            type = str,
                            help = '.ext (fasta/embl/gb)')
        parser.add_argument('-o','--output',
                            default='.',
                            type = str,
                            help = 'path to output folder')
        parser.add_argument('-e', '--exclude',
                            type = str,
                            help = 'file/folder to be excluded from conversion (only for folders)')
        parser.add_argument('-v', '--verbose',
                            action = 'store_true',
                            help = 'print all logs')
        
        args = parser.parse_args()

        self.input = args.input
        self.output = args.output

        self.format = args.format

        self.exclude = args.exclude
        self.verbose = args.verbose
