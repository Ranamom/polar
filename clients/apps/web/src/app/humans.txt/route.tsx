export async function GET(request: Request) {
  return new Response(
    `
                             ::-=+**########**++=:.                             
                        :=+##########################+=:                        
                    .=*########*#########################*=.                    
                 .=########+-=*#######***###########*-*######=:                 
              :=*######+:.:=######*-.     .-*########*..=#######=:              
            :*######+:  -###*=###=           :*#######*   +########-            
          :*######+.  .+###-.###:             .*#######+   +#####+###:          
         +######+.   =###*. *##:                +#######:   +#####:+##+.        
       .*#####*.   .*###-  *##-                  #######*    +####* -###-       
      =######=    :####-  +##=                   :#######-    *####* :###+      
    .######*     +###*   =###                     =#######     #####=  *##*     
    *#####+     +####.  :###+                      *######:    =####*  .####.   
   =#####+     +####.   +###:                      -######-    :#####.  :###+   
  :#####*     =####-    ####                       .######=     #####-   =###=  
 .######.    :####*    =###=                        +#####+     *####=   .####: 
 +#####:     *####.    *###.                        .#####*     *####+    *###* 
 #####+     +####+    :####                          #####*     +####+    +####.
-#####:    :#####     *###*                          *####*     +####+    =####:
+#####     =####+     ####*                          +####+     *####=    -####=
#####=     #####-    :####*                          +####=     #####-    -####+
#####:    -#####.    -####*                          =####-    .#####.    =####+
*####.    +#####     =####*                          =####:    -####*     *####=
=####:    #####*     =#####                          +####.    +####=     #####-
.####=    #####*     =#####.                         *###*     #####.    -#####.
 +####    ######     =#####=                         ####.    *####:     *####* 
 :####:   *#####     =######                        .###+    =####=     *#####- 
  =###+   =#####.    -######:                       +###-   .####+     =#####*  
   *###:  .#####-    :######=                       ####   .####*     -######   
   .####.  *####+     ######*                      :###.   *####     -######:   
    :###*  -#####:    +######:                     *##=   =###*.    -#####*.    
      +##*  +#####.    ######*                    =##*  .*###=    .*#####*      
       =###: *####+    +######*                  :###: .*###:    =######+       
        :###=.#####:   :#######=                 *##- =###*.   .#######-        
         .+##*=#####:   *#######+               +##- =###-   .+######=          
           .-*#######+. .########*.           :*#*==##*-  .=*######=.           
              -*#######=  *########+:       :*###*##*- .-*######*:              
                .=*#####*-.*##########+--=+#######+:.-*#######+:                
                   :=*#####+###################**=*########=:                   
                       :+*############################*+-.                      
                           .:-==+**#########***+==-:.                           



              Polar is made by all of our wonderfull contributors.

                    https://github.com/polarsource/polar

                Wanna work with us? https://polar.sh/careers

    `,
    {
      headers: {
        // 'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache',
      },
      status: 200,
    },
  )
}