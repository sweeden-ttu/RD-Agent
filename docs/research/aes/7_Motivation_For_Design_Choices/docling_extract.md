## 7.  Motivation for design choices

In  the  following  subsections,  we  will  motivate  the  choice  of  the  specific  transformations  and constants. We believe that the cipher structure does not offer enough degrees of freedom to hide a trap door.

## 7.1  The reduction polynomial m(x )

The  polynomial  m(x  )  ( ' 11B ' )  for  the  multiplication  in  GF(2 8 )  is  the  first  one  of  the  list  of irreducible polynomials of degree 8, given in [LiNi86, p. 378].

## 7.2  The ByteSub S-box

The design criteria for the S-box are inspired by differential and linear cryptanalysis on the one hand and attacks using algebraic manipulations, such as interpolation attacks, on the other:

1.  Invertibility;
2.  Minimisation  of  the  largest  non-trivial  correlation  between  linear  combinations  of input bits and linear combination of output bits;
3.  Minimisation of the largest non-trivial value in the EXOR table;
4.  Complexity of its algebraic expression in GF(2 8 );
5.  Simplicity of description.

In [Ny94] several methods are given to construct S-boxes that satisfy the first three criteria. For invertible S-boxes operating on bytes, the maximum input/output correlation can be made as low as 2 -3 and the maximum value in the EXOR table can be as low as 4 (corresponding to a difference propagation probability of 2 -6 ).

We have decided to take from the candidate constructions in [Ny94] the S-box defined by the mapping x ⇒ x -1 in GF(2 8 ).

By  definition,  the  selected  mapping  has  a  very  simple  algebraic  expression.  This  enables algebraic  manipulations  that  can  be  used  to  mount  attacks  such  as  interpolation  attacks [JaKn97].  Therefore,  the  mapping  is  modified  by  composing  it  with  an  additional  invertible affine transformation. This affine transformation does not affect the properties with respect tot the first three criteria, but if properly chosen, allows the S-box to satisfy the fourth criterion.

We  have  chosen  an  affine  mapping  that  has  a  very  simple  description  per  se,  but  a complicated algebraic expression if combined  with  the ' inverse ' mapping.  It  can  be  seen  as modular polynomial multiplication followed by an addition:

$$b ( x ) = ( x ^ { 7 } + x ^ { 6 } + x ^ { 2 } + x ) + a ( x ) ( x ^ { 7 } + x ^ { 6 } + x ^ { 5 } + x ^ { 4 } + 1 ) \bmod x ^ { 8 } + 1$$

The modulus has been chosen as the simplest modulus possible. The multiplication polynomial has been chosen  from  the  set  of  polynomials  coprime  to  the  modulus  as  the  one  with  the simplest description. The constant has been chosen in such a way that that the S-box has no fixed points (S-box(a) = a) and no ' opposite fixed points' (S-box(a) = a ).

Note: other S-boxes can be found that satisfy the criteria above. In the case of suspicion of a trapdoor being built into the cipher, the current S-box might be replaced by another one. The cipher structure and number of rounds as defined even allow the use of an S-box that does not optimise the differential and linear cryptanalysis properties (criteria 2 and 3). Even an Sbox that is 'average' in this respect is likely to provide enough resistance against differential and linear cryptanalysis.

## 7.3   The MixColumn transformation

MixColumn  has  been  chosen  from  the  space  of  4-byte  to  4-byte  linear  transformations according to the following criteria:

1.  Invertibility;
2.  Linearity in GF(2);
3.  Relevant diffusion power;
4.  Speed on 8-bit processors;
5.  Symmetry;
6.  Simplicity of description.

Criteria 2, 5 and 6 have lead us to the choice to polynomial multiplication modulo  x 4 +1. Criteria 1, 3 and 4 impose conditions on the coefficients. Criterion 4 imposes that the coefficients have small values, in order of preference ' 00 ' , ' 01 ' , ' 02 ' , ' 03 ' …The value ' 00 ' implies no processing at all, for ' 01 ' no multiplication needs to be executed, ' 02 ' can be implemented using xtime and ' 03 ' can be implemented using xtime and an additional EXOR.

The criterion 3 induces a more complicated conditions on the coefficients.

## 7.3.1  Branch number

In  our  design  strategy,  the  following  property  of  the  linear  transformation  of  MixColumn  is essential. Let F be a linear transformation acting on byte vectors and let the byte weight of a vector  be  the  number  of  nonzero  bytes  (not  to  be  confused  with  the  usual  significance  of Hamming weight, the number of nonzero bits). The byte weight of a vector is denoted by W(a). The Branch Number of a linear transformation is a measure of its diffusion power:

Definition: The branch number of a linear transformation F is

$$\min _ { a \neq 0 } ( W ( a ) + W ( F ( a ) ) ) \, .$$

A non-zero byte is called an active byte. For MixColumn it can be seen that if a state is applied with a single active byte, the output can have at most 4 active bytes, as MixColumn acts on the columns independently. Hence, the upper bound for the branch number is 5. The coefficients have been chosen in such a way that the upper bound is reached. If the branch number is 5, a difference in 1 input (or output) byte propagates to all 4 output (or input) bytes, a 2-byte input (or output) difference to at least 3 output (or input) bytes. Moreover, a linear relation between input and output bits involves bits from at least 5 different bytes from input and output.

