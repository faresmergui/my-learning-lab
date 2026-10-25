---
title: 'Le déroulé d''un duel : tour, zones et types de cartes'
chapter: 1
order: 1
duration: 10
level: Bases
tags:
- règles
- phases
- zones
cards:
- q: Quelles sont les phases d'un tour ?
  a: '**Draw** (pioche), **Standby**, **Main Phase 1**, **Battle Phase**, **Main Phase 2**, **End Phase**. La Battle Phase et la Main Phase 2 sont facultatives.'
- q: Le joueur qui commence pioche-t-il ?
  a: Non. Le premier joueur ne pioche pas à son premier tour et ne peut pas attaquer. Chaque joueur commence avec 5 cartes et 8000 points de vie.
- q: Combien de zones de monstres sur le terrain ?
  a: '5 **zones Monstre principales** par joueur, plus 2 **zones Monstre Extra** partagées au centre : chaque joueur ne peut en occuper qu''une, sauf via des monstres Lien.'
- q: Quel type de magie peut-on activer pendant le tour adverse ?
  a: 'Une seule : la **magie jeu-rapide** (Quick-Play), et seulement si elle a été posée face cachée avant. Les autres magies s''activent pendant sa propre Main Phase.'
- q: Quels sont les quatre types d'effets de monstre ?
  a: '**Ignition** (activé à sa Main Phase, vitesse 1), **déclenchement** (s''active quand quelque chose arrive), **rapide** (activable à tout moment, vitesse 2) et **continu** (s''applique tant que la carte est face recto, sans s''activer).'
- q: Qu'est-ce que l'Extra Deck ?
  a: 'Une pile à part, de 0 à 15 cartes, pour les monstres Fusion, Synchro, Xyz et Lien. Ils ne passent jamais par la main : on les invoque depuis l''Extra Deck en remplissant leurs conditions.'
- q: Une carte posée face cachée peut-elle être activée le tour même ?
  a: 'Un **piège** non : il faut attendre au moins le tour suivant (sauf effet contraire). Une magie **jeu-rapide** posée non plus pendant ce tour. Une magie normale posée peut s''activer à sa Main Phase, même le tour où elle a été posée.'
quiz:
- q: Tu commences le duel. Que peux-tu faire à ton premier tour ?
  options:
  - Piocher puis attaquer
  - Ni piocher ni attaquer, mais invoquer et poser des cartes
  - Piocher mais pas invoquer
  - Attaquer directement
  answer: 1
  explain: Le premier joueur saute sa pioche et sa Battle Phase au premier tour.
- q: L'adversaire attaque. Tu as une magie normale posée face cachée. Peux-tu l'activer ?
  options:
  - Oui
  - Non, une magie normale ne s'active que pendant ta Main Phase
  - Oui, si elle est posée depuis un tour
  - Seulement si tu paies des points de vie
  answer: 1
  explain: Seules les magies jeu-rapide (et les pièges) s'activent pendant le tour adverse.
- q: Tu termines ton tour avec 8 cartes en main. Que se passe-t-il ?
  options:
  - Rien
  - Tu en défausses jusqu'à en avoir 6
  - Tu perds le duel
  - Tu en remets 2 dans le deck
  answer: 1
  explain: En End Phase, la limite de main est de 6 cartes.
---

Avant de parler de combos et de hand traps, il faut avoir les règles de base parfaitement en tête : l'ordre d'un tour, les zones du terrain et ce que chaque type de carte a le droit de faire. Beaucoup d'erreurs en tournoi viennent d'un détail mal compris ici.

## Le duel en bref

- Chaque joueur a **8000 points de vie** (LP) et un deck de **40 à 60 cartes**, plus un **Extra Deck** de 0 à 15 cartes et un **Side Deck** de 0 à 15 cartes pour les matchs en plusieurs manches.
- On pioche **5 cartes** au départ.
- On gagne quand l'adversaire tombe à 0 LP, ne peut plus piocher, ou par un effet de victoire spécial.
- Le **premier joueur** ne pioche pas et ne peut pas attaquer à son premier tour. Ce désavantage apparent est en réalité un énorme avantage dans le jeu moderne (voir le chapitre « Jouer premier, jouer second »).

## Les phases d'un tour

