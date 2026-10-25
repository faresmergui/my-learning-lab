---
title: La Battle Phase et la Damage Step
chapter: 13
order: 1
duration: 15
level: Expert
tags:
- Battle Phase
- Damage Step
- replay
cards:
- q: Quelles sont les étapes de la Battle Phase ?
  a: '**Start Step**, **Battle Step** (déclaration d''attaque), **Damage Step** (début, avant le calcul des dommages, calcul, après le calcul, fin), puis **End Step**.'
- q: Quelles cartes peut-on activer pendant la Damage Step ?
  a: Les **contre-pièges**, les cartes qui **modifient directement l'ATK ou la DEF** (jusqu'à la fin du calcul des dommages), les cartes qui **nient une activation**, et les effets qui mentionnent explicitement la Damage Step ou le calcul des dommages, ou qui s'y déclenchent.
- q: Pourquoi beaucoup de hand traps ne servent à rien pendant la Damage Step ?
  a: 'Parce qu''elles nient un **effet** sans modifier l''ATK ni nier une activation : elles ne font pas partie des cartes autorisées dans la Damage Step. Il faut les utiliser avant, pendant la Battle Step.'
- q: Qu'est-ce qu'un replay ?
  a: Si le nombre de monstres de l'adversaire change après la déclaration d'attaque (avant la Damage Step), l'attaquant peut **choisir une nouvelle cible**, attaquer directement si le terrain est vide, ou renoncer à attaquer avec ce monstre.
- q: Quand un monstre face verso attaqué est-il retourné ?
  a: Au début de la Damage Step, avant le calcul des dommages. Son effet FLIP s'active **après** le calcul des dommages.
- q: 'ATK contre DEF : qui prend des dommages ?'
  a: Si l'ATK est plus haute, le monstre en défense est détruit **sans dommages**, sauf effet de percée. Si la DEF est plus haute, rien n'est détruit et l'**attaquant** perd la différence.
- q: Quand un monstre détruit au combat va-t-il au cimetière ?
  a: À la **fin de la Damage Step**. Les effets « si ce monstre est envoyé au cimetière » se déclenchent donc à ce moment.
quiz:
- q: L'adversaire attaque avec un monstre de 3000 ATK. Tu veux l'arrêter avec une hand trap qui nie les effets d'un monstre. Quand l'activer ?
  options:
  - Pendant le calcul des dommages
  - Pendant la Battle Step, en réponse à la déclaration d'attaque ou avant la Damage Step
  - À la fin de la Damage Step
  - Elle ne peut jamais servir en Battle Phase
  answer: 1
  explain: Une carte qui nie un effet sans modifier l'ATK ne peut pas être activée pendant la Damage Step. On la joue avant.
- q: L'adversaire déclare une attaque sur ton monstre A. En réponse, tu invoques Spécialement un monstre B. Que peut faire l'attaquant ?
  options:
  - Il doit attaquer A
  - 'Replay : il peut choisir A, B, ou ne pas attaquer avec ce monstre'
  - Il doit attaquer B
  - La Battle Phase se termine
  answer: 1
  explain: 'Le nombre de monstres adverses a changé après la déclaration : c''est un replay.'
- q: Ton monstre de 1800 ATK attaque un monstre en défense de 2000 DEF. Que se passe-t-il ?
  options:
  - Le monstre en défense est détruit
  - Rien n'est détruit et tu perds 200 LP
  - Les deux sont détruits
  - L'adversaire perd 200 LP
  answer: 1
  explain: 'La DEF est plus haute : aucune destruction, et l''attaquant perd la différence.'
- q: Pendant la Damage Step, avant le calcul des dommages, tu veux activer une magie jeu-rapide qui donne +1000 ATK. Est-ce possible ?
  options:
  - Non, aucune magie en Damage Step
  - 'Oui : elle modifie directement l''ATK, c''est autorisé jusqu''à la fin du calcul des dommages'
  - Seulement après le calcul
  - Seulement si c'est un contre-piège
  answer: 1
  explain: Les cartes qui modifient directement l'ATK ou la DEF font partie des exceptions autorisées.
---

