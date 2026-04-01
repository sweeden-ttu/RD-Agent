## 12.  Extensions

## 12.1  Other block and Cipher Key lengths

The key schedule supports any key length that is a multiple of 4 bytes. The only parameter that needs to be defined for other key lengths than 128, 192 or 256 is the number of rounds in the cipher.

The  cipher  structure  lends  itself  for  any  block  length  that  is  a  multiple  of  4  bytes,  with  a minimum of 16 bytes. The key addition and the ByteSub and MixColumn transformations are independent from the block length. The only transformation that depends on the block length is ShiftRow. For every block length, a specific array C1 , C2 , C3 must be defined.

We define an extension of Rijndael that also supports block and key lengths between 128 and 256 bits with increments of 32 bits. The number of rounds is given by:

$$\mathbf N r = \max ( \mathbf N k , \mathbf N b ) + 6 .$$

This interpolates the rule for the number of rounds to the alternative block and key lengths.

The additional values of C1 , C2 and C3 are specified in Table 8.

Table 8: Shift offsets in Shiftrow for the alternative block lengths

|   Nb |   C1 |   C2 |   C3 |
|------|------|------|------|
|    5 |    1 |    2 |    3 |
|    7 |    1 |    2 |    4 |

The choice of these shift offsets is based on the criteria discussed in Section 7.4.

## 12.2  Another primitive based on the same round transformation

The Rijndael Round transformation has been designed to provide high multiple-round diffusion and  guaranteed  distributed  nonlinearity.  These  are  exactly  the  requirements  for  the  state updating  transformation  in  a stream/hash  module  such  as  Panama  [DaCl98].  By  fitting  the round transformation (for Nb =8) in a Panama-like scheme, a stream/hash module can be built that can hash and do stream encryption about 4 times as fast as Rijndael and perform as a very powerful pseudorandom number generator satisfying all requirements cited in [KeScWaHa98].