| Phase | Ce qui s'y passe |
| --- | --- |
| **Draw Phase** | on pioche une carte |
| **Standby Phase** | certains effets s'appliquent (coûts d'entretien…) |
| **Main Phase 1** | invoquer, poser, activer magies et effets d'ignition |
| **Battle Phase** | attaquer avec ses monstres en position d'attaque |
| **Main Phase 2** | comme la Main Phase 1, après le combat |
| **End Phase** | fin des effets « jusqu'à la fin du tour », limite de main à 6 cartes |

En pratique, presque tout le jeu moderne se passe en Main Phase 1 : c'est là qu'on enchaîne les invocations d'un combo. Et c'est aussi là que l'adversaire cherchera à l'interrompre.

## Les zones du terrain

<!-- schema:zones -->
<figure class="diagram"><svg viewBox="0 0 680 300" role="img" aria-label="Les zones du terrain" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-a dg-pop" style="--d:0"><rect x="158" y="14" width="74" height="66" rx="9"/></g><text x="195.0" y="44.0" class="dg-s" text-anchor="middle" style="--d:0"><tspan x="195.0" dy="0">Extra</tspan><tspan x="195.0" dy="14">Monstre</tspan></text><g class="dg-box dg-a dg-pop" style="--d:0"><rect x="342" y="14" width="74" height="66" rx="9"/></g><text x="379.0" y="44.0" class="dg-s" text-anchor="middle" style="--d:0"><tspan x="379.0" dy="0">Extra</tspan><tspan x="379.0" dy="14">Monstre</tspan></text><text x="287" y="52" class="dg-s" text-anchor="middle">une par joueur</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="112" y="96" width="74" height="84" rx="9"/></g><text x="149.0" y="135.0" class="dg-t" text-anchor="middle" style="--d:1">M1</text><text x="149.0" y="153.0" class="dg-s" text-anchor="middle" style="--d:1">monstre</text><g class="dg-box dg-pop" style="--d:2"><rect x="112" y="192" width="74" height="84" rx="9"/></g><text x="149.0" y="231.0" class="dg-t" text-anchor="middle" style="--d:2">S1</text><text x="149.0" y="249.0" class="dg-s" text-anchor="middle" style="--d:2">Pendule</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="204" y="96" width="74" height="84" rx="9"/></g><text x="241.0" y="135.0" class="dg-t" text-anchor="middle" style="--d:1">M2</text><text x="241.0" y="153.0" class="dg-s" text-anchor="middle" style="--d:1">monstre</text><g class="dg-box dg-pop" style="--d:2"><rect x="204" y="192" width="74" height="84" rx="9"/></g><text x="241.0" y="231.0" class="dg-t" text-anchor="middle" style="--d:2">S2</text><text x="241.0" y="249.0" class="dg-s" text-anchor="middle" style="--d:2">magie/piège</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="296" y="96" width="74" height="84" rx="9"/></g><text x="333.0" y="135.0" class="dg-t" text-anchor="middle" style="--d:1">M3</text><text x="333.0" y="153.0" class="dg-s" text-anchor="middle" style="--d:1">monstre</text><g class="dg-box dg-pop" style="--d:2"><rect x="296" y="192" width="74" height="84" rx="9"/></g><text x="333.0" y="231.0" class="dg-t" text-anchor="middle" style="--d:2">S3</text><text x="333.0" y="249.0" class="dg-s" text-anchor="middle" style="--d:2">magie/piège</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="388" y="96" width="74" height="84" rx="9"/></g><text x="425.0" y="135.0" class="dg-t" text-anchor="middle" style="--d:1">M4</text><text x="425.0" y="153.0" class="dg-s" text-anchor="middle" style="--d:1">monstre</text><g class="dg-box dg-pop" style="--d:2"><rect x="388" y="192" width="74" height="84" rx="9"/></g><text x="425.0" y="231.0" class="dg-t" text-anchor="middle" style="--d:2">S4</text><text x="425.0" y="249.0" class="dg-s" text-anchor="middle" style="--d:2">magie/piège</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="480" y="96" width="74" height="84" rx="9"/></g><text x="517.0" y="135.0" class="dg-t" text-anchor="middle" style="--d:1">M5</text><text x="517.0" y="153.0" class="dg-s" text-anchor="middle" style="--d:1">monstre</text><g class="dg-box dg-pop" style="--d:2"><rect x="480" y="192" width="74" height="84" rx="9"/></g><text x="517.0" y="231.0" class="dg-t" text-anchor="middle" style="--d:2">S5</text><text x="517.0" y="249.0" class="dg-s" text-anchor="middle" style="--d:2">Pendule</text><g class="dg-box dg-pop" style="--d:3"><rect x="20" y="96" width="74" height="84" rx="9"/></g><text x="57.0" y="143.0" class="dg-s" text-anchor="middle" style="--d:3">Terrain</text><g class="dg-box dg-pop" style="--d:3"><rect x="20" y="192" width="74" height="84" rx="9"/></g><text x="57.0" y="231.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="57.0" dy="0">Extra</tspan><tspan x="57.0" dy="14">Deck</tspan></text><g class="dg-box dg-ghost dg-pop" style="--d:3"><rect x="572" y="14" width="74" height="66" rx="9"/></g><text x="609.0" y="52.0" class="dg-s" text-anchor="middle" style="--d:3">Bannies</text><g class="dg-box dg-pop" style="--d:3"><rect x="572" y="96" width="74" height="84" rx="9"/></g><text x="609.0" y="135.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="609.0" dy="0">Cime-</tspan><tspan x="609.0" dy="14">tière</tspan></text><g class="dg-box dg-pop" style="--d:3"><rect x="572" y="192" width="74" height="84" rx="9"/></g><text x="609.0" y="239.0" class="dg-s" text-anchor="middle" style="--d:3">Deck</text></svg><figcaption>Les monstres de l&#x27;Extra Deck vont dans une zone Monstre Extra, ou dans une zone pointée par un monstre Lien.</figcaption></figure>
<!-- /schema:zones -->

