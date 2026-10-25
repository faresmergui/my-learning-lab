---
title: 'Les limites d''utilisation : tous les « une fois par tour »'
chapter: 14
order: 1
duration: 14
level: Expert
tags:
- OPT
- hard OPT
- soft OPT
- verrou
cards:
- q: Que veut dire « Une fois par tour » seul (soft OPT) ?
  a: 'La limite vaut **pour cette copie**. Deux copies peuvent chacune utiliser l''effet, et une copie qui quitte le terrain puis revient est une nouvelle carte : elle peut le réutiliser.'
- q: Que veut dire « Vous ne pouvez utiliser cet effet de "X" qu'une fois par tour » (hard OPT) ?
  a: 'La limite vaut **pour le nom** : une seule utilisation de cet effet par tour, toutes copies confondues, même si la carte quitte le terrain et revient.'
- q: Une limite d'utilisation est-elle consommée si l'effet est nié ?
  a: '**Oui.** C''est l''activation qui compte. Nier l''effet ne rend pas l''utilisation, d''où la valeur d''une hand trap placée sur l''effet clé.'
- q: Que veut dire « Vous ne pouvez utiliser qu'1 effet de "X" par tour, et seulement une fois ce tour » ?
  a: La carte a plusieurs effets, mais on ne peut en utiliser **qu'un seul**, une seule fois, par tour et par nom. Choisir l'effet devient une décision.
- q: Que veut dire « Vous ne pouvez activer qu'1 "X" par tour » ?
  a: On ne peut **activer qu'une carte** de ce nom par tour (souvent une magie ou un piège). Ses effets sans activation (au cimetière par exemple) ne sont pas concernés, sauf mention.
- q: Qu'est-ce qu'un verrou (lock) d'invocation ?
  a: Une restriction du type « vous ne pouvez pas invoquer Spécialement depuis l'Extra Deck ce tour, sauf des monstres X ». Écrit sur l'activation, il s'applique **même si l'effet est nié**.
- q: Que veut dire « Vous ne pouvez invoquer Spécialement "X" qu'une fois par tour » ?
  a: Une limite sur l'**invocation** de ce nom, quelle que soit la manière (effet ou procédure). Une deuxième copie ne peut pas être invoquée Spécialement ce tour.
quiz:
- q: 'Tu as deux copies d''un monstre avec « Une fois par tour : vous pouvez piocher 1 carte ». Combien de fois peux-tu piocher ce tour ?'
  options:
  - Une fois
  - Deux fois, une par copie
  - Trois fois
  - Aucune si l'une est niée
  answer: 1
  explain: « Une fois par tour » seul est une limite par copie (soft OPT).
- q: L'effet « Vous ne pouvez utiliser cet effet de "X" qu'une fois par tour » de ta première copie est nié par Ash Blossom (Floraison de Cendres et Joyeux Printemps). Peux-tu utiliser celui de ta deuxième copie ?
  options:
  - Oui, le premier a été nié
  - 'Non : la limite par nom est consommée par l''activation'
  - Oui, si tu bannis la première
  - Seulement au tour adverse
  answer: 1
  explain: Une limite par nom (hard OPT) compte l'activation, même niée. C'est précisément ce que l'adversaire cherche en plaçant Ash sur cet effet.
- q: Un monstre avec un effet soft OPT est renvoyé dans ta main après l'avoir utilisé, puis réinvoqué. Peut-il réutiliser l'effet ?
  options:
  - Non, jamais
  - 'Oui : c''est une nouvelle carte pour le jeu'
  - Seulement si l'effet a été nié
  - Seulement en défense
  answer: 1
  explain: 'Une carte qui quitte le terrain et revient est traitée comme une nouvelle carte : la limite par copie repart à zéro. Une limite par nom, elle, resterait consommée.'
- q: 'Tu actives un effet qui dit : « Vous ne pouvez pas invoquer Spécialement depuis l''Extra Deck pour le reste de ce tour, sauf des monstres Synchro, si vous activez cet effet. » L''effet est nié. Le verrou s''applique-t-il ?'
  options:
  - Non, tout est annulé
  - 'Oui : il dépend de l''activation, pas de la résolution'
  - Seulement si l'effet se résout
  - Seulement au tour suivant
  answer: 1
  explain: 'Le verrou est lié à l''activation de l''effet. Nier l''effet ne le lève pas : c''est un piège classique quand on joue plusieurs moteurs.'
