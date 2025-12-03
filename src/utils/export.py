#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ =  'Felipe Fronchetti'
__contact__ = 'fronchetti@usp.br'

import re
import os
import csv
import xlsxwriter
import subprocess

def create_analysis_file(worksheet_name, raw_filepath, spreadsheet_filepath):
    """Exports documentation files as spreadsheet for qualitative analysis.

    This method receives as input filepaths of documentation files written
    in Markdown and transforms the content of these files into a spreadsheet
    for qualitative analysis. Each file will be represented by a worksheet of
    the spreadsheet, and its' content will be divided paragraphs, in such a way
    that a spreadsheet cell will represent a paragraph, and vice-versa.

    Notice that this method uses cmark-gfm, the official Markdown parser of
    GitHub, to transform the content of the documentation files into plaintext.
    If you don't have cmark-gfm installed, please, follow the official tutorial:
    github.com/github/cmark-gfm/blob/master/README.md

    Args:
        raw_filepaths: A dictionary of strings representing the filepaths of the
        documentation files to be used in the spreadsheet.
        spreadsheet_filepath: A string representing the filepath where the 
        spreadsheet will be saved. 
    """
 
    workbook = xlsxwriter.Workbook(spreadsheet_filepath)

    absolute_path = os.path.abspath(raw_filepath)

    # Path to cmark-gfm on macOS (installed via Homebrew)
    cmark_gfm_exe_path = '/opt/homebrew/bin/cmark-gfm'

    if os.path.isfile(cmark_gfm_exe_path):
        plaintext = subprocess.run([cmark_gfm_exe_path, absolute_path, '--to', 'plaintext'], stdout=subprocess.PIPE)
    else:
        print('Please, update the filepath to the `cmark-gfm.exe` file inside the scripts/scraper/export.py file')
        print('If you do not have cmark-gfm installed, please visit their repository and install it: github.com/github/cmark-gfm')
        raise ValueError('The cmark-gfm.exe variable was not defined in scripts/scraper/export.py (Line 38)')

    paragraphs = split_into_paragraphs(plaintext.stdout.decode('utf-8'))

    # Creating the worksheet 

    worksheet = workbook.add_worksheet(worksheet_name)

    # In each worksheet we have eight columns. The first column will be
    # used to store the documentation paragraphs in cells. The second
    # to the eigth column will be used during qualitative analysis to 
    # identify the categories of relevant documentation for newcomers.

    # Set up the width of the worksheet columns

    worksheet.set_column(0, 0, 60)
    worksheet.set_column(1, 7, 25)

    # Set up colors and text properties for each column

    default_format = workbook.add_format({'text_wrap': True})
    CF_format = workbook.add_format({'text_wrap': True, 'bg_color': '#ffd966'})
    CT_format = workbook.add_format({'text_wrap': True, 'bg_color': '#b6d7a8'})
    TC_format = workbook.add_format({'text_wrap': True, 'bg_color': '#d9d2e9'})
    BW_format = workbook.add_format({'text_wrap': True, 'bg_color': '#ea9999'})
    DC_format = workbook.add_format({'text_wrap': True, 'bg_color': '#a2c4c9'})
    SC_format = workbook.add_format({'text_wrap': True, 'bg_color': '#f9cb9c'})

    # Write the categories of relevant information for new contributors in
    # the first line of the spreadsheet, from the second to the eight column.

    worksheet.write(0, 1, 'CF – Contribution flow', CF_format)
    worksheet.write(0, 2, 'CT – Choose a task', CT_format)
    worksheet.write(0, 3, 'TC – Talk to the community', TC_format)
    worksheet.write(0, 4, 'BW – Build local workspace', BW_format)
    worksheet.write(0, 5, 'DC – Deal with the code', DC_format)
    worksheet.write(0, 6, 'SC – Submit the changes', SC_format)

    # Write paragraphs in the first column of the worksheet

    for index, paragraph in enumerate(paragraphs):
        worksheet.write(index + 1, 0, paragraph, default_format)

    workbook.close()

def starts_with_list_marker(line):

    # An ordered list marker is a sequence of 1–9 arabic digits (0-9),
    # followed by either a . character or a ) character. 
    # (The reason for the length limit is that with 10 digits GitHub 
    # start seeing integer overflows in some browsers.)

    if line.startswith(('-','+','*')) or re.match(r"\d{1,9}\..*", line) or re.match(r"\d{1,9}\).*", line):
        return True
    else:
        return False

def split_into_paragraphs(content):
    """Splits the content of a documentation file into paragraphs.

    To organize the content of a documentation file into a spreadsheet, first we
    divide it in paragraphs. We consider as paragraphs "one or more consecutive
    lines of text, separated by one or more blank lines (A blank line is any line
    that looks like a blank line — a line containing nothing but spaces or tabs is
    considered blank)". 

    The only exception are the un/ordered lists, which we consider separately as
    paragraphs. We did it because we noticed that some lists contained a significant
    amount of relevant information per item, and dividing it could help us to 
    increase the number of instances for analysis.

    Args:
        content: A string containing the content of a documentation file, including
            empty spaces, line breaks, etc.
    Returns:
        A list of strings, where each string represents a paragraph of the 
        documentation file.
    References:
        Markdown Syntax, by Jhon Gruber:
            daringfireball.net/projects/markdown/syntax
        GitHub Flavored Markdown Spec:
            github.github.com/gfm
    """

    lines = content.splitlines()
    text = []
    paragraph = []

    for line in lines:
        line = line.strip()

        # If line is empty, create a new paragraph
        if not line:
            if len(paragraph) > 0:
                text.append('\n'.join(paragraph))
                paragraph = []
        # If line is a list item, create a new paragraph:
        elif starts_with_list_marker(line):
            if len(paragraph) > 0:
                text.append('\n'.join(paragraph))
                paragraph = []                
            paragraph.append(line)
        # Else, append line to paragraph
        else:
            paragraph.append(line)
    
    if len(paragraph) > 0:
        text.append('\n'.join(paragraph))
        paragraph = []

    return text

def export_to_repositories_file(information, filepath):
    """Exports information about a repository to a spreadsheet file.

    Args:
        repositories: A dictionary containing information about a repository.
        filepath: A string representing the path where the spreadsheet file will be saved.
    """
    if os.path.isfile(filepath):
        with open(filepath, 'a', errors='replace') as writer:
            print("Exporting {}/{} to `repositories.csv`.".format(information['owner'], information['name']))
            fieldnames = information.keys()
            dict_writer = csv.DictWriter(writer, fieldnames)
            dict_writer.writerow(information)
            writer.close()
    else:
        with open(filepath, 'w', errors='replace') as writer:
            print("Exporting {}/{} to `repositories.csv`.".format(information['owner'], information['name']))
            fieldnames = information.keys()
            dict_writer = csv.DictWriter(writer, fieldnames)
            dict_writer.writeheader()
            dict_writer.writerow(information)
            writer.close()    
