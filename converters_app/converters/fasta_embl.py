from converters.baseConverter import ConverterContext

class EmblToFasta:
    IN_EXTENSION = ''
    OUT_EXTENSION = ''

    def convert(self, ctx : ConverterContext):
        for line in ctx:


class FastaToEmbl:
    IN_EXTENSION = ''
    OUT_EXTENSION = ''

    def convert(self, ctx : ConverterContext):
        for line in ctx:
