---
title: Construire sa liste Blue-Eyes
chapter: 27
order: 1
duration: 15
level: Archétype
tags:
- Blue-Eyes
- decklist
- ratios
- hand traps
- probabilités
- Extra Deck
cards:
- q: Combien de starters viser dans une liste Blue-Eyes, et pourquoi ?
  a: 'Une **dizaine** (Sage with Eyes of Blue, Maiden of White, Wishes for Eyes of Blue, plus ce qui les cherche). Avec 10 starters sur 40 cartes, tu en as au moins un dans **78 %** des mains de 5 cartes et **85 %** des mains de 6 ; avec 12, **85 %** et **90 %**. La version Primite monte à **16 starters** (avec Dragon Béryl Éthérique Primite et Filon Noble Primite) : **93 %** et **96 %**.'
- q: Combien de Blue-Eyes White Dragon (Dragon Blanc aux Yeux Bleus) jouer ?
  a: 'En général **trois** : Kaibaman the Legend doit en révéler trois, Majesty of the White Dragons en révèle jusqu''à trois, et la plupart des effets les prennent dans le deck. Ils sont des ressources, pas des starters : au-delà de trois, la main devient lourde.'
- q: Comment répartir les 40 cartes d'une liste Blue-Eyes ?
  a: 'Repère courant : **~16-18 cartes de moteur** (Syntoniseurs, Dragons Blancs, soutien qui les mentionne), **~12-15 interruptions** (hand traps et Pièges), **quelques cartes de second** (destruction, retournement), et **40 cartes pile** pour maximiser la probabilité de piocher ses starters.'
- q: Quels hand traps restent intéressants en TCG après le 19 octobre 2026 ?
  a: '**Ash Blossom & Joyous Spring**, **Effect Veiler**, **Infinite Impermanence**, **Ghost Ogre & Snow Rabbit**, **Ghost Belle & Haunted Mansion**, et un seul **Droll & Lock Bird** (limité). Maxx "C" est interdit ; Called by the Grave aussi, donc tes hand traps sont moins faciles à contrer… et ceux de l''adversaire aussi.'
- q: Pourquoi jouer plusieurs Blue-Eyes Spirit Dragon dans l'Extra Deck ?
  a: 'Parce que c''est la **pièce maîtresse** des fins de combo : une Synchro Niv. 9 facile à faire (un Syntoniseur Niv. 1 + un Dragon Blanc), qu''on peut faire **deux fois** dans un même tour, et dont le sacrifice amène une autre Synchro Dragon LUMIÈRE. Beaucoup de listes en jouent **trois**.'
- q: Comment décider d'ajouter un « moteur » extérieur (Bystial, Primite) ?
  a: 'Seulement s''il améliore ce qui te manque : plus de starters, plus d''interruptions ou un meilleur jeu en second, **sans casser** les restrictions du deck (Roar limite l''Extra Deck aux Dragons, Spirit Dragon gêne les invocations multiples). Mesure-le : 100 mains de test avec et sans, et compare le taux de bonnes mains.'
- q: Qu'est-ce qu'une carte « morte » dans une liste Blue-Eyes ?
  a: 'Une carte qui ne fait rien dans la situation la plus fréquente : un second Mausoleum of White (un seul peut être en jeu), un Dragon Blanc de trop, une carte de second dans une main où tu commences. Chaque carte morte baisse ta probabilité de starter et d''interruption.'
quiz:
- q: Tu hésites entre 40 et 44 cartes pour ajouter quatre « cartes sympas ». Avec 10 starters, que devient ta probabilité d'en avoir au moins un en 5 cartes ?
  options:
  - Elle augmente
  - Elle baisse d’environ 78 % à environ 74 %
  - Elle ne change pas
  - Elle passe à 100 %
  answer: 1
  explain: Diluer le deck baisse la probabilité de chaque carte importante. Reste à 40 sauf raison précise.
- q: Ta liste contient 2 Dragons Blancs, et tu as Kaibaman the Legend en main sans aucun Dragon Blanc visible ailleurs. Que se passe-t-il si tu l'invoques ?
  options:
  - Il invoque un Dragon Blanc
  - 'Son effet ne peut pas se résoudre utilement : il faut révéler trois Dragons Blancs, et tu n''en as que deux'
  - Il cherche une carte
  - Il détruit un monstre
  answer: 1
  explain: C'est l'argument principal pour garder trois Dragons Blancs, ou pour mesurer précisément quand Kaibaman est jouable.
