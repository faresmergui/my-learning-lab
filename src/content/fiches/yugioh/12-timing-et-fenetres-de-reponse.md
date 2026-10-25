---
title: Timing et fenêtres de réponse
chapter: 12
order: 1
duration: 16
level: Expert
tags:
- timing
- SEGOC
- rater le timing
- priorité
cards:
- q: Peut-on répondre à une invocation Lien, Xyz ou Synchro ?
  a: '**Pas pendant l''invocation**, sauf avec un contre-piège qui nie une invocation (Solemn Strike (*Assaut Solennel*)). Une fois l''invocation réussie, une fenêtre s''ouvre : on peut répondre à ses effets déclenchés ou utiliser un effet rapide sur le monstre.'
- q: Pourquoi peut-on répondre à une Polymérisation, mais pas à une invocation Lien ?
  a: 'Parce que Polymerization (*Polymérisation*) est une **magie qui s''active** et forme une chaîne, alors qu''une invocation Lien est une **procédure** : elle ne s''active pas.'
- q: Que deviennent les effets déclenchés pendant la résolution d'une chaîne ?
  a: Ils **attendent la fin de la chaîne**, puis forment une nouvelle chaîne dans l'ordre SEGOC. Un « quand … vous pouvez » déclenché au milieu d'une chaîne rate son timing s'il n'était pas la dernière chose à se produire.
- q: Quel est l'ordre SEGOC ?
  a: 'Quand plusieurs effets se déclenchent en même temps : 1) obligatoires du joueur du tour, 2) obligatoires de l''adversaire, 3) optionnels du joueur du tour, 4) optionnels de l''adversaire. Le **dernier** ajouté se résout en premier.'
- q: Quels effets peuvent rater leur timing ?
  a: Uniquement les effets **optionnels** écrits « **Quand** … vous pouvez ». Les « **Si** … vous pouvez » et les effets **obligatoires** ne ratent jamais leur timing.
- q: Qui a la priorité au début de chaque phase ?
  a: Le **joueur du tour**. Il peut activer en premier ; l'adversaire répond ensuite, ou agit quand le joueur du tour veut avancer.
- q: Peut-on activer un effet entre la résolution de deux maillons ?
  a: Non. Une fois qu'une chaîne commence à se résoudre, personne n'active rien jusqu'à la fin. Les effets déclenchés entre-temps attendent la chaîne suivante.
quiz:
- q: 'Ton monstre dit : « Quand cette carte est envoyée au cimetière : vous pouvez piocher 1 carte. » Tu l''envoies au cimetière comme coût d''un maillon 1, l''adversaire répond avec un maillon 2. La chaîne se résout. Pioches-tu ?'
  options:
  - Oui, toujours
  - 'Non : il a raté son timing, l''envoi au cimetière n''était pas la dernière chose à se produire'
  - Oui, en chaîne 3
  - Seulement si l'adversaire n'a pas répondu
  answer: 1
  explain: L'envoi a eu lieu à l'activation du maillon 1 ; ensuite, d'autres choses se sont passées. Un « quand … vous pouvez » rate alors son timing. Écrit « si », il aurait pu s'activer.
- q: 'Pendant ton tour, deux effets se déclenchent en même temps : un effet optionnel à toi et un effet obligatoire de l''adversaire. Lequel se résout en premier ?'
  options:
  - L'obligatoire de l'adversaire
  - Ton optionnel
  - Celui que tu choisis
  - Ils s'annulent
  answer: 1
  explain: 'Ordre de construction SEGOC : obligatoire de l''adversaire (maillon 1), puis ton optionnel (maillon 2). La chaîne se résout à l''envers : ton optionnel en premier.'
- q: L'adversaire invoque un monstre Lien. Peux-tu activer Infinite Impermanence (*Infini Éphémère*) pour empêcher l'invocation ?
  options:
  - Oui, en réponse à l'invocation
  - 'Non : on ne répond pas à une invocation par procédure ; tu peux l''utiliser après, sur le monstre invoqué'
  - Oui, si tu ne contrôles aucune carte
  - Seulement pendant la Battle Phase
  answer: 1
  explain: Seul un effet qui nie une invocation peut s'activer pendant l'invocation. Imperm vient après, dans la fenêtre ouverte par l'invocation réussie.
- q: 'Ton monstre a « Si cette carte est invoquée Normalement : vous pouvez ajouter 1 monstre à votre main. » L''adversaire répond à l''effet par Ash Blossom (Floraison de Cendres et Joyeux Printemps). La partie « une fois par tour » est-elle consommée ?'
  options:
  - Non, l'effet a été nié
  - 'Oui : l''effet a été activé, même s''il est nié'
  - Seulement si c'est une limite « une fois par tour » douce
  - Ça dépend du joueur
  answer: 1
  explain: Une limite d'utilisation compte l'activation. Nier l'effet ne la rend pas, d'où l'intérêt d'appâter les hand traps.
---

