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

"""
Callback functions for the cif file parser.
"""


def transition_comment_line(fsm_obj):
    rule_count = fsm_obj.current_group.rule_count
    fsm_obj.current_group.rules[rule_count - 1].op = fsm_obj.current_line


def transition_space(fsm_obj):
    pass


def transition_data_tag(fsm_obj):
    pass


def transition_newline(fsm_obj):
    pass


def transition_newline_or_space(fsm_obj):
    pass


def transition_end_of_file(fsm_obj):
    pass


def transition_semicolon_field_start(fsm_obj):
    pass


def transition_semicolon_field_end(fsm_obj):
    pass


def transition_tag_or_loop(fsm_obj):
    pass


def transiton_tag_not_loop(fsm_obj):
    pass


def transition_not_eol_plus_ordchar_or_semicol(fsm_obj):
    pass


def transition_eol_plus_ordchar(fsm_obj):
    pass


def transition_semicolon_field_data(fsm_obj):
    pass


def transition_single_quoted_start(fsm_obj):
    pass


def transition_single_quoted_end(fsm_obj):
    pass


def transition_double_quoted_start(fsm_obj):
    pass


def transition_double_quoted_end(fsm_obj):
    pass


T_SP = transition_space
T_DATA = transition_data_tag
T_COMMENT = transition_comment_line
T_NEWLINE = transition_newline
T_NEWL_or_SP = transition_newline_or_space
T_EOF = transition_end_of_file
T_SEMICOL_S = transition_semicolon_field_start
T_SEMICOL_E = transition_semicolon_field_end
T_TAG_or_LOOP = transition_tag_or_loop
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



FSM_MAP = (
    #  {'src':, 'dst':, 'condition':, 'callback': },
    {'src'      : S_DATABLOCK,
     'dst'      : S_WHITESP,
     'condition': "[ \r\n]",
     'callback' : T_TAG_or_LOOP},  # 1
    {'src'      : S_DATABLOCK,
     'dst'      : S_WHITESP,
     'condition': "[ \r\n]",
     'callback' : T_TAG_or_LOOP}  # 2
)


class Rule:
    def __init__(self):
        self.prefix = ""
        self.subject = ""
        self.op = None

    def __repr__(self):
        op = self.op
        if not op:
            op = ''
        return "<Rule: {} {}({})>".format(op, self.prefix, self.subject)


class RuleGroup:
    def __init__(self, parent, level, op):
        self.op = op
        self.parent = parent
        self.level = level
        self.rule_count = 1
        self.rules = [Rule(), ]

    def __repr__(self):
        return "<RuleGroup: {}>".format(self.__dict__)


class Rule_Parse_FSM:

    def __init__(self, input_lines):
        self.input_lines = input_lines
        self.current_state = S_START
        self.group_current_level = 0
        self.current_group = RuleGroup(None, self.group_current_level, None)
        self.current_char = ''

    def run(self):
        for line in self.input_lines:
            if not self.process_next(line):
                print("skip '{}' in {}".format(line, self.current_state))

    def process_next(self, achar):
        self.current_char = achar
        frozen_state = self.current_state
        for transition in FSM_MAP:
            if transition['src'] == frozen_state:
                if self.iterate_re_evaluators(achar, transition):
                    return True
        return False

    def iterate_re_evaluators(self, achar, transition):
        condition = transition['condition_re_compiled']
        if condition.match(achar):
            self.update_state(
                transition['dst'], transition['callback'])
            return True
        return False

    def update_state(self, new_state, callback):
        print("{} -> {} : {}".format(self.current_char,
                                     self.current_state,
                                     new_state))
        self.current_state = new_state
        callback(self)

if __name__ == '__main__':
    pass
    with open('./test-data/p21c.cif', 'r') as f:
        ciflines = f.readlines()
    fsm = Rule_Parse_FSM(ciflines)
    fsm.run()
    print(fsm.current_group)
