from converters.baseConverter import ConverterContext

class GbToFasta:
    IN_EXTENSION = ''
    OUT_EXTENSION = ''

    def convert(self, ctx : ConverterContext):
        for line in ctx:


class FastaToGb:
    IN_EXTENSION = ''
    OUT_EXTENSION = ''

    def convert(self, ctx : ConverterContext):
        for line in ctx:
