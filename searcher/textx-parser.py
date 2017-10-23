from textx.metamodel import metamodel_from_str
from pathlib import Path

grammar = r"""
CIF:
  Comments? WhiteSpace? DataBlock+ WhiteSpace?
;

DATA:
    /[d|D][a|A][t|T][a|A]\_/
;

DataBlockHeading:
    /DATA(NonBlankChar)+/
;

DataBlock:
  DataBlockHeading (WhiteSpace DataItems)*
;


DataItems:
    /TAG WhiteSpace Value | LoopHeader LoopBody/
;


LOOP_:
    '/[l|L][o|O][o|O][p|P]_/'
;

LoopHeader:
    LOOP_/(WhiteSpace+TAG)+/
;

LoopBody:
    /Value (WhiteSpace Value)*/
;


WhiteSpace:
    /(\s|\t|\r|\r\n|\n|TokenizedComments)+/
;

Comments:
    /(\#(AnyPrintChar)*$)+/
;

TokenizedComments:
    /(\s|\t|\r|\r\n|\n)+ Comments/
;

TAG:
    /_(NonBlankChar)+/
;

Value:
    /(\. | \? | Numeric | CharString | TextField)/
;

Numeric:
    / NUMBER+ | NUMBER+ \( UnsignedInteger+ \)/
;

NUMBER:
    /(\+|\-)?\d.?\d?/
;

UnsignedInteger:
    /\d+/
;

CharString:
    /UnquotedString | SingleQuotedString | DoubleQuotedString/
;

UnquotedString:
    /OrdinaryChar (NonBlankChar)*/
;

NonBlankChar:
    /OrdinaryChar | \" | \# | \' /
;

SingleQuotedString:
    / \' AnyPrintChar* \' WhiteSpace /
;

DoubleQuotedString:
    /\"(\S)*\"\s/
;

TextField:
    /SemiColonTextField/
;

eol:
    /\n|\r|\r\n/
;

SemiColonTextField:
    /eol \; (AnyPrintChar)* eol ((TextLeadChar (AnyPrintChar)*)? eol)* \;/
;

OrdinaryChar:
    /( \! | \% | \& | \( | \) | \* | \+ | \, | \- | \. | \/ | \: | \< | \= | \> 
    | \? | \@ | \\ | \^ | \` | \{ | \| | \} | \~ |
    0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
    A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P | Q | R | S | T | U | V | W | X | Y | Z |
    a | b | c | d | e | f | g | h | i | j | k | l | m | n | o | p | q | r | s | t | u | v | w | x | y | z |)?/
;

TextLeadChar:
    / OrdinaryChar | \" | \# | \$ | \' | \_ | \s | \t | \[ | \] /
;

AnyPrintChar:
    / OrdinaryChar | \" | \# | \$ | \' | \_ | \s | \; | \[ | \] /
;

"""



if __name__ == '__main__':
    mm = metamodel_from_str(grammar, skipws=False)

    # Meta-model knows how to parse and instantiate models.
    model = mm.model_from_file('./test-data/p21c.cif')

    print(model)

