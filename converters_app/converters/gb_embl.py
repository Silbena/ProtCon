from converters.baseConverter import ConverterContext
import re

class GbToEmbl:
    IN_EXTENSION = '.gb'
    OUT_EXTENSION = '.embl'

    # additional function to convert locus lines 
    def locus_converter(self, locus: str) -> str | bool:

        if not locus:
            return False
        
        locus_str = locus.split('LOCUS')[1]
        l = locus_str.split()
        if len(l) < 6:
            print('Error. Invalid format.')
        out = f"ID   {l[0]}; {l[4]}; {l[3]}; {l[5]}; {l[1]} BP."
        return f'{out}\nXX\n'


    # additional function to convert definition lines 
    def definition_converter(self, definition: str) -> str:

        if not definition:
            return False
        
        definition_str = definition.split('DEFINITION')[1]
        out = ''
        d = definition_str.split('\n')
        for el in range(len(d)):
            out += f'DE   {d[el].strip()}\n'
        return f'{out}XX\n'


    # additional function to convert accesion lines 
    def accesion_converter(self, accesion: str) -> str:

        if not accesion:
            return False
        
        accesion_str = accesion.split('ACCESSION')[1].split('\n')[0].strip()
        return f'AC   {accesion_str.strip()};\nXX\n'
    

    def keyword_converter(self, keyword: str) -> str:
        keyword_str = keyword.split('KEYWORDS')[1].strip()
        return f'KW    {keyword_str}\nXX\n'


    # additional function to convert organism lines 
    def organism_converter(self, organism: str) -> str:

        if not organism:
            return False

        out = ''
        o = organism.split("\n")
        if len(o) < 1:
            return False 
        out += f"OS   {o[0].strip()}\n" # for the first line its 'OS' and for the other 'OC'
        for el in o[1:]:
            out += f"OC   {el.strip()}\n"
        return f'{out}XX\n'


    # additional function to convert source lines 
    def source_converter(self, source: str) -> str:

        if not source:
            return False
        
        out = ''
        r = source.split('REFERENCE')   # split to have list of references
        if len(r) < 2:
            return False 
        for ref in r[1:]:       
            reference_list = []

            # find information about reference, authors, tittle and journal
            if 'AUTHORS' not in ref:
                reference = ref.split('\n')[0].strip().split()
                authors = 'unknown'
            else:
                reference = ref.split("AUTHORS")[0].strip().split()
                authors = ref.split("AUTHORS")[1].strip().split("TITLE")[0].strip()

            if 'TITLE' not in ref:
                title = 'unknown'
            else:
                title = ref.split("TITLE")[1].strip().split("JOURNAL")[0].strip()

            if 'JOURNAL'not in ref:
                journal = 'unknown'
            else:
                journal = ref.split("JOURNAL")[1].strip()

            reference_list.append((reference, authors, title, journal)) # adding information to the list

            for reference in reference_list:        # converting specific parts of information to embl format
                if len(reference) < 4:
                    return False 
                rl_lines = reference[3].strip().split("\n")
                rl_string = '\n'.join([f'RL   {line.strip()}' for line in rl_lines[:]])
                rt_lines = reference[2].strip().split("\n")
                rt_string = '\n'.join([f'RT   {line.strip()}' for line in rt_lines[:]])

                # compose everything into one string
                if len (reference[0]) < 3:
                    out += f'RN   [{reference[0][0].strip()}]\nRP\n' \
                       f'RA   {reference[1].strip()};\n{rt_string}\n' \
                       f'{rl_string}\nXX\n'
                else:
                    out += f'RN   [{reference[0][0].strip()}]\nRP   {reference[0][2].strip()}-{reference[0][4].strip().split(")")[0]}\n' \
                        f'RA   {reference[1].strip()};\n{rt_string}\n' \
                        f'{rl_string}\nXX\n'                               
        return out


    # additional function to convert features lines
    def features_converter(self, features: str) -> str:
        f = features.split('\n')        # split for every new line
        out = 'FH   Key             Location/Qualifiers\nFH\n'
        for line in f[1:]:
            if line.strip():
                if "/" in line:         # if we hava line starts with '/' it means additional info to some feature, we dont want to split lines then
                    parts = line
                else:                   # it its line with feature name we split it
                    parts = line.split(maxsplit=1)
                if len(parts) == 2:     # checking what type of a line is it (if has 2 parts its line with a feature name)
                    key, value = parts
                    out += f'FT   {key.ljust(16)}{value}\n'     # different conversion for line with a feature and lines with just additional info
                else:
                    out += f'FT{" " * 19}{line.strip()}\n'
        return out +'XX\n'


    # additional function to convert origin lines
    def origin_converter(self, origin) -> str:
        
        if not origin:
            return False

        origin = origin.split('//')[0]
        bp_dict = {"A": 0, "C": 0, "G": 0, "T": 0}      # creating the bases dictionary
        last_num = 0
        w = ''

        if len(origin.split()) < 1:
            return False 
        # splitting the sequence and checking if we have number or part of the sequence
        for element in origin.split()[2:]:
            if element.isalpha():       # for sequences adding them to w string
                w += element + " "
                for aa in element:
                    if aa.upper() not in bp_dict.keys():    # checking if bases are valid
                        return False 
                    else:
                        bp_dict[aa.upper()] += 1            # counting the bases in the dictionary
            else:
                last_num = int(element)             # looking for last number
                w += str(last_num - 1) + "\n    "   # for numbers adding them to w string (-1 because of the format difference)
        
        # counting the last sequence (in the last line)
        last_seq = origin.split()[origin.split().index(str(last_num)):]
        last_seq_number = len(last_seq[1:-1]) * 10 + len(last_seq[-1].strip()) # each part has 10 bases + len the last part

        aa_count = last_seq_number + last_num - 1   # -1 because difference in formating between gb and ambl
        w += " " * (66-last_seq_number- len(last_seq[1:-1])-1) + str(aa_count) +  "\n"  #  converting the last row to have number in the same spot as others (substracting from 66 bc we have max 60 bases in sequence line + 6 spaces)

        # creating the converted output
        bp_dict_str = ', '.join(f'{base}: {number}' for base, number in bp_dict.items())
        w_title = f'SQ  Sequence {aa_count} BP; {bp_dict_str} \n    '
        out = w_title + w + '\n//'
        return out


    def extract_sections(self, f) -> list:
        sections = ['LOCUS', 'DEFINITION', 'ACCESSION', 'KEYWORDS', 'SOURCE', 'ORGANISM',
                    'FEATURES', 'ORIGIN']

        # making pattern that matches any of the sections
        pattern = re.compile(r'^(LOCUS|DEFINITION|ACCESSION|KEYWORDS|SOURCE|ORGANISM|FEATURES|ORIGIN)', re.MULTILINE)

        # spliting data for each section
        section_positions = [match.start() for match in pattern.finditer(f)]
        section_positions.append(len(f))

        # adding the sections
        sections_data = [f[section_positions[i]:section_positions[i + 1]] for i in range(len(section_positions) - 1)]

        # filter the data that are not the part of the section
        filtered_sections = [section for section in sections_data if any(sec in section for sec in sections)]
        return filtered_sections
        

    # main function converting the file
    def convert(self, ctx : ConverterContext):    
        f = ''.join(ctx.read_lines())

        word_list = ['LOCUS', 'DEFINITION', 'ACCESSION', 'KEYWORDS', 'SOURCE', 'ORGANISM',
                     'REFERENCE', 'FEATURES', 'ORIGIN']
        
        for word in word_list:
            if word not in f:
                ctx.log_error('Invalid format.')
        

        output = []

        section_list = self.extract_sections(f)
        for element in section_list:
            if element.startswith('LOCUS'):
                locus = element.strip()
            if element.startswith('DEFINITION'):
                definition = element.strip()
            if element.startswith('ACCESSION'):
                accesion = element.strip()
            if element.startswith('KEYWORDS'):
                keyword = element.strip()
            if element.startswith('SOURCE'):
                source = element.split('ORGANISM', maxsplit=1)[1].strip()
                organism = element.split('ORGANISM', maxsplit=1)[1].strip().split('.')[0].strip()
            if element.startswith('FEATURES'):
                features = element.strip()
            if element.startswith('ORIGIN'):
                origin = element.strip()

        # converting
        conv_locus = self.locus_converter(locus) 
        conv_accesion = self.accesion_converter(accesion) 
        conv_definition = self.definition_converter(definition)
        conv_keyword = self.keyword_converter(keyword)
        conv_organism = self.organism_converter(organism)
        conv_source = self.source_converter(source)
        conv_features = self.features_converter(features)
        conv_origin = self.origin_converter(origin)

        # writing and logging the errors
        if conv_locus:
            ctx.write(conv_locus) 
        else:
            ctx.log_error('Invalid format.')

        if conv_accesion:
            ctx.write(conv_accesion) 
        else:
            ctx.log_error('Invalid format.')

        if conv_definition:
            ctx.write(conv_definition) 
        else:
            ctx.log_error('Invalid format.')

        if conv_keyword:
            ctx.write(conv_keyword) 
        else:
            ctx.log_error('Invalid format.')

        if conv_organism:
            ctx.write(conv_organism) 
        else:
            ctx.log_error('Invalid format.')

        if conv_source:
            ctx.write(conv_source) 
        else:
            ctx.log_error('Invalid format.')

        if conv_features:
            ctx.write(conv_features) 
        else:
            ctx.log_error('Invalid format.')
        
        if conv_origin:
            ctx.write(conv_origin) 
        else:
            ctx.log_error('Invalid format.')



