from textx.metamodel import metamodel_from_str
from pathlib import Path

grammar = r"""
CIF:
  Comments? DataBlock=DataBlock+
;

DataBlock:
  DataBlockHeading=DataBlockHeading DataItems=DataItems*
;

DATA:
    /[d|D][a|A][t|T][a|A]/
;

DataBlockHeading:
    DATA/_\S+/
;


DataItems:
    TAG=TAG /.*/
;


LOOP_:
    '/[l|L][o|O][o|O][p|P]_/'
;

LoopHeader:
    LOOP_/(WhiteSpace+TAG)+/
;

LoopBody:
    Value (WhiteSpace Value)*
;


WhiteSpace[noskipws]:
    /(\s|\t|\r|\r\n|\n|TokenizedComments)+ /
;

Comments[noskipws]:
    /^#.*$/
;

TokenizedComments:
    /(\s|\t|\r|\r\n|\n)+ Comments/
;

TAG:
    /_.*/
;

Value:
    /(\. | \? | NUMBER | CharString )/
;

NUMBER:
    /(\+|\-)?\d.?\d?/
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
    /\'(\S)*\'\s/
;

DoubleQuotedString:
    /\"(\S)*\"\s/
;

OrdinaryChar:
    /( \! | \% | \& | \( | \) | \* | \+ | \, | \- | \. | \/ | \: | \< | \= | \> | \? | \@ | \\ | \^ | \` | \{ | \| | \} | \~ )/
;

"""



if __name__ == '__main__':
    mm = metamodel_from_str(grammar)

    # Meta-model knows how to parse and instantiate models.
    model = mm.model_from_file('./test-data/p21c.cif')

    print(model)

