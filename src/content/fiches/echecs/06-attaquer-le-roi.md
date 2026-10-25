---
title: 'Attaquer le roi : mats types et sacrifices'
chapter: 6
order: 1
duration: 17
level: Tactique
tags:
- attaque
- mats types
- sacrifice grec
- mat du couloir
- roques opposés
cards:
- q: Qu'est-ce que le mat du couloir ?
  a: 'Une tour ou une dame mate sur la **première (ou dernière) rangée** un roi bloqué par **ses propres pions** (f7, g7, h7). Parade préventive : faire une **case de fuite** (h6, g6) ou garder une pièce sur la rangée du fond.'
- q: Qu'est-ce que le mat étouffé ?
  a: 'Un **cavalier** mate un roi entouré de **ses propres pièces**, qui lui ôtent toutes les cases. Schéma classique : Dg8+ !! Txg8, Cf7# (roi en h8). Aussi appelé « legs de Philidor ».'
- q: Quelles conditions pour le sacrifice grec Fxh7+ ?
  a: Fou sur la diagonale b1-h7, **cavalier qui peut aller en g5**, **dame qui peut rejoindre h5** (ou la colonne h), et **pas de cavalier noir en f6** pour défendre h7 (souvent chassé par un pion en e5). Après Fxh7+ Rxh7 Cg5+, la dame arrive en h5 ou h7.
- q: Qu'est-ce que le mat de Boden ?
  a: Deux **fous** qui se **croisent** sur des diagonales et matent un roi roqué côté dame (en c8), bloqué par ses propres pièces en d7 ou b7. Souvent après un sacrifice de dame en c6 ou b7.
- q: Qu'est-ce que le mat d'Anastasie ?
  a: Un **cavalier** (en e7) prive le roi de g8 et g6, et une **tour** mate sur la colonne **h** un roi en h7 bloqué par son pion g7. Souvent précédé d'un sacrifice de dame en h7.
- q: Quel principe gouverne une attaque sur le roi ?
  a: Avoir **plus d'attaquants que de défenseurs** dans la zone du roi, et **ouvrir des lignes** (colonnes, diagonales) vers lui. Une attaque sans assez de pièces échoue, même avec de beaux sacrifices.
- q: Que faire quand les roques sont opposés ?
  a: 'Une **course** : chaque camp pousse ses **pions** contre le roi adverse pour ouvrir des colonnes, sans craindre d''affaiblir son propre roi. Le temps est décisif : le premier qui ouvre une colonne gagne souvent.'
quiz:
- q: Les Noirs ont roi g8 et pions f7, g7, h7 ; leur seule tour est en d7. Ta tour arrive en e8 avec échec. Résultat ?
  options:
  - Échec simple, le roi s'échappe
  - Mat du couloir
  - Pat
  - La tour d7 peut prendre en e8
  answer: 1
  explain: Le roi est bloqué par ses pions, f8 et h8 sont tenues par ta tour, et la tour d7 ne peut ni prendre ni s'interposer en f8.
- q: Roi noir en h8, tour noire en g8, pions noirs en g7 et h7. Ton cavalier arrive en f7 avec échec, et aucune pièce noire ne peut le prendre. Quel mat ?
  options:
  - Mat de Boden
  - 'Mat étouffé : le roi est entouré par ses propres pièces'
  - Mat du couloir
  - Ce n'est pas mat
  answer: 1
  explain: g8, g7 et h7 sont occupées par des pièces noires, et l'échec d'un cavalier ne peut pas être intercepté.
- q: Tu envisages Fxh7+ mais les Noirs ont un cavalier en f6 et ton cavalier ne peut pas aller en g5. Que penser ?
  options:
  - Le sacrifice marche toujours
  - 'Les conditions ne sont pas réunies : le sacrifice est très probablement incorrect'
  - Il faut le jouer pour le style
  - C'est un mat forcé
  answer: 1
  explain: Sans Cg5 et avec un défenseur en f6, le roi noir s'échappe et tu perds un fou.
