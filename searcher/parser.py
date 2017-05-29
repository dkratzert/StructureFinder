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
    /[d]|[D][a]|[A][t]|[T][a]|[A]/
;

DataItems:
    Tag=Tag  /.*/
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
    model = mm.model_from_file('./test-data/p21c.cif')

    print(model)