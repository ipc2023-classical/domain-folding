# Reverse Folding PDDL Domain

This domain is essentially a reformulation of the Answer Set Programming (ASP)
problem of the same name
[submitted](https://www.mat.unical.it/aspcomp2011/FinalProblemDescriptions/ReverseFolding)
to the ASP Competition 2011 by Agostino Dovier (University of Udine, Italy),
Andrea Formisano (University of Perugia, Italy), and Enrico Pontelli (New Mexico
State University, USA).

It is a simplification of a biology/chemistry problem:
A string (e.g., representing a protein) composed of N consecutive elements at a
fixed unitary distance lays on a 2D (cartesian) plane.
At the beginning, the string forms a straight line and the goal is to fold the
string so that it forms some specified shape.
At each step, the shape of the string can be changed by selecting an internal
node of the string and rotating (bending) the string by 90 degrees clockwise or
counterclockwise.

An example where the leftmost configuration is the initial state and the rightmost one is the goal:
```
 | 
 | 
 | 
 | 
 | 
 |    _ _ _ _ _ _    _ _     _ _     _ _ 
 |   |              |   |   |   |   |   | 
 |   |              |   |   |   |   | |_| 
                        |      _| 
                        | 
```


This domain was submitted to International Planning Competition 2023 by
Daniel Fišer <danfis@danfis.cz>.



See
 - https://link.springer.com/chapter/10.1007/978-3-642-20832-4_17 Section 6.1
 - https://www.mat.unical.it/aspcomp2011/FinalProblemDescriptions/ReverseFolding

asp 2011:
Andrea Formisano, Agostino Dovier and Enrico Pontelli