- q: Le méta local est plein de decks qui jouent beaucoup depuis le cimetière. Quel hand trap prendre en priorité dans le main deck ?
  options:
  - Ghost Belle & Haunted Mansion
  - Aucun
  - Un troisième Dragon Blanc
  - Mausoleum of White
  answer: 0
  explain: Ghost Belle nie un effet qui part du cimetière ou le manipule ; Blue-Eyes Spirit Dragon complète avec sa négation au cimetière en fin de combo.
- q: Tu veux jouer Bystial Magnamhut. Combien d'exemplaires sont autorisés en TCG au 25 octobre 2026 ?
  options:
  - '3'
  - '2'
  - '1'
  - '0'
  answer: 2
  explain: 'Bystial Magnamhut est limité : un seul exemplaire.'
---

Une bonne liste Blue-Eyes n'est pas la somme des meilleures cartes : c'est un équilibre entre **commencer ses combos** souvent, **interrompre** l'adversaire et **survivre** à ses interruptions. Cette fiche donne une méthode pour construire et ajuster sa liste, puis la liste méta **Blue-Eyes Primite**, **légale en TCG au 25 octobre 2026**, construite d'après les listes récentes de 2025 et 2026 (YGOPRODeck, ygorganization, Dueling Nexus, Game8) et corrigée pour la liste TCG.

> **Les termes de cette fiche.**
> - **Main deck** : les 40 à 60 cartes piochées ; **Extra Deck** : jusqu'à 15 Fusions, Synchros, Xyz et Liens ; **Side deck** : 15 cartes échangeables entre les manches.
> - **Moteur** (engine) : le groupe de cartes qui produit le combo ; **non-engine** : les cartes qui interagissent avec l'adversaire (hand traps, Pièges).
> - **Brique** (brick) : une main sans starter, qui ne fait rien.
> - **Loi hypergéométrique** : la loi qui donne la probabilité de piocher un certain nombre de cartes d'un type sans remise ; elle est détaillée dans la fiche « Probabilités avancées ».

## Comprendre : trois questions pour chaque carte

1. **Est-ce qu'elle lance ou prolonge le combo ?** (starter ou extender)
2. **Est-ce qu'elle gêne l'adversaire ?** (interruption)
3. **Est-ce qu'elle est utile dans la situation la plus fréquente ?** Sinon, c'est une carte « morte » une partie du temps.

Une carte qui ne répond « oui » à aucune des trois n'a rien à faire dans le main deck.

## Les starters et la probabilité

Un starter Blue-Eyes, c'est une carte qui, **seule ou avec une défausse**, lance le jeu : **Sage with Eyes of Blue** (Sage avec des Yeux de Bleu), **Maiden of White** (Demoiselle Blanche, qui pose True Light, qui pose Vœux), **Wishes for Eyes of Blue** (Vœux pour les Yeux de Bleu). Kaibaman the Legend (Kaibaman la Légende) en est un aussi tant que trois Dragons Blancs sont révélables.

| Starters dans 40 cartes | Au moins un en 5 cartes (premier) | Au moins un en 6 cartes (second) |
| --- | --- | --- |
| 9 | 74 % | 81 % |
| 10 | 78 % | 85 % |
| 12 | 85 % | 90 % |
| 16 (Primite) | 93 % | 96 % |

Chaque starter ajouté vaut donc plusieurs points de probabilité. C'est pourquoi les listes jouent **3 Sage, 3 Maiden of White et 3 Vœux pour les Yeux de Bleu**, pourquoi le moteur Primite (3 Beryl, 3 Filon Noble) est devenu la norme, et pourquoi Deep-Eyes White Dragon, the Blue Abyss (un starter de plus) sera très joué dès sa sortie TCG le 12 novembre 2026.

## Le squelette d'une liste

