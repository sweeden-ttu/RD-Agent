## OCR page: page_001_600dpi.png

2. Mathematical preliminaries
Several operations in Rijndael are defined at byte level, with bytes representing elements in
the finite field GF(2°). Other operations are defined in terms of 4-byte words. In this section we
introduce the basic mathematical concepts needed in the following of the document.
2.1 The field GF(2°)
The elements of a finite field [LiNi86] can be represented in several different ways. For any
prime power there is a single finite field, hence all representations of GF(2°) are isomorphic.
Despite this equivalence, the representation has an impact on the implementation complexity.
We have chosen for the classical polynomial representation.
A byte b, consisting of bits b7 bg bs bs bs be by Do, is considered as a polynomial with coefficient
in {0,1}:

b; X + bg X° + bs X° + by X + bs X + bo xX +b, xX+ by
Example: the byte with hexadecimal value ‘57’ (binary 01010111) corresponds with
polynomial

XX eX exe.

2.1.1 Addition
In the polynomial representation, the sum of two elements is the polynomial with coefficients
that are given by the sum modulo 2 (i.e., 1 + 1 = 0) of the coefficients of the two terms.
Document version 2, Date: 03/09/99 Page: 4/45

## OCR page: page_002_600dpi.png

Authors: - .
Vincent Rijmen
Example: ‘57’ + ‘83’ = ‘D4’, or with the polynomial notation:
(+X 4X 4xe1)4¢(X 4x41) HW 4K 4K gm.
In binary notation we have: “01010111” + “10000011” = “11010100”. Clearly, the addition
corresponds with the simple bitwise EXOR ( denoted by © ) at the byte level.
All necessary conditions are fulfilled to have an Abelian group: internal, associative, neutral
element (‘00’), inverse element (every element is its own additive inverse) and commutative.
As every element is its own additive inverse, subtraction and addition are the same.
2.1.2 Multiplication
In the polynomial representation, multiplication in GF(2°) corresponds with multiplication of
polynomials modulo an irreducible binary polynomial of degree 8. A polynomial is irreducible if
ithas no divisors other than 1 and itself. For Rijndael, this polynomial is called m(x ) and given
by
mx)=xX +x 4x 4x41
or ‘11B’ in hexadecimal representation.
Example: ‘57’ * 83’ =‘C1’, or:
(4X +X 4x41) (x 4x41) = XP ex 4 xX ex 4x’ 4+
X 4X 4X4 4X4
XX 4X 4xt1
= ar an a a a ar a a
XP ex eX eX exer tx 4x41 modulox+xX +X 4x41
= X+xX 41
Clearly, the result will be a binary polynomial of degree below 8. Unlike for addition, there is no
simple operation at byte level.
The multiplication defined above is associative and there is a neutral element (‘01’). For any
binary polynomial b(x ) of degree below 8, the extended algorithm of Euclid can be used to
compute polynomials a(x ), c(x ) such that
D(x )a(x) + M(x )c(x) = 1.
Hence, a(x) * b(x) mod m(x )= 1 or
b'(x) = a(x) mod m(x)
Moreover, it holds that a(x ) ¢ (B(x) + c(x)) = a(x) © D(x) + a(x) © C(x).
It follows that the set of 256 possible byte values, with the EXOR as addition and the
multiplication defined as above has the structure of the finite field GF(2°).
Document version 2, Date: 03/09/99 Page: 5/45

## OCR page: page_003_600dpi.png

Authors: ws .
Vincent Rijmen
2.1.3 Multiplication by x
If we multiply b(x ) by the polynomial x, we have:
b; X° + bg X + bs X° + by X + bg X + bo X +b, X + by X

x * D(x) is obtained by reducing the above result modulo m(x ). If b, = 0, this reduction is the
identity operation, If 67 = 1, m(x ) must be subtracted (i.e., EXORed). It follows that
multiplication by x (hexadecimal ‘02’) can be implemented at byte level as a left shift and a
subsequent conditional bitwise EXOR with ‘1B’. This operation is denoted by b = xtime(a).
In dedicated hardware, xtime takes only 4 EXORs. Multiplication by higher powers of x can
be implemented by repeated application of xtime. By adding intermediate results,
multiplication by any constant can be implemented.
Example: ‘57’ ° ‘13’ = ‘FE’

‘57° ° ‘02’ =xtime(57) = ‘AE’

‘57> ° ‘04’ =xtime(AE) = ‘47’

‘57’ °‘08’=xtime(47) = ‘8E’

‘57’ °‘10’=xtime(8E) =‘07’
2.2 Polynomials with coefficients in GF(2°)
Polynomials can be defined with coefficients in GF(2°). In this way, a 4-byte vector
corresponds with a polynomial of degree below 4.
Polynomials can be added by simply adding the corresponding coefficients. As the addition in
GF(2°) is the bitwise EXOR, the addition of two vectors is a simple bitwise EXOR.
Multiplication is more complicated. Assume we have two polynomials over GF(2°):

a(x) =a3X + aX +a X+ Aap and b(x) = bs x° + bo X + by X+ bo.
Their product c(x ) = a(x )b(x ) is given by

C(X)=CoX +O5X + O4X + O3X + OX +O,X+C with

Co = Ao* Do C4 = a3°b; ® aoebs ® a;°bs

Cy = a;°Do @ ao? by C5 = a3°Do @ ao* Db

Co = A2* Do ® a,°b; ® Ap* Do Ce = a3°bz

C3 = €3°Do ® aod; © abo © Feed Oe
Document version 2, Date: 03/09/99 Page: 6/45

## OCR page: page_004_600dpi.png

oe an The Rijndael Block Cipher AES Proposal
Vincent Rijmen
Clearly, c(x) can no longer be represented by a 4-byte vector. By reducing c(x ) modulo a
polynomial of degree 4, the result can be reduced to a polynomial of degree below 4. In
Rijndael, this is done with the polynomial M(x) = x'+ 1. As
xX mod x*+1 =x 74,
the modular product of a(x ) and b(x ), denoted by a(x ) = a(x ) ® B(x) is given by
d(x) = d3xX° + doX +d; x+d with
O = Ao*bo ® Ag*by © Ae*bo © ai*bs
Ay = A1°Do © Ao°b; © A3*D2 © ao*by
Ap = A2*Dy © A1°D, © Ae © a3°bs
3 = A3%Do © A2°b; © a1*bo ® ao*bs
The operation consisting of multiplication by a fixed polynomial a(x ) can be written as matrix
multiplication where the matrix is a circulant matrix. We have
d, A a, a, a, \[B
d, a a a; a\||d,
d, 7 a, a a a;\||b,
: : Gy al ma) :
Note: x’ + 1 is not an irreducible polynomial over GF(2°), hence multiplication by a fixed
polynomial is not necessarily invertible. In the Rijndael cipher we have chosen a fixed
polynomial that does have an inverse.
2.2.1 Multiplication by x
If we multiply b(x ) by the polynomial x, we have:
b3 X° + bo X° + by X + by X
x ® b(x) is obtained by reducing the above result modulo 1 + x’. This gives
bo X° + by X + by X+ bs
The multiplication by x is equivalent to multiplication by a matrix as above with all a; ='00’
except a; =01’. Let c(x) = x @b(x ). We have:
Co 00 00 00 O1T[b,
C, O01 00 00 OOD,
c,| |00 01 00 OOlld,
: : 00 Ol : :
Hence, multiplication by x, or powers of x, corresponds to a cyclic shift of the bytes inside the
vector.

## OCR page: page_005_600dpi.png

oan Duemen The Rijndael Block Cipher AES Proposal