- q: Tu as roqué côté roi, l'adversaire côté dame. Quel plan ?
  options:
  - Attendre
  - Pousser tes pions a et b contre son roi pour ouvrir des colonnes, vite
  - Pousser tes pions g et h
  - Échanger toutes les pièces
  answer: 1
  explain: Avec les roques opposés, on attaque avec les pions situés devant le roi adverse, ceux qu'on n'a pas besoin de garder pour son propre roi.
---

Le mat met fin à la partie quel que soit le matériel : une attaque réussie sur le roi vaut plus que n'importe quel gain de pièce. Mais une attaque se **prépare** : il faut des pièces dans la zone, des lignes ouvertes, et connaître les **schémas de mat** qui reviennent partout.

## Les conditions d'une attaque

1. **Plus d'attaquants que de défenseurs** près du roi.
2. Des **lignes ouvertes** vers le roi (colonne, diagonale).
3. Des **faiblesses** dans le roque adverse : pions avancés (h6, g6), cases noires ou blanches sans fou pour les défendre.
4. Souvent une **avance de développement** ou un roi resté au centre.

Une attaque prématurée, sans ces éléments, rend souvent l'initiative à l'adversaire.

## Les mats types

| Mat | Pièces | Schéma |
| --- | --- | --- |
| **Couloir** | tour ou dame | mat sur la rangée du fond, roi bloqué par ses pions f, g, h |
| **Étouffé** | cavalier | roi en h8 entouré de ses pièces ; Dg8+ Txg8 Cf7# |
| **Anastasie** | cavalier + tour | Ce7 coupe g8 et g6, tour mate sur la colonne h (roi en h7) |
| **Arabe** | cavalier + tour | Cf6 protège Th7, roi en h8 |
| **Boden** | deux fous | diagonales croisées sur un roi roqué côté dame |
| **Damiano** | dame + pion | dame en h7 soutenue par un pion g6 |
| **Lolli** | dame + pion | pion en f6, dame en g7 |
| **Épaulettes** | dame | roi encadré par ses deux tours, dame en face |
| **Légal** | pièces mineures | sacrifice de dame en ouverture, mat par cavaliers et fou en e7 |

Les connaître permet de **voir le mat à l'avance** : on reconnaît la position cible et on cherche comment l'atteindre.

<!-- schema:etouffe -->
<figure class="diagram"><svg viewBox="0 0 680 320" role="img" aria-label="Le mat étouffé" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="60" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="20" width="34" height="34" rx="0" class="dg-sqh"/><rect x="60" y="20" width="272" height="272" rx="0" class="dg-board"/><text x="77.0" y="306" class="dg-coord" text-anchor="middle">a</text><text x="50" y="279.0" class="dg-coord" text-anchor="middle">1</text><text x="111.0" y="306" class="dg-coord" text-anchor="middle">b</text><text x="50" y="245.0" class="dg-coord" text-anchor="middle">2</text><text x="145.0" y="306" class="dg-coord" text-anchor="middle">c</text><text x="50" y="211.0" class="dg-coord" text-anchor="middle">3</text><text x="179.0" y="306" class="dg-coord" text-anchor="middle">d</text><text x="50" y="177.0" class="dg-coord" text-anchor="middle">4</text><text x="213.0" y="306" class="dg-coord" text-anchor="middle">e</text><text x="50" y="143.0" class="dg-coord" text-anchor="middle">5</text><text x="247.0" y="306" class="dg-coord" text-anchor="middle">f</text><text x="50" y="109.0" class="dg-coord" text-anchor="middle">6</text><text x="281.0" y="306" class="dg-coord" text-anchor="middle">g</text><text x="50" y="75.0" class="dg-coord" text-anchor="middle">7</text><text x="315.0" y="306" class="dg-coord" text-anchor="middle">h</text><text x="50" y="41.0" class="dg-coord" text-anchor="middle">8</text><text x="281.0" y="286.0" class="dg-pw" text-anchor="middle">♚︎</text><text x="247.0" y="82.0" class="dg-pw" text-anchor="middle">♞︎</text><text x="315.0" y="252.0" class="dg-pw" text-anchor="middle">♟︎</text><text x="281.0" y="252.0" class="dg-pw" text-anchor="middle">♟︎</text><text x="315.0" y="48.0" class="dg-pb" text-anchor="middle">♚︎</text><text x="281.0" y="48.0" class="dg-pb" text-anchor="middle">♜︎</text><text x="281.0" y="82.0" class="dg-pb" text-anchor="middle">♟︎</text><text x="315.0" y="82.0" class="dg-pb" text-anchor="middle">♟︎</text><path d="M247.0 71.0 L315.0 37.0" class="dg-l a dash" marker-end="url(#g2-a)"/><text x="380" y="110" class="dg-tl" text-anchor="start">Cf7# : le roi h8 est enfermé</text><text x="380" y="132" class="dg-tl" text-anchor="start">par ses propres pièces.</text><text x="380" y="170" class="dg-s" text-anchor="start">Souvent après Dg8+ !! Txg8 :</text><text x="380" y="188" class="dg-s" text-anchor="start">la tour vient boucher g8.</text></svg><figcaption>g8, g7 et h7 sont occupées par des pièces noires : l&#x27;échec du cavalier ne peut être ni intercepté ni fui.</figcaption></figure>
<!-- /schema:etouffe -->

