## 8.  Strength against known attacks

## 8.1  Symmetry properties and weak keys of the DES type

Despite  the  large  amount  of  symmetry,  care  has  been  taken  to  eliminate  symmetry  in  the behaviour of  the  cipher.  This  is  obtained  by  the  round  constants  that  are  different  for  each round. The fact that the cipher and its inverse use different components practically eliminates the possibility for weak and semi-weak keys, as existing for DES. The non-linearity of the key expansion practically eliminates the possibility of equivalent keys.

## 8.2  Differential and linear cryptanalysis

Differential  cryptanalysis  was  first  described  by  Eli  Biham  and  Adi  Shamir  [BiSh91].  Linear cryptanalysis was first described by Mitsuru Matsui [Ma94].

Chapter 5 of [Da95] gives a detailed treatment of difference propagation and correlation. To better  describe  the  anatomy  of  the  basic  mechanisms  of  linear  cryptanalysis  (LC)  and  of differential cryptanalysis (DC), new formalisms and terminology were introduced. With the aid of these it was, among other things, shown how input-output correlations over multiple rounds are  composed.  We  will  use  the  formalisms  of  [Da95]  in  the  description  of  DC  and  LC.  To provide the necessary background, Chapter 5 of [Da95] has been included in Annex.

## 8.2.1  Differential cryptanalysis

DC attacks  are  possible  if  there  are  predictable  difference  propagations  over  all  but  a  few (typically 2 or 3) rounds that have a prop ratio (the relative amount of all input pairs that for the given input difference give rise to the output difference) significantly larger than 2 1-n if n is the block length. A difference propagation is composed of differential trails, where its prop ratio is the  sum  of  the  prop  ratios  of  all  differential  trails  that  have  the  specified  initial  and  final difference patterns. To be resistant against DC, it is therefore a necessary condition that there are no differential trails with a predicted prop ratio higher than 2 1-n .

For Rijndael, we prove that there are no 4-round differential trails with a predicted prop ratio above 2 -150 (and no 8-round trails with a predicted prop ratio above 2 -300 ). For all block lengths of  Rijndael,  this  is  sufficient.  For  the  significance  of  these  predicted  prop  ratios,  we  refer  to Chapter 5 of [Da95]. The proof is given in Section 8.2.3.

In [LaMaMu91] it has been proposed to perform differential cryptanalysis with another notion of difference. This is especially applicable to ciphers where the key addition is not a simple EXOR operation. Although in Rijndael the keys are applied using EXORs, it was investigated whether attacks  could  be  mounted  using  another  notion  of  difference.  We  have  found  no  attack strategies better than using EXOR as the difference.

## 8.2.2  Linear cryptanalysis

LC  attacks  are  possible  if  there  are  predictable  input-output  correlations  over  all  but  a  few (typically 2 or 3) rounds significantly larger than 2 n/2 . An input-output correlation is composed of linear trails, where its correlation is the sum of the correlation coefficients of all linear trails that have the specified initial and final selection patterns. The correlation coefficients of the linear trails  are  signed  and  their  sign  depends  on  the  value  of  the  Round  Keys.  To  be  resistant against  LC,  it  is  a  necessary  condition  that  there  are  no  linear  trails  with  a  correlation coefficient higher than 2 n/2 .

For Rijndael, we prove that there are no 4-round linear trails with a correlation above 2 -75 (and no  8-round  trails  with  a  correlation  above  2 -150 ).  For  all  block  lengths  of  Rijndael,  this  is sufficient. The proof is given in Section 8.2.4.

## 8.2.3  Weight of differential and linear trails

In [Da95], it is shown that:

- The prop ratio of a differential trail can be approximated by the product of the prop ratios of its active S-boxes.
- The correlation of a linear trail can be approximated by the product of input-output correlations of its active S-boxes.

The wide trail strategy can be summarised as follows:

- Choose  an  S-box  where  the  maximum  prop  ratio  and  the  maximum  input-output correlation are as small as possible. For the Rijndael S-box this is respectively 2 -6 and 2 -3 .
- Construct the diffusion layer in such a way that there are no multiple-round trails with few active S-boxes.

