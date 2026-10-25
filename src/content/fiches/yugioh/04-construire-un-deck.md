---
title: Construire un deck cohérent
chapter: 4
order: 1
duration: 12
level: Deck
tags:
- deckbuilding
- ratios
- moteur
cards:
- q: Pourquoi jouer 40 cartes plutôt que 60 ?
  a: Pour maximiser la probabilité de piocher ses meilleures cartes. Avec 40 cartes, une carte jouée en 3 exemplaires se trouve dans la main de départ (5 cartes) environ 34 % du temps ; avec 60 cartes, environ 23 %.
- q: Qu'est-ce que le « moteur » d'un deck ?
  a: Les cartes qui font fonctionner sa stratégie (starters, extenders, recherches). Le reste, le **non-moteur**, ce sont les hand traps, les staples et les cartes de défense ou de destruction.
- q: Qu'est-ce qu'un starter ?
  a: Une carte qui, seule, lance le combo principal. Plus un deck a de starters différents, plus il est régulier.
- q: Qu'est-ce qu'un extender ?
  a: Une carte qui prolonge un combo déjà lancé ou permet de le continuer malgré une interruption. Seule, elle ne fait souvent rien.
- q: Qu'est-ce qu'une « brique » (brick) ?
  a: Une carte qui ne fait rien seule, ou une main de départ qui ne permet aucun jeu. Un bon deck limite les cartes qui ne servent qu'avec une autre.
- q: Probabilité d'avoir au moins un starter avec 12 starters dans un deck de 40, en main de 5 ?
  a: 'Environ **85 %** en main de 5 (premier joueur). C''est l''ordre de grandeur visé par les decks compétitifs : environ 1 main sur 7 sans starter.'
- q: À quoi sert l'Extra Deck dans la construction ?
  a: 'À stocker les monstres que le moteur atteint (Synchro, Xyz, Lien, Fusion) et quelques réponses génériques. Ses 15 places sont limitées : chaque carte doit être utile dans plusieurs situations.'
quiz:
- q: Ton deck a 43 cartes dont 3 « filler » sans utilité claire. Que faire ?
  options:
  - Les garder, plus de cartes c'est plus d'options
  - Les retirer pour revenir à 40 et piocher plus souvent tes meilleures cartes
  - Ajouter 17 cartes pour aller à 60
  - Rien, ça ne change rien
  answer: 1
  explain: Chaque carte en trop dilue les cartes clés.
- q: Tu ouvres une main avec trois extenders et aucun starter. Comment appelle-t-on ça ?
  options:
  - Une main parfaite
  - Une brique
  - Un OTK
  - Un side
  answer: 1
  explain: 'Des extenders sans starter ne font souvent rien : la main brique.'
- q: Pour un deck combo, quel est le premier objectif de construction ?
  options:
  - Jouer le plus de pièges possible
  - Maximiser la probabilité d'ouvrir un starter
  - Avoir 15 cartes dans l'Extra Deck à tout prix
  - Jouer 60 cartes
  answer: 1
  explain: 'La régularité d''abord : sans starter, le combo ne démarre pas.'
---

Construire un deck, c'est d'abord une affaire de **régularité** : piocher assez souvent les cartes qui font fonctionner la stratégie, et peu souvent celles qui ne font rien seules. Le reste (interaction, réponses) vient s'ajouter autour.

## Les tailles

| Pile | Taille | Conseil |
| --- | --- | --- |
| Main Deck | 40 à 60 | **40** dans l'immense majorité des cas |
| Extra Deck | 0 à 15 | remplir les 15 places, chacune doit servir |
| Side Deck | 0 à 15 | cartes échangées entre les manches d'un match |

Maximum **3 exemplaires** d'une même carte, sauf restriction de la **banlist** (une carte limitée se joue en 1, semi-limitée en 2, interdite en 0).

## Pourquoi 40 cartes

Plus le deck est petit, plus chaque carte a de chances d'être dans ta main. La probabilité d'avoir **au moins un exemplaire** d'une carte jouée en 3, dans une main de 5 :

| Taille du deck | Probabilité |
| --- | --- |
| 40 cartes | environ 34 % |
| 45 cartes | environ 30 % |
| 60 cartes | environ 23 % |

