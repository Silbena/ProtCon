from converters.baseConverter import ConverterContext

class EmblToFasta:
    IN_EXTENSION = ''
    OUT_EXTENSION = ''

    def convert(self, ctx : ConverterContext):
        for line in ctx:



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

