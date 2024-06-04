from converters.baseConverter import ConverterContext

### NIE WIEM CZY TO JEST DOBRZE NA RAZIE !!!!!!!!!!!!!!1
class GbToFasta:
    IN_EXTENSION = ''
    OUT_EXTENSION = ''

    def extract_protein_sequence(self, entry_lines):
        sequence = ""
        reading = False
        for line in entry_lines:
            if line.startswith('ORIGIN'):
                reading = True
                continue
            elif line.startswith('//'):
                break
            if reading:
                for part in line:
                    if len(part) > 0 and part[0].isalpha():
                        sequence += part
        return sequence.replace("\n", '').upper()

    def find_id(self, entry_lines, identifier_type):
        for line in entry_lines.split("\n"):
            if identifier_type == "accession" and line.startswith("ACCESSION"):
                return line.split()[1]
            elif identifier_type == "locus" and line.startswith("LOCUS"):
                return line.split()[1]
        return None

    def find_organism(self, entry_lines):
        for line in entry_lines.split("\n"):
            if line.strip().startswith("ORGANISM"):
                return ' '.join(line.split()[1:])
        return "Unknown"

    def convert(self, ctx: ConverterContext, identifier_type: str):
        genbank_file = ctx.input.read()
        entry_lines = genbank_file.split("//\n")
        for line in entry_lines:
            if not line.strip():
                continue
            try:
                identifier = self.find_id(line, identifier_type)
                organism = self.find_organism(line)
                sequence = self.extract_protein_sequence(line.split('\n'))
                ctx.write(f">{organism}-{identifier}\n{sequence}\n")
            except Exception as e:
                ctx.log_error(f"Error processing entry: {e}")

def convert_genbank_to_fasta(input_data: str, identifier_type: str, file_format: str) -> str:
    input_stream = io.StringIO(input_data)
    output_stream = io.StringIO()

    ctx = ConverterContext(dst=output_stream, src=input_stream)
    converter = GbToFasta()
    converter.convert(ctx, identifier_type)

    return output_stream.getvalue()


class FastaToGb:
    IN_EXTENSION = 'fasta'
    OUT_EXTENSION = 'gbk'

    def __init__(self, identifier_type='locus'):
        self.identifier_type = identifier_type

    def parse_fasta(self, ctx: ConverterContext):
        sequences = []
        header = None
        sequence = ""
        for line in ctx:
            line = line.strip()
            if line.startswith(">"):
                if header:
                    sequences.append((header, sequence))
                header = line[1:]
                sequence = ""
            else:
                sequence += line
        if header:
            sequences.append((header, sequence))
        return sequences

    def generate_genbank(self, header, sequence):
        id_parts = header.split('-')
        if self.identifier_type == "accession":
            identifier = id_parts[-1]
        else:
            identifier = id_parts[0]
        organism = " ".join(id_parts[:-1]) if self.identifier_type == "accession" else " ".join(id_parts[1:])

        genbank_entry = f"""LOCUS       {identifier} {len(sequence)} bp    DNA     linear   UNK {time.strftime('%d-%b-%Y').upper()}
DEFINITION  {header}.
ACCESSION   {identifier}
ORGANISM    {organism}
            Unclassified.
FEATURES             Location/Qualifiers
     source          1..{len(sequence)}
                     /organism="{organism}"
                     /mol_type="genomic DNA"
ORIGIN      
"""
        for i in range(0, len(sequence), 60):
            chunk = sequence[i:i+60]
            chunk_str = ' '.join([chunk[j:j+10] for j in range(0, len(chunk), 10)])
            genbank_entry += f"        {i+1:9} {chunk_str}\n"
        genbank_entry += "//\n"
        return genbank_entry

    def convert(self, ctx: ConverterContext):
        sequences = self.parse_fasta(ctx)
        for header, sequence in sequences:
            try:
                genbank_entry = self.generate_genbank(header, sequence)
                ctx.write(genbank_entry)
            except Exception as e:
                ctx.log_error(f"Error processing entry: {e}")

def convert_fasta_to_genbank(input_data: str, identifier_type: str, file_format: str) -> str:
    input_stream = io.StringIO(input_data)
    output_stream = io.StringIO()

    ctx = ConverterContext(dst=output_stream, src=input_stream)
    converter = FastaToGb(identifier_type)
    converter.convert(ctx)

    return output_stream.getvalue()