Ces calculs se font avec la **loi hypergéométrique** (tirage sans remise). Des calculateurs en ligne te donnent ces chiffres pour n'importe quelle combinaison.

## Les rôles des cartes

- **Starter** : lance le combo seul. C'est la carte qu'on veut voir dans chaque main.
- **Extender** : prolonge le combo, ou le relance après une interruption. Inutile sans starter.
- **Recherche** (*searcher*) : ajoute une carte précise du deck à la main ; elle fait office de starter supplémentaire.
- **Payoff** : le terrain final, ce que le combo cherche à installer (monstres qui nient, qui détruisent…).
- **Non-moteur** : hand traps, staples, cartes qui cassent un terrain adverse.

Un deck compétitif typique de 40 cartes ressemble à :

| Catégorie | Nombre |
| --- | --- |
| moteur (starters, extenders, recherches) | 22 à 28 |
| hand traps | 6 à 12 |
| staples et cartes de destruction | 3 à 8 |

## Viser la régularité

Le bon réflexe est de compter tes **starters réels** (y compris les recherches qui en trouvent un). Avec 40 cartes et une main de 5 :

| Starters dans le deck | Mains avec au moins un starter |
| --- | --- |
| 8 | environ 70 % |
| 10 | environ 78 % |
| 12 | environ 85 % |
| 15 | environ 92 % |

<!-- schema:regularite -->
<figure class="diagram"><svg viewBox="0 0 680 230" role="img" aria-label="Plus de starters, des mains plus régulières" style="--minw:560px"><defs><marker id="g3-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g3-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g3-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g3-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="14" y="20" class="dg-zl" text-anchor="start">mains de départ (5 cartes, deck de 40) avec au moins un starter</text><text x="120" y="60" class="dg-t" text-anchor="end" style="--d:0">8 starters</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="140" y="40" width="350" height="30" rx="6"/></g><text x="500" y="60" class="dg-ct" text-anchor="start" style="--d:0">≈ 70 %</text><text x="120" y="104" class="dg-t" text-anchor="end" style="--d:1">10 starters</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="140" y="84" width="390" height="30" rx="6"/></g><text x="540" y="104" class="dg-ct" text-anchor="start" style="--d:1">≈ 78 %</text><text x="120" y="148" class="dg-t" text-anchor="end" style="--d:2">12 starters</text><g class="dg-box dg-ok dg-pop" style="--d:2"><rect x="140" y="128" width="425" height="30" rx="6"/></g><text x="575" y="148" class="dg-ct" text-anchor="start" style="--d:2">≈ 85 %</text><text x="120" y="192" class="dg-t" text-anchor="end" style="--d:3">15 starters</text><g class="dg-box dg-ok dg-pop" style="--d:3"><rect x="140" y="172" width="460" height="30" rx="6"/></g><text x="610" y="192" class="dg-ct" text-anchor="start" style="--d:3">≈ 92 %</text></svg><figcaption>Passer de 8 à 12 starters fait gagner environ une main sur sept.</figcaption></figure>
<!-- /schema:regularite -->

Si le chiffre est trop bas, on ajoute des cartes qui cherchent un starter, ou on retire des cartes qui ne servent qu'en combinaison (**briques**).

## Le choix des ratios

- **3 exemplaires** : les cartes qu'on veut toujours voir (starters principaux, meilleures hand traps).
- **2** : utiles mais pas indispensables, ou mauvaises en double dans la main.
- **1** : les cartes qu'on va **chercher** depuis le deck plutôt que piocher, et celles limitées par la banlist.

Une carte qui est mauvaise quand on en pioche deux (une carte « une fois par tour » qu'on ne peut utiliser qu'une fois) se joue rarement en 3.

## L'Extra Deck

Il contient d'abord ce que le moteur atteint, puis quelques **cartes génériques** : un Lien-1 ou Lien-2 utile partout, un Xyz de Rang 4 polyvalent, des réponses aux stratégies du méta. Comme il n'est jamais pioché, il ne nuit pas à la régularité : il faut juste que chacune de ses 15 places serve.

> **À retenir.** 40 cartes, compter ses starters, et viser au moins 85 % de mains qui lancent quelque chose. Les cartes qu'on cherche se jouent en 1, celles qu'on veut piocher en 3. Une carte qui ne fait rien seule doit justifier sa place.
