---
title: Probabilités avancées
chapter: 18
order: 1
duration: 15
level: Expert
tags:
- probabilités
- hypergéométrique
- ratios
- construction
cards:
- q: Quelle loi décrit la main de départ ?
  a: 'La **loi hypergéométrique** : on tire sans remise un nombre de cartes dans un deck, et l''on compte combien appartiennent à une catégorie (starters, hand traps…).'
- q: Probabilité d'avoir au moins un exemplaire d'une carte jouée à 3, en 5 cartes, deck de 40 ?
  a: Environ **34 %**. À 6 cartes (en jouant second, après la pioche), environ **39 %**.
- q: Probabilité d'avoir au moins un starter avec 12 starters, en 5 cartes ?
  a: Environ **85 %** dans un deck de 40, **81 %** à 45 cartes, **76 %** à 50. Chaque carte de plus dilue les bonnes cartes.
- q: Avec 12 starters et 12 hand traps (différents), probabilité d'avoir les deux en 5 cartes ?
  a: Environ **71 %** ; environ **81 %** à 6 cartes. C'est la probabilité de la main « idéale » d'un deck équilibré.
- q: Pourquoi un combo à deux cartes précises est-il fragile ?
  a: Avec 3 copies de chaque, les avoir **toutes les deux** en 5 cartes n'arrive que dans environ **10 %** des mains. Un deck fiable s'appuie sur des cartes qui démarrent seules, ou sur beaucoup de façons d'obtenir chaque pièce.
- q: Qu'est-ce qu'une carte « morte » ?
  a: 'Une carte qui ne fait rien dans la situation : une hand trap en jouant premier contre un deck qui ne la craint pas, un board breaker quand l''adversaire n''a rien posé. Leur nombre détermine le choix des ratios.'
- q: Comment calculer facilement ces chiffres ?
  a: Avec un **calculateur hypergéométrique** en ligne ou un simulateur de mains de départ. Pour une probabilité « au moins un », on calcule 1 moins la probabilité de n'en avoir aucun.
quiz:
- q: Tu hésites entre 40 et 45 cartes pour ajouter 5 cartes de side « au cas où ». Tu as 12 starters. Que perds-tu ?
  options:
  - Rien
  - Environ 4 points de probabilité d'avoir un starter (85 % → 81 %)
  - La moitié de tes starters
  - Le droit de jouer en tournoi
  answer: 1
  explain: Diluer le deck fait baisser la probabilité de chaque bonne main. Les cartes « au cas où » vont plutôt dans le side deck.
- q: Ton deck a 9 hand traps. Tu passes à 12. Combien de mains de 5 cartes contiennent au moins une hand trap ?
  options:
  - 74 % → 85 %
  - 50 % → 60 %
  - 90 % → 95 %
  - Ça ne change rien
  answer: 0
  explain: '9 hand traps : environ 74 % ; 12 : environ 85 %. Le gain est réel, mais il se paie en starters ou en régularité.'
- q: Ta meilleure ligne demande deux cartes précises, chacune à 3 exemplaires. Comment fiabiliser ?
  options:
  - Rien à faire
  - Ajouter des cartes qui cherchent l'une ou l'autre, pour multiplier les façons de réunir les deux
  - Passer à 60 cartes
  - Jouer chaque carte à 1
  answer: 1
  explain: 'Chaque carte qui recherche une pièce compte comme un exemplaire de plus : on passe de 10 % à beaucoup plus.'
- q: En jouant second, tu vois 6 cartes au lieu de 5. Pourquoi les decks qui préfèrent jouer second jouent-ils plus de cartes de réponse ?
  options:
  - Par habitude
  - Parce que la sixième carte augmente nettement la probabilité de tenir à la fois un board breaker et de quoi comboter
  - Parce qu'ils piochent deux cartes
  - Parce que le side le demande
  answer: 1
  explain: Une carte de plus, c'est plusieurs points de probabilité sur chaque catégorie, et beaucoup plus sur les combinaisons.
---

