---
title: Règles complètes et notation
chapter: 1
order: 1
duration: 14
level: Bases
tags:
- règles
- notation
- roque
- prise en passant
- nulle
cards:
- q: Quelles sont les conditions du roque ?
  a: Le roi et la tour concernée **n'ont jamais bougé**, aucune pièce entre eux, le roi **n'est pas en échec**, et il ne **traverse** ni n'**arrive** sur une case attaquée. La tour, elle, peut être attaquée ou traverser une case attaquée.
- q: Qu'est-ce que la prise en passant ?
  a: Quand un pion avance de **deux cases** et s'arrête à côté d'un pion adverse sur sa 5ᵉ rangée (4ᵉ pour les Noirs), ce pion peut le prendre **comme s'il n'avait avancé que d'une case**. Uniquement au coup **immédiatement suivant**.
- q: Comment lire la notation algébrique ?
  a: 'Lettre de la pièce (**R** roi, **D** dame, **T** tour, **F** fou, **C** cavalier ; rien pour un pion) puis case d''arrivée : **Cf3**. Prise : **x** (Fxc6, exd5). Échec : **+**, mat : **#**, petit roque **O-O**, grand roque **O-O-O**, promotion **e8=D**. En anglais : K, Q, R, B, N.'
- q: Quelle différence entre mat et pat ?
  a: '**Mat** : le roi est en échec et aucun coup ne l''en sort, la partie est perdue. **Pat** : le joueur au trait n''est **pas en échec** mais n''a **aucun coup légal** : la partie est **nulle**. Le pat est le piège classique quand on gagne avec beaucoup de matériel.'
- q: Quelles sont les façons de faire nulle ?
  a: '**Pat**, **accord** mutuel, **triple répétition** de la même position (même joueur au trait, mêmes droits), règle des **50 coups** sans prise ni coup de pion, **matériel insuffisant** (roi contre roi, roi et fou, roi et cavalier), et à la pendule : temps écoulé quand l''adversaire ne peut plus mater.'
- q: Que dit la règle « pièce touchée, pièce jouée » ?
  a: En partie officielle, une pièce **touchée volontairement** doit être jouée (si elle a un coup légal), et une pièce adverse touchée doit être **prise** si possible. Pour ajuster une pièce sans la jouer, on dit **« j'adoube »** avant de la toucher.
- q: Que signifient !, ?, !? et ?! en annotation ?
  a: '**!** bon coup, **!!** coup brillant, **?** erreur, **??** gaffe, **!?** coup intéressant (risqué mais prometteur), **?!** coup douteux. On les trouve dans toutes les parties commentées.'
quiz:
- q: Ton roi est en e1, ta tour en h1, rien entre eux. Le fou adverse attaque f1. Peux-tu faire le petit roque ?
  options:
  - Oui, seule la case d'arrivée compte
  - 'Non : le roi traverserait f1, qui est attaquée'
  - Oui si tu n'es pas en échec
  - Non, parce que la tour serait attaquée
  answer: 1
  explain: Le roi ne peut ni partir d'une case en échec, ni traverser, ni arriver sur une case attaquée.
- q: Ton pion est en e5. Les Noirs jouent d7-d5. Que peux-tu faire au coup suivant ?
  options:
  - Rien de spécial
  - 'Prendre en passant : exd6'
  - Prendre en d5
  - Seulement si tu es en échec
  answer: 1
  explain: 'Le pion arrive à côté du tien après une double avance : exd6 est possible uniquement maintenant.'
- q: Tu as roi et dame contre roi seul. Le roi noir est en h8, ta dame en g6, ton roi loin. Les Noirs sont au trait et n'ont aucun coup légal, sans être en échec. Résultat ?
  options:
  - Tu as gagné
  - Nulle par pat
  - Les Noirs passent leur tour
  - Tu dois rejouer
  answer: 1
  explain: Le pat termine la partie par une nulle. Toujours vérifier que l'adversaire garde un coup avant de le serrer.
- q: La même position apparaît pour la troisième fois avec le même joueur au trait. Que peut-on faire ?
  options:
  - Rien
  - Réclamer la nulle par triple répétition
  - Le dernier à avoir joué perd
  - On recommence la partie
  answer: 1
  explain: 'La répétition n''a pas besoin d''être consécutive : il faut la même position, le même trait et les mêmes droits (roque, prise en passant).'
---

Les échecs se jouent sur 64 cases, avec des règles simples en apparence, mais quelques exceptions (roque, prise en passant, promotion, pat) décident de nombreuses parties. Cette fiche rassemble toutes les règles et la notation utilisée dans le reste du module.

## L'échiquier

- La case **en bas à droite** de chaque joueur est **blanche** (« blanc à droite »).
- Les **colonnes** vont de **a à h** (de gauche à droite vu des Blancs), les **rangées** de **1 à 8** (des Blancs vers les Noirs).
- La dame se place sur **sa couleur** : dame blanche en d1 (case blanche), dame noire en d8 (case noire).
- Les Blancs commencent.

