## 1.  Introduction

In  this  document  we  describe  the  cipher  Rijndael.  First  we  present  the  mathematical  basis necessary  for  understanding  the  specifications  followed  by  the  design  rationale  and  the description itself. Subsequently, the implementation aspects of the cipher and its inverse are treated.  This  is  followed  by  the  motivations  of  all  design  choices  and  the  treatment  of  the resistance  against  known  types  of  attacks.  We  give  our  security  claims  and  goals,  the advantages and limitations of the cipher, ways how it can be extended and how it can be used for functionality other than block encryption/decryption. We conclude with the acknowledgements, the references and the list of annexes.

Patent  Statement: Rijndael  or  any  of  its  implementations  is  not  and  will  not  be  subject  to patents.

## 1.1  Document history

This is the second version of the Rijndael documentation. The main difference with the  first version is the correction of a number of errors and inconsistencies, the addition of a motivation for the number of rounds, the addition of some figures in the section on differential and linear cryptanalysis, the inclusion of Brian Gladman ' s  performance  figures  and  the  specification  of Rijndael extensions supporting block and key lengths of 160 and 224 bits.