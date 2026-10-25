---
title: Synthèse échecs
description: "Règles, valeur des pièces, mats élémentaires, motifs tactiques, combinaisons, attaque du roi, calcul, stratégie, ouvertures, finales et méthode de progression."
---

## Bases

- Roque : roi et tour jamais déplacés, rien entre eux, roi ni en échec, ni traversant, ni arrivant sur une case attaquée.
- Prise en passant : seulement au coup qui suit la double avance. Promotion en D, T, F ou C.
- Pat = nulle. Nulles aussi par accord, triple répétition, 50 coups, matériel insuffisant.
- Notation : pièce + case (Cf3, Fxc6, O-O, e8=D). R, D, T, F, C en français ; K, Q, R, B, N en anglais.
- Valeurs : pion 1, cavalier 3, fou 3 (+ paire de fous), tour 5, dame 9. Qualité ≈ 2.
- Ouverture : centre, développement des pièces mineures, roque rapide, tours reliées, pas de dame trop tôt.
- Mats élémentaires : repousser le roi vers le bord. Dame à un saut de cavalier ; tour avec opposition des rois et échec latéral ; deux tours en escalier. Attention au pat.

## Tactique

| Motif | Idée |
| --- | --- |
| Fourchette | une pièce, deux cibles |
| Clouage | la pièce ne peut pas bouger sans exposer ce qui est derrière |
| Enfilade | la pièce précieuse devant s'écarte |
| Découverte | la pièce qui bouge démasque une autre ; échec double = le roi doit bouger |
| Déviation, attraction | faire partir un défenseur, faire venir le roi |
| Surcharge | un défenseur, deux tâches |
| Coup intermédiaire | un échec ou une menace avant la reprise attendue |

- Mats types : couloir, étouffé, Anastasie, arabe, Boden, Damiano.
- Sacrifice grec Fxh7+ : il faut Cg5, la dame vers h5 et pas de cavalier en f6.
- Calcul : menace adverse, puis échecs, prises, menaces des deux camps ; 2 à 4 candidats ; meilleure défense ; évaluation finale ; vérification anti-gaffe.

## Stratégie

- Faiblesses de pions : isolé, arriéré, doublés, îlots. La case devant est un avant-poste adverse.
- Pion dame isolé : activité avec les pièces, faiblesse en finale. Le bloquer avec un cavalier.
- Pion passé : le pousser, le bloquer avec un cavalier, tour derrière lui (Tarrasch).
- Chaîne : jouer du côté où elle pointe, attaquer la base adverse.
- Mauvais fou : pions fixés sur sa couleur. Fou en position ouverte et pions sur deux ailes, cavalier en position fermée et sur avant-poste.
- Espace : celui qui l'a évite les échanges, l'autre les cherche et prépare une rupture.
- Plan : lister les déséquilibres, choisir un objectif, placer les pièces, vérifier les ripostes. Prophylaxie : « que veut l'adversaire ? »
- Convertir : deux faiblesses, échanger les pièces avec un pion de plus, éviter les fous de couleur opposée.

## Ouvertures

| Après 1.e4 | Après 1.d4 |
| --- | --- |
| Italienne, Espagnole, Écossaise, Petrov | Gambit dame (accepté, refusé), Slave |
| Sicilienne (combative) | Nimzo-Indienne, Ouest-Indienne |
| Française, Caro-Kann (solides) | Est-Indienne, Grünfeld (dynamiques) |
| Pirc, Scandinave, Alekhine | Hollandaise, Benoni ; Londres côté Blancs |

- Répertoire : une ouverture avec les Blancs, une défense contre 1.e4 et contre 1.d4. Idées, structures et pièges avant les variantes.

## Finales

- Pions : roi actif, règle du carré, opposition, cases critiques (pion e4 : d6, e6, f6), pion de tour et roi dans le coin = nulle, triangulation, pion passé éloigné.
- Tours : tour active et derrière les pions passés. Lucena : construire un pont (tour en 4ᵉ rangée). Philidor : tour en 3ᵉ rangée, puis échecs par derrière.
- Pièces mineures : fou si pions sur deux ailes ; fous de couleur opposée souvent nuls ; fou de la mauvaise couleur + pion de tour = nulle.
- Dame contre pion en 7ᵉ : gain contre pion central ou de cavalier, souvent nulle contre pion de tour ou de fou.

## Progresser

- Elo : 200 points d'écart ≈ 75 % pour le plus fort.
- Tactique chaque jour, finales, parties lentes analysées seul puis avec le moteur.
- Temps : vite sur les coups évidents, lentement aux moments critiques. Pause en cas de tilt.
