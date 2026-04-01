## OCR page: page_001_600dpi.png

4. Specification

Rijndael is an iterated block cipher with a variable block length and a variable key length. The
block length and the key length can be independently specified to 128, 192 or 256 bits.

Note: this section is intended to explain the cipher structure and not as an implementation
guideline. For implementation aspects, we refer to Section 5.

4.1 The State, the Cipher Key and the number of rounds

The different transformations operate on the intermediate result, called the State:

Definition: the intermediate cipher result is called the State.

The State can be pictured as a rectangular array of bytes. This array has four rows, the
number of columns is denoted by Nb and is equal to the block length divided by 32.

Document version 2, Date: 03/09/99 Page: 8/45

## OCR page: page_002_600dpi.png

Authors: ws .
Vincent Rijmen
The Cipher Key is similarly pictured as a rectangular array with four rows. The number of
columns of the Cipher Key is denoted by Nk and is equal to the key length divided by 32.
These representations are illustrated in Figure 1.
In some instances, these blocks are also considered as one-dimensional arrays of 4-byte
vectors, where each vector consists of the corresponding column in the rectangular array
representation. These arrays hence have lengths of 4, 6 or 8 respectively and indices in the
ranges 0..3, 0..5 or 0..7. 4-byte vectors will sometimes be referred to as words.
Where it is necessary to specify the four individual bytes within a 4-byte vector or word the
notation (a, b, c, d) will be used where a, b, c and d are the bytes at positions 0, 1, 2 and 3
respectively within the column, vector or word being considered.
ao 81 Aaa toa 8a4 Mos

Figure 1: Example of State (with Nb = 6) and Cipher Key (with Nk = 4) layout.
The input and output used by Rijndael at its external interface are considered to be one-
dimensional arrays of 8-bit bytes numbered upwards from O to the 4*Nb-1. These blocks
hence have lengths of 16, 24 or 32 bytes and array indices in the ranges 0..15, 0..23 or 0..31.
The Cipher Key is considered to be a one-dimensional arrays of 8-bit bytes numbered upwards
from O to the 4*Nk-1. These blocks hence have lengths of 16, 24 or 32 bytes and array
indices in the ranges 0..15, 0..23 or 0..31.
The cipher input bytes (the “plaintext” if the mode of use is ECB encryption) are mapped onto
the state bytes in the order ao, 10, 20, 43,0, G01, 41.1, 421, 431, G41... , and the bytes of the
Cipher Key are mapped onto the array in the order ko 0; ki 0; ko o, ks 0, ko; ky, ko 4, k34, ka 4 ... At
the end of the cipher operation, the cipher output is extracted from the state by taking the state
bytes in the same order.
Hence if the one-dimensional index of a byte within a block is n and the two dimensional index
is /,J), we have:
Moreover, the index /is also the byte number within a 4-byte vector or word and 7 is the index
for the vector or word within the enclosing block.
The number of rounds is denoted by Nr and depends on the values Nb and Nk. It is given in
Table 1.
Document version 2, Date: 03/09/99 Page: 9/45

## OCR page: page_003_600dpi.png

Authors: - .
Vincent Rijmen
pose | om=4 | mp=6 | wp-8 |
=o | 12 | 2 |e
EE cn
Table 1: Number of rounds (Nr) as a function of the block and key length.
4.2 The round transformation
The round transformation is composed of four different transformations. In pseudo C notation
we have:
Round (State, RoundKey )
{
ByteSub(State);
ShiftRow(State) ;
MixColumn(State);
AddRoundKey (State, RoundKey) ;
}
The final round of the cipher is slightly different. It is defined by:
FinalRound(State,RoundKey)
{
ByteSub(State) ;
ShiftRow(State) ;
AddRoundKey (State, RoundKey) ;
}
In this notation, the “functions” (Round, ByteSub, ShiftRow, ...) operate on arrays to which
pointers (State, RoundKey) are provided.
It can be seen that the final round is equal to the round with the MixColumn step removed.
The component transformations are specified in the following subsections.
Document version 2, Date: 03/09/99 Page: 10/45

## OCR page: page_004_600dpi.png

