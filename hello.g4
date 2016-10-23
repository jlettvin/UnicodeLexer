/** 
hello.g4
Automatically generated Unicode based hello grammar.
 */ 

grammar      hello; 

import       classify; 

prog   : hi * EOF
; 

hi     : 'hello' ID
; 

ID     : [a-z]+              // TODO classify rule
; 

WS     : [ \t\r\n]+ -> skip  // TODO classify rule
; 

