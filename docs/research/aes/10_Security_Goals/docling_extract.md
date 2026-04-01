## 10.  Security goals

In this section, we present the goals we have set for the security of Rijndael. A cryptanalytic attack will  be  considered successful by the designers if  it  demonstrates  that  a  security  goal described herein does not hold.

## 10.1  Definitions of security concepts

In order to formulate our goals, some security-related concepts need to be defined.

## 10.1.1  The set of possible ciphers for a given block length and key length

A block cipher of block length v has V = 2 v possible inputs. If the key length is u it defines a set of  U  =  2 u permutations  over  {0,1} v .  The  number  of  possible  permutations  over  {0,1} v is  V!. Hence the number of all possible block ciphers of dimensions u and v is

$$( ( 2 ^ { v } ) ! ) ^ { ( 2 ^ { u } ) } \ \text {or equivalently } ( V \, ! ) ^ { U } \ .$$

For practical values of the dimensions (e.g., v and u above 40), the subset of block ciphers with exploitable weaknesses form a negligible minority in this set.

## 10.1.2  K-Security

Definition: A  block  cipher  is  K-secure  if  all  possible  attack  strategies  for  it  have  the  same expected work factor and storage requirements as for the majority of  possible  block  ciphers with  the  same  dimensions.  This  must  be  the  case  for  all  possible  modes  of  access  for  the adversary (known/chosen/adaptively chosen plaintext/ciphertext, known/chosen/adaptively chosen key relations...) and for any a priori key distribution.

K-security is a very strong notion of security. It can easily be seen that if one of the following weaknesses apply to a cipher, it cannot be called K-secure:

- Existence of key-recovering attacks faster than exhaustive search;
- Certain symmetry properties in the mapping (e.g., complementation property);
- Occurrence of non-negligible classes of weak keys (as in IDEA);
- related-key attacks.

K-security is essentially a relative measure. It is quite possible to build a K-secure block cipher with a 5-bit block and key length. The lack of security offered by such a scheme is due to its small dimensions, not to the fact that the scheme fails to meet the requirements imposed by these dimensions. Clearly, the longer the key, the higher the security requirements.

## 10.1.3  Hermetic block ciphers

It  is  possible  to  imagine  ciphers  that  have  certain  weaknesses  and  still  are  K-secure.  An example of such a weakness would be a block cipher with a block length larger than the key length  and  a  single  weak  key,  for  which  the  cipher  mapping  is  linear.  The  detection  of  the usage of the key would take at least a few encryptions, while checking whether the key is used would only take a single encryption.

If  this  cipher would be used for encipherment, this single weak key would pose no problem. However, used as a component in a larger scheme, for instance as the compression function of a hash function, this property could introduce a way to efficiently generate collisions.

For these reasons we introduce yet another security concept, denoted by the term hermetic.

Definition: A block cipher is hermetic if it does not have weaknesses that are not present for the majority of block ciphers with the same block and key length.

Informally,  a  block  cipher  is  hermetic  if  its  internal  structure  cannot  be  exploited  in  any application.

## 10.2  Goal

For all key and block lengths defined, the security goals are that the Rijndael cipher is :

- K-secure;
- Hermetic.

If Rijndael lives up to its goals, the strength against any known or unknown attacks is as good as can be expected from a block cipher with the given dimensions.

Authors: Joan Daemen Vincent Rijmen

The Rijndael Block Cipher

AES Proposal