## 5.  Implementation aspects

The Rijndael cipher is suited to be implemented efficiently on a wide range of processors and in dedicated hardware. We will concentrate on 8-bit processors, typical for current Smart Cards and on 32-bit processors, typical for PCs.

## 5.1  8-bit processor

On  an  8-bit  processor,  Rijndael  can  be  programmed  by  simply  implementing  the  different component  transformations.  This  is  straightforward  for  RowShift  and  for  the  Round  Key addition. The implementation of ByteSub requires a table of 256 bytes.

The Round Key addition, ByteSub and RowShift  can  be  efficiently  combined  and  executed serially per  State  byte.  Indexing  overhead is minimised by explicitly coding the operation for every State byte.

The transformation MixColumn requires matrix multiplication in  the  field  GF(2 8 ).  This  can  be implemented in an efficient way. We illustrate it for one column:

```
Tmp = a [ 0 ] ^ a [ 1 ] ^ a [ 2 ] ^ a [ 3 ] ; /* a is a byte array */ Tm = a [ 0 ] ^ a [ 1 ] ; Tm = xtime(Tm); a [ 0 ] ^= Tm ^ Tmp ; Tm = a [ 1 ] ^ a [ 2 ] ; Tm = xtime(Tm); a [ 1 ] ^= Tm ^ Tmp ; Tm = a [ 2 ] ^ a [ 3 ] ; Tm = xtime(Tm); a [ 2 ] ^= Tm ^ Tmp ; Tm = a [ 3 ] ^ a [ 0 ] ; Tm = xtime(Tm); a [ 3 ] ^= Tm ^ Tmp ;
```

This description is for clarity. In practice, coding is of course done in assembly language. To prevent  timing  attacks,  attention  must  be  paid  that xtime is  implemented  to  take  a  fixed number of cycles, independent of the value of its argument. In practice this can be achieved by using a dedicated table-lookup.

Obviously, implementing the key expansion in a single shot operation is likely to occupy too much RAM in a Smart Card. Moreover, in most applications, such as debit cards or electronic purses,  the  amount  of  data  to  be  enciphered,  deciphered  or  that  is  subject  to  a  MAC  is typically  only  a  few  blocks  per  session.  Hence,  not  much  performance  can  be  gained  by expanding the key only once for multiple applications of the block cipher.

The  key  expansion  can  be  implemented  in  a  cyclic  buffer  of 4*max( Nb , Nk ) bytes.  The Round  Key  is  updated  in  between  Rounds.  All  operations  in  this  key  update  can  be implemented efficiently on byte level. If the Cipher Key length and the blocks length are equal or  differ  by  a  factor  2,  the  implementation  is  straightforward.  If  this  is  not  the  case,  an additional buffer pointer is required.

## 5.2  32-bit processor

## 5.2.1  The Round Transformation

The  different  steps  of  the  round  transformation  can  be  combined  in  a  single  set  of  table lookups, allowing for very fast implementations on processors with word length 32 or above. In this section, it is explained how this can be done.

We express one column of the round output e in terms of bytes of the round input a. In this section, ai,j denotes the byte of a in row i and column j, aj denotes the column j of State a. For the key addition and the MixColumn transformation, we have

$$\begin{bmatrix} e _ { 0 , j } \\ e _ { 1 , j } \\ e _ { 2 , j } \\ e _ { 3 , j } \end{bmatrix} = \begin{bmatrix} e _ { 0 , j } \\ e _ { 1 , j } \\ d _ { 1 , j } \\ e _ { 2 , j } \\ e _ { 3 , j } \end{bmatrix} \bigoplus \begin{bmatrix} k _ { 0 , j } \\ k _ { 1 , j } \\ d _ { 2 , j } \\ d _ { 3 , j } \end{bmatrix} \text { and } \begin{bmatrix} d _ { 0 , j } \\ d _ { 1 , j } \\ 0 \\ 0 \\ k _ { 2 , j } \\ k _ { 3 , j } \end{bmatrix} = \begin{bmatrix} 0 2 & 0 3 & 0 1 & 0 1 \\ 0 1 & 0 2 & 0 3 & 0 1 \\ 0 1 & 0 1 & 0 2 & 0 3 \\ 0 3 & 0 1 & 0 1 & 0 2 \\ c _ { 3 , j } \end{bmatrix} .$$

For the ShiftRow and the ByteSub transformations, we have:

