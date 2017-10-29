from textx.metamodel import metamodel_from_str
from pathlib import Path

"""
CIF syntax at:

https://www.iucr.org/resources/cif/spec/version1.1/cifsyntax

"""

grammar = r"""
CIF:  // <Comments>? <WhiteSpace>? { <DataBlock> { <WhiteSpace> <DataBlock> }* { <WhiteSpace> }? }?
    WhiteSpace? DataBlock*=DataBlock WhiteSpace?
;

DataBlock:  //  <DataBlockHeading> {<WhiteSpace> { <DataItems> | <SaveFrame>} }*
    DataBlockHeading | (WhiteSpace | ditems+=DataItems)*
;

DATA_:
    /[dD][aA][tT][aA]_/
;

DataBlockHeading:
    DATA_ NonBlankChar+
;


DataItems: //    <Tag> <WhiteSpace> <Value> |  <LoopHeader> <LoopBody>
    tag=Tag WhiteSpace+ val=Value //| (LoopHeader | LoopBody)
;

WhiteSpace:
    (/\ / | eol)+                   //| TokenizedComments+
;

Tag:
    '_'NonBlankChar+
;

Value:   //  { '.' | '?' | <Numeric> | <CharString> | <TextField> }
    '.' | '?' | CharString | SemiColonTextField
;


LOOP_:
    /[lL][oO][oO][pP]_/
;

LoopHeader:   //  <LOOP_> {<WhiteSpace> <Tag>}+	
    LOOP_ (WhiteSpace | Tag)+
;

LoopBody:   //  <Value> { <WhiteSpace> <Value> }*
    LValue*=Value (WhiteSpace LValue*=Value)*
;


//Comment:
//    /(\#(AnyPrintChar)*)+/
//;

//TokenizedComments:
//    /\s+/  Comment
//;

//Numeric:  // Numeric values just as text for now
//    Number | Number '('INT+')'
//;

//Number:
//    INT | FLOAT  // (('+'|'-')? /\d\.?\d?/)
//;

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


SingleQuotedString:  // <single_quote>{<AnyPrintChar>}* <single_quote> <WhiteSpace>
    "'"AnyPrintChar*"'"WhiteSpace
;

DoubleQuotedString:
    '"'AnyPrintChar*'"'WhiteSpace
;

//TextField:
//    SemiColonTextField
//;

eol:
    /\n|\r|\r\n/
;

SemiColonTextField:
    eol ';' (AnyPrintChar)* eol ((TextLeadChar AnyPrintChar*)? eol)* ';'
;

OrdinaryChar:
    /[\w+-.\/\?]/
;

TextLeadChar:
    OrdinaryChar | /["#$'_ \t\[\]\(\)]/  
;

AnyPrintChar:
    OrdinaryChar | /[#$_ ;\[\]\(\)]/ 
;

"""
#######################################################################################

lgrammar = r"""
/* Für loop_ brauche ich eine Liste in der jedes list-item ein dictionary ist, wo {key=loopheaditem, value=loopvalue} ist.
   Der Loopheader bestimmt die keys, der body die values.
   Also: [{"_atom_type_symbol": 'C', "_atom_type_description": 'C', "_atom_type_scat_dispersion_real": 0.0033,      
           "_atom_type_scat_dispersion_imag": 0.0016, 
           "_atom_type_scat_source": 'International Tables Vol C Tables 4.2.6.8 and 6.1.1.4'}, {}, ... ]

from textx.metamodel import metamodel_from_str

grammar = '''
LoopModel:
  loops+=Loop    // each model has one or more entities
;

Loophead:
   foo
;

Loop:
  item+=loopheaditem 
    attribute=Attribute     
;

Attribute:
  loopheaditem type=[Entity]   // type is a reference to an entity. There are
                              // built-in entities registered on the meta-model
                              // for primitive types (integer, string)
;
'''

class Entity(object):
  def __init__(self, parent, name, attributes):
    # build the dictionary


# Use our Entity class. "Attribute" class will be created dynamically.
entity_mm = metamodel_from_str(grammar, classes=[Entity])


*/

DataItems: //    <Tag> <WhiteSpace> <Value> |  <LoopHeader> <LoopBody>
    (loop=LoopHeader LoopBody)+
;

WhiteSpace:
    (/\ / | eol)+                   //| TokenizedComments+
;

LOOP_:
    /[lL][oO][oO][pP]_/
;

LoopHeader:   //  <LOOP_> {<WhiteSpace> <Tag>}+	
    LOOP_ (WhiteSpace | ltag+=Tag)+
;

LoopBody:   //  <Value> { <WhiteSpace> <Value> }*
    (Value | WhiteSpace)*
;

Tag:
    '_'NonBlankChar+
;

Value:   //  { '.' | '?' | <Numeric> | <CharString> | <TextField> }
    '.' | '?' | CharString | SemiColonTextField
;


CharString:
    UnquotedString | SingleQuotedString | DoubleQuotedString
;

NonBlankChar:   
    OrdinaryChar | /["#']/
;

UnquotedString:
    eol OrdinaryChar NonBlankChar* | (OrdinaryChar | ';') NonBlankChar*
;


SingleQuotedString:  // <single_quote>{<AnyPrintChar>}* <single_quote> <WhiteSpace>
    "'"AnyPrintChar*"'"WhiteSpace
;

DoubleQuotedString:
    '"'AnyPrintChar*'"'WhiteSpace
;


eol:
    /\n|\r|\r\n/
;

SemiColonTextField:
    eol ';' (AnyPrintChar)* eol ((TextLeadChar AnyPrintChar*)? eol)* ';'
;

OrdinaryChar:
    /[\w+-.\/\?]/
;

TextLeadChar:
    OrdinaryChar | /["#$'_ \t\[\]\(\)]/  
;

AnyPrintChar:
    OrdinaryChar | /[#$_ ;\[\]\(\)]/ 
;

"""


if __name__ == '__main__':
    mm = metamodel_from_str(lgrammar, skipws=False, autokwd=False, debug=True)

    # Meta-model knows how to parse and instantiate models.
    data = ''.join(open('./test-data/p21c.cif', 'r').readlines()[13:32])
    print(data)
    #model = mm.model_from_file('../test-data/p21c.cif')
    model = mm.model_from_str(data)

    print(model)