## Le sacrifice grec

Fxh7+ Rxh7 Cg5+ suivi de Dh5 (ou Dd3, Dc2 selon les cas) : le plus célèbre sacrifice d'attaque.

Conditions habituelles :

- fou blanc sur la diagonale **b1-h7** ;
- cavalier pouvant aller en **g5** sans être pris (pas de fou noir en e7 qui le contrôle, ou alors calculé) ;
- dame pouvant rejoindre **h5** rapidement ;
- **pas de cavalier noir en f6** (souvent chassé par un pion blanc en e5) ;
- les Noirs ne peuvent pas défendre h7 par …Ff5 ou …Te8 suivi de …Rf8.

Après Fxh7+ Rxh7 Cg5+, le roi a trois réponses (Rg8, Rg6, Rh6) ; il faut les calculer **toutes** avant de sacrifier.

## Démolir le roque

- **Sacrifice en g7 ou h7** pour ouvrir les cases du roi ;
- **double sacrifice des fous** (Lasker contre Bauer, Amsterdam 1889) : Fxh7+ puis Fxg7, pour ouvrir complètement le roi ;
- **sacrifice en f7** (ou f2), la case défendue seulement par le roi au début de partie ;
- **levier de pions** : h4-h5 contre un roque fianchetté (fou en g7) pour ouvrir la colonne h.

## Les roques opposés

Quand les rois sont roqués de côtés différents, chaque camp peut lancer ses **pions** à l'assaut sans affaiblir son propre roi. C'est une **course** : chaque temps compte. Ouvrir une colonne en premier, échanger le fou qui défend le roi adverse, et ne pas réagir passivement sur l'autre aile. La Sicilienne Dragon, variante Yougoslave (Fe3, Dd2, O-O-O, h4-h5), en est l'exemple type.

## Défendre son roi

- garder des **défenseurs** près du roi, en particulier le cavalier f6 (ou f3) et le fou du fianchetto ;
- éviter les coups de pions inutiles devant le roi ;
- **échanger les attaquants** : chaque échange affaiblit l'attaque ;
- **contre-attaquer au centre** : « une attaque sur l'aile se combat par une action au centre ».

> **À retenir.** Une attaque demande plus d'attaquants que de défenseurs et des lignes ouvertes. Connais les mats types (couloir, étouffé, Anastasie, arabe, Boden, Damiano) pour les voir à l'avance. Le sacrifice grec Fxh7+ exige Cg5, la dame vers h5 et l'absence de cavalier en f6. Avec les roques opposés, lance tes pions vite. En défense, échange les attaquants et réagis au centre.
