from textx.metamodel import metamodel_from_str
from pathlib import Path

grammar = """
CIF:
  Comment? DataBlock=DataBlock+
;

DataBlock:
  DataBlockHeading=DataBlockHeading DataItems=DataItems*
;

DataBlockHeading:
    DATA_/\S+/
;

DATA_:
#    /[d]|[D][a]|[A][t]|[T][a]|[A]/
    "data"|"DATA"|"Data"
;

DataItems:
    Tag  /.*/
;

Comment:
    /^#.*$/
;

TokenizedComments:
    	{ <SP> | <HT> | <eol> |}+ <Comments>
;

Tag:
    /_\S+/
;

Value:
    /('.' | '?' | NUMBER | CharString | TextField)/
;

CharString:
    /(UnquotedStringLineStart | UnquotedStringAfterKeyword | SingleQuotedString | DoubleQuotedString)/
;

UnquotedStringLineStart:
    <eol><OrdinaryChar> {<NonBlankChar>}*	
;    
UnquotedStringAfterKeyword:
    <noteol>{<OrdinaryChar>|';'} {<NonBlankChar>}*
;

<SingleQuotedString> <WhiteSpace>:
    <single_quote>{<AnyPrintChar>}* <single_quote> <WhiteSpace>
;
    
<DoubleQuotedString> <WhiteSpace>:
    <double_quote> {<AnyPrintChar>}* <double_quote> <WhiteSpace>
;

TextField:
    SemiColonTextField
;

<eol><SemiColonTextField>:
    <eol>';' { {<AnyPrintChar>}* <eol>{{<TextLeadChar> {<AnyPrintChar>}*}? <eol>}*} ';'
;

WhiteSpace:
    { <SP> | <HT> | <eol> | <TokenizedComments>}+
;

<OrdinaryChar>:
     '!' | '%' | '&' | '(' | ')' | '*' | '+' | ',' | '-' | '.' | '/' | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | ':' | '<' | '=' | '>' | '?' | '@' | 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J' | 'K' | 'L' | 'M' | 'N' | 'O' | 'P' | 'Q' | 'R' | 'S' | 'T' | 'U' | 'V' | 'W' | 'X' | 'Y' | 'Z' | '\' | '^' | '`' | 'a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h' | 'i' | 'j' | 'k' | 'l' | 'm' | 'n' | 'o' | 'p' | 'q' | 'r' | 's' | 't' | 'u' | 'v' | 'w' | 'x' | 'y' | 'z' | '{' | '|' | '}' | '~' }

<NonBlankChar>:
    <OrdinaryChar> | <double_quote> | '#' | '$' | <single_quote> | '_' |';' | '[' | ']'

<TextLeadChar>:
    <OrdinaryChar> | <double_quote> | '#' | '$' | <single_quote> | '_' | <SP> | <HT> |'[' | ']'
    
<AnyPrintChar>:
    <OrdinaryChar> | <double_quote> | '#' | '$' | <single_quote> | '_' | <SP> | <HT> | ';' | '[' | ']'

 
"""

mm = metamodel_from_str(grammar)



# Meta-model knows how to parse and instantiate models.
model = mm.model_from_file('../test-data/p21c.cif')

print(model)

if __name__ == '__main__':
    pass