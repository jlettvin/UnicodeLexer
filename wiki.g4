/** 
wiki.g4
Automatically generated Unicode based wiki grammar.
 */ 

grammar      wiki;


import       classify;


prog   : ID *
; 



C      : [ Cc | Cf | Cn | Co | Cs           ]  // from PropertyValueAliases.txt
; 

LC     : [ Ll | Lt | Lu                     ]  // from PropertyValueAliases.txt
; 

M      : [ Mc | Me | Mn                     ]  // from PropertyValueAliases.txt
; 

L      : [ Ll | Lm | Lo | Lt | Lu           ]  // from PropertyValueAliases.txt
; 

N      : [ Nd | Nl | No                     ]  // from PropertyValueAliases.txt
; 

P      : [ Pc | Pd | Pe | Pf | Pi | Po | Ps ]  // from PropertyValueAliases.txt
; 

S      : [ Sc | Sk | Sm | So                ]  // from PropertyValueAliases.txt
; 

Z      : [ Zl | Zp | Zs                     ]  // from PropertyValueAliases.txt
; 

/* End of Unicode codepoint classification */


WS     : [ Z ]              // hand-written rule
; 

ID0    : [ L | '_' ]        // hand-written rule
; 

ID     : ID0 [ ID0 | N ] *  // hand-written rule
; 

DEFINE : '&' ID '=' .*? ';'
; 

ENTITY : '&' ID ';'
; 

