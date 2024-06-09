#!/usr/bin/env python3

import converters as conv

import os.path as path
import os

import io
import time


def log_strftime(t : time.struct_time):
    time_str = time.strftime("%H:%M:%S", t)
    return time_str


def log_info(msg : str):
    time_str = time.strftime("%H:%M:%S", time.localtime())
    print(f'[{time_str}][INFO] {msg}')


def log_error(msg : str):
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    time_str = time.strftime("%H:%M:%S",  time.localtime())
    print(f'{FAIL}[{time_str}][ERROR] {msg}{ENDC}')


def print_logs(file_name : str, ctx : conv.ConverterContext, verbose : bool):
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    # print errors
    for entry in ctx.errors:
        location = f'{file_name}:{entry.line}'
        time_str = log_strftime(entry.time)

        err_str = f'[{time_str}][ERROR][{location}] {entry.msg}'
        print(f'{FAIL}{err_str}{ENDC}')

    # print warnings
    if verbose:
        for entry in ctx.warnings:
            location = f'{file_name}:{entry.line}'
            time_str = log_strftime(entry.time)

            warn_str = f'[{time_str}][WARNING][{location}] {entry.msg}'     
            print(f'{WARNING}{warn_str}{ENDC}')


def convert_name(in_filename : str, output_dir : str, format : str):
    os.makedirs(output_dir, exist_ok=True)
    format = '.' + format.strip('.')
    out_filepath = os.path.join(output_dir, path.splitext(path.basename(in_filename))[0] + format)

    return out_filepath


def convert_single_file(in_filepath : str, output_dir: str, format: str, verbose: bool):
    
    out_filepath = convert_name(in_filepath, output_dir, format)

    if verbose:
        log_info(f'Converting {in_filepath}->{out_filepath}')

    out_buffer = io.StringIO()
    
    converter_key = conv.registry.getKey(in_filepath, out_filepath)
    
    converters = conv.registry.initRegistry()
    converter_class = converters.get(converter_key)
    if converter_class is None:
        log_error(f'Failed to find converter for key for {in_filepath} -> {out_filepath}')
        return
    
    converter_obj = converter_class()
    with open(in_filepath, 'r') as f:
        ctx = conv.ConverterContext(out_buffer, f)
        converter_obj.convert(ctx)

    print_logs(in_filepath, ctx, verbose)

    if len(ctx.errors) > 0:
        log_error(f'Failed with {len(ctx.errors)} error')
        return
        
    out_buffer.seek(0)
    
    with open(out_filepath, 'w') as f:
        f.write(out_buffer.read())

def convert_directory(input_dir : str, output_dir : str, out_extension : str, exclude : str, verbose: bool):
    if path.isdir(input_dir) == False:
        log_error('Input is not a directory')
        return
    
    os.makedirs(output_dir, exist_ok=True)

    # pick converter
    conv_registry = conv.registry.initRegistry()

    files = os.listdir(input_dir)

    for file_name in files:
        out_path = os.path.join(output_dir, path.splitext(path.basename(file_name))[0] + out_extension)
        conv_key = conv.registry.getKey(file_name, out_path)
        converter_class = conv_registry[conv_key]
        
        if converter_class is None:
            log_error(f'Failed to find {out_extension} converter for {file_name}')

        input_path = path.join(input_dir, file_name)

        converter_instance = converter_class()
        
        with open(input_path, 'r') as f:
            ctx = conv.ConverterContext(io.StringIO(), f)
            converter_instance.convert(ctx)
        
        print_logs(input_path, ctx, verbose)
        if len(ctx.errors) > 0:
            continue # don't save to output file

        ctx.output.seek(0)

        with open(out_path, 'w') as f:
            f.write(ctx.output.read())
        


def main():
    parser = conv.cl_parser.Parser()
    parser.run()

    if not path.exists(parser.input):
        log_error(f'The input: {parser.input} does not exist or there is no permission to execute os.stat().')
    
    if path.isdir(parser.input):
        convert_directory(parser.input, parser.output, parser.format, parser.exclude, parser.verbose)
        
    elif path.isfile(parser.input):
        convert_single_file(parser.input, parser.output, parser.format, parser.verbose)

    else:
        log_error(f'The input: {parser.input} is neither a file nor a directory.')
    

if __name__ == '__main__':
    main()
