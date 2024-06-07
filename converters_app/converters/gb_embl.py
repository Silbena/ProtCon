from converters.baseConverter import ConverterContext

class GbToEmbl:
    IN_EXTENSION = '.gb'
    OUT_EXTENSION = '.embl'

    # additional function to convert locus lines 
    def locus_converter(locus: str) -> str:
        l = locus.split()
        out = f"ID   {l[0]}; {l[4]}; {l[5]}; {l[1]} BP."
        return f'{out}\nXX\n'

    # additional function to convert definition lines 
    def definition_converter(definition: str) -> str:
        out = ''
        d = definition.split('\n')
        for el in range(len(d)):
            out += f'DE   {d[el].strip()}\n'
        return f'{out}XX\n'

    # additional function to convert accesion lines 
    def accesion_converter(accesion: str) -> str:
        return f'AC   {accesion.strip()};\nXX\n'

    # additional function to convert organism lines 
    def organism_converter(organism: str) -> str:
        out = ''
        o = organism.split("\n")
        for el in o:
            out += f"OS   {el.strip()}\n"
        return f'{out}XX\n'

    # additional function to convert source lines 
    def source_converter(source: str) -> str:
        out = ''
        r = source.split('REFERENCE')   # split to have list of references
        for ref in r[1:]:       
            reference_list = []

            # find information about reference, authors, tittle and journal
            reference = ref.split("AUTHORS")[0].strip().split()                 # What's the purpose of the last split()?   
            authors = ref.split("AUTHORS")[1].strip().split("TITLE")[0].strip()
            title = ref.split("TITLE")[1].strip().split("JOURNAL")[0].strip()
            journal = ref.split("JOURNAL")[1].strip()
            reference_list.append((reference, authors, title, journal)) # adding information to the list

            for reference in reference_list:        # converting specific parts of information to embl format
                rl_lines = reference[3].strip().split("\n")
                rl_string = '\n'.join([f'RL   {line.strip()}' for line in rl_lines[:]])
                rt_lines = reference[2].strip().split("\n")
                rt_string = '\n'.join([f'RT   {line.strip()}' for line in rt_lines[:]])

                # compose everything into one string
                out += f'RN   [{reference[0][0].strip()}]\nRP   {reference[0][2].strip()}-{reference[0][4].strip().split(")")[0]}\n' \
                    f'RA   {reference[1].strip()};\n{rt_string}\n' \
                    f'{rl_string}\nXX\n'                                         # Simplify?
        return out

    # additional function to convert features lines
    def features_converter(features: str) -> str:
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
    def origin_converter(origin) -> str:
        bp_dict = {"A": 0, "C": 0, "G": 0, "T": 0}      # creating the bases dictionary
        last_num = 0
        w = ''

        # splitting the sequence and checking if we have number or part of the sequence
        for element in origin.split()[1:]:
            if element.isalpha():       # for sequences adding them to w string
                w += element + " "
                for aa in element:
                    if aa.upper() not in bp_dict.keys():    # checking if bases are valid
                        return 'Error'
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


    # main function converting the file
    def convert(self, ctx : ConverterContext):    
         
        # dwa moliwe kody zeby miec zawartość pliku w f... na wypadek jeśli źle zrozumiałam działanie funkcji :) 
        # mozna poprawić


        # f = ''.join(ctx)
        # output = []

        with open('assistant_file.txt', 'w') as file:                       # To be discared
            for line in ctx:
                file.write(line)
        
        with open('assistant_file.txt', 'r') as file:                       # To be discared
            f = file.read()
            output = []

        # You can iterate over ctx just like you did above.
        # There is no need to make any assistant file, but I understand it is just for testing.
        # Consider using startswith(), which may simplify the code below and make your life much easier.

        # splitting the parts
            locus = f.split("LOCUS")[1].strip().split("DEFINITION")[0].strip()      
            definition = f.split("DEFINITION")[1].strip().split("ACCESSION")[0].strip()
            accesion = f.split("ACCESSION")[1].strip().split("VERSION")[0].strip()
            organism = f.split("ORGANISM")[1].strip().split("REFERENCE")[0].strip()
            source = f.split("ORGANISM")[1].strip().split("FEATURES")[0].strip()
            features = f.split("FEATURES")[1].strip().split("ORIGIN")[0].strip()
            origin = f.split("ORIGIN")[1].strip().split("//")[0].strip()

        # adding converted parts to the list
            output.append(self.locus_converter(locus))
            output.append(self.accesion_converter(accesion))
            output.append(self.definition_converter(definition))
            output.append(self.organism_converter(organism))
            output.append(self.source_converter(source))
            output.append(self.features_converter(features))
            output.append(self.origin_converter(origin))

        # writing the content of the list in the output
        for part in output:
            ctx.write(part)   # Not shure, if that's what intended,
                              # but it will write each element of the "output" list as a line of ctx.







class EmblToGb:
    IN_EXTENSION = '.embl'
    OUT_EXTENSION = '.gb'

    def convert(self, ctx : ConverterContext):
        for line in ctx:
            pass
