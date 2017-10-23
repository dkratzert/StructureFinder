from textx.metamodel import metamodel_from_str
from pathlib import Path

grammar = r"""
CIF:
  Comments? DataBlock=DataBlock+
;

DataBlock:
  DataBlockHeading=DataBlockHeading DataItems=DataItems*
;

DataBlockHeading:
    DATA_/\S+/
;

DATA_:
    /(data|DATA)/
;

DataItems:
    Tag=Tag  /.*/
;

LoopBlockHeading:
    LOOP_/\S+/
;

LOOP_:
    /(loop|LOOP)/
;

LoopHeader:
    LOOP_/(WhiteSpace Tag)+/
;

WhiteSpace:
    /(\s|\t|\r|\r\n|\n|TokenizedComments)+/
;

WhiteSpace[noskipws]:
    /(\s|\t|\r|\r\n|\n|TokenizedComments)+ /
;

Comments[noskipws]:
    /^#.*$/
;

TokenizedComments:
    /( \s | \t | \r | \r\n | \n )+ Comments/
;

Tag:
    /_\S+/
;

Value:
    /(\. | \? | NUMBER | CharString )/
;

CharString:
    /^\w+\s/
;



"""



if __name__ == '__main__':
    mm = metamodel_from_str(grammar)

    # Meta-model knows how to parse and instantiate models.
    model = mm.model_from_file('../test-data/p21c.cif')

    print(model)