class EmblToGb:
    IN_EXTENSION = '.embl'
    OUT_EXTENSION = '.gb'

    # additional function to convert locus lines 
    def locus_converter_embl(self, locus, accession):

        if not locus:
            return False
        
        parts = locus.split(';')
        if len(parts) < 5:
            return False 
        return f"LOCUS       {accession.strip().split('AC')[1].strip()} {parts[-1].split(' ')[1]} bp   {parts[1]}   {parts[2]}   {parts[3]}\n"
    
    # additional function to convert definition lines 
    def definition_converter_embl(self, definition: str) -> str:

        if not definition:
            return False
        
        lines = definition.split('\n')
        out = "DEFINITION  "
        for line in lines:          # for every line remove te 'DE' and connect the output string 
            e = line.strip().split('DE')
            out += "".join(el.strip() for el in e)
        return f"{out}\n"

    # additional function to convert accession line
    def accession_converter_embl(self, accession: str) -> str:

        if not accession:
            return False
        
        return f"ACCESSION   {accession.strip().split('AC')[1].strip()}\nVERSION\n" # the version output is empty as we dont have information about the version in embl format

    # additional function to convert keyword lines 
    def keyword_converter_embl(self, keyword: str) -> str:
        if len(keyword.split("KW")) < 2:
            return f'KEYWORDS\n'
        return f'KEYWORDS    {keyword.split("KW")[1].strip()}\n'    # keyword may also be empty, depending of the input

    # additional function to convert organism lines 
    def organism_converter_embl(self, organism: str) -> str:

        if not organism:
            return False
        
        lines = organism.split('\n')            # splitting the input by lines and converting it differently
        if len(lines) < 2:
            return False 
        out = f"SOURCE      {lines[1].split('OS')[1].strip()}\n" \
            f"  ORGANISM  {lines[1].split('OS')[1].strip()}\n"
        for line in lines[:]:       # removing the empty lines
            if not line:
                lines.remove(line)
        for line in lines[1:]:      # ignoring the first part because its 'OS'
            e = line.strip().split('OC')    # splitting by the line (it starts with 'OC')
            for el in e:            # ignoring empty lines in output
                if el != '':
                    out += f"{' '*9}{el}\n"
        return f"{out}"

    # additional function to convert reference lines 
    def reference_converter_embl(self, reference: str) -> str:
        out = ""
        is_pubmed = False

        for ref in reference[:]:        # we splitid the lines by XX (which are lines between different references as well so we iterate over each reference)

            if len(ref.split('RN')) < 2 or len(ref.split('RP')) < 2 or len(ref.split('RA')) < 2 or len(ref.split('RT')) < 2:
                    return False 
            # splitting specific lines containing different info (RN - number, RP - base count , RA - autor, RT - tittle, RL - citation)
            rn_part = ref.split('RN')[1].strip().split('\n')[0] 
            rp_part = ref.split('RP')[1].strip()

            # the reference lines may contain pubmed information, but not always, so its necessary to check if there's a RX line witch said info
            if 'RX' in rp_part:     # checking RP part because RX will be in next line
                is_pubmed = True    

                # if there is a pubmed info its necesary to split the RP part there and divide it into RP and pubmed info
                rp_part = rp_part.split('RX')[0].strip()
                p_part = ref.split('RX')[1].strip().split('RA')[0].strip().split(';')[1].split('.')[0].strip()

                # If there's none pubmed info it splits the line on RA - author row (which is the next info)
            elif 'RA' in rp_part:
                rp_part = rp_part.split('RA')[0].strip()

            # then it splits RA info
            ra_part = ref.split('RA')[1].strip().split('RT')[0]

            # title may be written in more than one line so it joins the parts (without 'RT' as long as it finds RL line which is the next info)
            rt_parts = ref.split('RT')
            combined_rt = []
            for part in rt_parts[1:]:       # part 1 is 'RL'
                if 'RL' not in part:
                    combined_rt.append(part.strip())
                else:
                    combined_rt.append(part.split('RL')[0].strip().split(';')[0].strip())
            rt_part = ' '.join(combined_rt)

            # converting the RL line
            rl_part = ref.split('RL')[1].strip().split('XX')[0]


            # combaining the output for each reference
            if len(rp_part.split('-')) < 2:
                out += f"REFERENCE   {rn_part}\n" \
                    f"  AUTHORS   {ra_part.split(';')[0]}\n" \
                    f"  TITLE     {rt_part}\n" \
                    f"  JOURNAL   {rl_part}\n"
            else:
                out += f"REFERENCE   {rn_part} (bases {rp_part.split('-')[0]} to {rp_part.split('-')[1].strip()})\n" \
                    f"  AUTHORS   {ra_part.split(';')[0]}\n"\
                    f"  TITLE     {rt_part}\n"\
                    f"  JOURNAL   {rl_part}\n"
            if is_pubmed:       # if there is pubmed line it is added into the output
                out += f"  PUBMED    {p_part}\n"
            is_pubmed = False      # its changed to false because next reference may don't have a pubmed info
        return f'{out}'

    # additional function to convert features lines 
    def features_converter_embl(self, features: str) -> str:
        lines = features.split('\n')        # splitting info about feature by lines
        out = "FEATURES             Location/Qualifiers\n"
        for line in lines[:]:       # removing empty lines
            if not line:
                lines.remove(line)
        for line in lines[2:]:      # first two lines are containgin unimportant info
            if "/" in line:         # if line starts with '/' it means additional info, no need to split it 
                parts = line
            else:                   # in different scenario its different type of lines and in case there are some additional spaces in the feature information it need to have maxsplit condition
                parts = line.split(maxsplit=2)
            if len(parts) == 3:     # the len of the parts is 3 it means that there it is always a 'FT', feature name and some info 
                f, key, value = parts
                out += f'{" "*5}{key.ljust(16)}{value}\n'   # converted info
            else:                   # in other scenario there are only additional info that starts with '/' or the end on protein sequences, in each case we only want to even the line, no need to convert it further
                out += f'{" " * 21}{line[3:].strip()}\n'
        return f"{out}"

    # additional function to convert origin lines 
    def origin_converter_embl(self, origin: str) -> str:

        if not origin:
            return False
        
        number = 1
        out = f"ORIGIN\n"
        seq_list = origin.split('\n')       # splitting info about origin by lines
        out_list = []
        for el in seq_list:                 # removing the empty parts
            if not el:
                seq_list.remove(el)

        if len(seq_list) < 2:
            return False 
        
        for o in seq_list[1:]:              # igniring first part as its 'SQ' and unimportant info
            # line conversion by adding the number at the beggining, evening the sequence output and removing the number at the end of the line (the split has to be minimum two spaces as there is one space in between each sequence part)
            out_list.append(f"{str(number).rjust(9)} {o.strip().split('  ')[0].strip()}\n")   # every line (number +sequence) is added to the list
            number += 60               # every line has 60 bases
        for seq in out_list[:-1]:      # every line appart from last (its only the number and '//') is added to the output string
            out += seq
        return f"{out}//"


    # main function
    def convert(self, ctx : ConverterContext):
        f = ''.join(ctx.read_lines())
        output = []

        # splitting the parts
        elements = f.split('XX')
        references = []

        for el in elements:
            el.strip()
            if el.startswith('ID'):
                locus = el
            elif el.startswith('AC') or el.startswith('\nAC'):
                accession = el
            elif el.startswith('DE') or el.startswith('\nDE'):
                definition = el
            elif el.startswith('KW') or el.startswith('\nKW'):
                keyword = el
            elif el.startswith('OS') or el.startswith('\nOS'):
                organism = el
            elif el.startswith('RN') or el.startswith('\nRN'):
                references.append(el)
            elif el.startswith('FH') or el.startswith('\nFH'):
                features = el
            elif el.startswith('SQ') or el.startswith('\nSQ'):
                origin = el
        
        # converting
        conv_locus_embl = self.locus_converter_embl(locus, accession) 
        conv_definition_embl = self.definition_converter_embl(definition)
        conv_accesion_embl = self.accession_converter_embl(accession) 
        conv_keyword_embl = self.keyword_converter_embl(keyword)
        conv_organism_embl = self.organism_converter_embl(organism)
        conv_references_embl = self.reference_converter_embl(references)
        conv_features_embl = self.features_converter_embl(features)
        conv_origin_embl = self.origin_converter_embl(origin)

        # writing and logging the errors
        if conv_locus_embl:
            ctx.write(conv_locus_embl) 
        else:
            ctx.log_error('Invalid format.')

        if conv_definition_embl:
            ctx.write(conv_definition_embl) 
        else:
            ctx.log_error('Invalid format.')

        if conv_accesion_embl:
            ctx.write(conv_accesion_embl) 
        else:
            ctx.log_error('Invalid format.')
        
        if conv_keyword_embl:
            ctx.write(conv_keyword_embl) 
        else:
            ctx.log_error('Invalid format.')

        if conv_organism_embl:
            ctx.write(conv_organism_embl) 
        else:
            ctx.log_error('Invalid format.')

        if conv_references_embl:
            ctx.write(conv_references_embl) 
        else:
            ctx.log_error('Invalid format.')

        if conv_features_embl:
            ctx.write(conv_features_embl) 
        else:
            ctx.log_error('Invalid format.')
        
        if conv_origin_embl:
            ctx.write(conv_origin_embl) 
        else:
            ctx.log_error('Invalid format.')
