---
title: 'Théorie des combos : lignes et points d''étranglement'
chapter: 16
order: 1
duration: 16
level: Expert
tags:
- combo
- point d'étranglement
- ressources
- end board
cards:
- q: Qu'est-ce qu'un point d'étranglement (choke point) ?
  a: Un effet de ta ligne dont la négation **arrête tout** ou presque. C'est là que l'adversaire placera sa meilleure interruption, et c'est ce qu'il faut protéger, doubler ou contourner.
- q: Qu'est-ce qu'une ligne ?
  a: Une séquence précise d'actions qui part d'une main donnée et mène à un terrain final (**end board**). Un bon joueur connaît plusieurs lignes par main, et sait laquelle choisir selon ce que l'adversaire peut faire.
- q: Quelles sont les ressources d'un combo ?
  a: L'**invocation Normale**, les **limites d'utilisation** (une par nom souvent), les **places de l'Extra Deck** et leurs copies, les **zones** de monstre, les **matériels** au cimetière, et les **verrous** déjà déclenchés.
- q: Qu'est-ce qu'une ligne résistante ?
  a: Une ligne qui, si un effet est nié, peut **bifurquer** vers une autre ligne avec les ressources restantes, au lieu de s'arrêter.
- q: Comment juger un end board ?
  a: Par le **nombre** d'interruptions, leur **type** (nier, bannir, renvoyer ; ciblé ou non), **quand** elles s'utilisent (tour adverse, à quelle phase), leur **protection**, et ce qui reste si le terrain est cassé (le **suivi**).
- q: Pourquoi noter ses combos par écrit ?
  a: Pour voir chaque **point d'étranglement**, compter les ressources, et préparer à l'avance la réponse à chaque hand trap (« si Ash ici, je passe par… »).
- q: Qu'est-ce qu'un deck qui « grind » ?
  a: 'Un deck qui gagne sur la durée : il récupère ses cartes du cimetière, réutilise ses effets et produit de la valeur à chaque tour, même après avoir été interrompu.'
quiz:
- q: Ta ligne commence par une recherche, puis tout en découle. L'adversaire a montré qu'il joue Ash Blossom (Floraison de Cendres et Joyeux Printemps), et ton deck en contient encore un exemplaire. Que fais-tu de Crossout Designator (Désignateur de la Suppression) en main ?
  options:
  - Je le garde pour plus tard
  - Je l'active avant la recherche, en déclarant Ash Blossom
  - Je l'active après la recherche
  - Je le défausse
  answer: 1
  explain: 'Crossout Designator bannit un Ash de ton deck et nie les effets activés des cartes de ce nom ce tour, y compris celles de l''adversaire : il protège ton point d''étranglement avant qu''il soit touché.'
- q: Deux lignes mènent au même terrain final. La première a un seul point d'étranglement au tout début ; la seconde a deux points moins graves. L'adversaire a 3 cartes en main au tour 1 ; tu joues premier. Laquelle préférer ?
  options:
  - Toujours la plus courte
  - Souvent celle qui, après une interruption, laisse encore un terrain jouable
  - Celle qui utilise le plus de cartes
  - Peu importe
  answer: 1
  explain: 'On choisit la ligne la plus résistante : celle dont la pire interruption laisse encore quelque chose.'
- q: Tu as déjà invoqué 4 monstres ce tour et le cinquième est la pièce maîtresse. L'adversaire n'a encore rien joué, il garde 5 cartes. Que considérer ?
  options:
  - Rien, on continue
  - 'Le risque de Nibiru (*Nibiru, l''Être Primitif*) après la 5e invocation : terminer d''abord ce qui doit l''être, ou garder de quoi répondre'
  - Arrêter le tour
  - Passer en Battle Phase
  answer: 1
  explain: Nibiru s'active quand l'adversaire a invoqué 5 monstres ou plus. On séquence pour que la 5e invocation arrive quand la perte serait la moins grave.
- q: 'Ton terrain final : deux monstres qui nient chacun une fois les effets de monstre, aucune protection. Quelle est sa faiblesse principale ?'
  options:
  - Aucune
  - Une magie de board breaking (Dark Ruler No More, Lightning Storm) ou une hand trap dans le bon ordre le défait
  - Il a trop d'interruptions
  - Les pièges adverses
  answer: 1
  explain: Deux négations du même type, sans protection, se contournent en commençant par ce qu'elles ne peuvent pas nier.