Le chapitre sur la construction de deck a montré pourquoi jouer 40 cartes. À haut niveau, les probabilités servent à trancher des questions précises : combien de hand traps, faut-il un troisième exemplaire, cette carte de side vaut-elle une place ? On n'a pas besoin de formules à la main : il faut savoir **quoi calculer** et **comment lire** le résultat.

## Le bon modèle

Une main de départ est un tirage **sans remise** : la loi est **hypergéométrique**. Pour une catégorie de K cartes dans un deck de N, avec une main de n cartes :

- probabilité de n'en avoir **aucune** = C(N − K, n) / C(N, n) ;
- probabilité d'en avoir **au moins une** = 1 − la précédente.

Un calculateur en ligne ou un simulateur de mains fait ce calcul en une seconde. L'important est de bien définir la catégorie : « les cartes qui démarrent seules », par exemple, et pas seulement les cartes nommées « starter ».

## Les chiffres à connaître (deck de 40)

| Catégorie | 5 cartes (premier) | 6 cartes (second) |
| --- | --- | --- |
| au moins 1 exemplaire d'une carte jouée à 3 | 34 % | 39 % |
| au moins 1 parmi 9 cartes | 74 % | 81 % |
| au moins 1 parmi 12 cartes | 85 % | 90 % |
| au moins 1 parmi 15 cartes | 92 % | 95 % |
| au moins 1 starter (12) **et** au moins 1 hand trap (12) | 71 % | 81 % |
| 2 cartes précises, 3 exemplaires chacune | 10 % | — |

Et l'effet de la taille du deck, pour 12 starters en 5 cartes : **85 %** à 40 cartes, **81 %** à 45, **76 %** à 50.

## Ce que ces chiffres enseignent

- **Les combinaisons sont rares.** Avoir deux catégories à la fois chute vite. Un deck qui a besoin de « starter + extender + hand trap » doit avoir des cartes qui remplissent plusieurs rôles.
- **Les recherches valent des exemplaires.** Une carte qui cherche ton starter compte comme un starter de plus dans le calcul.
- **La sixième carte compte.** En jouant second, la carte piochée fait gagner plusieurs points sur chaque catégorie, et beaucoup plus sur les combinaisons. C'est une des raisons pour lesquelles les mains de second joueur supportent plus de cartes de réponse.
- **Le troisième exemplaire** d'une carte apporte moins que le premier, mais pas tant que ça : passer de 2 à 3 copies fait passer de 24 % à 34 % de chances de la voir en 5 cartes.

## Les cartes mortes et les ratios

Une carte peut être excellente et pourtant **morte** dans certaines situations : une hand trap qui ne touche pas le deck adverse, un board breaker quand tu joues premier. Le bon nombre de hand traps dépend donc :

1. de la **proportion du méta** qu'elles touchent ;
2. du nombre de parties où tu joues **premier ou second** (le side deck permet d'ajuster entre les manches) ;
3. de ce que tu **retires** pour les jouer : chaque hand trap ajoutée retire un starter ou une carte de régularité.

## Les briques

Une **brique** est une main qui ne fait rien : pas de starter, ou des cartes qui ne se combinent pas. Pour réduire le taux de briques :

- augmenter le nombre de cartes qui **démarrent seules** ;
- réduire les cartes qui ne servent qu'**en combinaison** avec une autre ;
- privilégier les cartes qui ont **deux usages** (une hand trap qui sert aussi de matériel, un extender qui recherche).

Un simulateur de mains (tirer 100 mains virtuelles et noter celles qui fonctionnent) donne une idée plus juste qu'un calcul théorique, parce qu'il tient compte de toutes les combinaisons réelles du deck.

> **À retenir.** Un tirage de départ suit la loi hypergéométrique : « au moins un » = 1 − « aucun ». Avec 40 cartes : 34 % de voir une carte jouée à 3, 85 % d'avoir un parmi 12. Les combinaisons de deux catégories chutent vite, les recherches comptent comme des exemplaires, et chaque carte de plus dans le deck dilue les bonnes mains.
