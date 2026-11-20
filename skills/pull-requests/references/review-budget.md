# The review budget and its evidence

This reference explains where the skill's figures come from and how far
they can be trusted. Read it when a user questions an estimate or a split
recommendation.

## The figures

| Quantity | Value | Basis |
| -------- | ----- | ----- |
| Review rate | 300 changed lines an hour, range 200 to 400 | Best defect detection below 300 an hour at Cisco; personal review effective at or below 200 |
| Decline | above about 450 to 500 lines an hour | At Cisco, 87% of reviews faster than 450 lines an hour found fewer defects than average |
| Session | 60 minutes, 90 at most | Cisco conclusions and earlier inspection guidance |
| Single-review ceiling | 2,000 lines | Cisco excluded larger reviews as not real reviews |

The 800-line threshold for recommending a split is this skill's own
judgement: more than about three hours at the planning rate. No study
measured it.

## How strong the evidence is

The direction is consistent across studies: faster and larger reviews find
fewer problems. Mozilla patches were more likely to prove buggy after
review the larger they were. At Microsoft, the share of useful review
comments fell as the number of files rose. In a controlled experiment,
reviewers did significantly better on a small change. Reviewers comment
less on files shown last, and in one experiment had 64% lower odds of
finding a defect in the last file.

The precise rates are weaker:

- The Cisco study was run by the vendor of the review tool, excluded 21%
  of reviews and reports no significance tests. It found no consistent
  rate for any reviewer.
- The personal-review study used small programs reviewed by their own
  authors.
- The rate studies date from 2009 or earlier, before modern pull request
  review.
- Line count is a proxy. Several one-line changes at Cisco took over 15
  minutes because they affected the rest of the system.
- Splitting a change into coherent parts reduced false alarms in one
  experiment, but did not help reviewers find more defects.
- Cisco's reviews that the author had annotated first found few defects,
  and the study could not tell whether authors had fixed problems first or
  reviewers had looked less hard.

No study tests checking one example of a repeated mechanical change and
accepting the rest. That is why the description must say how the rest can
be verified.

## Sources

- Cohen, J. (2006). "Code Review at Cisco Systems", in *Best Kept Secrets
  of Peer Code Review*, Smart Bear Software, pp. 63–87.
  <https://static1.smartbear.co/support/media/resources/cc/book/code-review-cisco-case-study.pdf>
- Kemerer, C. F. and Paulk, M. C. (2009). "The Impact of Design and Code
  Reviews on Software Quality: An Empirical Study Based on PSP Data",
  *IEEE Transactions on Software Engineering* 35(4).
- Kononenko, O. and others (2015). "Investigating Code Review Quality: Do
  People and Participation Matter?", ICSME 2015.
- Bosu, A., Greiler, M. and Bird, C. (2015). "Characteristics of Useful
  Code Reviews: An Empirical Study at Microsoft", MSR 2015.
- Baum, T., Schneider, K. and Bacchelli, A. (2019). "Associating Working
  Memory Capacity and Code Change Ordering with Code Review Performance",
  *Empirical Software Engineering* 24.
- Fregnan, E. and others (2022). "First Come First Served: The Impact of
  File Position on Code Review", ESEC/FSE 2022.
- di Biase, M. and others (2019). "The Effects of Change Decomposition on
  Code Review: A Controlled Experiment", *PeerJ Computer Science* 5:e193.
