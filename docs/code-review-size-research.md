# How much code a reviewer can check well

This note is for contributors writing skills that size, split or describe
changes for human review. It records what published studies say about how
fast and how much code a reviewer can check before they find fewer
problems, how strong that evidence is, and the planning values this
repository takes from it. All sources were checked in November 2026.

## Summary

No single figure for review capacity holds up. The evidence supports a
range:

- **Rate:** careful review happens at roughly 200 to 400 changed lines an
  hour. Above about 450 to 500 lines an hour, reviewers find markedly fewer
  defects.
- **Session:** effectiveness falls after about 60 minutes, and 90 minutes
  is the usual ceiling.
- **Size:** about 200 to 400 changed lines is what one reviewer can check
  well in one session.
- **Planning value:** 300 changed lines an hour, with a range of 200 to
  400.

Line count is a weak measure of effort. The same studies show that a small
change with wide effects can take longer than a large mechanical one, and
that how complex and how spread out a change is matters as well as its
size.

## The often-quoted 450 lines an hour

The figure comes from the SmartBear study of lightweight, tool-assisted
review at Cisco ([Cohen, 2006](#sources)). It covered 2,500 reviews of 3.2
million lines by 50 developers over 10 months in 2005 and 2006. The source
sentence is:

> Reviewers slower than 400 lines per hour were above average in their
> ability to uncover defects. But when faster than 450 lines/hour the
> defect density is below average in 87% of the cases.

The 450 figure is therefore the speed beyond which reviews mostly found fewer
defects than average. It is not a measure of how much a person can review
in an hour. The study's own conclusions are:

- keep the code under review below 200 lines, and never above 400
- rates below 300 lines an hour find the most defects; below 500 is still
  good
- keep a review under 60 minutes, and never above 90
- review 100 to 300 lines at a time over 30 to 60 minutes, and spend at
  least 5 minutes even on a one-line change

The study has limits that its text states or shows:

- SmartBear sold the review tool used in the study.
- It excluded 21% of reviews as not real reviews: those under 30 seconds,
  faster than 1,500 lines an hour or larger than 2,000 lines.
- Defects were counted by hand from a random sample of 300 reviews, because
  the tool's defect log was unreliable.
- "Defect density" assumes that large and small changes contain the same
  number of defects per line. The authors acknowledge this assumption.
- The chapter reports no significance tests for the rate and size findings.
- It found no consistent rate for any reviewer or author. Several one- and
  two-line changes took over 15 minutes because they affected the rest of
  the system.

The finding is credible as a direction and an order of magnitude, but on
its own it is weak evidence for a precise threshold.

## Evidence that agrees

### Inspection and personal-review studies

[Kemerer and Paulk (2009)](#sources) analysed 371 C and 246 C++ programs
from Personal Software Process courses. They controlled for developer
ability and other factors, and found review rate a statistically significant
factor in defect removal effectiveness. Reviews at or below 200 lines an
hour removed 56 to 57% of code defects; faster reviews removed 45 to 47%.
Going slower than 200 lines an hour made no significant difference, and
effectiveness kept falling as reviews got faster. The reviewers reviewed
their own code, and the programs were small (median about 120 lines).

The same paper summarises earlier inspection guidance: preparation at
about 100 lines an hour and no more than 200, and inspection meetings at
about 125 lines an hour and no more than 250. It reports Buck finding an
optimal rate of 125 lines an hour. These rates come from formal,
meeting-based inspection rather than modern pull request review.

### Modern code review

These studies measure size against review quality, not reading speed:

- [Kononenko and others (2015)](#sources) studied Mozilla reviews. Patch
  size in lines was a significant predictor (p < 0.001) of a reviewed
  patch later proving buggy, in every model for every system studied. The
  number of files was also a significant predictor.
- [Bosu, Greiler and Bird (2015)](#sources) classified about 1.5 million
  review comments from five Microsoft projects. The proportion of useful
  comments fell as the number of files in a change rose. Build and
  configuration files received a lower proportion of useful comments than
  source code.
- [Baum, Schneider and Bacchelli (2019)](#sources) ran a controlled
  experiment with 50 participants, mostly professional developers. Review
  effectiveness was significantly higher for the small change. Working memory capacity was
  moderately associated with finding defects spread across several places.
- [Fregnan and others (2022)](#sources) analysed 219,476 GitHub pull
  requests. Files shown earlier received more comments. In a follow-up
  experiment with 106 participants, reviewers had 64% lower odds of finding one of the
  two seeded defects when its file came last.

[Rigby and Bird (2013)](#sources) found median change sizes from 25 lines
(Apache) to 78 lines (Chrome), with 263 lines at Lucent under formal
inspection. In the projects studied, most changes under review were small.

## Evidence that qualifies it

- **Splitting is not a guaranteed gain.** In a controlled experiment with
  28 developers, decomposing a change into coherent parts led to fewer
  wrongly reported issues, but did not change the number of defects found
  or reviewers' understanding of why the change was made
  ([di Biase and others, 2019](#sources)).
- **Lines are a proxy.** Baum and colleagues found similar effectiveness on
  two large changes that differed in size, one a refactoring full of moved
  code and the other smaller but more complex. They ask whether size or
  complexity is the real cause.
- **Causation is not shown.** Kemerer and Paulk note that finding a defect
  may slow a reviewer down, rather than slowness causing the finding.
- **Defects are not the only outcome.** A Microsoft talk titled
  [Code Reviews Do Not Find Bugs](#sources) argues that reviews mostly find
  maintainability issues and share knowledge. A rate tuned for finding
  defects may not suit those goals.

## Planning values for this repository

The values below are derived from the evidence. They are not measured
results, and they should be presented to reviewers as estimates.

| Quantity | Value | Basis |
|---|---|---|
| Review rate | 300 lines an hour (range 200 to 400) | Cisco best results below 300; PSP effective at or below 200; decline above 450 to 500 |
| Careful session | 60 minutes, 90 at most | Cisco conclusions; inspection guidance |
| Lines in one session | about 300 (range 200 to 400) | Rate multiplied by session length; Cisco size limit |
| Lines that cannot be one review | more than 2,000 | Cisco excluded these as not real reviews |

Count changed lines that need judgement. Generated files, lockfiles,
vendored code and moved code count only if a reviewer must read them,
because the evidence above shows line count alone is a poor measure of
effort. Build and configuration changes are not automatically low risk:
Bosu and colleagues suggest reviewers find their effects harder to assess.

Order matters as well as size. Putting the files where scrutiny matters
first fits the file-position finding. Explaining the change in advance fits
Cisco's finding that author-annotated reviews had low, consistent defect
densities, though the study could not tell whether that was because
authors caught defects themselves or because reviewers looked less hard.

## Open questions

- No study found here measures review rate for modern pull request review
  directly with significance tests. The rate evidence is from 2006 or
  earlier, or from personal review.
- None tests how effective a review is when the reviewer checks one example
  of a repeated mechanical change and accepts the others on trust.
- Reviewing agent-generated changes may differ, because the author cannot
  always explain its reasoning.

## Sources

- Cohen, J. (2006). "Code Review at Cisco Systems", in *Best Kept Secrets
  of Peer Code Review*, Smart Bear Software, pp. 63–87.
  [PDF](https://static1.smartbear.co/support/media/resources/cc/book/code-review-cisco-case-study.pdf)
- Kemerer, C. F. and Paulk, M. C. (2009). "The Impact of Design and Code
  Reviews on Software Quality: An Empirical Study Based on PSP Data",
  *IEEE Transactions on Software Engineering* 35(4).
  [PDF](https://sites.pitt.edu/~ckemerer/PSP_Data.pdf)
- Kononenko, O., Baysal, O., Guerrouj, L., Cao, Y. and Godfrey, M. W.
  (2015). "Investigating Code Review Quality: Do People and Participation
  Matter?", ICSME 2015, pp. 111–120.
  [PDF](https://plg.uwaterloo.ca/~migod/papers/2015/icsme15-OleksiiOlgaLatifa.pdf)
- Bosu, A., Greiler, M. and Bird, C. (2015). "Characteristics of Useful
  Code Reviews: An Empirical Study at Microsoft", MSR 2015.
  [PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/bosu2015useful.pdf)
- Baum, T., Schneider, K. and Bacchelli, A. (2019). "Associating Working
  Memory Capacity and Code Change Ordering with Code Review Performance",
  *Empirical Software Engineering* 24.
  [PDF](https://www.ifi.uzh.ch/dam/jcr:c47671a8-3fa4-4f76-bbd1-bb352a9ac6d0/emse2019a.pdf)
- Fregnan, E., Braz, L., D'Ambros, M., Çalikli, G. and Bacchelli, A.
  (2022). "First Come First Served: The Impact of File Position on Code
  Review", ESEC/FSE 2022. [paper](https://arxiv.org/abs/2208.04259)
- di Biase, M., Bruntink, M., van Deursen, A. and Bacchelli, A. (2019).
  "The Effects of Change Decomposition on Code Review: A Controlled
  Experiment", *PeerJ Computer Science* 5:e193.
  [paper](https://arxiv.org/abs/1805.10978)
- Rigby, P. C. and Bird, C. (2013). "Convergent Contemporary Software Peer
  Review Practices", ESEC/FSE 2013, pp. 202–212.
  [PDF](https://users.ece.utexas.edu/~miryung/teaching/EE379K-Spring2014/Papers/Paper%204.pdf)
- Czerwonka, J., Greiler, M. and Tilford, J. (2015). "Code Reviews Do Not
  Find Bugs: How the Current Code Review Best Practice Slows Us Down",
  ICSE 2015 SEIP talk.
  [Slides](https://www.microsoft.com/en-us/research/wp-content/uploads/2015/05/codereviewsdonotfindbugs-icse2015-seiptalk.pdf)
