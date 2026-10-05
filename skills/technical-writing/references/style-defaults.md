# Fallback style defaults

Use these only where the repository's own style guide is silent.

They mostly summarise the [GOV.UK style guide](https://www.gov.uk/guidance/style-guide)
and [writing for GOV.UK](https://www.gov.uk/guidance/content-design/writing-for-gov-uk),
published by the Government Digital Service under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
A few points, marked *(convention)*, are common technical-writing practice
rather than GOV.UK guidance. Read the sources for the full reasoning.

## Spelling

- British English with `-ise` endings: organise, realise, recognise.
- colour, behaviour, centre, catalogue, programme (but "program" for
  software).
- licence (noun), license (verb); practice (noun), practise (verb).
- Keep code, commands and product names exactly as they are, even when
  they use American spelling (`color:` in CSS, `normalize()`).
  *(convention)*

## Plain English

- Put the most important point first.
- Keep sentences short: 25 words or fewer.
- Use common words: "use" not "utilise", "help" not "facilitate", "buy"
  not "purchase", "start" not "commence".
- Prefer the active voice: "Run the script", not "The script should be
  run". The passive is fine when the actor doesn't matter.
- Address the reader as "you". Write instructions as direct commands.
- Avoid "simply", "just", "easy" and "obviously": what's easy for the
  writer may not be for the reader. *(convention)*

## Structure

- Use sentence case for headings: "Set up the database", not "Set Up The
  Database".
- Make headings say what the section is for. Front-load the key words.
- Use numbered lists for steps in order, and bullets otherwise.
- Introduce a list with a lead-in line. Keep list items parallel in form.
- Use descriptive link text that makes sense out of context. Never "click
  here" or "this link".

## Numbers, abbreviations and names

- Use numerals for numbers, including 1 to 9, except "one" in running
  prose ("one of the steps").
- Spell out an abbreviation on first use, unless it's better known than
  its expansion (USB, URL, PDF).
- Don't use full stops in abbreviations: "eg", "ie" and "etc" are better
  written as "for example", "that is" and "and so on".
- Write: email, website, online, Wi-Fi.
- Write product names as their makers do: GitHub, macOS, JavaScript.
  *(convention)*

## Markdown *(convention)*

- Give every fenced code block a language: `bash` for commands, `text` for
  output, trees and diagrams.
- Wrap bare URLs in `<...>` or give them link text.
- Put commands, file names, paths and identifiers in backticks.
- Use one sentence-case `#` heading per page, then `##` and below in
  order without skipping levels.
