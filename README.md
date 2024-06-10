# SeCon
SeCon is a nucleic acid sequence files batch converter. Able to convert both single files and batches of diverse sequence files.

# Supported formats
- FASTA
- GenBank
- EMBL

SeCon provides conversions:  
FASTA -> GenBank,  
GenBank -> FASTA,  
FASTA -> EMBL,  
EMBL -> FASTA,  
GenBank -> EMBL  
EMBL -> GenBank.  

# Requirements
Python 3.12.2

# Usage
```bash
secon.py [-h] [-o OUTPUT] [-e EXCLUDE] [-v] input format

positional arguments:
  input                 path to input file/folder
  format                .ext (fasta/embl/gb)

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        path to output folder
  -e EXCLUDE, --exclude EXCLUDE
                        pattern to be excluded from conversion (only for folders)
  -v, --verbose         print all logs
```

The command-line interface was designed to be flexible and intuitive. The input folder may contain files of various formats. The output folder and file names are automatically generated, unless specified with -o. Extension may be given with or without a dot. Files to be excluded (-e) from batch convertersion may be specified with the Unix shell-style pattern.

# Examples
Single file
```bash
secon.py ./input/gb/sequence.gb embl -o my_output -v
```

Batch 
```bash
secon.py ./input/embl gb -o my_output -e *.1* -v 
```

# Architecture



# Want to contribute?

