from converters.baseConverter import ConverterContext

class EmblToFasta:
    IN_EXTENSION = '.embl'
    OUT_EXTENSION = '.fasta'

    def convert(self, ctx: ConverterContext):
        """
        Convert an EMBL file to FASTA format.
        """
        accession, version, mol_type, description, organism_name, nucleobases = self.extract_data(ctx)
        fasta_output = self.format_fasta(accession, version, mol_type, description, organism_name, nucleobases)
        ctx.write(fasta_output)

    def extract_data(self, ctx: ConverterContext):
        """
        Extract relevant data from EMBL file lines.
        """
        accession = ""
        version = ""
        mol_type = ""
        description = ""
        organism_name = ""
        nucleobases = ""
        in_sequence = False

        for line in ctx:
            if line.startswith("AC"):
                accession = self.extract_accession(line)
            elif line.startswith("ID"):
                version, mol_type = self.extract_version_and_mol_type(line)
            elif line.startswith("DE"):
                description = self.extract_description(line)
            elif line.startswith("OS"):
                organism_name = self.extract_organism_name(line)
            elif line.startswith("SQ"):
                in_sequence = True
            elif in_sequence:
                if line.startswith("//"):
                    in_sequence = False
                else:
                    nucleobases += self.extract_nucleobases(line)
        
        return accession, version, mol_type, description, organism_name, nucleobases

    def extract_accession(self, line):
        """
        Extract accession number from the line.
        """
        return line.strip().split()[1].rstrip(';')

    def extract_version_and_mol_type(self, line):
        """
        Extract version and molecule type from the line.
        """
        parts = line.strip().split(";")
        version = parts[1].strip().split()[1]
        mol_type = parts[3].strip().rstrip(';')
        return version, mol_type

    def extract_description(self, line):
        """
        Extract description from the line and remove trailing dot if present.
        """
        return " ".join(line.strip().split()[1:]).rstrip('.')

    def extract_organism_name(self, line):
        """
        Extract organism name from the line.
        """
        return " ".join(line.strip().split()[1:])

    def extract_nucleobases(self, line):
        """
        Extract nucleobases from the sequence lines.
        """
        return ''.join([n for n in line if n.isalpha()]).upper()

    def format_fasta(self, accession, version, mol_type, description, organism_name, nucleobases):
        """
        Format the extracted data into FASTA format.
        """
        header = f">{accession}.{version} | {description} | {organism_name} | {mol_type}\n"
        sequence = "\n".join(nucleobases[i:i+60] for i in range(0, len(nucleobases), 60))
        return header + sequence


class FastaToEmbl:
    IN_EXTENSION = '.fasta'
    OUT_EXTENSION = '.embl'

    def convert(self, ctx: ConverterContext):
        header = ''
        sequence = ''
        Description = ''
        ID = ''
        Accession = ''
        SV = ''
        organism_name = '.'
        gene_name = ''

        for line in ctx:
            if line.startswith('>'):
                Description = line.split(">")[1].strip()
                ID = line[1:].strip().split()[0]
                if '.' in ID:
                    Accession, version = ID.split(".")
                    SV = f"SV {version}"
                else:
                    Accession = ID
                start_index = line.find('[')
                if start_index != -1:
                    end_index = line.find(']')
                    if end_index != -1:
                        organism_name = line[start_index + 1:end_index]
                        gene_name = line[1:].strip().split()[1] if len(line[1:].strip().split()) > 1 else ''
            else:
                sequence += line.strip()

        length = len(sequence)
        a_count = sequence.count('A')
        c_count = sequence.count('C')
        g_count = sequence.count('G')
        t_count = sequence.count('T')
        other_count = len(sequence) - (a_count + c_count + g_count + t_count)
        sequence = sequence.lower()

        formatted_sequence = ''
        total_bp = 0

        for i in range(0, len(sequence), 60):
            line = sequence[i:i+60]
            grouped_line = ' '.join([line[j:j+10] for j in range(0, len(line), 10)])
            total_bp += len(line)
            line_length = len(grouped_line)
            formatted_sequence += f"     {grouped_line}{' ' * (70 - line_length)}{total_bp:>5}\n"

        embl_output = f"ID   {Accession}; {SV}; ; DNA; ; UNC; {length} BP.\nXX\n"
        embl_output += f"AC   {Accession};\nXX\n"

        def split_long_lines(prefix, text):
            lines = []
            current_line = prefix
            for word in text.split():
                if len(current_line) + len(word) + 1 <= 80:
                    current_line += f" {word}"
                else:
                    lines.append(current_line)
                    current_line = f"{prefix} {word}"
            if current_line.strip():
                lines.append(current_line)
            return lines

        for de_line in split_long_lines("DE  ", Description):
            embl_output += f"{de_line}\n"

        embl_output += "XX\n"
        for os_line in split_long_lines("OS  ", organism_name):
            embl_output += f"{os_line}\n"

        embl_output += "OC   .\nXX\n"
        embl_output += "FH   Key             Location/Qualifiers\nFH\n"

        embl_output += f"FT   source          1..{length}\n"
        for ft_line in split_long_lines("FT                   /organism=\"", organism_name):
            embl_output += f"{ft_line}\"\n"
        embl_output += "FT                   /mol_type=\"DNA\"\nXX\n"

        embl_output += f"SQ   Sequence {len(sequence)} BP; {a_count} A; {c_count} C; {g_count} G; {t_count} T; {other_count} other;\n"
        embl_output += formatted_sequence
        embl_output += "//\n"

        ctx.write(embl_output)