Authors: ws .
Vincent Rijmen
4.2.1 The ByteSub transformation
The ByteSub Transformation is a non-linear byte substitution, operating on each of the State
bytes independently. The substitution table (or S-box ) is invertible and is constructed by the
composition of two transformations:
1. First, taking the multiplicative inverse in GF(2°), with the representation defined in
Section 2.1. ‘00’ is mapped onto itself.
2. Then, applying an affine (over GF(2) ) transformation defined by:
Vo 100 0 1 1 1 = Ix, ]
y, 1 100 0 1 1 «=SIiIx, ]
y5 1 1 100 0 1 = «=SJTYIx, 0
y3 1 1 1 1 0 0 0 I)I}x; 0
y,| [1 1 1 1 1.0.0 Olfx,|7]o
Vs O 1 1 1 1 1 O O}}x,; |
Ve O00 1 1 1 1 1 O}f}*X, ]
y; 00 0 1 1 1 1 =XIYiiIx, 0
The application of the described S-box to all bytes of the State is denoted by:
ByteSub(State) .
Figure 2 illustrates the effect of the ByteSub transformation on the State.
aaalise aoa s-box JL os, |, Liae
40 0,1 aoe Pe 0,1 — 0,4 0,5
tatu al ay Fos a mom By
Figure 2: ByteSub acts on the individual bytes of the State.
The inverse of ByteSub is the byte substitution where the inverse table is applied. This is
obtained by the inverse of the affine mapping followed by taking the multiplicative inverse in
GF(2°).
4.2.2 The ShiftRow transformation
In ShiftRow, the rows of the State are cyclically shifted over different offsets. Row 0 is not
shifted, Row 1 is shifted over C1 bytes, row 2 over C2 bytes and row 3 over C3 bytes.
The shift offsets C1, C2 and C3 depend on the block length Nb. The different values are
specified in Table 2.
Document version 2, Date: 03/09/99 Page: 11/45

## OCR page: page_005_600dpi.png

Authors: ws .
Vincent Rijmen
eT a [ @ [| 3
ef + | 2 | 3
CE ee
Table 2: Shift offsets for different block lengths.
The operation of shifting the rows of the State over the specified offsets is denoted by:
ShiftRow(State) .
Figure 3 illustrates the effect of the ShiftRow transformation on the State.
Ee: Ce
3 —
ee
es ooo ee
Bene) ee
Ww X y Z Ww X y
ee A
Figure 3: ShiftRow operates on the rows of the State.
The inverse of ShiftRow is a cyclic shift of the 3 bottom rows over Nb-C1, Nb-C2 and Nb-C3
bytes respectively so that the byte at position / in row / moves to position (/ + Nb-—Ci) mod Nb.
4.2.3 The MixColumn transformation
In MixColumn, the columns of the State are considered as polynomials over GF(2°) and
multiplied modulo x’ + 1 with a fixed polynomial c(x ), given by
C(x) = ‘03’ xX + ‘01’ X +‘01' x+ ‘02’.
This polynomial is coprime to x + 1 and therefore invertible. As described in Section 2.2, this
can be written as a matrix multiplication. Let b(x ) = c(x ) © a(x ),
by 02 03 O1 Ollfa,
b, O1 02 03 Olja,
b,| |01 O1 02 O3|fa,
b, 03 Ol OL O2I/a,
The application of this operation on all columns of the State is denoted by
MixColumn(State).
Figure 4 illustrates the effect of the MixColumn transformation on the State.
Document version 2, Date: 03/09/99 Page: 12/45

## OCR page: page_006_600dpi.png

Authors: ws .
Vincent Rijmen
oar] °° sda © olx Pato] as] in
+ C(X Lh
Aig | 444 ay athe Ais | PT D, | b by 31 5,4) O15
a, | b, .
7 3,]
Figure 4: MixColumn operates on the columns of the State.
The inverse of MixColumn is similar to MixColumn. Every column is transformed by multiplying
it with a specific multiplication polynomial a(x ), defined by
(‘03’ xX’ + ‘01’ X + ‘01’ x+ ‘02’) @ A(x) =‘01’.

It is given by:

d(x) = ‘0B’ x’ + ‘OD’ X + ‘09’ x+ ‘OE’.
4.2.4 The Round Key addition
In this operation, a Round Key is applied to the State by a simple bitwise EXOR. The Round
Key is derived from the Cipher Key by means of the key schedule. The Round Key length is
equal to the block length Nb.
The transformation that consists of EXORing a Round Key to the State is denoted by:

AddRoundKey(State,RoundKey ).
This transformation is illustrated in Figure 5.

fase [ [en] [ee fen] ee] eee] oe
o) =
Figure 5: In the key addition the Round Key is bitwise EXORed to the State.

AddRoundkKey is its own inverse.
Document version 2, Date: 03/09/99 Page: 13/45

## OCR page: page_007_600dpi.png

