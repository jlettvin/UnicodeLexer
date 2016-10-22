/** 
wiki.g4
Automatically generated Unicode based wiki grammar.
 */ 

grammar      wiki;


import       classify;


prog   : ID *
; 



DEFINE : '&' ID '=' .*? ';'
; 

ENTITY : '&' ID ';'
; 

