# Blood on the Clocktower tools

*Very* miscellaneous tools towards use with the social deduction game Blood on the Clocktower. If you're seeing this, odds are you're familiar. If not:
- Each player has a character role with associated ability
- Combinations of these roles form "scripts"
- The community makes heavy use of tools to create their own custom scripts from the officially published characters (and some of their own homebrew ones)
- These custom scripts are communicated between tools in JSON format according to a schema defined [by the official creators](https://github.com/ThePandemoniumInstitute/botc-release/blob/main/script-schema.json).

## Maximum Jinxes

[max-jinx-script.py](./max-jinx-script.py)

### What's a Jinx?

A "jinx" is a special rule between two characters that alters or clarifies the way they interact. These are typically used when the interaction between the two would clash or contradict in some way. For example:
- The Zealot's ability means they must vote in a certain way
- The Cannibal's ability grants them the ability of another player, but they do not know which ability they have
- Together, these can mean that the Cannibal is supposed to vote a certain way - but they wouldn't know this.
- So, a jinx is introduced between the two - If the Cannibal gains the Zealot ability, they learn this.

### Why this??

I've become interested in creating a script with the maximum possible number of jinxes. There are existing all-character scripts (such as Whalebuffet) that have all jinxes included, however a far more interesting question appears when we limit the characters to the distribution of a normal script:
- 13 Townsfolk
- 4 Outsiders
- 4 Minions
- 4 Demons

With this, we have a search space of $\binom{69}{13}\times\binom{23}{4}\times\binom{27}{4}\times\binom{19}{4} = 2.3281309\times 10^{25}$. This is interesting because of its sheer size - an inefficient search will functionally never be complete.

I've had an attempt at optimising for number of jinxes by hand and achieved a result of 43 out of a possible ~65. So it's time to spend several hours automating something that probably only would have taken another 30 minutes of my time!

### Progress

- [x] ~~Store and load jinxes~~ - *see [data/jinxes.yaml](data/jinxes.yaml)*
- [x] ~~Store and load character name and type~~ - *see [data/characters.yaml](data/characters.yaml)*
- [x] ~~Construct graph representation with jinxes as edges~~ - *see the _JinxGraph class in [max-jinx-script.py](max-jinx-script.py)*
- [x] ~~Define search runner and exhaustive search~~ - *see the Search class in [max-jinx-script.py](max-jinx-script.py)*
- [x] ~~Attempt simple search optimisations~~ - *see Search.EXHAUSTION_REDUCED and Search.PEELING_GREEDY in [max-jinx-script.py](max-jinx-script.py)*
- [ ] Construction-based search with added jinxes as primary heuristic and potential jinxes as secondary.
- [ ] Handle different distributions of town
- [ ] Output as JSON script instead of just printing to stdout

## Global Night Order

In the night phase of the game, characters wake in a specific order. Determining a global order allows:
1. Grabbing the order of a subset of characters
2. Understanding the generics of the order

One challenge of this was to include orderings for both the first night and successive nights, as these are different. Additionally, some reminders occur after the "dawn" step of the night when players are awoken.

### Progress

- [x] ~~Add night reminders to all characters~~ - *see [data/characters.yaml](data/characters.yaml)*
- [x] ~~Define generation code for night order with human-input comparisons~~ - *see generate_order in [order.py](order.py)*
- [x] ~~Create and store night order ranking~~ - *see [data/night-order.yaml](data/night-order.yaml)*
- [x] ~~Enable fetching order for a set of characters~~ - *see pick_from_order in [order.py](order.py)*
- [ ] Extend basic tests in [tests/test_order.py](tests/test_order.py)
- [ ] Create tool for custom ordering that forms an exception to the global order
- [ ] Output night order (customised or otherwise, though default night order doesn't need to be specified) in script-schema-compatible JSON.