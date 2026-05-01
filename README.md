# Social-Chem-101 Anki Deck

An [Anki](https://apps.ankiweb.net/) deck of **101,109 cards** built from the
[Social-Chem-101](https://maxwellforbes.com/social-chemistry/) dataset — a
corpus of crowd-sourced *rules of thumb* (RoTs) about everyday social and
moral situations.

Each card shows a rule of thumb on the front and reveals the situation,
action, judgment, moral score (−2 to +2), legality, and category on the back.

**👉 [Download the latest `.apkg`](https://github.com/andynu/social-chem-101-anki/releases/latest)** and import it into Anki via *File → Import*.

> [!NOTE]
> The deck is a study aid derived from the dataset published with the EMNLP 2020
> paper [Social Chemistry 101: Learning to Reason about Social and Moral
> Norms](https://arxiv.org/abs/2011.00620). All RoTs were written by
> crowdworkers in the original study; this repo only filters and reformats
> them.

## Card example

**Front**

> *If you owe someone money, you should pay them back.*
>
> What is the situation, action, and moral judgment?

**Back**

- **Situation:** A friend lent me $40 last month and keeps reminding me.
- **Action:** paying back money I owe
- **Judgment:** it's good
- **Moral Score:** ● ○ ○ ○ ○ &nbsp; *Very Good* (−2 … +2)
- **Legality:** legal
- **Category:** `morality-ethics` `social-norms`

Cards are also tagged with [moral
foundations](https://moralfoundations.org/) (`moral::care-harm`,
`moral::fairness-cheating`, etc.) where the dataset provides them, so you can
filter or build sub-decks by foundation.

## How the deck is built

`build_deck.py` reads the released TSV and applies these filters:

- `rot-bad == 0` (workers did not flag the RoT as confusing/low-quality)
- `rot-agree >= 3` (≥ 75–90% of people would agree)
- `split ∈ {train, dev, test}` (the main, single-annotator splits)
- `action` and `rot-judgment` are non-null

It then keeps **one RoT per situation** (the highest-agreement one), giving
**101,109** cards. Note GUIDs are derived from `rot-id`, so re-running the
build produces a stable deck that updates in place when imported into Anki.

| Stage                          |       Rows |
| ------------------------------ | ---------: |
| Raw dataset                    |    355,922 |
| After quality filter           |    237,975 |
| After dedup (one per situation)|    101,109 |

## Building it yourself

```bash
# 1. Download the dataset (CC BY-SA 4.0)
wget https://storage.googleapis.com/ai2-mosaic-public/projects/social-chemistry/data/social-chem-101.zip
unzip social-chem-101.zip

# 2. Build the deck
uv run --with genanki --with pandas python build_deck.py
# → writes social-chem-101.apkg
```

Tested with Python 3.11+, `genanki`, and `pandas`.

## Attribution and citation

If you use this deck or the dataset, please cite the original paper:

```bibtex
@inproceedings{forbes2020social,
  title     = {Social Chemistry 101: Learning to Reason about Social and Moral Norms},
  author    = {Forbes, Maxwell and Hwang, Jena D. and Shwartz, Vered and Sap, Maarten and Choi, Yejin},
  booktitle = {Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year      = {2020},
  url       = {https://arxiv.org/abs/2011.00620}
}
```

- **Project page:** https://maxwellforbes.com/social-chemistry/
- **Dataset & code:** https://github.com/mbforbes/social-chemistry-101
- **Paper:** https://arxiv.org/abs/2011.00620

## License

- **Code** in this repo (`build_deck.py`, etc.) — MIT, see [`LICENSE`](LICENSE).
- **Dataset and the built `.apkg` deck** — **CC BY-SA 4.0**, inherited from
  the upstream Social-Chem-101 release. See [`LICENSE-DATA`](LICENSE-DATA).
  If you redistribute the deck, you must attribute the original authors and
  share your derivative under the same license.

## Disclaimer

The RoTs reflect crowd-worker opinions about social and moral norms in a
specific cultural context (predominantly US-based MTurk workers, ca. 2020).
They are useful as a study corpus and a research artifact — they are not a
prescription, a definitive moral authority, or a representative sample of any
particular community.