$$\begin{bmatrix} c _ { 0 , j } \\ c _ { 1 , j } \\ c _ { 2 , j } \\ c _ { 3 , j } \end{bmatrix} & = \begin{bmatrix} b _ { 0 , j } \\ b _ { 1 , j - C 1 } \\ b _ { 2 , j - C 2 } \\ b _ { 3 , j - C 3 } \end{bmatrix} \text { and } b _ { i , j } = S [ a _ { i , j } ] .$$

In  this  expression  the  column  indices  must  be  taken  modulo Nb expressions can be combined into:

.  By  substitution,  the  above

$$\begin{bmatrix} 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0 \\ & & & & & & & 0$$

The matrix multiplication can be expressed as a linear a combination of vectors:

$$\begin{bmatrix} e _ { 0 , j } \\ \begin{bmatrix} e _ { 1 , j } \\ e _ { 2 , j } \\ e _ { 3 , j } \end{bmatrix} \begin{bmatrix} 0 2 \\ 0 1 \\ 0 1 \end{bmatrix} \oplus S [ a _ { 1 , j - C 1 } ] _ { 0 1 } \oplus S [ a _ { 2 , j - C 2 } ] _ { 0 2 } ^ { 0 1 } \oplus S [ a _ { 3 , j - C 3 } ] _ { 0 3 } ^ { 0 1 } \oplus S [ a _ { k _ { 3 , j } - C 3 } ] _ { 0 2 } ^ { 0 1 } \oplus \begin{bmatrix} k _ { 0 , j } \\ k _ { 1 , j } \\ k _ { 2 , j } \\ k _ { 3 , j } \end{bmatrix} . \\ \intertext { t h e w i s t i g h e f a r y } \begin{array} { c } \text {e} _ { 0 , j } \\ \text {e} _ { 1 , j } \\ \text {e} _ { 2 , j } \\ \text {e} _ { 3 , j } \end{array} \begin{array} { c } 0 2 \\ 0 1 \\ 0 3 \end{array} \oplus S [ a _ { 1 , j - C 1 } ] _ { 0 1 } ^ { 0 2 } \oplus S [ a _ { 2 , j - C 2 } ] _ { 0 2 } ^ { 0 1 } \oplus S [ a _ { 3 , j - C 3 } ] _ { 0 3 } ^ { 0 1 } \oplus \begin{bmatrix} k _ { 0 , j } \\ k _ { 1 , j } \\ k _ { 2 , j } \\ k _ { 3 , j } \end{bmatrix} . \\$$

The multiplication factors S [ ai,j ] of the four vectors are obtained by performing a table lookup on input bytes ai,j in the S-box table S [ 256 ] .

We define tables T0 to T3 :

$$T _ { 0 } [ a ] = \begin{bmatrix} S [ a ] \cdot 0 2 \\ S [ a ] \\ S [ a ] & T _ { 1 } [ a ] = \begin{bmatrix} S [ a ] \bullet 0 3 \\ S [ a ] \cdot 0 2 \\ S [ a ] \\ S [ a ] \end{bmatrix} & T _ { 2 } [ a ] = \begin{bmatrix} S [ a ] \\ S [ a ] \cdot 0 3 \\ S [ a ] \bullet 0 2 \\ S [ a ] \end{bmatrix} & T _ { 3 } [ a ] = \begin{bmatrix} S [ a ] \\ S [ a ] \\ S [ a ] \cdot 0 3 \\ S [ a ] \end{bmatrix} .$$

These are 4 tables with 256 4-byte word entries and make up for 4KByte of total space. Using these tables, the round transformation can be expressed as:

$$e _ { j } = T _ { 0 } [ a _ { 0 , j } ] \ominus T _ { 1 } [ a _ { 1 , j - C 1 } ] \ominus T _ { 2 } [ a _ { 2 , j - C 2 } ] \ominus T _ { 3 } [ a _ { 3 , j - C 3 } ] \ominus k _ { j } .$$

Hence, a table-lookup implementation with 4 Kbytes of tables takes only 4 table lookups and 4 EXORs per column per round.

It can be seen that Ti [ a ] = RotByte(Ti-1 [ a ] ). At the cost of 3 additional rotations per round per column, the table-lookup implementation can be realised with only one table, i.e., with a total table size of 1KByte. We have

$$e _ { j } = k _ { j } \oplus T _ { 0 } [ b _ { 0 , j } \Big ] \oplus R o t b y t e ( T _ { 0 } [ b _ { 1 , j - C 1 } ] \oplus R o t b y t e ( T _ { 0 } [ b _ { 2 , j - C 2 } ] \oplus R o t b y t e ( T _ { 0 } [ b _ { 3 , j - C 3 } ] ) ) )$$