We prove that the minimum number of active S-boxes in any 4-round differential or linear trail is 25. This gives a maximum prop ratio of 2 -150 for any 4-round differential trail and a maximum of 2 -75 for the correlation for any 4-round linear trail. This holds for all block lengths of Rijndael and is independent of the value of the Round Keys.

Note: the nonlinearity of an S-box chosen randomly from the set of possible invertible 8-bit Sboxes is expected to be less optimum. Typical values are 2 -5 to 2 -4 for the maximum prop ratio and 2 -2 for the maximum input-output correlation.

## 8.2.4  Propagation of patterns

For DC, the active S-boxes in a round are determined by the nonzero bytes in the difference of the states at the input of a round. Let the pattern that specifies the positions of the active Sboxes be denoted by the term (difference) activity pattern and let the (difference) byte weight be the number of active bytes in a pattern.

For LC, the active S-boxes in a round are determined by the nonzero bytes in the selection vectors (see Annex ) at the input of a round. Let the pattern that specifies the positions of the active  S-boxes  be  denoted  by  the  term  (correlation)  activity  pattern  and  let  the  (correlation) byte weight W(a) be the number of active bytes in a pattern a.

Moreover, let a column of an activity pattern with at least one active byte be denoted by active column.  Let  the  column  weight,  denoted  by  WC(a),  be  the  number  of  active  columns  in  a pattern. The byte weight of a column j of a, denoted by W(a)| j, is the number of active bytes in it.

The weight of a trail is the sum of the weights of its activity patterns at the input of each round.

Difference and  correlation activity patterns can be seen  as propagating through the transformations of the different rounds of the block cipher to form linear and differential trails. This is illustrated with an example in Figure 7.

Figure 7: Propagation of activity pattern (in grey) through a single round

<!-- image -->

The  different  transformations  of  Rijndael  have  the  following  effect  on  these  patterns  and weights:

- ByteSub and AddRoundKey: activity patterns, byte and column weight are invariant.
- ShiftRow: byte weight is invariant as there is no inter-byte interaction.
- MixColumn: column weight is invariant as there is no inter-column interaction.

ByteSub  and  AddRoundKey  do  not  play  a  role  in  the  propagation  of  activity  patterns  and therefore in this discussion the effect of a round is reduced to that  of  ShiftRow  followed  by MixColumn. In the following,  ByteSub  and  AddRoundKey  will  be  ignored.  MixColumn  has  a branch number equal to 5, implying:

- For any active column of a pattern  at  its  input  (or,  equivalently,  at  its  output),  the sum of the byte weights at input and output for this column is lower bounded by 5.

ShiftRow has the following properties:

- The column weight of a pattern at its output is lower bounded by the maximum of the byte weights of the columns of the pattern at its input.
- The column weight of a pattern at its input is lower bounded by the maximum of the byte weights of the columns of the pattern at its output.

This is thanks to the property that MixColumn permutes the bytes of a column to all different columns.

In our description, the activity pattern at the input of a round i is denoted by ai-1 and the activity pattern after applying ShiftRow of round i is denoted by bi-1. The initial round is numbered 1 and the initial difference pattern is denoted by a0. Clearly, ai and bi are separated by ShiftRow and have the same byte weight, bj-1 and aj are separated by MixColumn and have the same column weight. The weight of an m-round trail is given by the sum of the weights of a0 to am-1 . The propagation properties are illustrated in Figure 8. In this figure, active bytes are indicated in dark grey, active columns in light grey.

Figure 8: Propagation of patterns in a single round.

<!-- image -->

Theorem 1: The weight of a two-round trail with Q active columns at the input of the second round is lower bounded by 5Q.

Proof: The fact that MixColumn has a Branch Number equal to 5 implies that sum of the byte weights of each column in b0 and a1 is lower bounded by 5. If the column weight of a1 is Q, this gives a lower bounded of 5Q for the sum of the byte weights of  b0 and a1 . As a0 and b0 have the same byte weight, the lower bounded is also valid for the sum of the weights a0 and a1 , proving the theorem.

