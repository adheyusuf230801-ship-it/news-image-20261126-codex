# World in One Day — Thursday 26 November 2026
[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/adheyusuf230801-ship-it/news-image-20261126-codex/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/adheyusuf230801-ship-it/news-image-20261126-codex/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)


A deterministic newspaper front page for make.fun competition
`news-image-20261126`. Off-white paper, navy bitmap lettering, a red masthead
rule and hero headline, and muted blue-grey illustrations keep the page clear.
The large date sits above a New York storm scene with grounded parade balloons.
Six illustrated news cells form three paired rows; a seventh spans the bottom.
Everything is drawn in Python, including the embedded 5×7 font and PNG encoder.

These eight stories were each first reported on **26 November 2026**. The entry
uses only the supplied story list:

1. **Macy's 100th parade postponed.** First postponement in 100 years. The
   Thanksgiving storm grounds the balloons; the parade moves to Saturday
   28 November.
2. **Storm floods East Coast.** Bomb cyclone brings coastal flooding; New York
   and New Jersey declare emergencies.
3. **Ukraine hits Russian air base.** Five Russian military jets damaged in a
   strike on Savasleyka airbase.
4. **Kim orders wider nuclear deployment.** North Korea's Kim Jong Un calls for
   tactical nuclear weapons across more domains.
5. **SpaceX cleared for 1M satellites.** US approves a plan for up to one million
   data-centre satellites in orbit.
6. **Norway court voids oil licences.** Supreme Court rules climate-disputed oil
   licences invalid.
7. **Ramaphosa wins Farmgate reprieve.** South Africa's president escapes an
   impeachment investigation — for now.
8. **Kenya's last Ebola patient goes home.** DRC death toll passes 5,300 as Kenya
   discharges its final patient.

Run with Python 3.13; no packages, network access, input files, clock, or random
values are used:

```sh
python3 main.py
# Or select an output directory:
MAKEFUN_OUTPUT_DIR=./output python3 main.py
```

The program writes just `entry.png` into the selected directory (default
`/output`). The RGB PNG is exactly 1024×1024 and must be at most 1 MiB; the encoder
checks the size. Text wraps at word boundaries, rejects missing glyphs, and
checks each line against its panel bounds. All lettering is uppercase, with
every glyph contained within its seven bitmap rows.

Reproduce the determinism check:

```sh
MAKEFUN_OUTPUT_DIR=.verify/run1 python3 main.py
MAKEFUN_OUTPUT_DIR=.verify/run2 python3 main.py
sha256sum .verify/run1/entry.png .verify/run2/entry.png
cmp .verify/run1/entry.png .verify/run2/entry.png
```
