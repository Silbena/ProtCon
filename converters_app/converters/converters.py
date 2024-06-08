import converters.csvConverter as csv
import converters.fasta_embl as fe
import converters.fasta_gb as fg
import converters.gb_embl as ge

# Add the rest of converters

def get_converters() -> list:
    return [
        csv.CsvToTsv,
        csv.TsvToCsv,
        fg.GbToFasta,
        fg.FastaToGb,
        fe.EmblToFasta,
        fe.FastaToEmbl,
        ge.EmblToGb,
        ge.GbToEmbl
        ]
