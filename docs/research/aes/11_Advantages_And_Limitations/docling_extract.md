## 11.  Advantages and limitations

## 11.1  Advantages

Implementation aspects:

- Rijndael can be implemented to run at speeds unusually fast for a block cipher on a Pentium (Pro). There is a trade-off between table size/performance.
- Rijndael can be implemented on a Smart Card in a small amount of code, using a small  amount  of  RAM  and  taking  a  small  number  of  cycles.  There  is  some ROM/performance trade-off.
- The  round  transformation  is  parallel  by  design,  an  important  advantage  in  future processors and dedicated hardware.
- As the cipher does not make use of arithmetic operations, it has no bias towards bigor little endian processor architectures.

Simplicity of Design:

- The cipher is fully 'self-supporting'. It does not make use of another cryptographic component,  S-boxes  'lent'  from  well-reputed  ciphers,  bits  obtained  from  Rand tables, digits of π or any other such jokes.
- The  cipher  does  not  base  its  security  or  part  of  it  on  obscure  and  not  well understood interactions between arithmetic operations.
- The tight cipher design does not leave enough room to hide a trapdoor.

Variable block length:

- The block lengths of 192 and 256 bits allow the construction of a collision-resistant iterated hash function using Rijndael as the compression function. The block length of 128 bits is not considered sufficient for this purpose nowadays.

Extensions:

- The design allows the specification of variants with the block length and key length both ranging from 128 to 256 bits in steps of 32 bits.
- Although the  number  of  rounds  of  Rijndael  is  fixed  in  the  specification,  it  can  be modified as a parameter in case of security problems.

## 11.2  Limitations

The limitations of the cipher have to do with its inverse:

- The inverse cipher is less suited to be implemented on a smart card than the cipher itself:  it  takes  more  code  and  cycles.  (Still,  compared  with  other  ciphers,  even  the inverse is very fast)
- In software, the cipher and its inverse make use of different code and/or tables.
- In hardware, the inverse cipher can only partially re-use the circuitry that implements the cipher.

Authors: Joan Daemen Vincent Rijmen

The Rijndael Block Cipher

AES Proposal