QED

Theorem 1 is illustrated in Figure 9.

Figure 9: Illustration of Theorem 1 with Q = 2.

<!-- image -->

From this it follows that any two-round trail has at least 5 active S-boxes.

Lemma 1: in a two-round trail, the sum of the number of active columns at its input and the number of active columns at its output is at least 5. In other words, the sum of the columns weights of a0 and a2 is at least 5.

Proof: ShiftRow moves all bytes in a column of ai to different columns in bi and vice versa. It follows  that  the  column  weight  of ai  is  lower  bounded  the  byte  weights  of  the  individual columns of bi. Likewise the column weight of bi is lower bounded by the byte weights of the individual columns of ai.

In a trail, at least one column of a1 (or equivalently b0 ) is active. Let this column be denoted by 'column g'. Because MixColumn has a branch number of 5, the sum of the byte weights of column g in b0 and column g  in a1 is lower bounded by 5. The column weight of a0 is lower bounded by the byte weight of column g of b0. The column weight of b1 is lower bounded by the byte weight of column g of a1. It follows that the sum of the column weights of  a0 and b1 is lower bounded by 5. As the column weight of a2 is equal to that of b1, the lemma is proven.

QED

Lemma 1 is illustrated in Figure 10.

Figure 10: Illustration of Lemma 1 with one active column in a1.

<!-- image -->

Theorem 2: Any trail over four rounds has at least 25 active bytes.

Proof: By applying Theorem 1 on the first two rounds (1 and 2) and on the last two rounds (3 and 4), it follows that the byte weight of the trail is lower bounded by the sum of the column weight of a1 and a3 multiplied by 5. By applying Lemma 1, the sum of the column weight of  a1 and a3 is lower bounded by 5. From this it follows that the byte weight of the four-round trail is lower bounded by 25.

QED

Theorem 2 is illustrated in Figure 11.

Figure 11: Illustration of Theorem 2.

<!-- image -->

## 8.3  Truncated differentials

The  concept  of  truncated  differentials  was  first  published  by  Lars  Knudsen  [Kn95].  The corresponding class of attacks exploit the fact that in some ciphers differential  trails  tend  to cluster  [Da95]  (see  Annex  ).  Clustering  takes  place  if  for  certain  sets  of  input  difference patterns and output difference patterns, the number of differential trails is exceedingly large. The expected probability that a differential trail stays within the boundaries of the cluster can be  computed  independently  of  the  prop  ratios  of  the  individual  differential  trails.  Ciphers  in which all transformation operate on the state in well aligned blocks are prone to be susceptible to this type of attack. Since this is the case for Rijndael, all transformations operating on bytes rather than individual bits, we investigated its resistance against 'truncated differentials'. For 6 rounds or more, no attacks faster than exhaustive key search have been found.

## 8.4  The Square attack

The 'Square' attack is a dedicated attack on Square that exploits the byte-oriented structure of Square cipher and was published in the paper presenting the Square cipher itself [DaKnRi97]. This attack is  also  valid  for  Rijndael,  as  Rijndael  inherits  many  properties  from  Square.  We describe this attack in this section.

The attack is a chosen plaintext attack and is independent of the specific choices of ByteSub, the  multiplication  polynomial  of  MixColumn  and  the  key  schedule.  It  is  faster  than  an exhaustive key search for Rijndael versions of up to 6 rounds. After describing the basic attack on 4 rounds, we will show how it can be extended to 5 and 6 rounds. For 7 rounds or more, no attacks faster than exhaustive key search have been found.

## 8.4.1  Preliminaries

Let a Λ -set be a set of 256 states that are all different in some of the state bytes (the active) and all equal in the other state bytes (the passive) We have

$$\forall x , y \in \Lambda \colon \begin{cases} x _ { i , j } \not \cong y _ { i , j } \text { if } ( i , j ) \text { active } \\ x _ { i , j } = y _ { i , j } \text { else } \end{cases} .$$

.

