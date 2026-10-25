---
title: Les motifs tactiques
chapter: 4
order: 1
duration: 15
level: Tactique
tags:
- tactique
- fourchette
- clouage
- enfilade
- découverte
- double attaque
cards:
- q: Qu'est-ce qu'une fourchette ?
  a: Une pièce qui attaque **deux cibles à la fois**. Le cavalier est le spécialiste (fourchette roi-dame, « fourchette royale »), mais pions, fous et dames en font aussi. L'adversaire ne peut parer qu'une menace.
- q: Quelle différence entre clouage absolu et relatif ?
  a: '**Absolu** : la pièce clouée protège le **roi**, elle ne peut légalement pas bouger. **Relatif** : elle protège une pièce plus précieuse (dame, tour) ; elle peut bouger, mais on perd ce qu''il y a derrière.'
- q: Qu'est-ce qu'une enfilade ?
  a: 'Le contraire du clouage : on attaque une pièce **précieuse** qui doit s''écarter et découvre une pièce **moins précieuse** derrière elle, qu''on prend. Exemple : une tour donne échec au roi, qui bouge, et la tour prend la dame derrière.'
- q: Qu'est-ce qu'une attaque à la découverte ?
  a: Une pièce bouge et **démasque** l'attaque d'une pièce placée derrière elle. Si la pièce qui bouge crée **aussi** une menace, l'adversaire fait face à deux attaques. Si la pièce démasquée donne échec, c'est un **échec à la découverte**, l'une des armes les plus fortes.
- q: Qu'est-ce qu'un échec double ?
  a: 'Une découverte où **les deux pièces** donnent échec en même temps. On ne peut ni prendre ni s''interposer contre deux pièces : **le roi doit bouger**. C''est souvent décisif.'
- q: Qu'est-ce qu'une pièce en prise ou non protégée ?
  a: 'Une pièce **attaquée et non défendue** (ou défendue moins de fois qu''attaquée). « Les pièces non protégées tombent » : la majorité des combinaisons commencent par une pièce sans défense.'
- q: Qu'est-ce que la menace de mat comme motif ?
  a: Un coup qui **menace de mater** oblige l'adversaire à parer, ce qui lui interdit de répondre à une autre menace. Combiner menace de mat et attaque d'une pièce est une double attaque.
quiz:
- q: Ton cavalier peut aller en c7, où il attaque le roi noir en e8 et la tour en a8. La case est sûre. Quel motif ?
  options:
  - Clouage
  - Fourchette
  - Enfilade
  - Surcharge
  answer: 1
  explain: 'Une fourchette avec échec : le roi doit bouger, la tour tombe.'
- q: Ton fou en b5 attaque le cavalier c6 ; derrière lui sur la diagonale, il y a le roi en e8. Le cavalier peut-il bouger ?
  options:
  - Oui
  - Non, il est cloué de façon absolue
  - Seulement pour prendre
  - Seulement en arrière
  answer: 1
  explain: 'Bouger le cavalier exposerait le roi : coup illégal. On peut ensuite attaquer la pièce clouée avec un pion (d4-d5), car elle ne peut pas fuir.'
- q: Ta tour est en e1, ton fou en e4, le roi noir en e8, rien d'autre sur la colonne e. Tu joues Fxh7 et prends un pion. Que se passe-t-il ?
  options:
  - Rien de spécial
  - 'Échec à la découverte : les Noirs doivent d''abord parer l''échec de la tour, ton fou est provisoirement à l''abri'
  - Échec double
  - Clouage du fou
  answer: 1
  explain: La tour démasquée donne échec. Le fou a pu prendre sans crainte immédiate.
- q: Le roi noir est en d6 et la dame noire en d2, sur la même colonne. Ta tour arrive en d8 avec échec. Quel motif ?
  options:
  - 'Enfilade : le roi s''écarte, la tour prend la dame'
  - Fourchette
  - Clouage relatif
  - Pat
  answer: 0
  explain: 'La pièce la plus précieuse est devant : elle s''écarte, celle de derrière tombe.'
---

Les combinaisons qui gagnent des parties reposent sur une dizaine de **motifs** qui reviennent sans cesse. Les reconnaître instantanément est la compétence qui fait le plus progresser jusqu'à un bon niveau de club : on dit souvent que les échecs sont « à 99 % de la tactique » pour l'amateur.

## La double attaque et la fourchette

Une pièce menace **deux choses** : l'adversaire ne peut en sauver qu'une.

| Pièce | Fourchette typique |
| --- | --- |
| **Cavalier** | roi et dame (« fourchette royale »), dame et tour ; il ne peut pas être bloqué |
| **Pion** | deux pièces en avançant (e4-e5 attaquant cavalier et fou) |
| **Dame** | une pièce non protégée et une menace de mat |
| **Fou, tour** | deux pièces sur deux diagonales ou deux lignes |

Pour repérer une fourchette de cavalier : chercher les pièces adverses **à un saut de cavalier l'une de l'autre** (même couleur de case, distance en « double L »).

