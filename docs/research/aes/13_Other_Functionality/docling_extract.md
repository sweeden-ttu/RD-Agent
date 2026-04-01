## 13.  Other functionality

In  this  section  we  mention  some  functions  that  can  be  performed  with  the  Rijndael  block cipher, other than encryption.

## 13.1  MAC

Rijndael  can  be  used  as  a  MAC  algorithm  by  using  it  as  the  Block  cipher  in  a  CBC-MAC algorithm. [ISO9797]

## 13.2  Hash function

Rijndael can be used as an iterated hash function by using it as the round function. Here is one possible implementation. It is advised to use a block and key length both equal to 256 bits. The chaining variable goes into the 'input' and the message block goes into the 'Cipher Key'. The  new  value  of  the  chaining  variable  is  given  by  the  old  value  EXORed  with  the  cipher output.

## 13.3  Synchronous stream cipher

Rijndael  can  be  used  as  a  synchronous  stream  cipher  by  applying  the  OFB  mode  or  the Filtered Counter Mode. In the latter mode, the key stream sequence is created by encrypting some type of counter using a secret key [Da95].

## 13.4  Pseudorandom number generator

In  [KeScWaHa98]  a  set  of  guidelines  are  given  for  designing  a  Pseudorandom  Number Generator (PRNG). There are many ways in which Rijndael could be used to form a PRNG that satisfies these guidelines. We give an example in which Rijndael with a block length of 256 and a cipher key length of 256 is used.

There are three operations:

Reset:

- The Cipher Key and 'state' are reset to 0.

Seeding (and reseeding):

- 'seed  bits'  are  collected  taking  care  that  their  total  has  some  minimum  entropy. They are padded with zeroes until the resulting string has a length that is a multiple of 256 bits.
- A new Cipher Key is computed by encrypting with Rijndael a block of seed bits using the  current  Cipher  Key.  This  is  applied  recursively  until  the  seed  blocks  are exhausted.
- The state is updated by applying Rijndael using the new Cipher Key.

Pseudorandom Number generation:

- The state is updated by applying Rijndael using the Cipher Key. The first 128 bits of the state are output as a 'pseudorandom number'. This step may be repeated many times.

## 13.5  Self-synchronising stream cipher

Rijndael  can  be  used  as  a  self-synchronising  stream  cipher  by  applying  the  CFB  mode  of operation.

Authors: Joan Daemen Vincent Rijmen

The Rijndael Block Cipher

AES Proposal