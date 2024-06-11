from converters.baseConverter import ConverterContext

class EmblToFasta:
    IN_EXTENSION = '.embl'
    OUT_EXTENSION = '.fasta'

    def convert(self, ctx: ConverterContext):
        """
        Convert an EMBL file to FASTA format.
        """
        accession = ""
        version = ""
        mol_type = ""
        description = ""
        organism_name = ""
        nucleobases = ""
        in_sequence = False

        try:
            embl_file = ctx.input.read()
            
            if not embl_file.strip():
                ctx.log_error("The input file is empty.")
                return

            lines = embl_file.splitlines()
            in_description = False
            in_organism = False

            for line in lines:
                if line.startswith("AC"):
                    accession = self.extract_accession(line)
                elif line.startswith("ID"):
                    version, mol_type = self.extract_version_and_mol_type(line)
                elif line.startswith("DE"):
                    if description:
                        description += " " + self.extract_description(line)
                    else:
                        description = self.extract_description(line)
                    in_description = True
                    in_organism = False
                elif line.startswith("OS"):
                    if organism_name:
                        organism_name += " " + self.extract_organism_name(line)
                    else:
                        organism_name = self.extract_organism_name(line)
                    in_organism = True
                    in_description = False
                elif line.startswith("SQ"):
                    in_sequence = True
                    in_description = False
                    in_organism = False
                elif in_description and not line.startswith(" "):
                    in_description = False
                elif in_description:
                    description += " " + self.extract_description(line)
                elif in_organism and not line.startswith(" "):
                    in_organism = False
                elif in_organism:
                    organism_name += " " + self.extract_organism_name(line)
                elif in_sequence:
                    if line.startswith("//"):
                        in_sequence = False
                    else:
                        nucleobases += self.extract_nucleobases(line)

            if not accession:
                ctx.log_warning("Accession number not found.")
            if not version:
                ctx.log_warning("Version not found.")
            if not description:
                ctx.log_warning("Description not found.")
            if not organism_name:
                ctx.log_warning("Organism name not found.")
                organism_name = "Organism unknown"
            if not nucleobases:
                ctx.log_error("No sequence found.")

            header = f">{accession}.{version} | {description} | {organism_name} | {mol_type}\n"
            sequence = "\n".join(nucleobases[i:i+60] for i in range(0, len(nucleobases), 60))
            fasta_output = header + sequence
            ctx.write(fasta_output)
        
        except Exception as e:
            ctx.log_error(f"Error processing entry with accession number {accession}: {e}")

    def extract_accession(self, line):
        """
        Extract accession number from the line.
        """
        try:
            return line.strip().split()[1].rstrip(';')
        except IndexError:
            return ""

    def extract_version_and_mol_type(self, line):
        """
        Extract version and molecule type from the line.
        """
        try:
            parts = line.strip().split(";")
            version = parts[1].strip().split()[1]
            mol_type = parts[3].strip().rstrip(';')
            return version, mol_type
        except (IndexError, ValueError):
            return "", ""

    def extract_description(self, line):
        """
        Extract description from the line and remove trailing dot if present.
        """
        try:
            return " ".join(line.strip().split()[1:]).rstrip('.')
        except IndexError:
            return ""

    def extract_organism_name(self, line):
        """
        Extract organism name from the line.
        """
        try:
            return ' '.join(line.strip().split()[1:])
        except IndexError:
            return "Unknown"

    def extract_nucleobases(self, line):
        """
        Extract nucleobases from the sequence lines.
        """
        try:
            return ''.join([n for n in line if n.isalpha()]).upper()
        except Exception:
            return ""


