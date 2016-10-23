/** 
hello0.g4
Sample grammar for comparison.
 */ 

grammar      hello0;



prog   : hello * EOF
;

hello  : 'hello' ID
;

/* in hello1.g4 ID and WS will be provided by classify.g4 */

ID      : [A-Za-z_] +           ;

WS      : [ \t\r\n] + -> skip   ;
