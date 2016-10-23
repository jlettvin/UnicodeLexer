grammar hi;
prog    : hi* EOF ;
hi      : 'hello' ID ;
ID      : [a-z]+ ;
WS      : [ \t\r\n]+ -> skip ;