---

Apprendre un combo par cœur, c'est savoir le faire quand personne ne l'interrompt. Ce qui fait progresser, c'est de comprendre **sa structure** : quelles ressources il consomme, où il peut être arrêté, et ce qu'il reste à faire quand il l'est. C'est aussi la clé pour casser les combos adverses.

## Décrire une ligne

Une **ligne** est une suite d'actions qui mène d'une main de départ à un **end board**. La noter permet de la comprendre. Une notation simple :

```text
NS A        → recherche B                 [point 1 : Ash, Droll]
SS B (A)    → envoie C au cimetière       [point 2 : Ghost Belle]
Lien 2 (A+B) → invoque C depuis le cimetière
...
End board : 2 négations + 1 piège posé
```

Pour chaque étape, on note **ce qui peut l'interrompre** et **ce qui reste si c'est le cas**.

## Les ressources d'un combo

Un combo n'est pas infini. Il consomme :

| Ressource | Pourquoi elle compte |
| --- | --- |
| **Invocation Normale** | une seule par tour ; beaucoup de lignes en dépendent |
| **Limites d'utilisation** | une utilisation par nom ; une utilisation niée est perdue |
| **Extra Deck** | 15 places ; chaque monstre utilisé n'est plus disponible pour la suite |
| **Zones** | la zone Monstre Extra et les flèches de Lien limitent ce qu'on pose |
| **Matériels et cimetière** | ce qu'on y met sert de carburant à la suite |
| **Verrous** | une restriction déclenchée ferme certaines bifurcations |

Compter ces ressources dit si une **bifurcation** est possible après une interruption.

## Les points d'étranglement

Un **point d'étranglement** est un effet dont la négation coupe la ligne. Les plus fréquents :

1. **la première recherche** : la nier prive le joueur de sa deuxième pièce ;
2. **l'invocation d'un monstre pivot** (souvent un Lien qui recherche ou qui invoque) ;
3. **l'effet qui remplit le cimetière** dont dépend tout le reste.

Un deck bien construit **double** ses points d'étranglement (deux cartes différentes qui font la même chose) ou les **protège** (Called by the Grave (*Appelé par la Tombe*), Crossout Designator (*Désignateur de la Suppression*)).

## Choisir sa ligne

Avec une main donnée, plusieurs lignes existent souvent. On choisit selon :

- **la résistance** : celle dont la pire interruption laisse encore un terrain jouable ;
- **ce que l'adversaire a montré** : en deuxième manche, ses hand traps sont connues ;
- **le nombre d'invocations** : au-delà de 4, Nibiru (*Nibiru, l'Être Primitif*) devient un risque ; on séquence pour que la 5e invocation arrive au moment le moins grave ;
- **les cartes de recherche** : contre Droll & Lock Bird (*Hurluberlu et Oiseau de Verrouillage*), on fait d'abord la recherche la plus importante, puisque Droll bloque les suivantes.

## Juger un end board

| Critère | Question |
| --- | --- |
| Nombre | combien de fois peut-il interrompre ? |
| Type | nie-t-il, bannit-il, renvoie-t-il ? cible-t-il ? |
| Moment | utilisable pendant le tour adverse ? à quelle phase ? en réponse à quoi ? |
| Couverture | arrête-t-il les magies, les pièges, les effets de monstre, les invocations ? |
| Protection | survit-il à un board breaker ? |
| Suivi | que reste-t-il pour le tour suivant s'il est cassé ? |

Trois négations du même type, sans protection, sont souvent moins solides que deux interruptions de types différents protégées.

## Le grind

Certains decks ne gagnent pas par la taille de leur terrain, mais par la **durée** : ils récupèrent leurs cartes, réutilisent leurs effets et produisent de la valeur à chaque tour. Contre eux, une interruption au tour 1 ne suffit pas ; il faut gérer leur cimetière (Ghost Belle (*Beauté Fantôme et Manoir Hanté*), Bystial, cartes qui bannissent) et compter leurs ressources sur plusieurs tours.

> **À retenir.** Une ligne consomme des ressources : invocation Normale, limites d'utilisation, places d'Extra Deck, zones, cimetière. Ses points d'étranglement sont là où l'adversaire frappera : on les double, on les protège, ou on choisit la ligne qui résiste le mieux. Un end board se juge sur le nombre, le type, le moment, la protection et le suivi de ses interruptions.
