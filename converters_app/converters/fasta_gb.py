from converters.baseConverter import ConverterContext
import time

from converters.baseConverter import ConverterContext
import time

class GbToFasta:
    IN_EXTENSION = '.gb'
    OUT_EXTENSION = '.fasta'

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
        if not entry_lines:
            ctx.log_error("No entries found in the GenBank file.")

        for entry in entry_lines:
            if not entry.strip():
                continue
            try:
                identifier = self.find_id(entry, "accession")
                if not identifier:
                    ctx.log_warning("No identifier found in the entry.")
                    identifier = "Unknown"

                organism = self.find_organism(entry)
                if organism == "Unknown":
                    ctx.log_warning(f"No organism name found for entry with identifier {identifier}.")

                sequence = self.extract_nucleotide_sequence(entry.split('\n'))
                if not sequence:
                    ctx.log_warning(f"No sequence found for entry with identifier {identifier}.")
                else:
                    ctx.write(f">{organism}-{identifier}\n{sequence}\n")  # Write to context in FASTA format

            except Exception as e:
                ctx.log_error(f"Error processing entry with identifier {identifier}: {e}")

class FastaToGb:
    IN_EXTENSION = '.fasta'
    OUT_EXTENSION = '.gb'

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

    def generate_genbank(self, ctx: ConverterContext, header: str, sequence: str) -> str:
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
            ctx.log_warning(f"Missing identifier in header: {header}. Using 'UNKNOWN'.")
            identifier = "UNKNOWN"
        if not organism:
            ctx.log_warning(f"Missing organism name in header: {header}. Using 'Unknown'.")
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
        if not sequences:
            ctx.log_warning("No sequences found in the FASTA file.")

        for header, sequence in sequences:
            if not header:
                ctx.log_warning("Empty header found. Skipping this entry.")
                continue
            if not sequence:
                ctx.log_warning(f"Empty sequence found for header: {header}. Skipping this entry.")
                continue
            try:
                genbank_entry = self.generate_genbank(ctx, header, sequence)
                ctx.write(genbank_entry)  # Write to context in GenBank format
            except Exception as e:
                ctx.log_error(f"Error processing entry with header {header}: {e}")

