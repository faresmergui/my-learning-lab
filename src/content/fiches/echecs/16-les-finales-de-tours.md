---
title: 'Les finales de tours : Lucena, Philidor et principes'
chapter: 16
order: 1
duration: 18
level: Finales
tags:
- finale de tours
- Lucena
- Philidor
- tour active
- roi coupé
cards:
- q: Pourquoi étudier les finales de tours en priorité ?
  a: Ce sont les finales **les plus fréquentes** en partie (environ la moitié des finales). Deux positions théoriques, **Lucena** (gain) et **Philidor** (nulle), servent de repères à presque toutes les autres.
- q: Qu'est-ce que la position de Lucena ?
  a: 'Tour et pion contre tour : le pion est en **7ᵉ rangée**, le roi attaquant **devant lui** sur la case de promotion, le roi défenseur **coupé** d''au moins une colonne. Le gain passe par **« construire un pont »** : la tour attaquante va en **4ᵉ rangée** pour bloquer les échecs latéraux.'
- q: Qu'est-ce que la position de Philidor ?
  a: 'Tour et pion contre tour, **roi défenseur devant le pion**. La tour défensive reste sur la **3ᵉ rangée** (de son côté ; la 6ᵉ vue de l''attaquant) pour empêcher le roi adverse d''avancer. Quand le pion avance sur cette rangée, la tour passe **en 1ʳᵉ rangée** et donne des **échecs par derrière** : nulle.'
- q: Pourquoi la tour doit-elle être active ?
  a: Une tour **passive** (qui défend un pion depuis une case inutile) perd souvent la finale ; une tour **active** (qui attaque des pions ou coupe le roi adverse) la sauve. Il vaut souvent mieux sacrifier un pion que de rendre sa tour passive.
- q: Qu'est-ce que couper le roi ?
  a: 'Placer la tour sur une **colonne** (ou rangée) qui empêche le roi adverse de rejoindre le pion. Un roi coupé de **plusieurs colonnes** du côté long du pion ne peut plus défendre : c''est souvent la clé du gain.'
- q: Où placer la tour face à un pion passé ?
  a: '**Derrière** lui (règle de Tarrasch). Derrière son propre pion, elle soutient sa marche ; derrière le pion adverse, elle le freine et devient plus active à mesure qu''il avance. Devant le pion, elle devient passive.'
- q: Qu'est-ce que le côté long et le côté court ?
  a: Par rapport au pion, le **côté long** est le côté où il y a le plus de colonnes. La tour défensive doit donner ses échecs latéraux **depuis le côté long**, assez loin pour que le roi adverse ne puisse pas s'approcher de la tour.
quiz:
- q: Pion blanc en e7, roi blanc en e8, tour blanche en f1, roi noir en g7 (coupé), tour noire en d2. Quel est le plan de gain ?
  options:
  - Pousser tout de suite
  - 'Construire un pont : Tg1+ puis la tour en 4ᵉ rangée pour bloquer les échecs de la tour noire'
  - Échanger les tours
  - Attendre
  answer: 1
  explain: 'C''est la position de Lucena : sortir le roi de devant le pion, puis interposer la tour sur la 4ᵉ rangée.'
- q: Tu défends tour contre tour et pion. Ton roi est devant le pion (pion blanc en e5, ton roi en e8). Où mettre ta tour ?
  options:
  - Derrière ton roi
  - Sur la 6ᵉ rangée, pour empêcher le roi blanc d'y arriver
  - Sur la 8ᵉ rangée
  - Devant le pion en e6
  answer: 1
  explain: Défense de Philidor. Quand le pion vient en e6, ta tour passe en 1ʳᵉ rangée et donne des échecs par derrière.