Applying the transformations ByteSub or AddRoundKey on (the elements of) a Λ -set results in  a  (generally  different) Λ -set  with  the  positions  of  the  active  bytes  unchanged.  Applying ShiftRow results in a Λ -set in which the active bytes are transposed by ShiftRow. Applying MixColumn to a Λ -set does not necessarily result in a Λ -set.  However, since every output byte of MixColumn is a linear combination (with invertible coefficients) of the four input bytes in the same column, an input column with a single active byte gives rise to an output column with all four bytes active.

## 8.4.2  The basic attack

Consider a Λ -set  in  which  only  one  byte  is  active.  We  will  now  trace  the  evolution  of  the positions of the active bytes through 3 rounds. MixColumn of the 1 st round converts the active byte to a complete column of active bytes. The four active bytes of this column are spread over four distinct columns by ShiftRow of the 2 nd round. MixColumn of the 2 nd round subsequently converts this to 4 columns of only active bytes. This stays a Λ -set until the input of MixColumn of the 3 rd round.

Since the bytes of this (in fact, any) Λ -set, denoted by a, range over all possible values and are therefore balanced over the Λ -set, we have

$$\bigoplus _ { b \text {-MixColumn} ( a ) \text {a} \in \Lambda } b _ { i , j } & = \bigoplus _ { a \in \Lambda } \left ( 2 a _ { i , j } \oplus 3 a _ { i + 1 , j } \oplus a _ { i + 2 , j } \oplus a _ { i + 3 , j } \right ) \\ & = 2 \bigoplus _ { a \in \Lambda } a _ { i , j } \oplus 3 \bigoplus _ { a \in \Lambda } a _ { i + 1 , j } \oplus \bigoplus _ { a \in \Lambda } a _ { i + 2 , j } \oplus \bigoplus _ { a \in \Lambda } a _ { i + 3 , j } \\ & = 0 \oplus 0 \oplus 0 \oplus 0 = 0$$

Hence,  all  bytes  at  the  input  of  the  4 th round  are  balanced.  This  balance  is  in  general destroyed by the subsequent application of ByteSub.

We assume the 4 th round  is  a  final  round,  i.e.,  it  does  not  include  a  MixColumn  operation. Every output byte of the 4 th round depends on only one input byte of the 4 th round. Let a be the output of the 4 th round, b its output and k the Round Key of the 4 th round. We have:

$$a _ { i , j } = S b o x { \left ( b _ { i ^ { \prime } , j ^ { \prime } } \right ) } \ominus k _ { i , j } \, .$$

By assuming a value for k i j , , the value of bi j ′ ′ , for all elements of the Λ -set can be calculated from the ciphertexts. If the values of this byte are not balanced over Λ , the assumed value for the key byte was wrong. This is expected to eliminate all but approximately 1 key value. This can be repeated for the other bytes of k.

## 8.4.3  Extension by an additional round at the end

If an additional round is added, we have to calculate the above value of bi j ′ ′ , from the output of the 5th round instead of the 4th round. This can be done by additionally assuming a value for a  set  of  4  bytes  of  the  5 th Round  Key.  As  in  the  case  of  the  4-round  attack,  wrong  key assumptions are eliminated by verifying that bi j ′ ′ , is not balanced.

In  this  5-round  attack 2 40 key  values  must  be  checked, and this must be repeated 4  times. Since by checking a single Λ -set leaves only 1/256 of the wrong key assumptions as possible candidates, the Cipher Key can be found with overwhelming probability with only 5 Λ -sets.

## 8.4.4  Extension by an additional round at the beginning

The basic idea is to choose a set of plaintexts that results in a Λ -set at the output of the 1 st round with a single active S-box. This requires the assumption of values of four bytes of the Round Key that is applied before the first round.

