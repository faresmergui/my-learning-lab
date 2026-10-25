---
title: Lire une carte comme un juge (PSCT)
chapter: 11
order: 1
duration: 16
level: Expert
tags:
- PSCT
- coût
- ciblage
- rulings
cards:
- q: Que sépare le deux-points (:) dans un texte de carte ?
  a: 'Ce qui est **avant** les deux-points est une **condition** : quand ou pourquoi l''effet peut s''activer. Le reste décrit l''activation et l''effet. Pas de deux-points : pas de condition particulière.'
- q: Que sépare le point-virgule (;) ?
  a: 'Ce qui est **avant** le point-virgule se fait **à l''activation** : payer un coût, choisir une cible. Ce qui est **après** se fait **à la résolution**. Nier l''effet n''annule pas ce qui est avant le point-virgule.'
- q: Pourquoi Called by the Grave (*Appelé par la Tombe*) répond-il si bien à Ash Blossom (Floraison de Cendres et Joyeux Printemps) ?
  a: 'Parce que défausser Ash est un **coût** : Ash est déjà au cimetière quand son effet est sur la chaîne. Called by the Grave cible Ash au cimetière, la bannit et nie ses effets : Ash se résout sans rien faire.'
- q: Différence entre « puis » (then) et « et si vous le faites » (and if you do) ?
  a: 'Les deux exigent que la première action réussisse. Avec **« puis »**, les actions sont **successives** : un « quand » déclenché par la première rate son timing. Avec **« et si vous le faites »**, elles sont **simultanées**.'
- q: Que signifie « aussi » (also) entre deux actions ?
  a: 'Les deux actions sont **indépendantes** : la seconde a lieu même si la première ne peut pas se faire.'
- q: Quand choisit-on la cible d'un effet ?
  a: '**À l''activation**, avant le point-virgule. Si la cible n''est plus là ou plus valide à la résolution, la partie de l''effet qui la concerne ne fait rien.'
- q: Qu'est-ce qu'une condition d'activation qui n'est pas un coût ?
  a: 'Ce qui est avant le deux-points : « si votre adversaire contrôle un monstre », « pendant la Main Phase ». Il faut qu''elle soit vraie pour activer, mais on ne « paie » rien, et elle n''a pas besoin de rester vraie jusqu''à la résolution (sauf si l''effet le redemande).'
quiz:
- q: Ton adversaire active Ash Blossom (Floraison de Cendres et Joyeux Printemps) sur ta recherche. Tu chaînes Called by the Grave (Appelé par la Tombe) sur Ash. Que se passe-t-il pour ta recherche ?
  options:
  - Elle est niée quand même
  - 'Elle se résout normalement : Ash est bannie et ses effets sont niés avant de se résoudre'
  - Les deux cartes sont annulées et la chaîne recommence
  - Ash revient dans la main
  answer: 1
  explain: 'Called by the Grave se résout en premier (dernier maillon) : l''effet d''Ash sur la chaîne est nié, donc ta recherche se résout.'
- q: 'Une carte dit : « Défaussez 1 carte, puis ciblez 1 monstre ; détruisez-le. » L''adversaire nie l''effet. As-tu défaussé ta carte ?'
  options:
  - Non, tout est annulé
  - 'Oui : défausser est un coût, payé à l''activation'
  - Seulement si le monstre est détruit
  - Ça dépend de la carte niée
  answer: 1
  explain: Tout ce qui est avant le point-virgule est payé à l'activation. Nier l'effet n'efface pas le coût.
- q: « Infligez 500 dommages à votre adversaire, et aussi, il ne peut pas activer de pièges ce tour. » L'adversaire annule les dommages. La seconde partie s'applique-t-elle ?
  options:
  - Non, si la première échoue tout échoue
  - 'Oui : « aussi » rend les deux parties indépendantes'
  - Seulement s'il a des pièges posés
  - Seulement au tour suivant
  answer: 1
  explain: '« Aussi » sépare deux actions indépendantes : l''une peut échouer sans empêcher l''autre.'
- q: Un effet cible un monstre adverse. En réponse, l'adversaire le renvoie dans sa main. Que fait ton effet ?
  options:
  - Il frappe un autre monstre
  - Il ne fait rien sur cette cible, qui n'est plus valide
  - Il est nié et ta carte revient
  - Il s'applique dans la main
  answer: 1
  explain: La cible est choisie à l'activation ; si elle a quitté le terrain, l'effet ne la trouve plus.
---

Les rulings de Yu-Gi-Oh! paraissent arbitraires tant qu'on ne lit pas les cartes comme elles sont écrites. Depuis une dizaine d'années, Konami rédige les textes selon une grammaire stricte, le **PSCT** (*Problem-Solving Card Text*). La ponctuation et quelques mots-clés suffisent à répondre à la plupart des questions de timing, de coût et de négation sans chercher de ruling.

