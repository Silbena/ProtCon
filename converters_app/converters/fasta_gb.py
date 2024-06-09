from converters.baseConverter import ConverterContext
import time

class GbToFasta:
    IN_EXTENSION = 'gb'
    OUT_EXTENSION = 'fasta'

    def extract_nucleotide_sequence(self, entry_lines):
        """
        Extracts nucleotide sequence from GenBank entry lines.
        """
        sequence = ""
        reading = False
        for line in entry_lines:
            if line.startswith('ORIGIN'):
                reading = True
                continue
            elif line.startswith('//'):
                break
            if reading:
                for part in line.split():
                    if part.isdigit():
                        continue
                    sequence += part
        return sequence.upper()

    def find_id(self, entry_lines, identifier_type):
        """
        Finds the identifier (accession or locus) in the GenBank entry lines.
        """
        for line in entry_lines.split("\n"):
            if identifier_type == "accession" and line.startswith("ACCESSION"):
                return line.split()[1]
            elif identifier_type == "locus" and line.startswith("LOCUS"):
                return line.split()[1]
        return None

    def find_organism(self, entry_lines):
        """
        Finds the organism name in the GenBank entry lines.
        """
        for line in entry_lines.split("\n"):
            if line.strip().startswith("ORGANISM"):
                return ' '.join(line.split()[1:])
        return "Unknown"

    def convert(self, ctx: ConverterContext):
        """
        Converts GenBank format to FASTA format.
        """
        genbank_file = ctx.input.read()  # Read the entire GenBank file
        entry_lines = genbank_file.split("//\n")  # Split entries by "//"
        for entry in entry_lines:
            if not entry.strip():
                continue
            try:
                identifier = self.find_id(entry, "accession")
                organism = self.find_organism(entry)
                sequence = self.extract_nucleotide_sequence(entry.split('\n'))
                ctx.write(f">{organism}-{identifier}\n{sequence}\n")  # Write to context in FASTA format
            except Exception as e:
                ctx.log_error(f"Error processing entry: {e}")

class FastaToGb:
    IN_EXTENSION = 'fasta'
    OUT_EXTENSION = 'gbk'

    def __init__(self, identifier_type='locus'):
        self.identifier_type = identifier_type

    def parse_fasta(self, ctx: ConverterContext) -> list:
        """
        Parses FASTA formatted data from the context.
        """
        sequences = []
        header = None
        sequence = ""
        for line in ctx.input:
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

    def generate_genbank(self, header: str, sequence: str) -> str:
        """
        Generates a GenBank formatted entry from FASTA header and sequence.
        """
        id_parts = header.split('-')
        if self.identifier_type == "accession":
            identifier = id_parts[-1]
            organism = " ".join(id_parts[:-1])
        else:
            identifier = id_parts[0]
            organism = " ".join(id_parts[1:])
        
        # If identifier or organism is missing, provide defaults
        if not identifier:
            identifier = "UNKNOWN"
        if not organism:
            organism = "Unknown"
        
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
        # Add the nucleotide sequence in GenBank format with line numbers
        for i in range(0, len(sequence), 60):
            chunk = sequence[i:i+60]
            chunk_str = ' '.join([chunk[j:j+10] for j in range(0, len(chunk), 10)])
            genbank_entry += f"        {i+1:9} {chunk_str}\n"
        genbank_entry += "//\n"
        return genbank_entry

    def convert(self, ctx: ConverterContext):
        """
        Converts FASTA format to GenBank format.
        """
        sequences = self.parse_fasta(ctx)  # Parse sequences from FASTA format
        for header, sequence in sequences:
            try:
                genbank_entry = self.generate_genbank(header, sequence)
                ctx.write(genbank_entry)  # Write to context in GenBank format
            except Exception as e:
                ctx.log_error(f"Error processing entry: {e}")
