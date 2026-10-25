---
title: 'Le calcul : coups candidats et vérification'
chapter: 7
order: 1
duration: 15
level: Tactique
tags:
- calcul
- coups candidats
- coups forcés
- gaffes
- visualisation
cards:
- q: Quels coups examiner en premier ?
  a: 'Les **coups forcés**, dans l''ordre : **échecs**, **prises**, **menaces** (en anglais *checks, captures, threats*). Ils limitent les réponses adverses, donc ils se calculent loin et cachent la plupart des combinaisons. On les regarde pour **soi et pour l''adversaire**.'
- q: Qu'est-ce qu'un coup candidat ?
  a: 'Un coup **sérieux** retenu avant de calculer : en général **2 à 4**. On les liste d''abord, puis on calcule chaque ligne, au lieu de se perdre dans le premier coup venu.'
- q: Qu'est-ce que la méthode de l'arbre (Kotov) ?
  a: Calculer chaque coup candidat **une seule fois** et à fond, sans revenir sans cesse sur les mêmes lignes. Elle structure la réflexion en branches, mais en pratique les forts joueurs l'appliquent avec souplesse.
- q: Qu'est-ce que la vérification anti-gaffe ?
  a: 'Avant de jouer, se demander : **après mon coup, quels sont les échecs, prises et menaces de l''adversaire ?** Ce contrôle de quelques secondes évite la majorité des pièces perdues bêtement.'
- q: Pourquoi chercher la menace adverse ?
  a: Chaque coup adverse change la position. Se demander **« que veut-il ? »** (que menacerait-il s'il jouait encore ?) évite de jouer son plan pendant que l'adversaire prépare un mat ou un gain de pièce.
- q: Qu'est-ce que l'évaluation finale d'une ligne ?
  a: 'À la fin d''une variante calculée, **juger la position obtenue** : matériel, sécurité des rois, activité des pièces. Un calcul sans évaluation est inutile : « je gagne un pion » ne vaut rien si mon roi est perdu.'
- q: Comment améliorer sa visualisation ?
  a: Résoudre des exercices **sans bouger les pièces**, rejouer de tête des parties courtes, jouer des parties à l'aveugle simples, et lire des livres de parties commentées en suivant les variantes mentalement.
quiz:
- q: C'est ton tour. Tu as un plan positionnel en tête. Que vérifies-tu d'abord ?
  options:
  - Rien, tu joues ton plan
  - Les échecs, prises et menaces des deux camps
  - Le temps de la pendule
  - Les ouvertures connues
  answer: 1
  explain: Les coups forcés décident souvent de la partie avant tout plan.
- q: Tu as trouvé un beau sacrifice. Avant de le jouer, que fais-tu ?
  options:
  - Tu le joues vite pour impressionner
  - Tu cherches la meilleure défense, y compris les coups intermédiaires, et tu évalues la position finale
  - Tu regardes une autre partie
  - Tu proposes nulle
  answer: 1
  explain: 'Le défaut le plus courant : calculer seulement les réponses qui nous arrangent.'
- q: Ton adversaire vient de jouer un coup « bizarre » de tour. Quel réflexe ?
  options:
  - L'ignorer
  - 'Se demander ce qu''il menace : quel coup jouerait-il s''il rejouait ?'
  - Répondre tout de suite
  - Échanger la tour
  answer: 1
  explain: Un coup inhabituel prépare souvent une menace qu'on ne voit pas d'emblée.
- q: Tu calcules une ligne de 6 coups qui gagne un pion, mais ton roi y devient exposé à toutes les pièces adverses. Conclusion ?
  options:
  - Gagner le pion
  - 'Évaluer : un pion ne compense pas un roi perdu, chercher un autre coup'
  - Calculer 10 coups de plus
  - Jouer au hasard
  answer: 1
  explain: L'évaluation finale compte autant que le calcul.
---

Le calcul est la capacité de **voir plusieurs coups à l'avance** sans bouger les pièces. Il ne s'agit pas de calculer le plus loin possible, mais de calculer **les bons coups**, **dans le bon ordre**, et de bien **évaluer** la position au bout. La plupart des erreurs d'amateurs ne viennent pas d'un calcul trop court, mais d'un coup adverse oublié.

## Le processus de réflexion

1. **Que veut l'adversaire ?** Quelle menace son dernier coup crée-t-il ?
2. **Coups forcés** : échecs, prises, menaces, pour moi et pour lui.
3. **Coups candidats** : 2 à 4 coups sérieux, forcés ou de plan.
4. **Calcul** de chaque candidat jusqu'à une position calme.
5. **Évaluation** de chaque position finale ; choix du meilleur candidat.
6. **Vérification anti-gaffe** avant de toucher la pièce.

En partie rapide, on raccourcit, mais on garde les étapes 1, 2 et 6.

## Les coups forcés d'abord

Les **échecs**, **prises** et **menaces** limitent les réponses adverses : là où un coup calme laisse 30 réponses, un échec n'en laisse que 2 ou 3. On peut donc calculer loin. Et c'est là que se cachent les combinaisons, dans les deux sens.

Regarder **tous** les échecs, même ceux qui semblent absurdes (un sacrifice de dame avec échec) : c'est ainsi qu'on trouve les coups que l'adversaire n'attend pas.

## Bien calculer

| Erreur | Correction |
| --- | --- |
| Ne calculer que les réponses qui arrangent | chercher la **meilleure défense** à chaque coup |
| Oublier un coup intermédiaire adverse | à chaque prise prévue, regarder ses échecs et menaces |
| S'arrêter au milieu d'une séquence de prises | calculer jusqu'à une position **calme** |
| Revenir dix fois sur la même ligne | calculer chaque candidat une fois, à fond (méthode de l'arbre) |
| Calculer sans évaluer | juger matériel, roi, activité à la fin |
| « Voir » une pièce qui a bougé dans la variante | rejouer la variante lentement, pièce par pièce |

## La méthode de l'arbre

Le grand maître Alexandre Kotov a proposé (*Pensez comme un grand maître*, 1971) de lister tous les candidats, puis de calculer chaque branche **une seule fois**. En pratique, les forts joueurs mêlent calcul et intuition : ils examinent d'abord le coup qui « semble » le meilleur, puis vérifient les alternatives. L'important est de **ne pas se disperser**.

## L'élimination

Quand une ligne est compliquée, on peut raisonner à l'envers : écarter les candidats qui **perdent clairement**, et jouer le dernier qui reste. Utile en zeitnot (manque de temps) et en défense.

## La vérification anti-gaffe

Avant chaque coup : **après mon coup, quels échecs, prises et menaces a mon adversaire ?** Ce contrôle d'une dizaine de secondes supprime la plupart des pièces perdues. Une règle simple : jamais de coup sans avoir regardé les **cases attaquées** par la dernière pièce adverse jouée.

## S'entraîner

- **Exercices de calcul** sans bouger les pièces, de difficulté croissante ;
- **études** d'échecs (positions composées avec une solution unique), excellentes pour la précision ;
- parties **lentes** (longue cadence) pour prendre le temps du processus complet ;
- analyse de ses défaites : chercher **le moment** où l'on a raté un coup forcé.

> **À retenir.** Commence par la menace adverse, puis les échecs, prises et menaces des deux camps. Retiens 2 à 4 candidats, calcule chacun une fois jusqu'à une position calme, en cherchant la meilleure défense, y compris les coups intermédiaires. Évalue la position finale. Avant de jouer, vérifie les échecs, prises et menaces adverses après ton coup.