## La structure d'un effet

Un effet suit presque toujours le même schéma :

> **condition** : **coût et cible** ; **effet**

| Partie | Ce qu'elle dit | Quand elle compte |
| --- | --- | --- |
| Avant le **:** | la condition d'activation (« si… », « pendant la Main Phase… ») | pour **pouvoir** activer |
| Entre **:** et **;** | ce que tu fais **en activant** : coût, choix de cible | **à l'activation** |
| Après le **;** | ce qui se passe **à la résolution** | quand le maillon se résout |

Un texte sans deux-points n'a pas de condition. Un texte sans point-virgule n'a ni coût ni cible : tout se passe à la résolution.

## Le coût n'est pas l'effet

Tout ce qui est **avant le point-virgule** est fait au moment de l'activation : défausser, bannir, payer des LP, sacrifier, détacher un matériel Xyz. Conséquences directes :

- **Nier l'effet ne rend pas le coût.** La carte défaussée reste au cimetière.
- **Le coût ne peut pas être « répondu ».** L'adversaire voit le coût payé, puis répond à l'activation.
- **Le coût peut créer une opportunité.** Une hand trap qui se défausse elle-même (Ash Blossom (*Floraison de Cendres et Joyeux Printemps*), Ghost Belle (*Beauté Fantôme et Manoir Hanté*), Droll) est déjà au cimetière pendant que son effet attend sur la chaîne. Called by the Grave (*Appelé par la Tombe*) peut alors la cibler, la bannir et nier ses effets : elle se résout sans rien faire.

## Le ciblage

Le mot **« ciblez »** signifie que la cible est choisie à l'activation, avant le point-virgule. Trois conséquences :

1. **L'adversaire sait ce qui est visé** et peut répondre en protégeant, en déplaçant ou en sacrifiant la cible.
2. **Si la cible disparaît ou change**, la partie de l'effet qui la concerne ne fait rien. Un monstre ciblé puis renvoyé en main ne peut plus être détruit.
3. **« Ne peut pas être ciblé »** bloque ces cartes dès l'activation, mais pas les effets qui ne ciblent pas (« détruisez tous les monstres », « l'adversaire choisit »).

À l'inverse, un effet qui dit « choisissez » ou « envoyez » sans « ciblez » choisit **à la résolution** : on ne peut pas répondre en retirant la carte visée, puisqu'elle n'est pas encore désignée.

## Les mots qui relient deux actions

| Mot | Anglais | Ce qu'il signifie |
| --- | --- | --- |
| **et** | and | les deux actions ont lieu en même temps ; si l'une est impossible, on ne peut souvent pas activer |
| **et si vous le faites** | and if you do | la seconde dépend de la réussite de la première ; elles sont **simultanées** |
| **puis** | then | la seconde dépend de la première et vient **après** |
| **aussi** | also | les deux sont **indépendantes** : la seconde a lieu même si la première échoue |

La différence entre « puis » et « et si vous le faites » paraît mince, mais elle décide du **timing** : avec « puis », la première action n'est pas la dernière chose qui s'est passée. Un effet « **quand** … vous pouvez » déclenché par elle **rate son timing** (voir le chapitre suivant). Avec « et si vous le faites », les deux actions sont simultanées et rien n'est raté.

## Condition d'activation et condition de résolution

La condition avant les deux-points doit être vraie **pour activer**. Elle n'a pas besoin de rester vraie jusqu'à la résolution, sauf si l'effet la répète ou en dépend (par exemple « si ce monstre est toujours face recto »). C'est pourquoi répondre à une carte en rendant sa condition fausse ne suffit pas toujours à l'arrêter : il faut regarder ce que l'**effet** demande à la résolution.

## Une méthode pour lire une carte inconnue

1. **Repérer les deux-points** : qu'est-ce qui permet l'activation ?
2. **Repérer le point-virgule** : qu'est-ce que je paie et qu'est-ce que je cible maintenant ?
3. **Lire l'effet** et ses mots de liaison (et, puis, aussi).
4. **Chercher la limite** d'utilisation (une fois par tour, une seule activation, nom de carte), détaillée plus loin dans ce module.
5. **Se demander quelle zone** l'effet attend : main, terrain, cimetière. Un effet qui s'active au cimetière n'est pas arrêté par une carte qui protège le terrain.

> **À retenir.** Avant le « : », la condition ; entre « : » et « ; », ce qui est fait à l'activation (coût, cible) ; après le « ; », ce qui se passe à la résolution. Nier l'effet ne rend pas le coût. « Puis » sépare dans le temps, « et si vous le faites » relie dans le même instant, « aussi » rend indépendant.
