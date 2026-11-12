# Chains, cohomology, and the cup product in the toric code

**Source:** Section III.3.1 of [arXiv:2602.12228v1](https://arxiv.org/html/2602.12228v1), *Non-Abelian Quantum Low-Density Parity Check Codes and Non-Clifford Operations from Gauging Logical Gates via Measurements*. The [local LaTeX source](../arXiv-2602.12228v1/main.tex) contains the square-lattice cup-product definition.

**Background assumed:** the toric code, Pauli strings, stabilizers, and logical operators, as introduced in [Non-Abelian anyons from gauging logical gates](non-abelian-anyons-from-gauging-v2.md). No prior knowledge of homology or cohomology is assumed.

This note builds the language needed to start reading “Non-Abelian Codes from Poincaré Duality.” It covers chains, cochains, homology, cohomology, the local cup-product definition, and its compatibility with the coboundary map. Poincaré duality and the gauging construction come later. Section 7 develops cocycles, coboundaries, and the Leibniz rule through explicit lattice calculations.

## 1. A chain is a selection of lattice cells

Take the usual toric code: vertices, edges carrying qubits, and square plaquettes.

A **1-chain** is a selection of edges. Mathematicians write it as a sum:

\[
b=e_1+e_2+e_3.
\]

For a qubit code, all coefficients are in \(\mathbb F_2=\{0,1\}\), with addition modulo two. Thus selecting an edge twice cancels it:

\[
e+e=0.
\]

This exactly matches multiplication of Pauli strings:

\[
Z_b=Z_{e_1}Z_{e_2}Z_{e_3},
\qquad
Z_bZ_{b'}=Z_{b+b'}.
\]

Similarly, a **0-chain** selects vertices, and a **2-chain** selects plaquettes. The spaces of these objects are denoted \(D_0,D_1,D_2\).

The word “chain” does not require the selected edges to form one connected string. Any selection is allowed.

## 2. The boundary map finds endpoints

The operation \(\partial\) takes the boundary of a selected object:

- The boundary of an edge consists of its two endpoints.
- The boundary of a plaquette consists of its four edges.
- The boundary of a string consists of the vertices touched an odd number of times.

Internal endpoints cancel modulo two. Consequently, a closed loop \(b\) satisfies

\[
\partial b=0.
\]

Such a chain is called a **cycle**.

A plaquette boundary is a cycle too. More generally, the boundary of any patch of plaquettes is a closed loop. This gives

\[
\partial_1\partial_2=0:
\]

**the boundary of a boundary is zero.** The subscripts identify the input dimension: \(\partial_2\) takes plaquettes to edges, and \(\partial_1\) takes edges to vertices.

The sequence

\[
D_2\xrightarrow{\partial_2}D_1
\xrightarrow{\partial_1}D_0
\]

is called a **chain complex**. For the toric code, it records “plaquettes → edges → vertices.”

## 3. Homology means closed strings, modulo stabilizers

Consider a \(Z\) string \(Z_b\). It commutes with every \(X\) star precisely when it has no endpoints:

\[
\partial_1b=0.
\]

But some closed \(Z\) strings are just products of plaquette stabilizers. Their supports have the form

\[
b=\partial_2s,
\]

where \(s\) is a selection of plaquettes.

Therefore the space of distinct \(Z\)-logical operators is

\[
\boxed{
H_1=\frac{\ker\partial_1}{\operatorname{im}\partial_2}.
}
\]

Read this as: take all closed \(Z\) strings, and identify two strings whenever they differ by a product of \(Z\) stabilizers.

Here **kernel**, written \(\ker\), means “objects mapped to zero,” and **image**, written \(\operatorname{im}\), means “objects produced by the map.” The quotient does not mean numerical division: it groups together objects equivalent under stabilizer multiplication.

On a torus, a small contractible loop represents zero in \(H_1\). A loop winding around the torus represents a nonzero element.

An element of \(H_1\) is a **class of equivalent loops**, rather than one particular loop. A particular loop is a **representative** of that class.

## 4. A cochain assigns bits to cells

A chain selects cells. A **cochain** is a linear rule that evaluates selections.

Concretely, a 1-cochain \(\mathbf a\) assigns a bit \(\mathbf a(e)\) to each edge. Its evaluation on a chain is

\[
\mathbf a(b)=\sum_e \mathbf a(e)b_e\pmod2,
\]

where \(b_e\) is 1 if the chain selects edge \(e\), and 0 otherwise. This counts the overlap between their selected edges, modulo two.

The paper associates a 1-cochain with an \(X\) operator:

\[
X_{\mathbf a}=\prod_e X_e^{\mathbf a(e)}.
\]

Thus

\[
Z_bX_{\mathbf a}
=(-1)^{\mathbf a(b)}X_{\mathbf a}Z_b.
\]

So **evaluating a cochain on a chain computes Pauli commutation**: overlap on an odd number of qubits gives anticommutation.

Chains and cochains can look like identical bit vectors. The distinction is their role: one is an object being evaluated; the other is an evaluator. Their maps consequently run in opposite directions.

The space of \(n\)-cochains is denoted \(D^n\). The paper also uses \(C^n\) when discussing the cup product; the superscript has the same meaning there: cochains of degree \(n\).

## 5. The coboundary map is the transpose of the boundary map

The cochain counterpart of \(\partial\) is \(d\), called the **coboundary**:

\[
D^0\xrightarrow{d_0}D^1
\xrightarrow{d_1}D^2,
\qquad
d_0=\partial_1^{T},\quad d_1=\partial_2^{T}.
\]

The superscript \(T\) means matrix transpose.

A 0-cochain \(f\) assigns bits to vertices. On an edge joining \(u\) and \(v\),

\[
(df)(uv)=f(u)+f(v).
\]

Selecting just one vertex gives its four-edge star.

A 1-cochain \(\mathbf a\) assigns bits to edges. On a plaquette \(p\),

\[
(d\mathbf a)(p)=\sum_{e\in\partial p}\mathbf a(e).
\]

This tests whether the selected edges overlap that plaquette in even or odd parity.

Therefore \(d\mathbf a=0\) means that \(X_{\mathbf a}\) commutes with every \(Z\) plaquette. Such an \(\mathbf a\) is a **cocycle**.

An operator with support \(\mathbf a=df\) is a product of star stabilizers. Such a cochain is a **coboundary**. Just as \(\partial^2=0\), we have \(d^2=0\), so every coboundary is a cocycle.

Consequently,

\[
\boxed{
H^1=\frac{\ker d_1}{\operatorname{im}d_0}
}
\]

describes \(X\)-logical operators modulo \(X\) stabilizers.

| Mathematical object | Toric-code meaning |
|---|---|
| 1-chain | Support of a \(Z\) string |
| 1-cycle | \(Z\) string with no star violations |
| 1-boundary | Product of \(Z\) plaquette stabilizers |
| \(H_1\) | \(Z\) logicals modulo stabilizers |
| 1-cochain | Support of an \(X\) operator |
| 1-cocycle | \(X\) operator with no plaquette violations |
| 1-coboundary | Product of \(X\) star stabilizers |
| \(H^1\) | \(X\) logicals modulo stabilizers |

Geometrically, an \(X\) cocycle forms closed strings on the **dual lattice**: its path crosses the physical edges carrying its \(X\) operators.

## 6. The cup product: a local rule for combining cochains

The **cup product**, denoted \(\smile\), combines two assignments of bits to lattice cells into a new assignment of bits. The degrees add:

\[
\boxed{
\smile:D^p\times D^q\longrightarrow D^{p+q}.
}
\]

Here \(p,q\) denote degrees, not particular plaquettes. For example, two edge assignments, each of degree 1, combine into a plaquette assignment of degree 2:

\[
\mathbf a\smile\mathbf b\in D^2.
\]

The paper specifies the operation using pictures. We must distinguish the rule for **single-cell indicator cochains**, shown in the pictures, from its extension to arbitrary cochains, which may select many cells.

### What the bold symbols mean

For an edge \(e\), the bold symbol \(\mathbf e\) means the cochain that assigns 1 to that particular edge and 0 to every other edge.

Similarly, \(\mathbf p\) assigns 1 to one particular plaquette and 0 to all other plaquettes.

Thus

\[
\mathbf e\smile\mathbf e'=\mathbf p
\]

means: combining these two particular edge indicators gives an assignment with value 1 on this plaquette and 0 elsewhere.

The output is a **plaquette cochain**. It is not the four-edge boundary of that plaquette, and this equation does not itself denote multiplication of Pauli operators.

For arbitrary edge cochains \(\mathbf a,\mathbf b\), the output \(\mathbf a\smile\mathbf b\) assigns a bit to **each plaquette**.

### Label one square

Use these corner and edge labels:

```text
                 top
          D o-------------o C
            |             |
       left |      p      | right
            |             |
          A o-------------o B
                bottom
```

The paper makes a consistent directional choice: **rightwards and upwards**. There are two paths from the bottom-left corner \(A\) to the top-right corner \(C\):

```text
Path 1: A --bottom--> B --right--> C

Path 2: A --left----> D --top----> C
```

The two edge-edge pictures in the paper correspond to these two paths. In each path, the **first edge belongs to the first input of the cup product**, and the **second edge belongs to the second input**.

### The first edge-edge picture: bottom, then right

The first picture says

\[
\mathbf{bottom}\smile\mathbf{right}=\mathbf p.
\]

```text
          D o-------------o C
            |             ^
            |      p      |  second input: e'
            |             |
          A o============>o B
              first input: e
```

### The second edge-edge picture: left, then top

The second picture says

\[
\mathbf{left}\smile\mathbf{top}=\mathbf p.
\]

```text
              second input: e'
          D o============>o C
            ^             |
 first      |      p      |
 input: e   |             |
          A o-------------o B
```

The arrows are explanatory: they show the paper's right/up convention.

These are the **two allowed ordered edge pairs** for this plaquette. Other ordered pairs give zero on this plaquette. For example,

\[
\mathbf{bottom}\smile\mathbf{top}=0,
\qquad
\mathbf{right}\smile\mathbf{bottom}=0.
\]

Reversing an allowed pair does not preserve the result. At the level of individual cochains, the order of the cup-product inputs matters.

### From the pictures to arbitrary edge cochains

The crucial word is **bilinear**. It means the product distributes over sums in each input:

\[
(\mathbf a+\mathbf a')\smile\mathbf b
=\mathbf a\smile\mathbf b+\mathbf a'\smile\mathbf b,
\]

and likewise for sums in the second input. Since every edge cochain is a sum of edge indicators, the pictures determine the whole operation.

On our square, the rule becomes

\[
\boxed{
(\mathbf a\smile\mathbf b)(p)
=
\mathbf a(\mathrm{bottom})\,\mathbf b(\mathrm{right})
+\mathbf a(\mathrm{left})\,\mathbf b(\mathrm{top})
\pmod2.
}
\]

Read it as two tests:

1. Does the first input select the bottom edge **and** the second input select the right edge?
2. Does the first input select the left edge **and** the second input select the top edge?

Each successful test contributes 1. Add the contributions modulo two. Ordinary multiplication of bits acts like **AND**, while addition modulo two acts like **XOR**:

| Bottom–right test | Left–top test | Output on \(p\) |
|---:|---:|---:|
| 0 | 0 | 0 |
| 1 | 0 | 1 |
| 0 | 1 | 1 |
| 1 | 1 | 0 |

So “both paths contribute” gives zero, because \(1+1=0\).

For a concrete example, suppose

\[
\mathbf a=\mathbf{bottom}+\mathbf{left},
\qquad
\mathbf b=\mathbf{right}+\mathbf{top}.
\]

Expanding gives

\[
\begin{aligned}
\mathbf a\smile\mathbf b
={}&\mathbf{bottom}\smile\mathbf{right}
+\mathbf{bottom}\smile\mathbf{top}\\
&+\mathbf{left}\smile\mathbf{right}
+\mathbf{left}\smile\mathbf{top}.
\end{aligned}
\]

The four terms are respectively

\[
\mathbf p+0+0+\mathbf p=0.
\]

That cancellation is part of the definition, not an exception.

For a larger lattice, apply the same formula to every square. The result is a pattern of 0s and 1s on plaquettes. The product is **local** because the value on a square uses only the inputs on its own edges.

### The vertex–plaquette pictures

The next two pictures define products between a vertex indicator, which has degree 0, and a plaquette indicator, which has degree 2. The output has degree \(0+2=2\), so it is again a plaquette cochain.

The first says

\[
\mathbf A\smile\mathbf p=\mathbf p,
\]

where \(A\) is the **bottom-left vertex**:

```text
          D o-------------o C
            |             |
            |      p      |
            |             |
          A *-------------o B

       vertex first, plaquette second
       * marks the selected vertex
```

The second says

\[
\mathbf p\smile\mathbf C=\mathbf p,
\]

where \(C\) is the **top-right vertex**:

```text
          D o-------------* C
            |             |
            |      p      |
            |             |
          A o-------------o B

       plaquette first, vertex second
       * marks the selected vertex
```

Other vertices give zero for the corresponding ordering. In particular,

\[
\mathbf C\smile\mathbf p=0,
\qquad
\mathbf p\smile\mathbf A=0.
\]

For arbitrary vertex values \(f\) and plaquette values \(\mathbf c\), these rules say

\[
(f\smile\mathbf c)(p)=f(A)\mathbf c(p),
\]

\[
(\mathbf c\smile f)(p)=\mathbf c(p)f(C).
\]

Placing the vertex cochain **first** samples the starting corner; placing it **second** samples the ending corner.

### The rules in the text below the pictures

For a horizontal edge, its starting vertex is on the left and its ending vertex is on the right:

```text
       start                 end
         u o------ e ------o v
                 ---->
```

For a vertical edge, its starting vertex is below and its ending vertex is above.

The rules are

\[
\mathbf u\smile\mathbf e=\mathbf e,
\qquad
\mathbf e\smile\mathbf v=\mathbf e.
\]

For general cochains,

\[
(f\smile\mathbf a)(e)
=f(\mathrm{start}(e))\,\mathbf a(e),
\]

\[
(\mathbf a\smile f)(e)
=\mathbf a(e)\,f(\mathrm{end}(e)).
\]

For two vertex cochains, the product is simply pointwise multiplication:

\[
(f\smile g)(v)=f(v)g(v).
\]

This explains the paper's formula

\[
\mathbf v\smile\mathbf w=\delta_{v,w}\mathbf v.
\]

The symbol \(\delta_{v,w}\) is 1 when the two vertices are the same and 0 otherwise.

These rules have a common pattern: **split the output cell into an initial piece for the first input and a final piece for the second input**.

For an edge, that is “starting vertex + edge” or “edge + ending vertex.” For a square, it is “starting vertex + square,” “two successive edges,” or “square + ending vertex.”

### Why these particular pairs?

This is a chosen lattice convention, not something that follows merely from two edges touching. Bottom and left touch, for example, but their ordered pair does not contribute. The definition selects successive pieces of the two right/up paths across the square.

The convention is useful because it makes the cup product compatible with the coboundary operation \(d\). The next equation in the paper expresses that compatibility:

\[
d(\mathbf a\smile\mathbf b)
=d\mathbf a\smile\mathbf b
+\mathbf a\smile d\mathbf b.
\]

This is the **Leibniz rule**, a discrete product rule. Its consequences for cohomology are the next topic. For understanding the figure itself, the operation is already completely specified: every square receives the parity of the two allowed contributions, **first-input bottom with second-input right, and first-input left with second-input top**.

## 7. Compatibility with d: cocycles, coboundaries, and the Leibniz rule

The goal is to understand why the cup product can describe cohomology classes, rather than merely particular patterns of selected cells. We first make the distinction between a cochain, a cocycle, and a coboundary concrete. All sums below are modulo two.

### A cochain is an arbitrary pattern; a cocycle passes a test

A 1-cochain \(\mathbf a\) assigns 0 or 1 to every edge. Associate it with an operator that puts \(X\) on the edges assigned 1.

For example, select just the edge separating two plaquettes \(p,q\):

```text
          o---------o---------o
          |         |         |
          |    p    X    q    |
          |         |         |
          o---------o---------o
```

Call the selected edge \(e_0\). In this example, \(\mathbf a\) is the single **basis cochain** \(\mathbf e_0\):

\[
\mathbf a=\mathbf e_0,
\qquad
\mathbf a(e)=
\begin{cases}
1 & e=e_0,\\
0 & e\ne e_0.
\end{cases}
\]

There are three related but distinct objects:

| Notation | Meaning |
|---|---|
| \(e_0\in D_1\) | Basis chain selecting the edge |
| \(\mathbf e_0\in D^1\) | Basis cochain testing whether a chain contains that edge |
| \(X_{\mathbf e_0}=X_{e_0}\) | Physical \(X\) operator on the edge's qubit |

In general, \(\mathbf a\) may be a sum of many basis cochains. It does not always select just one edge.

The coboundary tests every plaquette:

\[
(d\mathbf a)(p)
=\sum_{e\in\partial p}\mathbf a(e).
\]

Here the marked edge belongs to both plaquettes, giving

\[
(d\mathbf a)(p)=1,
\qquad
(d\mathbf a)(q)=1.
\]

Equivalently,

\[
d\mathbf a=\mathbf p+\mathbf q.
\]

The output is a **2-cochain** assigning 1 to those two plaquettes and 0 elsewhere. In code language, it records the plaquette syndrome of the \(X\) pattern: the single \(X\) anticommutes with both plaquette checks and creates two excitations when applied to a ground state.

A **cocycle** is an edge cochain satisfying

\[
\boxed{d\mathbf a=0.}
\]

Every plaquette then has even overlap with the \(X\) pattern. The operator creates no plaquette excitations. Thus:

- **Cochain:** any edge pattern.
- **Cocycle:** an edge pattern with zero plaquette syndrome.

A cocycle need not be a nontrivial logical operator. Stabilizers also have zero syndrome.

### What (df)(e) means: no product of vertices

Take a **0-cochain** \(f\), which assigns a bit to each vertex. Consider an edge \(e\) joining vertices \(u,v\):

```text
       u o-------- e --------o v
```

Its coboundary \(df\) is an assignment of bits to edges, with

\[
\boxed{(df)(e)=f(u)+f(v)\pmod2.}
\]

Each pair of parentheses denotes **evaluation**:

- \(f(u)\) is the bit assigned to vertex \(u\).
- \(f(v)\) is the bit assigned to vertex \(v\).
- \((df)(e)\) is the bit the resulting edge cochain assigns to edge \(e\).

Sometimes an edge joining \(u,v\) is written \(uv\), leading to the notation \((df)(uv)\). Here \(uv\) is just an edge label, **not multiplication of vertices**. We use the label \(e\) to avoid that ambiguity.

| \(f(u)\) | \(f(v)\) | \((df)(e)\) |
|---:|---:|---:|
| 0 | 0 | 0 |
| 1 | 0 | 1 |
| 0 | 1 | 1 |
| 1 | 1 | 0 |

Thus \(df\) selects exactly the edges whose endpoints have different bits.

This follows from the relation between boundary and coboundary:

\[
(df)(e)=f(\partial e).
\]

The boundary of an edge is its two endpoints, \(\partial e=u+v\). Since a cochain evaluates sums linearly,

\[
f(\partial e)=f(u+v)=f(u)+f(v).
\]

The expression \(u+v\) is a **0-chain selecting both vertices**. No cup product is involved in this calculation.

### A coboundary is a pattern built from stars

Select just one vertex with \(f\):

```text
                    0
                    |
                    |
          0---------1---------0
                    |
                    |
                    0
```

Every incident edge connects 1 to 0. Consequently, \(df\) selects its four-edge star:

```text
                    o
                    X
                    |
          o----X----o----X----o
                    |
                    X
                    o
```

The corresponding operator is

\[
X_{df}=A_v,
\]

where \(A_v\) denotes the star stabilizer at the selected vertex \(v\). If \(f\) selects several vertices,

\[
X_{df}=\prod_{v:f(v)=1}A_v.
\]

Edges joining two selected vertices cancel because their endpoint values give \(1+1=0\). This matches the cancellation when neighboring stars are multiplied.

A **1-coboundary** is any edge cochain that can be written

\[
\boxed{\mathbf a=df}
\]

for some vertex assignment \(f\). In code language, it is the support of a product of \(X\)-star stabilizers.

The word “coboundary” describes how a cochain is produced. A general \(d\mathbf a\) is a 2-coboundary, whereas \(df\) is a 1-coboundary. The input degree determines the output degree.

### Every coboundary is a cocycle

Give the corners of a square arbitrary vertex values:

```text
          D o-------------o C
            |             |
            |      p      |
            |             |
          A o-------------o B
```

For the edge assignment \(df\), its parity around the square is

\[
\begin{aligned}
(d(df))(p)
={}&[f(A)+f(B)]+[f(B)+f(C)]\\
&+[f(C)+f(D)]+[f(D)+f(A)].
\end{aligned}
\]

Each vertex value occurs twice, so everything cancels:

\[
\boxed{d(df)=0.}
\]

This is the concrete meaning of \(d^2=0\). In code language, every product of \(X\) stabilizers commutes with every \(Z\) plaquette.

The converse fails: some cocycles cannot be built from stars. Those are the nontrivial logical patterns.

### Closed dual strings make the distinction visible

An \(X\) string follows a path on the **dual lattice**, placing \(X\) on each physical edge crossed by that path. For one plaquette:

```text
                 o---------o
                 |         |
     dual path --X----+-----X--
                 |         |
                 o---------o
```

The path enters through one edge and exits through another. That plaquette sees two \(X\) operators, so its parity is zero. At an endpoint of an open dual path, a plaquette sees only one crossing, so its parity is one.

- An open dual string has a nonzero syndrome.
- A closed dual string is a cocycle.
- A small closed dual loop surrounding one vertex is a star, hence a coboundary.
- A dual loop winding around the torus is a cocycle that is not a coboundary.

This separates **zero syndrome** from **trivial logical action**:

| \(X\) pattern | Cocycle? | Coboundary? |
|---|---|---|
| One edge | No | No |
| One star | Yes | Yes |
| Product of stars | Yes | Yes |
| Noncontractible dual loop | Yes | No |

The empty pattern is both a cocycle and a coboundary.

### Cohomology identifies patterns differing by stars

Suppose two zero-syndrome patterns satisfy

\[
\mathbf a'=\mathbf a+df.
\]

Their operators obey

\[
X_{\mathbf a'}=X_{\mathbf a}X_{df}.
\]

Since \(X_{df}\) is a stabilizer product, they act identically on the code space. Thus

\[
H^1=\frac{\{\text{1-cocycles}\}}{\{\text{1-coboundaries}\}}
\]

means: keep the zero-syndrome patterns, but regard two patterns as equivalent when they differ by stars.

We write \([\mathbf a]\) for the equivalence class containing \(\mathbf a\). A coboundary belongs to the zero class, \([df]=[0]\), while a noncontractible dual loop belongs to a nonzero class.

### What we want the cup product to preserve

For two edge cocycles \(\mathbf a,\mathbf b\), the cup product assigns bits to plaquettes. Replacing \(\mathbf a\) by \(\mathbf a+df\) may change those individual plaquette bits even though the input logical class is unchanged.

For the product to describe cohomology classes, the resulting plaquette cochains must still belong to the same class. This is what the Leibniz rule guarantees.

### The Leibniz rule is a product rule for d

Over \(\mathbb F_2\), the rule is

\[
\boxed{
d(\mathbf a\smile\mathbf b)
=d\mathbf a\smile\mathbf b
+\mathbf a\smile d\mathbf b.
}
\]

It resembles the derivative rule \((fg)'=f'g+fg'\). Here \(d\) is a discrete operation that raises the cochain degree by one. The identity says that applying \(d\) to a cup product can be distributed between its two inputs. Over coefficients other than \(\mathbb F_2\), the general formula has a degree-dependent sign; modulo two that sign disappears.

### A fully explicit calculation: vertex cochain times edge cochain

In the calculation below, the inputs are:

- \(f\): a **0-cochain**, assigning bits to vertices.
- \(\mathbf b\): a **1-cochain**, assigning bits to edges. It is arbitrary and need not select just one edge or be a cocycle at this stage.

Use the labels

```text
                  e_top
           D o-------------o C
             |             |
      e_left |      p      | e_right
             |             |
           A o-------------o B
                 e_bottom
```

Expressions such as \(b_{\mathrm{bottom}}\) are shorthand for \(\mathbf b(e_{\mathrm{bottom}})\), the bit assigned to that edge. We will initially write the evaluations out in full.

**Step 1: make a new edge assignment using the cup product.** Define

\[
\mathbf c=f\smile\mathbf b.
\]

The output is an edge cochain because the degrees add to \(0+1=1\). The vertex–edge rule samples the starting vertex of each edge:

\[
\mathbf c(e)=f(\mathrm{start}(e))\,\mathbf b(e).
\]

Thus

\[
\begin{aligned}
\mathbf c(e_{\mathrm{bottom}})&=f(A)\mathbf b(e_{\mathrm{bottom}}),\\
\mathbf c(e_{\mathrm{right}})&=f(B)\mathbf b(e_{\mathrm{right}}),\\
\mathbf c(e_{\mathrm{left}})&=f(A)\mathbf b(e_{\mathrm{left}}),\\
\mathbf c(e_{\mathrm{top}})&=f(D)\mathbf b(e_{\mathrm{top}}).
\end{aligned}
\]

Each product on the right is ordinary multiplication of two bits.

**Step 2: apply d to test the new assignment around the square.** By definition,

\[
(d\mathbf c)(p)
=\mathbf c(e_{\mathrm{bottom}})
+\mathbf c(e_{\mathrm{right}})
+\mathbf c(e_{\mathrm{left}})
+\mathbf c(e_{\mathrm{top}}).
\]

Substituting Step 1, and using the shorthand for edge values, gives

\[
\begin{aligned}
d(f\smile\mathbf b)(p)
={}&f(A)b_{\mathrm{bottom}}+f(B)b_{\mathrm{right}}\\
&+f(A)b_{\mathrm{left}}+f(D)b_{\mathrm{top}}.
\end{aligned}
\]

For example, if \(f\) selects only \(A\) and \(\mathbf b\) selects only the bottom edge, their cup product selects that edge and \(d(f\smile\mathbf b)(p)=1\).

**Step 3: compute the other side of the Leibniz rule.** The identity we want is

\[
d(f\smile\mathbf b)=df\smile\mathbf b+f\smile d\mathbf b.
\]

Both \(df\) and \(\mathbf b\) are edge cochains. The edge–edge cup rule gives

\[
(df\smile\mathbf b)(p)
=[f(A)+f(B)]b_{\mathrm{right}}
+[f(A)+f(D)]b_{\mathrm{top}}.
\]

Meanwhile, \(d\mathbf b\) is a plaquette cochain. The vertex–plaquette rule samples \(A\), giving

\[
(f\smile d\mathbf b)(p)
=f(A)\bigl(
b_{\mathrm{bottom}}+b_{\mathrm{right}}
+b_{\mathrm{left}}+b_{\mathrm{top}}
\bigr).
\]

Adding these expressions cancels the two copies of \(f(A)b_{\mathrm{right}}\) and the two copies of \(f(A)b_{\mathrm{top}}\). The remaining terms are exactly the expression in Step 2.

The abstract product rule is therefore a statement about local bit assignments and their cancellations.

### Changing a representative changes the product by a coboundary

Now assume \(\mathbf b\) is a cocycle, so \(d\mathbf b=0\). The identity just verified simplifies to

\[
d(f\smile\mathbf b)=df\smile\mathbf b.
\]

Change the first input by stars:

\[
\mathbf a'=\mathbf a+df.
\]

By bilinearity and the simplified product rule,

\[
\begin{aligned}
\mathbf a'\smile\mathbf b
&=\mathbf a\smile\mathbf b+df\smile\mathbf b\\
&=\mathbf a\smile\mathbf b+d(f\smile\mathbf b).
\end{aligned}
\]

The difference between the outputs is a **2-coboundary**. Unlike a 1-coboundary, it is not the support of a star operator: it is a plaquette assignment obtained by applying \(d\) to an edge assignment.

In the two-dimensional complex,

\[
H^2=D^2/\operatorname{im}d_1,
\]

because there is no further coboundary map to degree 3. Two plaquette cochains therefore represent the same \(H^2\) class if their difference is a 2-coboundary. We have shown

\[
\boxed{[\mathbf a'\smile\mathbf b]=[\mathbf a\smile\mathbf b].}
\]

Changing the second input by a coboundary works similarly, using \(d\mathbf a=0\). This makes the cup product an operation

\[
H^1\times H^1\longrightarrow H^2:
\]

the output class depends on the input classes, even though its particular plaquette pattern depends on the representatives.

More generally, the Leibniz rule also implies that the cup product of cocycles is a cocycle: if \(d\mathbf a=d\mathbf b=0\), then \(d(\mathbf a\smile\mathbf b)=0\). On a purely two-dimensional complex, every 2-cochain is already a cocycle because there are no 3-cells to test. For the edge–edge product here, the substantial result is **independence from the choice of representatives**.
