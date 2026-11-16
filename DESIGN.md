# Design

Fill this in as you go. Your partner, future teammates, and the review bot read it
to learn where your project is headed. Replace each _italic prompt_.

## Target

_One or two sentences: what is this creature, what does it eat, where does it live,
and what should playing feel like?_

## Menu choices

Two items from two different groups (see the D4 guide's "The menu" tab).

| Item | Group | Done when (in your words) |
| --- | --- | --- |
| _item_ | _group_ | _what you will be able to show_ |
| _item_ | _group_ | _what you will be able to show_ |

## Words we use

Each word your project uses, what it means, and where it lives in code. A few are
already here from the starter; keep them accurate as you change things.

| Word | Meaning | In code |
| --- | --- | --- |
| cell | one square of the grid | `Vector2i` |
| session | one run at the game, from the first tick until it ends; owns the board and the dragon | `Session` in `core/session.gd` |
| tick | one step of the rules; the dragon moves one cell | `Session.tick()`, `Dragon.tick()` |
| tile kind | what a cell is made of, such as `floor` or `wall` | `Board.TILES`, `TILES` in `tools/build_art.py` |
| piece | one model in the kit: head, straight, turn, tail | `Kit.Piece`, `PIECES` in `tools/build_art.py` |
| _word_ | _meaning_ | _where_ |

## Where things live

_Where do the rules live, where does drawing happen, and how does an event get from
one to the other in your project?_

## Adding a tile kind

_The steps a teammate would follow, naming your actual files._

## Patterns, and what they bought us

_Each pattern you used on purpose, where it is, and what it made easier (or harder)._