- **Zones Monstre principales** (5) : les monstres invoqués depuis la main ou le deck.
- **Zones Monstre Extra** (2, au centre) : chaque joueur ne peut en utiliser qu'une. Les monstres de l'Extra Deck y vont, ou dans une zone principale pointée par un monstre Lien.
- **Zones Magie/Piège** (5) : les deux zones des extrémités servent aussi de **zones Pendule**.
- **Zone Terrain** : une magie de terrain par joueur.
- **Cimetière** (GY) : les cartes détruites, défaussées ou utilisées. Beaucoup de decks s'en servent comme d'une ressource.
- **Bannies** : les cartes retirées du jeu. Plus difficile à récupérer que le cimetière.

## Les types de cartes

**Monstres** : normaux (sans effet) ou à effet. Les monstres de l'Extra Deck (Fusion, Synchro, Xyz, Lien) sont détaillés au chapitre suivant.

**Magies**

| Type | Quand l'activer |
| --- | --- |
| normale | à sa Main Phase, puis elle va au cimetière |
| jeu-rapide (*Quick-Play*) | à tout moment de son tour ; pendant le tour adverse si elle était posée avant |
| continue | reste sur le terrain et s'applique |
| terrain | dans la zone Terrain |
| équipement | s'attache à un monstre |
| rituelle | pour invoquer un monstre Rituel |

**Pièges** : ils doivent être **posés** face cachée et attendre au moins un tour avant d'être activés (sauf effet qui le permet). Normaux, continus, ou **contre-pièges**, les plus rapides du jeu.

## Les effets de monstre

| Type | Fonctionnement | Exemple d'usage |
| --- | --- | --- |
| **Ignition** | tu l'actives pendant ta Main Phase, quand la chaîne est vide | la plupart des pièces de combo |
| **Déclenchement** | s'active quand un événement se produit (« si cette carte est invoquée… ») | rechercher une carte après une invocation |
| **Rapide** | activable à tout moment, même pendant le tour adverse | les hand traps |
| **Continu** | s'applique tant que la carte est face recto, sans activation | « les monstres adverses perdent 500 ATK » |

Retiens surtout la différence entre **ignition** et **rapide** : un effet rapide est ce qui permet d'interagir pendant le tour de l'adversaire.

> **À retenir.** Le premier joueur ne pioche pas et n'attaque pas, mais il construit son terrain sans être dérangé. Seules les magies jeu-rapide, les pièges et les effets rapides de monstre s'utilisent pendant le tour adverse. Tout le reste attend ta propre Main Phase.
