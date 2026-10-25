---
title: La chaîne et les vitesses de sort
chapter: 3
order: 1
duration: 12
level: Bases
tags:
- chaîne
- spell speed
- timing
cards:
- q: Dans quel ordre se résout une chaîne ?
  a: 'À l''envers : le dernier maillon ajouté (le plus haut) se résout en premier, et on redescend jusqu''au maillon 1.'
- q: Quelles sont les trois vitesses de sort ?
  a: '**Vitesse 1** : magies normales, effets d''ignition et de déclenchement (toujours maillon 1). **Vitesse 2** : jeu-rapides, pièges normaux et continus, effets rapides. **Vitesse 3** : contre-pièges.'
- q: Quelle vitesse faut-il pour répondre à un maillon de vitesse 2 ?
  a: Vitesse 2 ou plus. On ne peut répondre à une carte qu'avec une vitesse **égale ou supérieure**. Seule une vitesse 3 répond à une vitesse 3.
- q: Différence entre un coût et un effet ?
  a: Le **coût** se paie au moment de l'activation (souvent avant le « ; » dans le texte) et reste payé même si l'effet est nié. L'**effet** se produit à la résolution.
- q: Différence entre « nier l'activation » et « nier l'effet » ?
  a: 'Nier l''**activation** : l''activation échoue, et la carte est souvent détruite ou envoyée au cimetière. Nier l''**effet** : la carte s''est bien activée et reste en place, seul son effet ne se produit pas. Dans les deux cas, la limite « une fois par tour » est consommée.'
- q: Que veut dire « rater le timing » (missing timing) ?
  a: 'Un effet facultatif rédigé « **quand** … : vous pouvez » ne s''active pas si l''événement déclencheur n''était pas la toute dernière chose arrivée. Les effets rédigés « **si** … : vous pouvez » ne ratent jamais leur timing.'
- q: Qu'est-ce que le SEGOC ?
  a: '*Simultaneous Effects Go On Chain* : quand plusieurs effets de déclenchement surviennent en même temps, on les place en chaîne dans l''ordre : obligatoires du joueur du tour, obligatoires de l''adversaire, facultatifs du joueur du tour, facultatifs de l''adversaire.'
quiz:
- q: 'Chaîne : maillon 1 l''adversaire active une magie normale, maillon 2 tu réponds avec Infinite Impermanence (Infini Éphémère), maillon 3 il répond avec un jeu-rapide. Lequel se résout en premier ?'
  options:
  - La magie normale
  - Infinite Impermanence
  - Le jeu-rapide du maillon 3
  - Tous en même temps
  answer: 2
  explain: La chaîne se résout du dernier maillon vers le premier.
- q: L'adversaire active un contre-piège (vitesse 3). Que peux-tu activer en réponse ?
  options:
  - Une hand trap à effet rapide
  - Un piège normal
  - Seulement un autre contre-piège
  - Une magie jeu-rapide
  answer: 2
  explain: Seule une vitesse 3 peut répondre à une vitesse 3.
- q: 'Un effet de monstre dit « Si cette carte est envoyée au cimetière : vous pouvez… ». Elle est envoyée en maillon 1 d''une chaîne de 3 maillons. Peut-il s''activer après la chaîne ?'
  options:
  - Non, il a raté son timing
  - Oui, un effet « si » ne rate pas son timing
  - Seulement si c'est ton tour
  - Seulement s'il est obligatoire
  answer: 1
  explain: Les effets « si … vous pouvez » s'activent même si l'événement n'était pas la dernière chose arrivée.
---

La **chaîne** est le mécanisme qui décide de l'ordre dans lequel les effets se produisent quand plusieurs joueurs veulent agir en même temps. C'est la règle la plus importante du jeu moderne : toute interaction (hand traps, négations, réponses) passe par elle.

## Comment se construit une chaîne

1. Un joueur active une carte ou un effet : c'est le **maillon 1**.
2. L'adversaire peut répondre avec un effet assez rapide : **maillon 2**.
3. Puis le premier joueur peut répondre à son tour, et ainsi de suite.
4. Quand plus personne ne veut répondre, la chaîne **se résout à l'envers** : maillon le plus haut d'abord, maillon 1 en dernier.

Exemple : l'adversaire active un effet qui recherche une carte (maillon 1). Tu réponds avec Ash Blossom (*Floraison de Cendres et Joyeux Printemps*), qui nie cet effet (maillon 2). Ash se résout d'abord : l'effet du maillon 1 est nié. Quand le maillon 1 se résout, il ne fait rien.

