## 9.  Expected strength

Rijndael  is  expected,  for  all  key  and  block  lengths  defined,  to  behave  as  good  as  can  be expected from a block cipher with the given block and key lengths. What we mean by this is explained in Section 10.

This  implies  among  other  things,  the  following.  The  most  efficient  key-recovery  attack  for Rijndael is exhaustive key search. Obtaining information from given plaintext-ciphertext pairs about other plaintext-ciphertext pairs cannot be done more efficiently than by determining the key by exhaustive key search. The expected effort of exhaustive key search depends on the length of the Cipher Key and is:

- for a 16-byte key, 2 127 applications of Rijndael;
- for a 24-byte key, 2 191 applications of Rijndael;
- for a 32-byte key, 2 255 applications of Rijndael.

The rationale for this is that a considerable safety margin is taken with respect to all known attacks. We do however realise that it is impossible to make non-speculative statements on things unknown.