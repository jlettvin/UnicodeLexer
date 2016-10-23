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