- q: Ton adversaire a un pion passé en a5. Ta tour peut se mettre en a8 (devant le pion) ou en a1 (derrière). Lequel ?
  options:
  - a8, devant
  - a1, derrière, selon la règle de Tarrasch
  - Indifférent
  - Ni l'un ni l'autre
  answer: 1
  explain: Derrière le pion, la tour reste active ; devant, elle est enchaînée à la défense.
- q: Tu as un pion de moins en finale de tours. Tu peux défendre passivement ou activer ta tour en attaquant les pions adverses. Que choisir ?
  options:
  - Défendre passivement
  - 'Activer ta tour, même au prix d''un pion : l''activité est souvent décisive'
  - Échanger les tours
  - Abandonner
  answer: 1
  explain: 'Le principe numéro un des finales de tours : l''activité de la tour.'
---

La **moitié** des finales jouées sont des finales de tours. Elles semblent simples, mais réputées techniques : un même pion de plus peut gagner ou faire nulle selon l'activité des pièces. Deux positions de référence suffisent à comprendre la plupart d'entre elles.

## Les principes

1. **Activité de la tour** avant tout : attaquer les pions, couper le roi, donner des échecs.
2. **Tour derrière les pions passés** (les siens comme ceux de l'adversaire).
3. **Roi actif** : centralisé, proche des pions.
4. **Couper le roi adverse** de son pion ou des pions passés.
5. **Échanger des pions** quand on défend : moins il y a de pions, plus la nulle est probable.

## La position de Lucena (gain)

Tour et pion contre tour. Exemple : pion blanc en e7, roi blanc en e8, roi noir coupé en g7, tour noire qui donne des échecs sur la colonne d ou la 1ʳᵉ rangée.

Le problème : le roi blanc ne peut pas sortir de devant son pion sans subir des échecs à répétition.

La solution, **construire un pont** :

1. la tour blanche **coupe** d'abord le roi noir (Tg1+, le roi noir recule) ;
2. la tour blanche va en **4ᵉ rangée** (Tg4) ;
3. le roi blanc sort de e8 du côté opposé à la tour noire (Rf7), puis descend vers sa tour (Re6, Rf6, Re5) ;
4. quand la tour noire donne des échecs, le roi blanc **revient vers la tour**, qui s'interpose en e4 ou d4 : les échecs s'arrêtent, le pion va à dame.

<!-- schema:lucena -->
<figure class="diagram"><svg viewBox="0 0 680 320" role="img" aria-label="La position de Lucena" style="--minw:560px"><defs><marker id="g4-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g4-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g4-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g4-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="60" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="156" width="34" height="34" rx="0" class="dg-sqh"/><rect x="196" y="156" width="34" height="34" rx="0" class="dg-sqh"/><rect x="60" y="20" width="272" height="272" rx="0" class="dg-board"/><text x="77.0" y="306" class="dg-coord" text-anchor="middle">a</text><text x="50" y="279.0" class="dg-coord" text-anchor="middle">1</text><text x="111.0" y="306" class="dg-coord" text-anchor="middle">b</text><text x="50" y="245.0" class="dg-coord" text-anchor="middle">2</text><text x="145.0" y="306" class="dg-coord" text-anchor="middle">c</text><text x="50" y="211.0" class="dg-coord" text-anchor="middle">3</text><text x="179.0" y="306" class="dg-coord" text-anchor="middle">d</text><text x="50" y="177.0" class="dg-coord" text-anchor="middle">4</text><text x="213.0" y="306" class="dg-coord" text-anchor="middle">e</text><text x="50" y="143.0" class="dg-coord" text-anchor="middle">5</text><text x="247.0" y="306" class="dg-coord" text-anchor="middle">f</text><text x="50" y="109.0" class="dg-coord" text-anchor="middle">6</text><text x="281.0" y="306" class="dg-coord" text-anchor="middle">g</text><text x="50" y="75.0" class="dg-coord" text-anchor="middle">7</text><text x="315.0" y="306" class="dg-coord" text-anchor="middle">h</text><text x="50" y="41.0" class="dg-coord" text-anchor="middle">8</text><text x="213.0" y="48.0" class="dg-pw" text-anchor="middle">♚︎</text><text x="213.0" y="82.0" class="dg-pw" text-anchor="middle">♟︎</text><text x="247.0" y="286.0" class="dg-pw" text-anchor="middle">♜︎</text><text x="281.0" y="82.0" class="dg-pb" text-anchor="middle">♚︎</text><text x="179.0" y="252.0" class="dg-pb" text-anchor="middle">♜︎</text><path d="M247.0 275.0 L281.0 275.0 L281.0 173.0" class="dg-l a" marker-end="url(#g4-a)"/><text x="380" y="90" class="dg-tl" text-anchor="start">1. Tg1+ coupe le roi noir</text><text x="380" y="112" class="dg-tl" text-anchor="start">2. Tg4 ! prépare le pont</text><text x="380" y="150" class="dg-s" text-anchor="start">Le roi blanc sort par f7,</text><text x="380" y="168" class="dg-s" text-anchor="start">descend vers sa tour, et la tour</text><text x="380" y="186" class="dg-s" text-anchor="start">s&#x27;interpose en e4 contre les échecs.</text></svg><figcaption>Pion en 7ᵉ, roi devant lui, roi adverse coupé : la tour en 4ᵉ rangée servira d&#x27;abri contre les échecs latéraux.</figcaption></figure>
<!-- /schema:lucena -->

## La position de Philidor (nulle)

Le défenseur a son **roi devant le pion**.

1. la tour défensive se place sur la **3ᵉ rangée** de son camp (la 6ᵉ vue des Blancs) : le roi blanc ne peut pas y avancer sans l'aide du pion ;
2. quand le pion avance sur cette rangée (e5-e6), il ne protège plus son roi : la tour défensive passe en **1ʳᵉ rangée** de l'adversaire ;
3. elle donne des **échecs par derrière** : le roi blanc ne trouve aucun abri, nulle.

Erreur classique : laisser sa tour en 8ᵉ rangée passivement, ce qui permet au roi blanc d'avancer en 6ᵉ et de gagner.

<!-- schema:philidor -->
<figure class="diagram"><svg viewBox="0 0 680 320" role="img" aria-label="La position de Philidor" style="--minw:560px"><defs><marker id="g5-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g5-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g5-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g5-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="60" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="60" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="94" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="94" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="128" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="128" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="162" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="162" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="196" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="196" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="230" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="230" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="258" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="224" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="190" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="156" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="122" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="88" width="34" height="34" rx="0" class="dg-sql"/><rect x="264" y="54" width="34" height="34" rx="0" class="dg-sqd"/><rect x="264" y="20" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="258" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="224" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="190" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="156" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="122" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="88" width="34" height="34" rx="0" class="dg-sqd"/><rect x="298" y="54" width="34" height="34" rx="0" class="dg-sql"/><rect x="298" y="20" width="34" height="34" rx="0" class="dg-sqd"/><rect x="60" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="94" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="128" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="162" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="196" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="230" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="264" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="298" y="88" width="34" height="34" rx="0" class="dg-sqh"/><rect x="60" y="20" width="272" height="272" rx="0" class="dg-board"/><text x="77.0" y="306" class="dg-coord" text-anchor="middle">a</text><text x="50" y="279.0" class="dg-coord" text-anchor="middle">1</text><text x="111.0" y="306" class="dg-coord" text-anchor="middle">b</text><text x="50" y="245.0" class="dg-coord" text-anchor="middle">2</text><text x="145.0" y="306" class="dg-coord" text-anchor="middle">c</text><text x="50" y="211.0" class="dg-coord" text-anchor="middle">3</text><text x="179.0" y="306" class="dg-coord" text-anchor="middle">d</text><text x="50" y="177.0" class="dg-coord" text-anchor="middle">4</text><text x="213.0" y="306" class="dg-coord" text-anchor="middle">e</text><text x="50" y="143.0" class="dg-coord" text-anchor="middle">5</text><text x="247.0" y="306" class="dg-coord" text-anchor="middle">f</text><text x="50" y="109.0" class="dg-coord" text-anchor="middle">6</text><text x="281.0" y="306" class="dg-coord" text-anchor="middle">g</text><text x="50" y="75.0" class="dg-coord" text-anchor="middle">7</text><text x="315.0" y="306" class="dg-coord" text-anchor="middle">h</text><text x="50" y="41.0" class="dg-coord" text-anchor="middle">8</text><text x="179.0" y="150.0" class="dg-pw" text-anchor="middle">♚︎</text><text x="213.0" y="150.0" class="dg-pw" text-anchor="middle">♟︎</text><text x="77.0" y="82.0" class="dg-pw" text-anchor="middle">♜︎</text><text x="213.0" y="48.0" class="dg-pb" text-anchor="middle">♚︎</text><text x="111.0" y="116.0" class="dg-pb" text-anchor="middle">♜︎</text><text x="380" y="90" class="dg-tl" text-anchor="start">La tour noire tient la 6ᵉ rangée :</text><text x="380" y="112" class="dg-tl" text-anchor="start">le roi blanc ne peut pas avancer.</text><text x="380" y="150" class="dg-s" text-anchor="start">Si e6, la tour passe en b1</text><text x="380" y="168" class="dg-s" text-anchor="start">et donne des échecs par derrière :</text><text x="380" y="186" class="dg-s" text-anchor="start">le roi blanc n&#x27;a plus d&#x27;abri.</text><text x="380" y="220" class="dg-ct" text-anchor="start">Nulle.</text></svg><figcaption>Le roi défenseur devant le pion et la tour sur la 6ᵉ rangée : c&#x27;est la défense de référence des finales de tours.</figcaption></figure>
<!-- /schema:philidor -->

## Couper le roi

Un roi défenseur coupé de **deux colonnes ou plus** du pion, du côté long, ne peut plus revenir à temps : la finale est souvent gagnée. Les défenseurs doivent donc, dès que possible, ramener leur roi **devant** le pion.

## Les échecs latéraux et le côté long

Quand le roi défenseur est coupé, sa tour donne des échecs **sur le côté**. Il faut les donner du **côté long** (le côté du pion où il y a le plus de colonnes) et à au moins **trois colonnes** du pion : sinon le roi attaquant s'approche de la tour et les échecs s'arrêtent.

## Tour et pion de tour

Avec un **pion de tour** (a ou h), le défenseur a de meilleures chances : le roi défenseur devant le pion ou près du coin fait nulle facilement ; même avec le roi coupé, la **position de Vancura** (tour défensive sur le flanc du pion, en attaquant le pion de côté) tient contre un pion a en 6ᵉ.

## Les situations fréquentes

| Situation | Évaluation habituelle |
| --- | --- |
| 1 pion de plus, tous les pions sur la même aile (4 contre 3) | souvent nulle avec une bonne défense |
| 1 pion de plus, pions sur les deux ailes | bonnes chances de gain |
| tour en 7ᵉ rangée attaquant des pions | gros avantage |
| tour passive défendant un pion | souvent perdant |
| roi défenseur devant le pion | souvent nulle (Philidor) |

« Toutes les finales de tours sont nulles » est une exagération, mais elle rappelle que le défenseur a beaucoup de ressources s'il garde sa tour active.

> **À retenir.** Tour active, derrière les pions passés, roi actif. Lucena (pion en 7ᵉ, roi devant, roi adverse coupé) : construire un pont avec la tour en 4ᵉ rangée. Philidor (roi défenseur devant le pion) : tour en 3ᵉ rangée, puis échecs par derrière quand le pion avance. Coupe le roi adverse ; en défense, donne les échecs depuis le côté long.