Authors: - .
Vincent Rijmen
4.3 Key schedule
The Round Keys are derived from the Cipher Key by means of the key schedule. This consists
of two components: the Key Expansion and the Round Key Selection. The basic principle is
the following:
¢ The total number of Round Key bits is equal to the block length multiplied by the
number of rounds plus 1. (e.g., for a block length of 128 bits and 10 rounds, 1408
Round Key bits are needed).
e The Cipher Key is expanded into an Expanded Key.
¢ Round Keys are taken from this Expanded Key in the following way: the first Round
Key consists of the first Nb words, the second one of the following Nb words, and so
on.
4.3.1 Key expansion
The Expanded Key is a linear array of 4-byte words and is denoted by W|Nb*(Nr+1) ]. The
first Nk words contain the Cipher Key. All other words are defined recursively in terms of words
with smaller indices. The key expansion function depends on the value of Nk: there is a
version for Nk equal to or below 6, and a version for Nk above 6.
For Nk < 6, we have:
KeyExpansion(byte Key[4*Nk] word W[Nb*(Nr+1) ])
{
for(i = 0; i < Nk; itt)
W[i] = (Key[4*i],Key[4*i+1],Key[4*i+2],Key[4*i+3]);
for(i = Nk; i < Nb * (Nr + 1); itt)
{
temp = W[i - 1];
if (i % Nk == 0)
temp = SubByte(RotByte(temp)) * Rcon[i / Nk];
W[i] = W[i - Nk] * temp;
}
}
In this description, SubByte(W) is a function that returns a 4-byte word in which each byte is
the result of applying the Rijndael S-box to the byte at the corresponding position in the input
word. The function RotByte(W) returns a word in which the bytes are a cyclic permutation of
those in its input such that the input word (a,b,c,d) produces the output word (b,c,d,a).
It can be seen that the first Nk words are filled with the Cipher Key. Every following word w[i]|
is equal to the EXOR of the previous word W[i-1] and the word Nk positions earlier Wl i-Nk].
For words in positions that are a multiple of Nk, a transformation is applied to w[i-1] prior to
the EXOR and a round constant is EXORed. This transformation consists of a cyclic shift of
the bytes in a word (RotByte), followed by the application of a table lookup to all four bytes
of the word (SubByte).
Document version 2, Date: 03/09/99 Page: 14/45

## OCR page: page_008_600dpi.png

Authors: ws .
Vincent Rijmen
For Nk > 6, we have:
KeyExpansion(byte Key[4*Nk] word W[Nb*(Nr+1) ])
{
for(i = 0; 1 < Nk; itt)
W[i] = (key[4*i],key[4*i+1],key[4*i+2],key[4*i+3]);
for(i = Nk; i < Nb * (Nr + 1); itt)
{
temp = W[i - 1];
if (i % Nk == 0)
temp = SubByte(RotByte(temp)) * Rcon[i / Nk];
else if (1 3 Nk == 4)
temp = SubByte(temp);
W[i] = W[i - Nk] * temp;
}
}
The difference with the scheme for Nk < 6 is that for i-4 a multiple of Nk, SubByte is applied
to W[i-1] prior to the EXOR.
The round constants are independent of Nk and defined by:
Rcon[i] = (RC[i],‘00’,‘00’,‘00’)
with RC[I] representing an element in GF(2°) with a value of x‘'~” so that:
RC[1] = 1 (i.e. ‘01’)
RC[i] = x (i.e. ’02’) *(RC[i-1]) = x“
4.3.2 Round Key selection
Round key i is given by the Round Key buffer words W[Nb*i]| to W[Nb*(it+1)]. This is
illustrated in Figure 6.
are
Round key 0 Round key 17 a
Figure 6: Key expansion and Round Key selection for Nb = 6 and Nk = 4.
Note: The key schedule can be implemented without explicit use of the array WI Nb* (Nr+1) |.
For implementations where RAM is scarce, the Round Keys can be computed on-the-fly using
a buffer of Nk words with almost no computational overhead.
Document version 2, Date: 03/09/99 Page: 15/45

## OCR page: page_009_600dpi.png

Authors: as .
oan Demen The Rijndael Block Cipner = AES Proposal
Vincent Rijmen
4.4 The cipher
The cipher Rijndael consists of
¢ an initial Round Key addition;
¢ Nr-1 Rounds;
° a final round.
In pseudo C code, this gives:
Rijndael(State,CipherKey )
{
KeyExpansion(CipherKey,ExpandedKey) ;
AddRoundKey(State,ExpandedKey ) ;
For( i=l ; i<Nr ; it+ ) Round(State,ExpandedKey + Nb*i) ;
FinalRound(State,ExpandedKey + Nb*Nr);
}
The key expansion can be done on beforehand and Rijndael can be specified in terms of the
Expanded Key.
Rijndael(State,ExpandedKey )
{
AddRoundKey(State,ExpandedKey ) ;
For( i=l ; i<Nr ; it+ ) Round(State,ExpandedKey + Nb*i) ;
FinalRound(State,ExpandedKey + Nb*Nr);
}
Note: the Expanded Key shall always be derived from the Cipher Key and never be specified
directly. There are however no restrictions on the selection of the Cipher Key itself.