If the intermediate state after MixColumn of the 1 st round has only a single active byte, this is also the case for the input of the 2 nd round. This imposes the following conditions on a column of  four  input  bytes  of  MixColumn  of  the  second  round:  one  particular  linear  combination  of these  bytes  must  range  over  all  256  possible  values  (active)  while  3  other  particular  linear combinations must be constant for all 256 states. This imposes identical conditions on 4 bytes, in different positions at the input of ShiftRow of the first round. If the corresponding bytes of the  first  Round  Key  are  known,  these  conditions  can  be  converted  to  conditions  on  four plaintext bytes.

Now  we  consider  a  set  of 2 32 plaintexts,  such  that  one  column  of  bytes  at  the  input  of MixColumn of the first round range over all possible values and all other bytes are constant.

Now, an assumption is made for the  value  of  the  4  bytes  of  the  relevant  bytes  of  the  first Round Key. From the set of 2 32 available plaintexts, a set of 256 plaintexts can be selected that result in a Λ -set at the input of round 2. Now the 4-round attack can be performed. For the given key assumption, the attack can be repeated for a several plaintext sets. If the byte values of the last Round Key are not consistent, the initial assumption must have been wrong. A  correct  assumption  for  the  32  bytes  of  the  first  Round  Key  will  result  in  the  swift  and consistent recuperation of the last Round Key.

## 8.4.5  Working factor and memory requirements for the attacks

Combining  both  extensions  results  in  a  6  round  attack.  Although  infeasible  with  current technology,  this  attack  is  faster  than  exhaustive  key  search,  and  therefore  relevant.  The working factor and memory requirements are summarised in Figure 12. For the different block lengths of Rijndael no extensions to 7 rounds faster than exhaustive key search have been found.

Figure 12: Complexity of the Square attack applied to Rijndael.

| Attack                 | # Plaintexts   | # Cipher executions   | Memory   |
|------------------------|----------------|-----------------------|----------|
| Basic (4 rounds)       | 2 9            | 2 9                   | small    |
| Extension at end       | 2 11           | 2 40                  | small    |
| Extension at beginning | 2 32           | 2 40                  | 2 32     |
| Both Extensions        | 2 32           | 2 72                  | 2 32     |

## 8.5  Interpolation attacks

In [JaKn97] Jakobsen and Knudsen introduced a new attack on block ciphers. In this attack, the attacker constructs polynomials using cipher input/output pairs. This attack is feasible if the components in the cipher have a compact algebraic expression and can be combined to give expressions  with  manageable  complexity.  The  basis  of  the  attack  is  that  if  the  constructed polynomials (or rational expressions) have a small degree, only few cipher input/output pairs are necessary to solve for the (key-dependent) coefficients of the polynomial. The complicated expression of the S-box in GF(2 8 ), in combination with the effect of the diffusion layer prohibits these types of attack for more than a few rounds. The expression for the S-box is given by:

$$6 3 + 8 f \, x ^ { 1 2 7 } + b 5 \, x ^ { 1 9 1 } + 0 1 \, x ^ { 2 2 3 } + f 4 \, x ^ { 2 3 9 } + 2 5 \, x ^ { 2 4 7 } + f 9 \, x ^ { 2 5 1 } + 0 9 \, x ^ { 2 5 3 } + 0 5 \, x ^ { 2 5 4 }$$

## 8.6  Weak keys as in IDEA

The weak keys discussed in this subsection are keys that result in a block cipher mapping with detectable  weaknesses.  The  best  known  case  of  weak  keys  are  those  of  IDEA  [Da95]. Typically, this weakness occurs for ciphers in which the non-linear operations depends on the actual key value. This is not the case for Rijndael, where keys are applied using the EXOR and all non-linearity is in the fixed S-box. In Rijndael, there is no restriction on key selection.

## 8.7  Related-key attacks

In [Bi96], Eli Biham introduced a related-key attack. Later it was demonstrated by John Kelsey, Bruce  Schneier  and  David  Wagner  that  several  ciphers  have  related-key  weaknesses  In [KeScWa96].

In related-key attacks, the cryptanalyst can do cipher operations using different (unknown or partly  unknown)  keys  with  a  chosen  relation.  The  key  schedule  of  Rijndael,  with  its  high diffusion and non-linearity, makes it very improbable that this type of attack can be successful for Rijndael.