class FastaToEmbl:
    IN_EXTENSION = '.fasta'
    OUT_EXTENSION = '.embl'

    def convert(self, ctx: ConverterContext):
        """
        Convert a FASTA file to EMBL format.
        """
        try:
            header, sequence = self.extract_fasta_data(ctx)
            if not header:
                ctx.log_error("Header not found in the input file.")
                return
            if not sequence:
                ctx.log_error("Sequence data not found in the input file.")
                return

            length = len(sequence)
            if length == 0:
                ctx.log_error("Sequence length is zero.")
                return

            sequence_stats = self.calculate_sequence_stats(sequence, ctx)
            formatted_sequence = self.format_sequence(sequence, ctx)

            Description, Accession, SV, organism_name, gene_name = self.extract_header_info(header, ctx)
            
            if not Accession:
                ctx.log_warning("Accession not found.")
            if not SV:
                ctx.log_warning("Sequence version not found.")
            if not Description:
                ctx.log_warning("Description not found.")
            if organism_name == ".":
                ctx.log_warning("Organism name not found.")

            ctx.write(f"ID   {Accession}; {SV}; ; DNA; ; UNC; {length} BP.\nXX\n")
            ctx.write(f"AC   {Accession};\nXX\n")

            for de_line in self.split_long_lines("DE  ", Description, ctx):
                ctx.write(f"{de_line}\n")

            ctx.write("XX\n")
            for os_line in self.split_long_lines("OS  ", organism_name, ctx):
                ctx.write(f"{os_line}\n")

            ctx.write("OC   .\nXX\n")
            ctx.write("FH   Key             Location/Qualifiers\nFH\n")

            ctx.write(f"FT   source          1..{length}\n")
            ctx.write(f"FT                   /organism=\"{organism_name}\"\n")
            ctx.write("FT                   /mol_type=\"DNA\"\nXX\n")

            a_count, c_count, g_count, t_count, other_count = sequence_stats
            ctx.write(f"SQ   Sequence {len(sequence)} BP; {a_count} A; {c_count} C; {g_count} G; {t_count} T; {other_count} other;\n")
            ctx.write(formatted_sequence)
            ctx.write("//\n")

        except Exception as e:
            ctx.log_error(f"Error processing entry: {e}")

    def extract_fasta_data(self, ctx: ConverterContext):
        """
        Extract header and sequence data from the FASTA file.
        """
        header = ''
        sequence = ''
        try:
            fasta_file = ctx.input.read()

            if not fasta_file.strip():
                ctx.log_error("The input file is empty.")
                return header, sequence

            for line in fasta_file.splitlines():
                if line.startswith('>'):
                    header = line.strip()
                else:
                    sequence += line.strip()
        except Exception as e:
            ctx.log_error(f"Error extracting FASTA data: {e}")
        
        return header, sequence

    def calculate_sequence_stats(self, sequence, ctx: ConverterContext):
        """
        Calculate statistics for the sequence (A, C, G, T, other counts).
        """
        try:
            a_count = sequence.count('A')
            c_count = sequence.count('C')
            g_count = sequence.count('G')
            t_count = sequence.count('T')
            other_count = len(sequence) - (a_count + c_count + g_count + t_count)
            return a_count, c_count, g_count, t_count, other_count
        except Exception as e:
            ctx.log_error(f"Error calculating sequence stats: {e}")
            return 0, 0, 0, 0, 0

    def format_sequence(self, sequence, ctx: ConverterContext):
        """
        Format the sequence into EMBL format with appropriate line breaks and grouping.
        """
        try:
            sequence = sequence.lower()
            formatted_sequence = ''
            total_bp = 0

            for i in range(0, len(sequence), 60):
                line = sequence[i:i+60]
                grouped_line = ' '.join([line[j:j+10] for j in range(0, len(line), 10)])
                total_bp += len(line)
                line_length = len(grouped_line)
                formatted_sequence += f"     {grouped_line}{' ' * (70 - line_length)}{total_bp:>5}\n"

            return formatted_sequence
        except Exception as e:
            ctx.log_error(f"Error formatting sequence: {e}")
            return ""

    def split_long_lines(self, prefix, text, ctx: ConverterContext):
        """
        Split long lines to ensure they do not exceed 80 characters.
        """
        try:
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
        except Exception as e:
            ctx.log_error(f"Error splitting long lines: {e}")
            return []

    def extract_header_info(self, header, ctx: ConverterContext):
        """
        Extract and parse information from the FASTA header.
        """
        try:
            header_parts = header.split(maxsplit=1)
            ID = header_parts[0][1:]  
            Description = header_parts[1].strip().rstrip(".") if len(header_parts) > 1 else ''  
            Accession = ID.split(".")[0] if '.' in ID else ID
            SV = f"SV {ID.split('.')[1]}" if '.' in ID else ''
            start_index = header.find('[')
            if start_index != -1:
                end_index = header.find(']')
                if end_index != -1:
                    organism_name = header[start_index + 1:end_index].rstrip(".")
                    gene_name = header[1:].strip().split()[1] if len(header[1:].strip().split()) > 1 else ''
                else:
                    organism_name = "."
                    gene_name = ''
            else:
                organism_name = "."
                gene_name = ''
            return Description, Accession, SV, organism_name, gene_name
        except Exception as e:
            ctx.log_error(f"Error extracting header info: {e}")
            return "", "", "", ".", ""
