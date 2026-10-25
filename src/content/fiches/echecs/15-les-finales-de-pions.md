---
title: Les finales de pions
chapter: 15
order: 1
duration: 17
level: Finales
tags:
- finale
- opposition
- règle du carré
- cases critiques
- triangulation
cards:
- q: Qu'est-ce que la règle du carré ?
  a: 'Pour savoir si un roi rattrape un pion passé sans aide : tracer un **carré** dont un côté va du pion à sa case de promotion. Si le roi peut **entrer dans le carré** (au trait), il rattrape le pion. Au premier coup, un pion qui avance de deux cases : compter depuis la case d''arrivée.'
- q: Qu'est-ce que l'opposition ?
  a: 'Les deux rois **face à face** sur une colonne (ou rangée), avec **une case** entre eux. Celui qui **n''est pas au trait** « a l''opposition » : l''autre doit céder le passage. Variantes : opposition **lointaine** (3 ou 5 cases entre eux) et **diagonale**.'
- q: Que sont les cases critiques ?
  a: 'Les cases que le roi attaquant doit atteindre pour **gagner à coup sûr** avec un pion. Pour un pion (hors pion de tour) sur sa 2ᵉ, 3ᵉ ou 4ᵉ rangée : les **trois cases deux rangées devant lui** (pion e4 : d6, e6, f6). Pour un pion en 5ᵉ ou 6ᵉ rangée, les cases juste devant et deux rangées devant.'
- q: 'Roi et pion contre roi : quand est-ce gagné ?'
  a: 'Si le roi attaquant atteint une **case critique**. En pratique : roi **devant son pion**, et l''opposition au bon moment. Si le roi défenseur se place **devant le pion** avec l''opposition, c''est souvent nulle. Le roi attaquant en **6ᵉ rangée devant son pion** gagne toujours (sauf pion de tour).'
- q: Pourquoi le pion de tour est-il spécial ?
  a: 'Avec un pion **a** ou **h**, si le roi défenseur atteint le **coin** de promotion (ou la case devant), c''est **nulle** : le roi attaquant ne peut pas le déloger sans faire pat. Même règle avec un fou qui ne contrôle pas la case de promotion.'
- q: Qu'est-ce que la triangulation ?
  a: Une manœuvre du roi en **trois coups** (un triangle) pour revenir sur la même case et **perdre un temps**, et ainsi donner le trait à l'adversaire. Elle fonctionne quand le roi adverse a moins de cases disponibles pour faire de même.
- q: Qu'est-ce que le zugzwang ?
  a: 'Une position où **le joueur au trait** aurait préféré passer : tout coup aggrave sa position. Très fréquent en finale de pions, c''est le ressort de l''opposition et de la triangulation.'
quiz:
- q: Pion blanc en a4, roi noir en d4, Noirs au trait. Rattrapent-ils le pion ?
  options:
  - Non
  - 'Oui : le roi est déjà dans le carré a4-e4-e8-a8'
  - Seulement si les Blancs jouent mal
  - Impossible à dire
  answer: 1
  explain: 'Le pion a 5 cases à parcourir jusqu''à a8 (a4 compris) : le carré va de a4 à e4 et de a8 à e8. Le roi en d4 y est : après Rc5, a5 Rb6, il rattrape le pion.'
- q: Roi blanc e5, pion e4, roi noir e7. Les Noirs sont au trait. Que se passe-t-il ?
  options:
  - Nulle
  - 'Les Blancs ont l''opposition : le roi noir doit céder, et le roi blanc atteint une case critique (d6, e6 ou f6) : gain'
  - Les Noirs gagnent
  - Pat
  answer: 1
  explain: 'Les rois sont face à face, les Noirs au trait doivent s''écarter : Re5-d6 ou f6 suit, avec gain.'
- q: Pion blanc en h6, roi blanc en g6, roi noir en h8. Résultat ?
  options:
  - Gain facile
  - 'Nulle : le roi noir tient le coin, et les Blancs ne peuvent pas le déloger sans pat'
  - Défaite blanche
  - Gain en 3 coups
  answer: 1
  explain: Avec un pion de tour, le roi défenseur dans le coin suffit pour la nulle.
- q: 'Finale de pions : tu as un pion passé éloigné à l''aile dame, les autres pions sont à l''aile roi. Quel plan ?'
  options:
  - Le garder chez toi
  - Le pousser pour attirer le roi adverse, puis aller manger ses pions à l'aile roi avec ton roi
  - L'échanger
  - Rien
  answer: 1
  explain: Le pion passé éloigné est l'avantage décisif typique des finales de pions.
---

Les finales de pions sont les plus **exactes** : avec peu de pièces, tout se calcule, et un seul temps change le résultat. Elles sont aussi la destination de nombreuses simplifications : les connaître permet de savoir **quand** on peut échanger la dernière pièce.

## Le roi devient actif

En finale, le roi est une pièce **forte**, qui contrôle 8 cases. Règle n° 1 : **centraliser le roi** dès que les dames sont échangées. Un roi actif vaut souvent un pion.

## La règle du carré

Un pion passé seul contre le roi adverse : tracer le carré dont un côté va du pion à sa case de promotion.

- si le roi adverse, **à son tour de jouer**, peut entrer dans le carré, il rattrape le pion ;
- sinon, le pion va à dame ;
- un pion encore sur sa case de départ compte comme s'il avait déjà avancé de deux cases ;
- attention aux pièces qui **gênent** le roi sur son chemin.

## L'opposition

Deux rois face à face avec une case entre eux : celui qui n'est **pas au trait** a l'opposition. L'autre doit céder une case.