<!-- schema:chaine -->
<figure class="diagram"><svg viewBox="0 0 680 230" role="img" aria-label="Une chaîne se résout à l&#x27;envers" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="70" y="24" class="dg-zl" text-anchor="middle">on empile</text><path d="M70 190 L70 40" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="130" y="40" width="300" height="60" rx="9"/></g><text x="280.0" y="67.0" class="dg-t" text-anchor="middle" style="--d:1">maillon 2 · toi</text><text x="280.0" y="85.0" class="dg-s" text-anchor="middle" style="--d:1">Ash Blossom : nie l&#x27;effet</text><g class="dg-box dg-pop" style="--d:0"><rect x="130" y="120" width="300" height="60" rx="9"/></g><text x="280.0" y="147.0" class="dg-t" text-anchor="middle" style="--d:0">maillon 1 · adversaire</text><text x="280.0" y="165.0" class="dg-s" text-anchor="middle" style="--d:0">effet qui recherche une carte</text><text x="470" y="24" class="dg-zl" text-anchor="middle">on résout</text><path d="M470 40 L470 190" class="dg-l a" marker-end="url(#g2-a)"/><g class="dg-box dg-a dg-pop" style="--d:2"><rect x="500" y="40" width="166" height="60" rx="9"/></g><text x="583.0" y="60.0" class="dg-t" text-anchor="middle" style="--d:2">1er à se résoudre</text><text x="583.0" y="78.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="583.0" dy="0">l&#x27;effet du maillon 1</tspan><tspan x="583.0" dy="14">est nié</tspan></text><g class="dg-box dg-pop" style="--d:3"><rect x="500" y="120" width="166" height="60" rx="9"/></g><text x="583.0" y="147.0" class="dg-t" text-anchor="middle" style="--d:3">2e à se résoudre</text><text x="583.0" y="165.0" class="dg-s" text-anchor="middle" style="--d:3">ne fait rien</text><text x="340" y="212" class="dg-ct" text-anchor="middle" style="--d:4">le dernier maillon ajouté se résout en premier</text></svg><figcaption>C&#x27;est pour cela qu&#x27;une réponse peut nier un effet activé avant elle.</figcaption></figure>
<!-- /schema:chaine -->

## Les vitesses de sort

| Vitesse | Cartes | Peut répondre à |
| --- | --- | --- |
| **1** | magies normales, de terrain, d'équipement, continues, rituelles ; effets d'ignition ; la plupart des déclenchements | rien : toujours maillon 1 |
| **2** | magies jeu-rapide, pièges normaux et continus, effets rapides de monstre | vitesses 1 et 2 |
| **3** | contre-pièges | toutes les vitesses |

La règle : on ne répond qu'avec une vitesse **égale ou supérieure** au dernier maillon. Les hand traps sont des effets rapides de vitesse 2 : elles répondent à presque tout, sauf aux contre-pièges.

## Coût et effet

Le texte des cartes modernes suit une structure : **condition** `:` **coût** `;` **effet**.

> « Quand votre adversaire active une carte : vous pouvez défausser cette carte ; annulez l'activation. »

- La **défausse** est le coût : elle a lieu à l'activation, et ne revient pas même si l'effet est nié.
- L'**annulation** est l'effet : elle se produit à la résolution, si rien ne l'a empêchée entre-temps.

Cette distinction explique pourquoi certaines cartes évitent les négations en payant leur avantage en coût.

## Nier une activation ou un effet

- **Nier l'activation** : l'activation échoue, et la carte est souvent détruite ou envoyée au cimetière.
- **Nier l'effet** : la carte s'est activée, mais son effet ne fait rien.

Dans les deux cas, la limite « une fois par tour » (*OPT*) est consommée : une carte qui dit « vous ne pouvez utiliser cet effet qu'une fois par tour » a utilisé son tour, même si rien ne s'est produit. Une hand trap qui nie l'effet d'un starter coûte donc au combo son utilisation du tour, pas seulement l'effet.

## « Si » et « quand » : rater le timing

Pour un effet facultatif de déclenchement :

- rédigé « **si** … : vous pouvez » → il s'active toujours après l'événement, même au milieu d'une chaîne ;
- rédigé « **quand** … : vous pouvez » → il ne s'active **que si** l'événement était la toute dernière chose qui s'est produite. Si l'événement survient au maillon 1 d'une chaîne plus longue, il rate son timing.

Les cartes récentes utilisent presque toutes « si ». Le problème reste fréquent avec les cartes anciennes.

## Plusieurs déclenchements en même temps (SEGOC)

Quand plusieurs effets se déclenchent simultanément, on les place dans une même chaîne dans cet ordre :

1. effets **obligatoires** du joueur du tour ;
2. effets **obligatoires** de l'adversaire ;
3. effets **facultatifs** du joueur du tour ;
4. effets **facultatifs** de l'adversaire.

Le joueur choisit l'ordre entre ses propres effets d'une même catégorie. Comme la chaîne se résout à l'envers, les effets facultatifs de l'adversaire se résolvent en premier.

> **À retenir.** La chaîne se résout à l'envers. On répond avec une vitesse égale ou supérieure, et les hand traps sont en vitesse 2. Le coût est payé à l'activation et ne revient pas. Les effets « si » ne ratent jamais leur timing, les effets « quand » oui.