<!-- schema:fourchette -->
<figure class="diagram"><svg viewBox="0 0 680 320" role="img" aria-label="La fourchette royale" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="60" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="54" width="34" height="34" rx="0" class="dg-sqh"/><rect x="60" y="20" width="272" height="272" rx="0" class="dg-board"/><text x="77.0" y="306" class="dg-coord" text-anchor="middle">a</text><text x="50" y="279.0" class="dg-coord" text-anchor="middle">1</text><text x="111.0" y="306" class="dg-coord" text-anchor="middle">b</text><text x="50" y="245.0" class="dg-coord" text-anchor="middle">2</text><text x="145.0" y="306" class="dg-coord" text-anchor="middle">c</text><text x="50" y="211.0" class="dg-coord" text-anchor="middle">3</text><text x="179.0" y="306" class="dg-coord" text-anchor="middle">d</text><text x="50" y="177.0" class="dg-coord" text-anchor="middle">4</text><text x="213.0" y="306" class="dg-coord" text-anchor="middle">e</text><text x="50" y="143.0" class="dg-coord" text-anchor="middle">5</text><text x="247.0" y="306" class="dg-coord" text-anchor="middle">f</text><text x="50" y="109.0" class="dg-coord" text-anchor="middle">6</text><text x="281.0" y="306" class="dg-coord" text-anchor="middle">g</text><text x="50" y="75.0" class="dg-coord" text-anchor="middle">7</text><text x="315.0" y="306" class="dg-coord" text-anchor="middle">h</text><text x="50" y="41.0" class="dg-coord" text-anchor="middle">8</text><text x="213.0" y="286.0" class="dg-pw" text-anchor="middle">♚︎</text><text x="179.0" y="150.0" class="dg-pw" text-anchor="middle">♞︎</text><text x="213.0" y="48.0" class="dg-pb" text-anchor="middle">♚︎</text><text x="77.0" y="48.0" class="dg-pb" text-anchor="middle">♜︎</text><text x="111.0" y="82.0" class="dg-pb" text-anchor="middle">♟︎</text><text x="247.0" y="82.0" class="dg-pb" text-anchor="middle">♟︎</text><path d="M179.0 139.0 L145.0 71.0" class="dg-l a" marker-end="url(#g1-a)"/><path d="M145.0 71.0 L213.0 37.0" class="dg-l a dash" marker-end="url(#g1-a)"/><path d="M145.0 71.0 L77.0 37.0" class="dg-l a dash" marker-end="url(#g1-a)"/><text x="380" y="110" class="dg-tl" text-anchor="start">Cc7+ attaque le roi e8</text><text x="380" y="132" class="dg-tl" text-anchor="start">et la tour a8 en même temps.</text><text x="380" y="170" class="dg-s" text-anchor="start">Le roi doit bouger :</text><text x="380" y="188" class="dg-s" text-anchor="start">Cxa8 gagne la qualité.</text></svg><figcaption>Le cavalier arrive en c7 avec échec et attaque aussi la tour : une seule des deux menaces peut être parée.</figcaption></figure>
<!-- /schema:fourchette -->

## Le clouage

Une pièce ne peut pas (ou ne doit pas) bouger parce qu'elle protège ce qui est derrière elle.

- **Absolu** : derrière, le **roi**. Bouger est illégal.
- **Relatif** : derrière, la dame ou une tour. Bouger coûte cher.

Seuls les fous, tours et dames clouent. Exploiter un clouage : **attaquer la pièce clouée** à nouveau, idéalement avec un pion, car elle ne peut pas fuir. Se libérer : interposer, rompre le clouage en attaquant la pièce qui cloue, ou déplacer ce qu'il y a derrière.

## L'enfilade

Le clouage à l'envers : la pièce **précieuse est devant**. Elle s'écarte, celle qui était derrière tombe. Fréquent en finale : une tour donne échec au roi, et prend la tour cachée derrière lui.

## L'attaque à la découverte

Une pièce s'écarte et **démasque** une ligne. Deux armes en une :

- la pièce qui bouge fait sa propre menace (prise, échec, attaque) ;
- la pièce démasquée attaque autre chose.

Variante maximale : l'**échec à la découverte**. La pièce qui bouge peut aller **n'importe où**, même se faire prendre, puisque l'adversaire doit parer l'échec. Et l'**échec double**, où les deux pièces donnent échec : le roi doit bouger, aucune autre parade n'existe.

Le « **moulin** » (tour et fou alternant échecs à la découverte) peut raser une position entière : célèbre exemple, Torre contre Lasker, Moscou 1925.

## Les pièces non protégées

La règle de John Nunn : « **Loose pieces drop off** » (les pièces non protégées tombent). Avant chaque coup, repérer :

- les pièces **non défendues** des deux camps ;
- les pièces **défendues une seule fois** et attaquées deux fois ;
- le **roi** exposé (échecs possibles).

Ce sont les cibles des doubles attaques.

## La rangée du fond et la menace de mat

Une **menace de mat** est une attaque sur la pièce la plus précieuse. Combinée à une autre menace, elle fait une double attaque imparable : la dame qui menace mat **et** une tour non protégée.

## S'entraîner

- **Exercices tactiques** quotidiens (15 à 30 minutes) sur Lichess ou Chess.com, organisés par thème puis mélangés ;
- résoudre **sans bouger les pièces**, calculer jusqu'au bout avant de répondre ;
- revoir les motifs manqués : on apprend un motif quand on l'a raté une fois.

> **À retenir.** Fourchette : une pièce, deux cibles (le cavalier excelle). Clouage : la pièce ne peut pas bouger sans exposer ce qui est derrière ; attaque-la encore. Enfilade : la pièce précieuse devant s'écarte. Découverte : la pièce qui bouge menace aussi ; l'échec double force le roi à bouger. Les pièces non protégées sont les cibles de toutes ces combinaisons.