| Bloc | Nombre | Contenu |
| --- | --- | --- |
| Syntoniseurs du moteur | 7 à 9 | 3 Sage with Eyes of Blue, 3 Maiden of White, 1 Kaibaman the Legend, éventuellement Master with Eyes of Blue (Maître avec des Yeux de Bleu) |
| Dragons et monstres « Blue-Eyes » | 4 à 6 | 3 Blue-Eyes White Dragon, Blue-Eyes Jet Dragon (Dragon à Réaction aux Yeux Bleus), Blue-Eyes Chaos MAX Dragon (Dragon du Chaos MAX aux Yeux Bleus) |
| Soutien qui mentionne le Dragon Blanc | 6 à 8 | 3 Vœux pour les Yeux de Bleu, True Light, 1 ou 2 Roar, Ultimate Fusion, Majesty, Mausoleum of White |
| Interruptions | 12 à 15 | hand traps et Pièges |
| Cartes de second | 0 à 3 | selon le méta |

### La liste méta : Blue-Eyes Primite (TCG, 25 octobre 2026)

**Main deck (40)**

| Cartes | Nb | Rôle |
| --- | --- | --- |
| Blue-Eyes White Dragon (Dragon Blanc aux Yeux Bleus) | 3 | ressource : Kaibaman en révèle 3 |
| Sage with Eyes of Blue (Sage avec des Yeux de Bleu) | 3 | starter |
| Maiden of White (Demoiselle Blanche) | 3 | starter, Syntoniseur recyclable |
| Kaibaman the Legend (Kaibaman la Légende) | 1 | extender, recherche au cimetière |
| Primite Dragon Ether Beryl (Dragon Béryl Éthérique Primite) | 3 | starter d'invocation normale |
| Primite Imperial Dragon (Dragon Impérial Primite) | 1 | carte de second |
| Wishes for Eyes of Blue (Vœux pour les Yeux de Bleu) | 3 | starter |
| Primite Lordly Lode (Filon Noble Primite) | 3 | starter, invoque un Dragon Blanc |
| Primite Drillbeam (Rayon de Forage Primite) | 1 | interruption |
| Roar of the Blue-Eyed Dragons (Hurlement des Dragons aux Yeux de Bleu) | 1 | extender |
| Mausoleum of White (Mausolée Blanc) | 1 | invocation normale en plus |
| Ultimate Fusion (Fusion Ultime) | 1 | second, tour adverse |
| True Light (Véritable Lumière) | 1 | pose Vœux |
| Majesty of the White Dragons (Majesté des Dragons Blancs) | 1 | second |
| Ash Blossom & Joyous Spring (Floraison de Cendres et Joyeux Printemps) | 3 | hand trap |
| Effect Veiler (Illusionniste d'Effet) | 2 | hand trap, cherchable par Vœux |
| Infinite Impermanence (Infini Éphémère) | 3 | hand trap |
| Ghost Belle & Haunted Mansion (Beauté Fantôme et Manoir Hanté) | 2 | hand trap |
| Droll & Lock Bird (Hurluberlu et Oiseau de Verrouillage) | 1 | limité |
| Nibiru, the Primal Being (Nibiru, l'Être Primitif) | 1 | contre les combos longs |
| Bystial Magnamhut, Bystial Druiswurm | 1 + 1 | limités ; Dragons, compatibles avec les verrous |
| **Total** | **40** | |

**Extra Deck (15)** : 3 Blue-Eyes Spirit Dragon (Dragon Esprit aux Yeux Bleus), 1 Blue-Eyes Ultimate Spirit Dragon (Dragon Esprit Ultime aux Yeux Bleus), 1 Dragon Master Magia (Magia Maître des Dragons), 1 Blue-Eyes Ultimate Dragon (Dragon Ultime aux Yeux Bleus), 1 Neo Blue-Eyes Ultimate Dragon (Néo Dragon Ultime aux Yeux Bleus), 1 Blue-Eyes Tyrant Dragon (Dragon Tyran aux Yeux Bleus), 2 Spirit with Eyes of Blue (Esprit avec des Yeux de Bleu), 2 Hieratic Seal of the Heavenly Spheres (Sceau Hiératique des Sphères Divines), 1 Crimson Dragon (Dragon Cramoisi), 1 Stardust Sifr Divine Dragon (Sifr Poussière d'Étoile Dragon Divin), 1 Cosmic Blazar Dragon (Dragon Blazar Cosmique).

**Pourquoi ces choix.** Seize starters pour ne presque jamais briquer ; un seul Rayon de Forage, car il se repose depuis le cimetière ; deux Esprit avec des Yeux de Bleu, car Beryl y va dans presque toutes les lignes ; Effect Veiler plutôt qu'un autre hand trap, car Vœux peut le chercher. Le Dragon Impérial est le seul « luxe » : remplace-le par un hand trap si ton méta n'a pas de Dragons ni de LUMIÈRE.

**La version pure** (sans Primite) remplace les 8 cartes Primite par Master with Eyes of Blue (Maître avec des Yeux de Bleu), Neo Kaiser Sea Horse (Néo Kaiser Hippocampe), Blue-Eyes Jet Dragon (Dragon à Réaction aux Yeux Bleus), Blue-Eyes Chaos MAX Dragon (Dragon du Chaos MAX aux Yeux Bleus), un second Roar et trois hand traps. Elle a plus d'interruptions en main et moins de starters : 10 au lieu de 16.

**Attention aux listes en ligne.** Une liste « Blue-Eyes Primite 2026 » trouvée sur Dueling Nexus ou YGOPRODeck contient souvent des cartes **OCG** pas encore sorties en TCG (Deep-Eyes White Dragon, the Blue Abyss arrive le 12 novembre 2026) et des cartes **interdites** depuis (Called by the Grave, Kewl Tune Rotary, Maxx "C"). Vérifie chaque carte dans la liste officielle avant un tournoi.

## Les moteurs extérieurs

Les listes de 2026 ajoutent parfois un petit moteur :

| Moteur | Ce qu'il apporte | Ce qu'il coûte |
| --- | --- | --- |
| **Bystial** (Magnamhut, Druiswurm, limités) | bannit un monstre LUMIÈRE ou TÉNÈBRES d'un cimetière pour s'invoquer ; corps supplémentaire et interaction | des slots, et il bannit parfois tes propres ressources |
| **Primite** (soutien des monstres Normaux) | 6 starters, une interruption sans invocation, une bombe de second ; c'est le moteur de la liste méta (fiche précédente) | 7 à 8 slots, et le verrou de Filon Noble à gérer |

La règle : un moteur n'entre que s'il **améliore le taux de bonnes mains** ou le jeu en second. Teste-le sur 100 mains de départ et compare.

## L'Extra Deck : choisir 15 cartes

1. **Les incontournables** : Blue-Eyes Spirit Dragon (×2 ou ×3), Ultimate Spirit Dragon, Dragon Master Magia et son matériel Blue-Eyes Ultimate Dragon.
2. **Les cibles de Spirit Dragon** : d'autres Synchros Dragon LUMIÈRE (Azure-Eyes Silver Dragon, Crimson Dragon, Stardust Sifr) ; sans elles, son sacrifice ne sert à rien.
3. **Les finisseurs de second** : Neo Blue-Eyes Ultimate Dragon, Blue-Eyes Tyrant Dragon.
4. **Les Liens utiles** : Spirit with Eyes of Blue (cherche Mausoleum of White), Hieratic Seal of the Heavenly Spheres.

Avant de jouer une carte de l'Extra Deck, demande-toi dans **quelle ligne** elle sort. Si tu ne sais pas la nommer, elle prend la place d'une carte utile.

## Le side deck

Il dépend du méta (fiche « Le side deck par matchup »). Pour Blue-Eyes, trois familles reviennent :

- **contre les decks de cimetière** : D.D. Crow (Corbeau D.D.), Ghost Belle supplémentaires ;
- **contre les gros terrains** (quand tu joues second) : Dark Ruler No More, Forbidden Droplet, Evenly Matched (À Forces Égales), Harpie's Feather Duster (Le Plumeau de Dame Harpie) ;
- **contre les decks qui jouent second** (quand tu commences) : des Pièges comme Solemn Strike (Assaut Solennel).

> **À retenir.** Vise au moins une dizaine de starters (3 Sage, 3 Maiden of White, 3 Vœux pour les Yeux de Bleu, Kaibaman), et seize avec le moteur Primite (3 Beryl, 3 Filon Noble) : on passe de 78 % à 93 % des mains de cinq cartes avec un starter. Garde trois Dragons Blancs, joue 40 cartes pile, et choisis tes 12 à 15 interruptions d'après la liste du 19 octobre 2026 (plus de Called by the Grave, Droll limité). Chaque carte de l'Extra Deck doit avoir une ligne où elle sort, et un moteur extérieur n'entre que s'il améliore tes mains de test.
