from textx.metamodel import metamodel_from_str
from pathlib import Path

"""
CIF syntax at:

https://www.iucr.org/resources/cif/spec/version1.1/cifsyntax

"""

grammar = r"""
CIF:
    Comment? WhiteSpace? (DataBlock=DataBlock (WhiteSpace DataBlock)* (WhiteSpace)? )?
;

DATA_:
    /[d|D][a|A][t|T][a|A]\_/
;

DataBlockHeading:
    DATA_/\w+/
;

DataBlock:
    DataBlockHeading=DataBlockHeading (WhiteSpace DataItems)*
;


DataItems:
    Tag=Tag WhiteSpace Value=Value | Loophead=LoopHeader Loopbody=LoopBody
;


LOOP_:
    /[l|L][o|O][o|O][p|P]_/
;

LoopHeader:
    LOOP_/(WhiteSpace+Tag)+/
;

LoopBody:
    Value/(WhiteSpace Value)*/
;

WhiteSpace:
    /\s+/|TokenizedComments+
;

Comment:
    /(\#(AnyPrintChar)*)+/
;

TokenizedComments:
    /(\s|\t|\r|\r\n|\n|eol)+/ Comment
;

Tag:
    /\_/NonBlankChar+
;

Value:
    /\.|\?/ | Numeric | CharString | TextField
;

Numeric:
    Number | Number /\(UnsignedInteger+\)/
;

Number:
    Integer | /(\+|\-)?\d\.?\d?/
;

Integer:
     /(\+|\-)?/ UnsignedInteger
;

UnsignedInteger:
    INT
;

CharString:
    UnquotedString | SingleQuotedString | DoubleQuotedString
;

NonBlankChar:   
    OrdinaryChar | /\"/|/\#/|/\'/
;

UnquotedString:
    (eol OrdinaryChar (NonBlankChar)*)+ | ((OrdinaryChar | /\;/) NonBlankChar*)+
;


SingleQuotedString:
    (/\'/|AnyPrintChar|/\'/|WhiteSpace)*
;

DoubleQuotedString:
    /\"/ AnyPrintChar* /\"/WhiteSpace
;

TextField:
    SemiColonTextField
;

eol:
    /\n|\r|\r\n/
;

SemiColonTextField:
    eol /\;/ (AnyPrintChar)* eol ((TextLeadChar (AnyPrintChar)*)? eol)* /\;/
;

OrdinaryChar:
    /\w|\!|\%|\&|\(|\)|\*|\+|\,|\-|\.|\/|\:|\<|\=|\>|\?|\@|\\|\^|\`|\{|\||\}|\~/
;

TextLeadChar:
    OrdinaryChar | /\"|\#|\$|\'|\_|\s|\t|\[|\]/  // \s is not ok here?
;

AnyPrintChar:
    OrdinaryChar | /\"|\#|\$|\'|\_|\s|\;|\[|\]/  // \s is not ok here?
;

"""



if __name__ == '__main__':
    mm = metamodel_from_str(grammar, skipws=False, autokwd=False, debug=False)

    # Meta-model knows how to parse and instantiate models.
    model = mm.model_from_file('./test-data/p21c.cif')

    print(model)

