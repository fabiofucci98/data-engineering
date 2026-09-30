# Name Pools (steam punk)

Word pools for deterministic city naming — one word (or short phrase) per line, plain
text, each pool in its own file. The generator (`citygen` / `generate.py`, see
`notes/city-geo-simulation.md`) draws one line per pool at generation time — seeded,
without replacement — and **never calls an AI/LLM at runtime**.

## Files → naming recipe

| Recipe part | File |
|---|---|
| Road `[first] [middle] [type]` | `road_first.txt` · `road_middle.txt` · `road_type.txt` |
| District `[character] [place]` | `district_character.txt` · `district_place.txt` |
| Park `[name] Park` | `park_name.txt` |
| School `[name] [level]` | `school_name.txt` · `school_level.txt` |
| Hospital `[name] [suffix]` | `hospital_name.txt` · `hospital_suffix.txt` |
| Shop `[adjective] [noun]` | `shop_adjective.txt` · `shop_noun.txt` |
| Workplace `[noun] [suffix]` | `workplace_noun.txt` · `workplace_suffix.txt` |
| Restaurant `[noun] & [noun]` (two draws, same pool) | `restaurant_noun.txt` |
| Civic / culture `[name] [type]` | `civic_name.txt` · `civic_type.txt` |

## Rules

- One word per line; no numbering, no inline commas.
- Distinct names per entity = product of the pool sizes it draws from (roads:
  |first| × |middle| × |type|). Pools should support ≥ 100× the largest count a city
  can need, so they should feel bigger than necessary.
- Adding a line grows the space with no code changes. (It also shifts which names a
  given seed produces — settle on a seed to keep a city stable.)