| Type | Distance entre les rois |
| --- | --- |
| directe | 1 case |
| lointaine | 3 ou 5 cases sur la même ligne |
| diagonale | sur une diagonale, nombre impair de cases |

L'opposition sert à **forcer le passage** (attaquant) ou à **bloquer** (défenseur).

<!-- schema:opposition -->
<figure class="diagram"><svg viewBox="0 0 680 320" role="img" aria-label="L&#x27;opposition" style="--minw:560px"><defs><marker id="g3-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g3-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g3-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g3-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="60" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="196" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="230" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="60" y="20" width="272" height="272" rx="0" class="dg-board"/><text x="77.0" y="306" class="dg-coord" text-anchor="middle">a</text><text x="50" y="279.0" class="dg-coord" text-anchor="middle">1</text><text x="111.0" y="306" class="dg-coord" text-anchor="middle">b</text><text x="50" y="245.0" class="dg-coord" text-anchor="middle">2</text><text x="145.0" y="306" class="dg-coord" text-anchor="middle">c</text><text x="50" y="211.0" class="dg-coord" text-anchor="middle">3</text><text x="179.0" y="306" class="dg-coord" text-anchor="middle">d</text><text x="50" y="177.0" class="dg-coord" text-anchor="middle">4</text><text x="213.0" y="306" class="dg-coord" text-anchor="middle">e</text><text x="50" y="143.0" class="dg-coord" text-anchor="middle">5</text><text x="247.0" y="306" class="dg-coord" text-anchor="middle">f</text><text x="50" y="109.0" class="dg-coord" text-anchor="middle">6</text><text x="281.0" y="306" class="dg-coord" text-anchor="middle">g</text><text x="50" y="75.0" class="dg-coord" text-anchor="middle">7</text><text x="315.0" y="306" class="dg-coord" text-anchor="middle">h</text><text x="50" y="41.0" class="dg-coord" text-anchor="middle">8</text><text x="213.0" y="150.0" class="dg-pw" text-anchor="middle">♚︎</text><text x="213.0" y="184.0" class="dg-pw" text-anchor="middle">♟︎</text><text x="213.0" y="82.0" class="dg-pb" text-anchor="middle">♚︎</text><text x="380" y="100" class="dg-tl" text-anchor="start">Les rois sont face à face :</text><text x="380" y="122" class="dg-tl" text-anchor="start">le camp au trait doit céder.</text><text x="380" y="160" class="dg-s" text-anchor="start">Cases critiques du pion e4 :</text><text x="380" y="178" class="dg-s" text-anchor="start">d6, e6, f6. Si le roi blanc</text><text x="380" y="196" class="dg-s" text-anchor="start">en atteint une, c&#x27;est gagné.</text><text x="380" y="230" class="dg-ct" text-anchor="start">Noirs au trait : gain blanc.</text><text x="380" y="250" class="dg-s" text-anchor="start">Blancs au trait : nulle.</text></svg><figcaption>Celui qui n&#x27;a pas le trait « a l&#x27;opposition ». Ici, les Noirs au trait doivent s&#x27;écarter et le roi blanc entre en d6 ou f6.</figcaption></figure>
<!-- /schema:opposition -->

## Roi et pion contre roi

| Situation | Résultat |
| --- | --- |
| roi attaquant sur une **case critique** | gain |
| roi attaquant en **6ᵉ rangée devant son pion** (hors pion de tour) | gain, quel que soit le trait |
| roi défenseur **devant le pion** avec l'opposition | nulle |
| **pion de tour**, roi défenseur dans le coin | nulle |

Les **cases critiques** d'un pion en e4 sont d6, e6, f6 ; d'un pion en e5 : d6, e6, f6 et d7, e7, f7. Le défenseur, lui, cherche à garder l'opposition **devant** le pion, et à reculer **droit devant** le pion (pas sur le côté) quand il est repoussé.

## Les finales à plusieurs pions

- **Pion passé éloigné** : il attire le roi adverse loin du reste ; le roi attaquant mange alors les pions de l'autre aile.
- **Pion passé protégé** : le roi adverse ne peut jamais le prendre ; il est souvent décisif.
- **Majorité saine** : créer un pion passé en poussant d'abord le pion sans vis-à-vis.
- **Percée** : trois pions contre trois face à face (a5, b5, c5 contre a7, b7, c7) : b6 ! crée un pion passé par sacrifice.

## Le zugzwang et la triangulation

Dans de nombreuses finales de pions, la position est un **zugzwang mutuel** : celui qui est au trait perd. La **triangulation** permet de « passer son tour » : le roi fait trois coups sur un triangle de cases et revient au point de départ, tandis que le roi adverse, plus à l'étroit, ne peut pas en faire autant. Les **coups de pions de réserve** (un pion qui peut encore avancer d'une case sans rien changer) jouent le même rôle : les garder pour le bon moment.

## Avant d'entrer en finale de pions

1. Compter les **temps** : qui arrive le premier sur les pions adverses ?
2. Repérer les **pions passés** potentiels.
3. Vérifier la position des **rois** (centralisation, opposition).
4. Compter les **coups de réserve**.

Une finale de pions perdue ne se sauve pas : calculer avant d'échanger.

> **À retenir.** Centralise ton roi. Règle du carré pour un pion passé seul. L'opposition : celui qui n'est pas au trait la possède. Le roi attaquant doit atteindre une case critique (deux rangées devant un pion en 4ᵉ) ; le défenseur se place devant le pion. Pion de tour et roi dans le coin : nulle. Le pion passé éloigné et la triangulation gagnent de nombreuses finales.
