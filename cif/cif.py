# -*- coding: utf-8 -*-
"""
Created on 01.11.2017

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <daniel.kratzert@uni-freiburg.de> wrote this file. As long as you retain this
* notice you can do whatever you want with this stuff. If we meet some day, and
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: daniel
"""

with open('../test-data/p-1_a.cif', 'r') as f:
    ciflines = f.readlines()


"""
T_SP = transition_space
T_DATA = transition_data_tag
T_COMMENT = transition_comment_line
T_NEWLINE = transition_newline
T_NEWL_or_SP = transition_newline_or_space
T_TAG_or_LOOP = transition_tag_or_loop
T_EOF = transition_end_of_file
T_SEMICOL_S = transition_semicolon_field_start
T_SEMICOL_E = transition_semicolon_field_end
T_T_or_L = transition_tag_or_loop
T_TAG = transiton_tag_not_loop
T_NOTEOL = transition_not_eol_plus_ordchar_or_semicol
T_EOL = transition_eol_plus_ordchar
T_SEMI_DATA = transition_semicolon_field_data
T_SING_ST = transition_single_quoted_start
T_SING_END = transition_single_quoted_end 
T_DOUBL_ST = transition_double_quoted_start 
T_DOUBL_END = transition_double_quoted_end  

S_START = "SATE: Start of file"
S_DATABLOCK = "SATE: Datablock begins"
S_COMMENT = "STATE: A comment line"
S_WHITESP = "STATE: Whitespace"
S_DATAITEMS = "STATE: Dataitems of Datablock"
S_TAG = "STATE: A tag from a dataitem"
S_VALUE = "STATE: A value of a dataitem"
S_UNQUOTED_STRING = "STATE: A value as unquoted string"
S_SINGLEQUOTED_STRING = "STATE: A value as singlequoted string"
S_DOUBLEQUOTED_STRING = "STATE: A value as doublequoted string"

"""

FSM_MAP = (
    #  {'src':, 'dst':, 'condition':, 'callback': },
    {'src': S_NEW_GROUP,
        'dst': S_PRE,
        'condition': "[A-Za-z|+|-|\d]",
        'callback': T_APPEND_CHAR_PRE}  # 1
)

if __name__ == '__main__':
    pass
    #import doctest
    #failed, attempted = doctest.testmod()  # verbose=True)
    #if failed == 0:
    #    print('passed all {} tests!'.format(attempted))