La Battle Phase paraît simple : on attaque, on compare les ATK. Pourtant c'est là que se gagnent beaucoup de parties serrées, surtout en jouant second quand on cherche le dernier point de dommages. Ses règles sont plus restrictives que celles de la Main Phase, en particulier pendant la **Damage Step**.

## Les étapes

| Étape | Ce qui s'y passe |
| --- | --- |
| **Start Step** | début de la Battle Phase ; on peut activer des effets rapides |
| **Battle Step** | déclaration d'attaque ; c'est ici que réagissent la plupart des pièges (« quand un monstre adverse déclare une attaque ») |
| **Damage Step** | le combat lui-même, en cinq moments (voir ci-dessous) |
| **End Step** | fin de la Battle Phase, une fois que le joueur ne veut plus attaquer |

Le joueur revient à la Battle Step pour chaque nouvelle attaque.

## La Damage Step en cinq moments

1. **Début de la Damage Step** : un monstre face verso attaqué est retourné face recto.
2. **Avant le calcul des dommages** : dernier moment pour modifier l'ATK ou la DEF en connaissant les deux monstres.
3. **Calcul des dommages** : on compare et on applique les dommages.
4. **Après le calcul des dommages** : les effets FLIP s'activent, ainsi que les effets « si ce monstre inflige des dommages de combat ».
5. **Fin de la Damage Step** : les monstres détruits au combat vont au cimetière, et leurs effets « si envoyé au cimetière » se déclenchent.

## Ce qui est autorisé pendant la Damage Step

Pendant la Damage Step, on ne peut activer que :

- les **contre-pièges** ;
- les cartes qui **modifient directement l'ATK ou la DEF**, jusqu'à la fin du calcul des dommages ;
- les cartes qui **nient une activation** ;
- les effets qui **mentionnent la Damage Step ou le calcul des dommages**, et les effets qui **s'y déclenchent** (destruction au combat, dommages de combat).

Conséquence importante : une hand trap qui nie un **effet** sans toucher à l'ATK (Effect Veiler (*Illusionniste d'Effet*), Infinite Impermanence (*Infini Éphémère*)) se joue **avant** la Damage Step. Le bon moment est en général la déclaration d'attaque, pendant la Battle Step.

## Le calcul des dommages

| Situation | Destruction | Dommages |
| --- | --- | --- |
| ATK > ATK | le plus faible | différence au contrôleur du plus faible |
| ATK = ATK | les deux | aucun |
| ATK > DEF | le monstre en défense | aucun, sauf effet de percée |
| ATK < DEF | aucune | différence à l'**attaquant** |
| ATK = DEF | aucune | aucun |
| attaque directe | aucune | ATK à l'adversaire |

## Le replay

Si le **nombre de monstres** de l'adversaire change entre la déclaration d'attaque et la Damage Step (un monstre est invoqué ou quitte le terrain), il y a **replay** : l'attaquant choisit une nouvelle cible, attaque directement si le terrain est désormais vide, ou renonce à attaquer avec ce monstre (il ne pourra pas attaquer de nouveau ce tour).

Le replay est un outil : invoquer un monstre en réponse à une déclaration d'attaque oblige l'adversaire à refaire son choix, souvent moins bien.

## Calculer le lethal

Pour gagner un tour, il faut compter précisément :

1. **les LP adverses** ;
2. **les attaquants disponibles** et leur ATK, en tenant compte des effets qui les empêchent d'attaquer (beaucoup de monstres d'Extra Deck interdisent d'attaquer le tour de leur invocation, ou l'Extra Deck verrouille certaines invocations) ;
3. **les obstacles** : monstres en défense, pièges posés, hand traps qui gagnent du temps ;
4. **une marge** : prévoir un dommage de plus que nécessaire si une carte adverse peut en annuler un.

Si l'OTK n'est pas certain, il vaut souvent mieux garder des ressources que tout engager et se retrouver sans terrain.

> **À retenir.** Dans la Damage Step, seuls les contre-pièges, les modifications d'ATK/DEF, les négations d'activation et les effets propres à la Damage Step s'activent : les hand traps « qui nient un effet » se jouent avant, à la déclaration d'attaque. Un changement du nombre de monstres adverses provoque un replay.