The code-size (relevant in applets) can be kept small by including code to generate the tables instead of the tables themselves.

In the final round, there is no MixColumn operation. This boils down to the fact that the S table must be used instead of the T tables. The need for additional tables can be suppressed by extracting the S table from the T tables by masking while executing the final round.

Most  operations  in  the  key  expansion  can  be  implemented  by  32-bit  word  EXORs.  The additional transformations are the application of the S-box and a cyclic shift over 8-bits. This can be implemented very efficiently.

## 5.2.2  Parallelism

It  can  be  seen  that  there  is  considerable  parallelism  in  the  round  transformation.  All  four component transformations of the round act in a parallel way on bytes, rows or columns of the State.

In the table-lookup implementation, all table lookups can in principle be done in parallel. The EXORs can be done in parallel for the most part also.

The key expansion is clearly of a more sequential nature: the value of W [ i-1 ] is needed for the computation of W [ i ] . However, in most applications where speed is critical, the KeyExpansion has to be done only once for a large number of cipher executions. In applications where the Cipher  Key  changes  often  (in  extremis  once  per  application  of  the  Block  Cipher),  the  key expansion and the cipher Rounds can be done in parallel..

## 5.2.3  Hardware suitability

The cipher is suited to be implemented in dedicated hardware.  There  are  several  trade-offs between  area  and  speed  possible.  Because  the  implementation  in  software  on  generalpurpose  processors  is  already  very  fast,  the  need  for  hardware  implementations  will  very probably be limited to two specific cases:

- Extremely high speed chip with no area restrictions: the T tables can be hardwired and the EXORs can be conducted in parallel.
- Compact  co-processor  on  a  Smart  Card  to  speed  up  Rijndael  execution:  for  this platform typically the S-box and the xtime (or  the  complete MixColumn) operation can be hardwired.

## 5.3  The inverse cipher

In the table-lookup implementation it is essential that the only non-linear step (ByteSub) is the first transformation in a round and that the rows are shifted before MixColumn is applied. In the Inverse of a round, the order of the transformations in the round is reversed, and consequently the non-linear step will end up being the last step of the inverse round and the rows are shifted after the application of (the inverse of) MixColumn. The inverse of a round can therefore not be implemented with the table lookups described above.

This implementation aspect has been anticipated  in  the  design.  The  structure  of  Rijndael  is such that the sequence of transformations of its inverse is equal to that of the cipher itself, with the  transformations  replaced  by  their  inverses  and  a  change  in  the  key  schedule.  This  is shown in the following subsections.

Note: this  identity  in structure  differs  from  the  identity  of components  and  structure  in  IDEA [LaMaMu91].

## 5.3.1  Inverse of a two-round Rijndael variant

```
The inverse of a round is given by: InvRound(State,RoundKey) { AddRoundKey(State,RoundKey); InvMixColumn(State); InvShiftRow(State); InvByteSub(State); } The inverse of the final round is given by: InvFinalRound(State,RoundKey) { AddRoundKey(State,RoundKey); InvShiftRow(State); InvByteSub(State); }
```

The  inverse  of  a  two-round  variant  of  Rijndael  consists  of  the  inverse  of  the  final  round followed by the inverse of a round, followed by a Round Key Addition. We have:

```
AddRoundKey(State,ExpandedKey+2*Nb); InvShiftRow(State); InvByteSub(State); AddRoundKey(State,ExpandedKey+Nb); InvMixColumn(State); InvShiftRow(State); InvByteSub(State); AddRoundKey(State,ExpandedKey);
```

## 5.3.2  Algebraic properties

In deriving the equivalent structure of the inverse cipher, we make use of two properties of the component transformations.

First, the order of ShiftRow and ByteSub is indifferent. ShiftRow simply transposes the bytes and has no effect on the byte values. ByteSub works on individual bytes, independent of their position.

## Second, the sequence

```
AddRoundKey(State,RoundKey); InvMixColumn(State); can be replaced by: InvMixColumn(State); AddRoundKey(State,InvRoundKey);
```

with InvRoundKey obtained by applying InvMixColumn to the corresponding RoundKey. This is based on the fact that for a linear transformation A, we have A(x+k)= A(x )+A(k).

## 5.3.3  The equivalent inverse cipher structure

Using  the  properties  described  above,  the  inverse  of  the  two-round  Rijndael  variant  can  be transformed into:

```
AddRoundKey(State,ExpandedKey+2*Nb); InvByteSub(State); InvShiftRow(State); InvMixColumn(State); AddRoundKey(State,I_ExpandedKey+Nb); InvByteSub(State); InvShiftRow(State); AddRoundKey(State,ExpandedKey);
```

It can be seen that we have again an initial Round Key addition, a round and a final round. The Round and the final round have the same structure as those of the cipher itself. This can be generalised to any number of rounds.

```
We define a round and the final round of the inverse cipher as follows: I_Round(State,I_RoundKey) { InvByteSub(State); InvShiftRow(State); InvMixColumn(State); AddRoundKey(State,I_RoundKey); } I_FinalRound(State,I_RoundKey) { InvByteSub(State); InvShiftRow(State); AddRoundKey(State,RoundKey0); } The Inverse of the Rijndael Cipher can now be expressed as follows: I_Rijndael(State,CipherKey) { I_KeyExpansion(CipherKey,I_ExpandedKey) ; AddRoundKey(State,I_ExpandedKey+ Nb*Nr); For( i=Nr-1 ; i>0 ; i-- ) Round(State,I_ExpandedKey+ Nb*i) ; FinalRound(State,I_ExpandedKey); } The key expansion for the Inverse Cipher is defined as follows: 1.  Apply the Key Expansion. 2.  Apply InvMixColumn to all Round Keys except the first and the last one. In Pseudo C code, this gives: I_KeyExpansion(CipherKey,I_ExpandedKey) { KeyExpansion(CipherKey,I_ExpandedKey); for( i=1 ; i < Nr ; i++ ) InvMixColumn(I_ExpandedKey + Nb*i) ; }
```

## 5.3.4  Implementations of the inverse cipher

The choice of the MixColumn polynomial and the key expansion was partly based on cipher performance arguments. Since the inverse cipher is similar in structure, but uses a MixColumn transformation  with  another  polynomial  and  (in  some  cases)  a  modified  key  schedule,  a performance degradation is observed on 8-bit processors.

This asymmetry is due to the fact that the performance of the inverse cipher is considered to be less important than that of the cipher. In many applications of a block cipher, the inverse cipher operation is not used. This is the case for the calculation of MACs, but also when the cipher is used in CFB-mode or OFB-mode.

## 5.3.4.1  8-bit processors

As explained in Section 4.1, the operation MixColumn can be implemented quite efficiently on 8-bit processors. This is because the coefficients of MixColumn are limited to ' 01 ' , ' 02 ' and ' 03 ' and  because  of  the  particular  arrangement  in  the  polynomial.  Multiplication  with  these coefficients can be done very efficiently by means of the procedure xtime() . The coefficients of InvMixColumn are ' 09 ' , ' 0E ', ' 0B ' and ' 0D '. In our 8-bit implementation, these multiplications take significantly more time. A considerable speed-up can be obtained by using table lookups at the cost of additional tables.

The key expansion operation that generates W is defined in such a way that we can also start with the last Nk words of Round Key information and roll back to the original Cipher Key. So, calculation ' on-the-fly'  of  the  Round  Keys,  starting  from  an  'Inverse  Cipher  Key',  is  still possible.

## 5.3.4.2  32-bit processors

The Round of the inverse cipher can be implemented with table lookups in exactly the same way as the round of the cipher and there is no performance degradation with respect to the cipher. The look-up tables for the inverse are of course different.

The key expansion for the inverse cipher is slower, because after the key expansion all but two of the Round Keys are subject to InvMixColumn (cf. Section 5.3.3).

## 5.3.4.3  Hardware suitability

Because  the  cipher  and  its  inverse  use  different  transformations,  a  circuit  that  implements Rijndael does not automatically support the computation of the inverse of Rijndael. Still, in a circuit  implementing  both  Rijndael  and  its  inverse,  parts  of  the  circuit  can  be  used  for  both functions.

This  is  for  instance  the  case  for  the  non-linear  layer.  The  S-box  is  constructed  from  two mappings:

$$S ( x ) = f ( g ( x ) ) ,$$

$$x \Rightarrow x ^ { - 1 } \text { in } G F ( 2 ^ { 8 } )$$

where g(x ) is the mapping:

and f(x ) is the affine mapping.

The mapping g(x ) is self-inverse and hence S -1 (x ) = g -1 (f -1 (x )) = g(f -1 (x )). Therefore when we want both S and S -1 ,  we  need to implement only g, f and f -1 .  Since  both  f  and  f -1 are  very simple bit-level functions, the extra hardware can be reduced significantly compared to having two full S-boxes.

Similar arguments apply to the re-use of the xtime transformation in the diffusion layer.