## Le déplacement des pièces

| Pièce | Lettre | Déplacement |
| --- | --- | --- |
| **Roi** | R | une case dans toutes les directions |
| **Dame** | D | ligne droite et diagonale, autant de cases que voulu |
| **Tour** | T | ligne droite (colonne ou rangée) |
| **Fou** | F | diagonale ; reste toujours sur la même couleur |
| **Cavalier** | C | en « L » (deux cases puis une sur le côté) ; **saute** par-dessus les pièces |
| **Pion** | — | avance d'une case (deux au premier coup) ; **prend en diagonale** |

Aucune pièce sauf le cavalier ne peut sauter. On prend en se posant sur la case de la pièce adverse.

## Les coups spéciaux

### Le roque

Le roi se déplace de **deux cases** vers une tour, et la tour passe de l'autre côté du roi. Petit roque (côté roi) : **O-O** ; grand roque (côté dame) : **O-O-O**.

Conditions :

1. ni le roi ni cette tour n'ont encore bougé ;
2. aucune pièce entre eux ;
3. le roi n'est **pas en échec** ;
4. le roi ne **traverse** pas et n'**arrive** pas sur une case attaquée.

On peut roquer si la **tour** est attaquée, ou si elle traverse une case attaquée (b1 au grand roque).

### La prise en passant

Un pion qui avance de deux cases et s'arrête **à côté** d'un pion adverse placé sur sa 5ᵉ rangée peut être pris comme s'il n'avait avancé que d'une case. Le droit ne vaut **qu'au coup suivant**. Exemple : pion blanc en e5, les Noirs jouent d7-d5, les Blancs peuvent jouer **exd6**.

### La promotion

Un pion qui atteint la dernière rangée devient obligatoirement une **dame, une tour, un fou ou un cavalier**, au choix (pas un roi ni un pion). On choisit presque toujours la dame ; une **sous-promotion** (en cavalier pour donner échec, en tour pour éviter un pat) sert parfois.

## Échec, mat et pat

- **Échec** : le roi est attaqué. On doit parer : déplacer le roi, prendre la pièce qui donne échec, ou s'interposer (impossible contre un cavalier).
- **Mat** : échec sans parade, la partie est perdue.
- **Pat** : pas d'échec, mais **aucun coup légal** : partie **nulle**.

## Les autres fins de partie

| Fin | Règle |
| --- | --- |
| **Abandon** | un joueur s'avoue vaincu |
| **Nulle par accord** | proposée après avoir joué son coup |
| **Triple répétition** | même position trois fois (même trait, mêmes droits), même non consécutive |
| **50 coups** | 50 coups de chaque joueur sans prise ni mouvement de pion |
| **Matériel insuffisant** | R contre R, R+F contre R, R+C contre R, R+F contre R+F de même couleur |
| **Temps** | perdu si la pendule tombe, sauf si l'adversaire n'a plus de matériel pour mater (nulle) |

## La notation algébrique

Chaque coup s'écrit : **lettre de la pièce + case d'arrivée**.

| Exemple | Signification |
| --- | --- |
| e4 | pion en e4 |
| Cf3 | cavalier en f3 |
| Fxc6 | fou prend en c6 |
| exd5 | pion de la colonne e prend en d5 |
| Tad1 | la tour de la colonne a va en d1 (quand deux tours peuvent y aller) |
| Dh5+ | dame en h5, échec |
| Dxf7# | dame prend f7, mat |
| O-O, O-O-O | petit roque, grand roque |
| e8=D | promotion en dame |

En anglais (sites et livres) : K roi, Q dame, R tour, B fou, N cavalier. Une partie s'écrit par paires numérotées : **1.e4 e5 2.Cf3 Cc6 3.Fb5**. « 3...a6 » désigne le coup noir.

Annotations : **!** bon coup, **!!** brillant, **?** erreur, **??** gaffe, **!?** intéressant, **?!** douteux.

## En partie officielle

- **Pièce touchée, pièce jouée** ; « j'adoube » pour ajuster une pièce.
- On joue avec **une seule main** et on appuie sur la pendule avec la même main.
- Un coup illégal est corrigé et pénalisé (souvent du temps donné à l'adversaire ; au second, la partie peut être perdue).
- Cadences : **classique** (90 minutes et plus), **rapide** (10 à 60 minutes), **blitz** (moins de 10 minutes), souvent avec un **incrément** par coup (Fischer : par exemple 3 min + 2 s).

> **À retenir.** Roque : ni roi ni tour déplacés, rien entre eux, roi ni en échec, ni traversant, ni arrivant sur une case attaquée. Prise en passant : uniquement au coup suivant la double avance. Le pat est une nulle, piège classique du camp qui gagne. Nulles aussi par répétition, 50 coups, matériel insuffisant. Notation : pièce + case (Cf3, Fxc6, O-O, e8=D).