---

Presque toutes les cartes compétitives ont une limite d'utilisation. Elles se ressemblent, mais leurs différences changent tout : savoir si une deuxième copie est utile, si une hand trap a « gâché » un effet, ou si l'on peut encore passer par l'Extra Deck après un effet nié.

## Les différentes limites

| Texte | Portée | Effet nié ? | La carte sort et revient ? |
| --- | --- | --- | --- |
| « Une fois par tour » | **cette copie** | utilisation consommée | nouvelle carte : réutilisable |
| « Vous ne pouvez utiliser cet effet de "X" qu'une fois par tour » | **le nom** | utilisation consommée | toujours consommée |
| « Vous ne pouvez utiliser chaque effet de "X" qu'une fois par tour » | chaque effet, par nom | utilisation consommée | toujours consommée |
| « Vous ne pouvez utiliser qu'1 effet de "X" par tour, et seulement une fois ce tour » | un seul effet au choix, par nom | utilisation consommée | toujours consommée |
| « Vous ne pouvez activer qu'1 "X" par tour » | l'activation de la carte | activation consommée | ne concerne pas ses autres effets |
| « Vous ne pouvez invoquer Spécialement "X" qu'une fois par tour » | l'invocation de ce nom | — | une seule invocation Spéciale du nom |

On parle souvent de **soft OPT** pour la première ligne et de **hard OPT** pour les limites par nom (*once per turn*).

## La règle qui compte le plus

**Une limite d'utilisation est consommée par l'activation.** Si l'adversaire nie l'effet, l'utilisation est perdue quand même. C'est la raison d'être des hand traps : elles ne détruisent rien, mais elles brûlent l'utilisation d'un effet qui ne reviendra pas ce tour.

À l'inverse, un effet qui ne peut pas être activé (par exemple parce qu'une carte l'interdit) n'a pas été utilisé : il reste disponible si l'interdiction disparaît.

## Ce que ça change pour la construction

- **Les doublons d'un hard OPT** ne servent pas à refaire l'effet, mais à le trouver plus souvent, ou à servir de matériel, de coût, de cible.
- **Les cartes soft OPT** gagnent en valeur quand le deck peut les renvoyer en main ou les faire revenir : chaque retour donne une nouvelle utilisation.
- **Les cartes à plusieurs effets « 1 effet par tour »** obligent à choisir : utiliser l'effet de recherche maintenant, ou garder l'effet de protection pour le tour adverse.

## Les verrous

Beaucoup de cartes ajoutent une contrepartie : « vous ne pouvez pas invoquer Spécialement depuis l'Extra Deck pour le reste de ce tour, sauf des monstres X ». Deux formes existent :

- **liée à l'activation** (« si vous activez cet effet », ou écrite avant le point-virgule) : elle s'applique **même si l'effet est nié** ;
- **liée à la résolution** (écrite dans l'effet lui-même) : si l'effet est nié, le verrou ne s'applique pas.

Quand un deck mélange deux moteurs, l'ordre des actions dépend de ces verrous : on joue d'abord ce qui a besoin de l'Extra Deck sans restriction, ensuite ce qui verrouille.

## Lire les limites de l'adversaire

Connaître les limites des cartes adverses permet de savoir ce qu'une négation lui coûte vraiment :

- nier un effet **hard OPT** de sa carte de départ lui retire cette ligne pour le tour ;
- nier un effet **soft OPT** qu'il peut réutiliser en faisant revenir la carte ne le ralentit que temporairement ;
- un **verrou** qu'il a déjà déclenché l'empêche parfois de répondre à ta propre négation par un plan B.

> **À retenir.** « Une fois par tour » seul vaut pour une copie et repart si la carte revient ; les limites qui citent le nom valent pour toutes les copies. Une utilisation niée est une utilisation consommée. Un verrou lié à l'activation tient même si l'effet est nié.
