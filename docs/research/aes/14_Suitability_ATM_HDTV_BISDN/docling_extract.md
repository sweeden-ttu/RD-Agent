## 14.  Suitability for ATM, HDTV, B-ISDN, voice and satellite

It was requested to give comments on the suitability of Rijndael to be used for ATM, HDTV, BISDN,  Voice  and  Satellite.  As  a  matter  of  fact,  the  only  thing  that  is  relevant  here,  is  the processor on which the cipher is implemented. As Rijndael can be implemented efficiently in software on a wide range of processors, makes use of a limited set of instructions and has sufficient parallelism to fully exploit modern pipelined multi-ALU processors, it is well suited for all mentioned applications.

For applications that require rates higher than 1 Gigabits/second, Rijndael can be implemented in dedicated hardware.