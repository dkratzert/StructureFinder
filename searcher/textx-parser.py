from textx.metamodel import metamodel_from_str
from pathlib import Path

"""
CIF syntax at:

https://www.iucr.org/resources/cif/spec/version1.1/cifsyntax

"""

grammar = r"""
CIF:
    Comment? WhiteSpace? DataBlock*=DataBlock WhiteSpace? 
;

DATA_:
    /[dD][aA][tT][aA]_/
;

DataBlockHeading:
    data=DATA_ NonBlankChar+
;

DataBlock:
    DataBlockHeading=DataBlockHeading (WhiteSpace items*=DataItems)*
;


DataItems:
    Tag=Tag WhiteSpace Value=Value | LOOP_ Loophead+=LoopHeader Loopbody*=LoopBody
;


LOOP_:
    /[lL][oO][oO][pP]_/
;

LoopHeader:
    WhiteSpace Tag
;

LoopBody:
    LValue*=Value (WhiteSpace LValue*=Value)*
;

WhiteSpace:
    /\s+/ | TokenizedComments+
;

Comment:
    /(\#(AnyPrintChar)*)+/
;

TokenizedComments:
    /\s+/  Comment
;

Tag:
    '_'NonBlankChar+
;

Value:
    '.' | '?' | Numeric | CharString | TextField+=SemiColonTextField
;

Numeric:
    Number | Number '('INT+')'
;

Number:
    INT | FLOAT  // (('+'|'-')? /\d\.?\d?/)
;

//Integer:
//     ('+'|'-')? UnsignedInteger
//;

//UnsignedInteger:
//    INT
//;

CharString:
    UnquotedString | SingleQuotedString | DoubleQuotedString
;

NonBlankChar:   
    OrdinaryChar | /["#']/
;

UnquotedString:
    (eol OrdinaryChar NonBlankChar*)+ | ((OrdinaryChar | ';') NonBlankChar*)+
;


SingleQuotedString:
    ("'"|AnyPrintChar|"'"|WhiteSpace)*
;

DoubleQuotedString:
    '"' AnyPrintChar* '"' WhiteSpace
;

//TextField:
//    SemiColonTextField
//;

eol:
    /\n|\r|\r\n/
;

SemiColonTextField:
    eol ";" (AnyPrintChar)* eol ((TextLeadChar AnyPrintChar*)? eol)* ";"
;

OrdinaryChar:
    /[\w+-.\/\?]/
;

TextLeadChar:
    OrdinaryChar | /["#$'_ \t\[\]\(\)]/  
;

AnyPrintChar:
    OrdinaryChar | /["#$'_ ;\[\]\(\)]/ 
;

"""



if __name__ == '__main__':
    mm = metamodel_from_str(grammar, skipws=False, autokwd=False, debug=True)

    # Meta-model knows how to parse and instantiate models.
    data = '\n'.join(open('./test-data/p21c.cif', 'r').readlines(805))
    #model = mm.model_from_file('../test-data/p21c.cif')
    model = mm.model_from_str(data)
    print(model)

