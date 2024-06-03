from converters.baseConverter import ConverterContext

class CsvToTsv:
    IN_EXTENSION = '.csv'
    OUT_EXTENSION = '.tsv'

    def convert(self, ctx : ConverterContext):
        for line in ctx:
            if '\t' in line:
                ctx.log_error('input contains tab character')
                continue

            if 'warn' in line:
                ctx.log_warning('example warning')

            ctx.write(line.replace(',', '\t'))


class TsvToCsv:
    IN_EXTENSION = '.tsv'
    OUT_EXTENSION = '.csv'

    def convert(self, ctx : ConverterContext):
        for line in ctx:
            if ',' in line:
                ctx.log_error('input contains tab character')
                continue

            if 'warn' in line:
                ctx.log_warning('example warning')

            ctx.write(line.replace('\t', ','))
