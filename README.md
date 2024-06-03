# ProtCon
ProtCon is a protein sequence files batch converter.

Able to convert both single files and batches of diverse sequence files.

# Supported formats
- FASTA
- GenBank
- EMBL

# Interface
```python
protcon
-i input_file/folder
-o output_file
--outdir output_folder # to create new folder and save output there
--format(-f) format
--exclude file         # only for folder input
```
