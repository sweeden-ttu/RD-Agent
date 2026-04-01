## 2.  Mathematical preliminaries

Several operations in Rijndael are defined at byte level, with bytes representing elements in the finite field GF(2 8 ). Other operations are defined in terms of 4-byte words. In this section we introduce the basic mathematical concepts needed in the following of the document.

## 2.1  The field GF(2 8 )

The elements of a finite field [LiNi86] can be represented in several different ways. For any prime power there is a single finite field, hence all representations of GF(2 8 )  are isomorphic. Despite this equivalence, the representation has an impact on the implementation complexity. We have chosen for the classical polynomial representation.

A byte b, consisting of bits b7 b6 b5 b4 b3 b2 b1 b0, is considered as a polynomial with coefficient in {0,1}:

$$b _ { 7 } \, x ^ { 7 } + b _ { 6 } \, x ^ { 6 } + b _ { 5 } \, x ^ { 5 } + b _ { 4 } \, x ^ { 4 } + b _ { 3 } \, x ^ { 3 } + b _ { 2 } \, x ^ { 2 } + b _ { 1 } \, x + b _ { 0 }$$

Example : the byte with hexadecimal  value ' 57 ' (binary 01010111 ) corresponds  with polynomial

$$x ^ { 6 } + x ^ { 4 } + x ^ { 2 } + x + 1 \, .$$

## 2.1.1  Addition

In the polynomial representation, the sum of two elements is the polynomial with coefficients that are given by the sum modulo 2 (i.e., 1 + 1 = 0) of the coefficients of the two terms.

Example: ' 57 ' + ' 83 ' = ' D4 ' , or with the polynomial notation:

$$( \ x ^ { \mathfrak { b } } + x ^ { 4 } + x ^ { 2 } + x + 1 ) + ( \ x ^ { \mathfrak { b } } + x + 1 ) = x ^ { \mathfrak { b } } + x ^ { \mathfrak { b } } + x ^ { 4 } + x ^ { 2 } \, .$$

In  binary  notation  we  have:  ' 01010111 '  +  ' 10000011 '  =  ' 11010100 '.  Clearly,  the  addition corresponds with the simple bitwise EXOR ( denoted by ⊕ ) at the byte level.

All  necessary conditions are  fulfilled  to  have  an  Abelian  group:  internal,  associative,  neutral element ( ' 00 ' ),  inverse element (every element is its own additive inverse) and commutative. As every element is its own additive inverse, subtraction and addition are the same.

## 2.1.2  Multiplication

In  the  polynomial  representation,  multiplication  in  GF(2 8 )  corresponds  with  multiplication  of polynomials modulo an irreducible binary polynomial of degree 8. A polynomial is irreducible if it has no divisors other than 1 and itself. For Rijndael, this polynomial is called m(x ) and given by

$$m ( x ) = x ^ { 8 } + x ^ { 4 } + x ^ { 3 } + x + 1$$

or ' 11B ' in hexadecimal representation.

Example: ' 57 ' ' 83 ' = ' C1 ' , or:

$$\begin{array} { r l r l } & { \exp ( \cdot \, 5 ^ { 7 } \, \cdot \, \real ^ { 8 } = \, ^ { C 1 } , \, \text {or.} } \\ & { \quad ( x ^ { 6 } + x ^ { 4 } + x ^ { 2 } + x + 1 ) \, ( \, x ^ { 7 } + x ^ { 9 } + x ^ { 8 } + x ^ { 7 } + \cdots + x ^ { 1 1 } + x ^ { 9 } + x ^ { 8 } + x ^ { 7 } + \cdots + x ^ { 1 2 } + x + 1 } \\ & { \quad = \, \cdots \, ( \, x ^ { 6 } + x ^ { 4 } + x ^ { 2 } + x + 1 \, \cdots + x ^ { 1 6 } + x ^ { 9 } + x ^ { 8 } + x ^ { 6 } + x ^ { 5 } + x ^ { 4 } + x ^ { 3 } + 1 } \end{array}$$

$$x ^ { 1 3 } + x ^ { 1 1 } + x ^ { 9 } + x ^ { 8 } + x ^ { 6 } + x ^ { 5 } + x ^ { 4 } + x ^ { 3 } + 1 & \text {modulo } x ^ { 8 } + x ^ { 4 } + x ^ { 3 } + x + 1 \\ & = \quad x ^ { 7 } + x ^ { 6 } + 1$$

Clearly, the result will be a binary polynomial of degree below 8. Unlike for addition, there is no simple operation at byte level.

The multiplication defined above is associative and there is a neutral element ( ' 01 ' ).  For any binary polynomial b(x  ) of degree below 8, the extended algorithm of Euclid can be used to compute polynomials a(x ), c(x ) such that

$$b ( x ) a ( x ) + m ( x ) c ( x ) = 1 \, .$$

Hence, a(x ) · b(x ) mod m(x )= 1 or

$$b ^ { - 1 } ( x ) = a ( x ) \bmod m ( x )$$

Moreover, it holds that a(x ) · (b(x ) + c(x )) = a(x ) · b(x ) + a(x ) · c(x ).

It  follows  that  the  set  of  256  possible  byte  values,  with  the  EXOR  as  addition  and  the multiplication defined as above has the structure of the finite field GF(2 8 ).

## 2.1.3  Multiplication by x

If we multiply b(x ) by the polynomial x, we have:

$$b _ { 7 } \, x ^ { 8 } + b _ { 6 } \, x ^ { 7 } + b _ { 5 } \, x ^ { 6 } + b _ { 4 } \, x ^ { 5 } + b _ { 3 } \, x ^ { 4 } + b _ { 2 } \, x ^ { 3 } + b _ { 1 } \, x ^ { 2 } + b _ { 0 } \, x$$

x · b(x ) is obtained by reducing the above result modulo m(x ). If b7 = 0,  this reduction is the identity  operation,  If b7  =  1, m(x  )  must  be  subtracted  (i.e.,  EXORed).  It  follows  that multiplication by x  (hexadecimal ' 02 ' )  can  be  implemented at byte level as a left shift and a subsequent conditional bitwise EXOR with ' 1B ' . This operation is denoted by b = xtime(a). In dedicated hardware, xtime takes only 4 EXORs. Multiplication by higher powers of x  can be implemented by repeated application of xtime . By adding intermediate results, multiplication by any constant can be implemented.

```
Example: ' 57 ' · ' 13 ' = ' FE ' ' 57 ' · ' 02 ' = xtime(57) = ' AE ' ' 57 ' · ' 04 ' = xtime(AE) = ' 47 ' ' 57 ' · ' 08 ' = xtime(47) = ' 8E ' ' 57 ' · ' 10 ' = xtime(8E) = ' 07 ' ' 57 ' · ' 13 ' = ' 57 ' · ( ' 01 ' ⊕ ' 02 ' ⊕ ' 10 ' ) = ' 57 ' ⊕ ' AE ' ⊕ ' 07 ' = ' FE '
```

## 2.2  Polynomials with coefficients in GF(2 8 )

Polynomials  can  be  defined  with  coefficients  in  GF(2 8 ). In this  way,  a 4-byte vector corresponds with a polynomial of degree below 4.

Polynomials can be added by simply adding the corresponding coefficients. As the addition in GF(2 8 ) is the bitwise EXOR, the addition of two vectors is a simple bitwise EXOR.

Multiplication is more complicated. Assume we have two polynomials over GF(2 8

):

a(x ) = a 3 x 3 + a2 x 2 + a1 x + a 0 and b(x ) = b3 x 3 + b2 x 2 + b1 x + b 0 . Their product c(x ) = a(x )b(x ) is given by c(x ) = c 6 x 6 + c 5 x 5 + c 4 x 4 + c 3 x 3 + c 2 x 2 + c 1 x + c 0 with c0 = a0 · b0 c4 = a3 · b1 ⊕ a 2 · b2 ⊕ a 1 · b3 c1 = a1 · b0 ⊕ a 0 · b1 c5 = a3 · b2 ⊕ a 2 · b3 c2 = a2 · b0 ⊕ a 1 · b1 ⊕ a 0 · b2 c6 = a3 · b3 c3 = a3 · b0 ⊕ a 2 · b1 ⊕ a 1 · b2 ⊕ a 0 · b3

Clearly, c(x ) can no longer be represented by a 4-byte vector. By reducing c(x ) modulo a polynomial of degree 4, the result can be reduced to a polynomial of degree below 4. In Rijndael, this is done with the polynomial M(x ) = x 4 + 1. As

$$\downarrow _ { \text {mod} } x ^ { 4 } \downarrow _ { 1 } 1 = \downarrow ^ { j m o d \, 4 }$$

$$x ^ { ^ { \prime } } \bmod x ^ { 4 } + 1 = x ^ { ^ { \prime } \bmod 4 } \, ,$$

the modular product of a(x ) and b(x ), denoted by d(x ) = a(x ) ⊗ b(x ) is given by

$$\text {the modular product of a} ( x ) \text { and } b ( x ) , \text { denoted by } d ( x ) = a ( x ) \otimes \\ d ( x ) = d _ { 3 } \, x ^ { 3 } + d _ { 2 } \, x ^ { 2 } + d _ { 1 } \, x + d _ { 0 } & \quad \text {with} \\ d _ { 0 } = a _ { 0 } \bullet b _ { 0 } \oplus a _ { 3 } \bullet b _ { 1 } \oplus a _ { 2 } \bullet b _ { 2 } \oplus a _ { 1 } \bullet b _ { 3 } \\ d _ { 1 } = a _ { 1 } \bullet b _ { 0 } \oplus a _ { 0 } \bullet b _ { 1 } \oplus a _ { 3 } \bullet b _ { 2 } \oplus a _ { 2 } \bullet b _ { 3 } \\ d _ { 2 } = a _ { 2 } \bullet b _ { 0 } \oplus a _ { 1 } \bullet b _ { 1 } \oplus a _ { 0 } \bullet b _ { 2 } \oplus a _ { 3 } \bullet b _ { 3 } \\ d _ { 3 } = a _ { 3 } \bullet b _ { 0 } \oplus a _ { 2 } \bullet b _ { 1 } \oplus a _ { 1 } \bullet b _ { 2 } \oplus a _ { 0 } \bullet b _ { 3 } \\ \text {The operation consisting of multiplication by a fixed polynomial}$$

The operation consisting of multiplication by a fixed polynomial a(x ) can be written as matrix multiplication where the matrix is a circulant matrix. We have

$$\begin{bmatrix} d _ { 0 } \\ d _ { 1 } \\ d _ { 2 } \\ d _ { 3 } \end{bmatrix} = \begin{bmatrix} a _ { 0 } & a _ { 3 } & a _ { 2 } & a _ { 1 } \\ a _ { 1 } & a _ { 0 } & a _ { 3 } & a _ { 2 } \\ a _ { 2 } & a _ { 1 } & a _ { 0 } & a _ { 3 } \\ a _ { 3 } & a _ { 2 } & a _ { 1 } & a _ { 0 } \end{bmatrix} \begin{bmatrix} b _ { 0 } \\ b _ { 1 } \\ b _ { 2 } \\ b _ { 3 } \end{bmatrix} \\$$

Note: x 4 +  1  is  not  an  irreducible  polynomial  over  GF(2 8 ),  hence  multiplication  by  a  fixed polynomial  is  not  necessarily  invertible.  In  the  Rijndael  cipher  we  have  chosen  a  fixed polynomial that does have an inverse.

## 2.2.1  Multiplication by x

If we multiply b(x ) by the polynomial x, we have:

$$x ^ { 4 } \pm b { h } ^ { 3 } \pm b { h } ^ { 2 } \pm$$

$$b _ { 3 } \, x ^ { 4 } + b _ { 2 } \, x ^ { 3 } + b _ { 1 } \, x ^ { 2 } + b _ { 0 } \, x$$

x ⊗ b(x ) is obtained by reducing the above result modulo 1 + x 4 . This gives

$$\tilde { v } ^ { 3 } \downarrow h \downarrow ^ { 2 }$$

$$b _ { 2 } \, x ^ { 3 } + b _ { 1 } \, x ^ { 2 } + b _ { 0 } \, x + b _ { 3 }$$

The multiplication by x is equivalent to multiplication by a matrix as above with all ai = ' 00 ' except a1 = ' 01 ' . Let c(x ) = x ⊗ b(x ). We have:

$$\begin{bmatrix} c _ { 0 } \\ c _ { 1 } \\ c _ { 2 } \\ c _ { 3 } \end{bmatrix} = \begin{bmatrix} 0 0 & 0 0 & 0 0 & 0 1 \\ 0 1 & 0 0 & 0 0 & 0 0 \\ 0 0 & 0 1 & 0 0 & 0 0 \\ 0 0 & 0 0 & 0 1 & 0 0 \end{bmatrix} \begin{bmatrix} b _ { 0 } \\ b _ { 1 } \\ b _ { 2 } \\ b _ { 3 } \end{bmatrix}$$

Hence, multiplication by x, or powers of x, corresponds to a cyclic shift of the bytes inside the vector.

Authors: Joan Daemen Vincent Rijmen

The Rijndael Block Cipher

AES Proposal