Une chaîne se lit à l'envers, c'est la base. Ce qui fait la différence à haut niveau, c'est de savoir **quand** on peut agir : quelles fenêtres existent, qui a la priorité, et quels effets peuvent être perdus en route. Ces règles décident de nombreux duels sans qu'un des deux joueurs s'en rende compte.

## Ce qui s'active, et ce qui ne s'active pas

On ne peut répondre qu'à une **activation**. Or beaucoup d'actions ne s'activent pas :

| Action | Elle s'active ? | Peut-on y répondre ? |
| --- | --- | --- |
| Invocation Normale, Lien, Xyz, Synchro (procédure) | non | seulement avec un effet qui **nie une invocation** |
| Invocation Spéciale par l'effet d'une carte | l'effet s'active | oui, à l'activation de l'effet |
| Polymérisation, rituel | oui, c'est une magie | oui |
| Effet continu (« tant que… ») | non | non, mais on peut le nier ou retirer la carte |

C'est pourquoi un deck qui enchaîne des invocations Lien ne se fait pas interrompre **pendant** ses invocations, seulement **entre** elles : à chaque fois qu'une invocation réussit, une fenêtre s'ouvre où les joueurs peuvent activer des effets rapides ou répondre aux effets déclenchés par cette invocation.

## La fenêtre après une invocation

Quand une invocation réussit :

1. les effets qui se **déclenchent** sur cette invocation (« si cette carte est invoquée… ») forment une chaîne ;
2. le joueur du tour peut y ajouter des effets rapides, puis l'adversaire ;
3. s'il n'y a aucun déclenchement, une fenêtre existe quand même : l'adversaire peut utiliser un effet rapide sur le monstre qui vient d'arriver.

C'est dans cette fenêtre que l'on place Infinite Impermanence (*Infini Éphémère*) ou une autre négation, **avant** que le monstre utilise un effet d'ignition.

## Les effets déclenchés au milieu d'une chaîne

Pendant la résolution d'une chaîne, personne ne peut rien activer. Les effets qui se déclenchent à cause d'un maillon **attendent la fin de la chaîne**, puis forment une nouvelle chaîne. Les effets déclenchés en même temps s'ordonnent selon le **SEGOC** (*Simultaneous Effects Go On Chain*) :

| Maillon | Quoi |
| --- | --- |
| 1 | effets obligatoires du joueur du tour |
| 2 | effets obligatoires de l'adversaire |
| 3 | effets optionnels du joueur du tour |
| 4 | effets optionnels de l'adversaire |

Chaque joueur choisit l'ordre de ses propres effets dans son groupe. Comme une chaîne se résout à l'envers, l'**optionnel de l'adversaire se résout en premier** : c'est un avantage réel pour lui. Après la construction SEGOC, les deux joueurs peuvent encore ajouter des effets rapides, comme sur n'importe quelle chaîne.

## Rater le timing

Seuls les effets **optionnels** écrits « **Quand** … : vous pouvez » peuvent rater leur timing. La règle : ils ne peuvent s'activer que si l'événement qui les déclenche est **la dernière chose qui s'est produite**.

Ils ratent leur timing quand :

- l'événement a lieu au **milieu** d'une chaîne, ou à l'activation d'un maillon (un coût par exemple), et que d'autres maillons se résolvent après ;
- l'événement est la **première partie** d'un effet suivi de « **puis** » : la seconde partie s'est produite après.

Ne ratent **jamais** leur timing :

- les effets **obligatoires** (« quand … : ciblez », sans « vous pouvez ») ;
- les effets optionnels écrits « **Si** … : vous pouvez ».

Les cartes récentes utilisent presque toutes « si ». Le problème revient surtout avec des cartes anciennes, encore jouées dans certains decks.

## La priorité

Au début de chaque phase et après chaque résolution, le **joueur du tour** a la priorité : il peut agir en premier. L'adversaire peut répondre à ce qu'il fait, ou agir quand le joueur du tour veut passer à la phase suivante. Concrètement :

- annoncer clairement « je passe en Battle Phase » donne à l'adversaire l'occasion d'agir **à la fin de la Main Phase** ;
- un effet rapide qu'on veut utiliser au tout début du tour adverse se place pendant sa **Standby Phase** ou en réponse à sa première action.

## Ce que ça change en pratique

- **Placer ses négations au bon maillon.** Répondre au maillon qui compte, pas au premier venu.
- **Profiter de l'ordre SEGOC.** L'adversaire qui déclenche un optionnel en même temps que toi se résout avant toi.
- **Vérifier les « quand ».** Avant de construire une ligne avec une vieille carte, se demander si son effet peut rater son timing dans cette séquence.

> **À retenir.** On ne répond qu'à ce qui s'active : une invocation par procédure ne s'active pas, mais elle ouvre une fenêtre une fois réussie. Les déclenchements au milieu d'une chaîne attendent la fin, puis s'ordonnent selon le SEGOC. Seuls les « Quand … vous pouvez » ratent leur timing.