## 7.4  The ShiftRow offsets

The choice from all possible combinations has been made based on the following criteria:

1.  The four offsets are different and C0 = 0;
2.  Resistance against attacks using truncated differentials [Kn95];
3.  Resistance against the Square attack [DaKnRi97];
4.  Simplicity.

For  certain  combinations,  attacks  using  truncated  differentials  can  tackle  more  rounds (typically  only  one)  than  for  other  combinations.  For  certain  combinations  the  Square  attack can  tackle  more  rounds  than  others.  From  the  combinations  that  are  best  with  respect  to criteria 2 and 3, the simplest ones have been chosen.

## 7.5  The key expansion

The key expansion specifies the derivation of the Round Keys in terms of the Cipher Key. Its function is to provide resistance against the following types of attack:

- Attacks in which part of the Cipher Key is known to the cryptanalyst;
- Attacks where the Cipher Key is known or can be chosen, e.g., if the cipher is used as the compression function of a hash function[Kn95a];
- Related-key  attacks  [Bi93],  [KeScWa96].  A  necessary  condition  for  resistance against related-key attacks is that there should not be two different Cipher Keys that have a large set of Round Keys in common.

The key expansion also plays an important role in the elimination of symmetry:

- Symmetry in the round transformation: the round transformation treats all bytes of a state in very much the same way. This symmetry can be removed by having round constants in the key schedule;
- Symmetry between the rounds: the round transformation is the same for all rounds. This  equality  can  be  removed  by  having  round-dependent  round  constants  in  the key schedule.

The key expansion has been chosen according to the following criteria:

- It shall use an invertible transformation, i.e., knowledge of any Nk consecutive words of the Expanded Key shall allow to regenerate the whole table;
- Speed on a wide range of processors;
- Usage of round constants to eliminate symmetries;
- Diffusion of Cipher Key differences into the Round Keys;
- Knowledge of a part of the Cipher Key or Round Key bits shall not allow to calculate many other Round Key bits.
- Enough non-linearity to prohibit the full determination of Round Key differences from Cipher Key differences only;
- Simplicity of description.

In order to be efficient on 8-bit processors, a light-weight, byte oriented expansion scheme has been adopted. The application of  SubByte  ensures  the  non-linearity  of  the  scheme,  without adding much space requirements on an 8-bit processor.

## 7.6  Number of rounds

We have determined the number of rounds by looking at the maximum number of rounds for which shortcut attacks have been found and added a considerable security margin. (A shortcut attack is an attack more efficient than exhaustive key search.)

For  Rijndael  with  a  block  length  and  key  length  of  128  bits,  no  shortcut  attacks  have  been found for reduced versions with more than 6 rounds. We added 4 rounds as a security margin. This is a conservative approach, because:

- Two rounds of Rijndael provide 'full diffusion' in the following sense: every state bit depends on all state bits two rounds ago, or, a change in one state bit is likely to affect  half  of  the  state  bits  after  two  rounds.    Adding  4  rounds  can  be  seen  as adding a 'full diffusion' step at the beginning and at the end of the cipher. The high diffusion  of  a  Rijndael  round  is  thanks  to  its  uniform  structure  that  operates  on  all state bits. For so-called Feistel ciphers, a round only operates on half of the state bits  and  full  diffusion  can  at  best  be  obtained  after  3  rounds  and  in  practice  it typically takes 4 rounds or more.
- Generally,  linear  cryptanalysis,  differential  cryptanalysis  and  truncated  differential attacks  exploit  a  propagation  trail  through n  rounds  in  order  to  attack n+1  or  n+2 rounds. This is also the case for the Square attack that uses a 4-round propagation structure to attack 6 rounds. In this respect, adding 4 rounds actually doubles  the number of rounds through which a propagation trail has to be found.

For  Rijndael  versions  with  a  longer  Key,  the  number  of  rounds  is  raised  by  one  for  every additional 32 bits in the Cipher Key, for the following reasons:

- One of the main objectives is the absence of shortcut attacks, i.e., attacks that are more efficient than exhaustive key search. As with the key length the workload of exhaustive  key  search  grows,  shortcut  attacks  can  afford  to  be  less  efficient  for longer keys.
- Known-key (partially)  and  related-key  attacks  exploit  the  knowledge  of  cipher  key bits  or  ability  to  apply  different  cipher  keys.  If  the  cipher  key  grows,  the  range  of possibilities available to the cryptanalyst increases.

As no threatening known-key or related-key attacks have been found for Rijndael, even for 6 rounds, this is a conservative margin.

For Rijndael versions with a higher block length, the number  of  rounds  is  raised  by  one  for every additional 32 bits in the block length, for the following reasons:

- For a block length above 128 bits, it takes 3 rounds to realise full diffusion, i.e., the diffusion  power  of  a  round,  relative  to  the  block  length,  diminishes  with  the  block length.
- The larger block length causes the range of possible patterns that can be applied at the input/output of a sequence of rounds to increase. This added flexibility may allow to extend attacks by one or more rounds.

We have found that extensions of attacks by a single round are even hard to realise for the maximum block length of 256 bits. Therefore, this is a conservative margin.