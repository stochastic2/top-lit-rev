The essential idea is that **the twenty measurement bits contain only four independent bits of information**. The remaining information lets us identify and correct mistakes in the reports. Let me unpack that statement. Annotation 1

### 1. A simple example of classical error correction

Suppose we want to store one bit, but a stored bit might accidentally flip. We could store three copies:

\[
0\longmapsto 000,\qquad 1\longmapsto111.
\]

Only **000 and 111 are valid words**. If we read 010, we infer that the intended word was 000: correcting one bit makes it valid, whereas reaching 111 would require changing two bits.

This inference is called **decoding**. The extra copies provide **redundancy**.

Our graph uses the same principle, with a more structured set of valid words.

### 2. Which twenty-bit words are valid for our graph?

Imagine assigning a bit \(t_v\) to each of the five vertices. The bit on an edge is the difference, modulo two, between its endpoint bits:

\[
w_q=t_u\oplus t_v.
\]

Here \(\oplus\) means XOR:

- Equal endpoint bits give edge bit 0.
- Different endpoint bits give edge bit 1.

For example,

\[
w_7=t_a\oplus t_b,
\qquad
w_{11}=t_a\oplus t_c,
\qquad
w_8=t_b\oplus t_c.
\]

A **valid word** is any twenty-bit pattern that can arise this way.

We choose \(t_a=0\). The remaining four vertex bits can be chosen freely, giving

\[
2^4=16
\]

valid twenty-bit words. These sixteen patterns are the set \(\mathcal W\).

Thus, the situation is analogous to the repetition example:

| Example | Number of measured bits | Valid words |
|---|---:|---:|
| Three copies of one bit | 3 | 2 |
| Our graph | 20 | 16 |

Most twenty-bit strings are invalid. That restriction is what makes error correction possible.

### 3. What does “redundancy” look like here?

The edge bits must satisfy consistency relations.

For instance, edges 7 and 15 both connect a to b, so every valid word satisfies

\[
w_7=w_{15}.
\]

Also, going around the triangle a–b–c–a gives

\[
w_7\oplus w_8\oplus w_{11}=0.
\]

Indeed, substituting the endpoint expressions gives

\[
(t_a\oplus t_b)
\oplus(t_b\oplus t_c)
\oplus(t_a\oplus t_c)=0,
\]

because each vertex bit appears twice.

A faulty report can violate these relations. **The redundancy means that the reports constrain one another.** It does not mean that sixteen particular edge reports are individually unnecessary: we use all twenty together to protect the four independent bits.

### 4. A concrete faulty-readout example

Take the vertex assignment

\[
t=(0,1,0,0,0).
\]

Only b has bit 1. Therefore, the edges with bit 1 are precisely the eight edges incident on b:

\[
\{4,7,8,9,14,15,16,19\}.
\]

All other edges have bit 0. Call this ideal word w.

Now suppose report 7 is accidentally flipped from 1 to 0. The reported word m then has ones only at

\[
\{4,8,9,14,15,16,19\}.
\]

If we immediately used \(t_b=m_7\), we would infer \(t_b=0\), which is wrong.

Instead, we compare m against the sixteen valid words:

- The true word w differs from m at **one position**, edge 7.
- The all-zero valid word differs from m at **seven positions**.
- The other valid words are also too far away to qualify.

The decoder therefore selects w and repairs the faulty report before calculating the SWAP correction.

The repaired word is written

\[
\widehat w.
\]

**The hat means “the word inferred by our decoder.”** Under the assumed error bound, \(\widehat w=w\).

### 5. What exactly does the distance calculation do?

The **Hamming distance** between two words is the number of positions at which they differ:

\[
d_H(m,w)
=
\#\{q:m_q\ne w_q\}.
\]

For example,

\[
d_H(00110,01100)=2.
\]

Our decoding algorithm is simply:

1. List the sixteen valid words.
2. Count how many positions each one disagrees with m.
3. Keep the candidate with at most two disagreements.
4. Reject if no candidate exists.

This is a small, entirely classical calculation performed after the quantum measurements.

### 6. Why can there be only one candidate?

First, why do distinct valid words differ in at least eight positions?

Changing one vertex bit changes the bits on all edges incident on that vertex. There are four neighboring vertices, with two edges to each:

\[
4\times2=8
\]

changed edge bits.

More generally, if two vertex assignments differ on k vertices, their edge words differ on the edges crossing between those k vertices and the remaining \(5-k\). There are

\[
2k(5-k)
\]

such edges. For distinct assignments with \(t_a=0\), \(k=1,2,3,4\), giving distances

\[
8,\quad12,\quad12,\quad8.
\]

So distinct valid words are always separated by at least eight bit changes.

Now suppose two different valid words were both within two changes of m. Going from the first word to m, then from m to the second, would require at most

\[
2+2=4
\]

changes. But we just established that reaching another valid word requires at least eight. That is impossible.

Therefore, **if at most two reports have flipped, the true valid word is present among the candidates and is the unique candidate**.

### 7. Where this fits into ungauging

The sequence is

\[
\boxed{
\text{twenty reports }m
\ \longrightarrow\
\text{corrected word }\widehat w
\ \longrightarrow\
\text{inferred vertex bits }\widehat t
\ \longrightarrow\
\text{SWAP correction}.
}
\]

The first arrow is the additional protection against faults. The remaining arrows determine and apply the ordinary ungauging correction.

We use a two-error decoding radius because the complete protocol is being analyzed under a total budget of two faults. The graph’s classical redundancy protects this particular readout step; the other verification stages handle other ways the quantum circuit can fail.