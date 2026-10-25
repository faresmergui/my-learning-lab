---
title: 'Progresser : entraînement, analyse et compétition'
chapter: 18
order: 1
duration: 15
level: Progresser
tags:
- progression
- Elo
- analyse
- moteur
- gestion du temps
- psychologie
cards:
- q: Comment fonctionne le classement Elo ?
  a: Chaque joueur a un nombre ; après une partie, on gagne ou perd des points selon le résultat **comparé au résultat attendu**. Avec **200 points** d'écart, le plus fort est censé marquer environ **75 %** des points. Battre un joueur mieux classé rapporte beaucoup, perdre contre un moins bien classé coûte cher.
- q: Comment répartir son temps d'entraînement ?
  a: 'Jusqu''à un bon niveau de club : beaucoup de **tactique** (exercices quotidiens), des **finales** de base, des **parties lentes** analysées, et un répertoire **simple**. L''ouverture prend peu de place : les parties se décident rarement là.'
- q: Comment analyser une partie ?
  a: 'D''abord **seul, sans moteur** : noter ses réflexions et les moments critiques, chercher ses erreurs. Puis avec l''**adversaire** si possible. Enfin avec le **moteur**, pour vérifier. On retient **une ou deux leçons** par partie, pas la liste des coups imprécis.'
- q: Comment bien utiliser un moteur ?
  a: Comme **vérificateur**, pas comme oracle. Après son analyse personnelle, regarder où l'évaluation **change brutalement** (les vraies erreurs) et **comprendre pourquoi** le coup du moteur est meilleur. Un +0,3 ou −0,3 n'a pas de signification pratique pour un humain.
- q: Comment gérer son temps à la pendule ?
  a: Jouer **vite** les coups connus et évidents, **investir** le temps aux moments critiques (changement de structure, sacrifice, passage en finale), et garder une **réserve** pour la fin. Le manque de temps (zeitnot) est la cause d'innombrables gaffes.
- q: Qu'est-ce que le « tilt » et comment l'éviter ?
  a: 'Un état de **frustration** après une défaite ou une erreur, qui pousse à jouer vite et mal. Parades : **pause** après deux défaites d''affilée en ligne, pas de parties rapides en série quand on est fatigué, et accepter les erreurs comme une partie du jeu.'
- q: Quels livres classiques pour progresser ?
  a: '**Logical Chess Move by Move** (Chernev) pour comprendre chaque coup, **Mon système** (Nimzowitsch) pour la stratégie, **Reassess Your Chess** (Silman) pour les déséquilibres, la série **Yusupov** pour un programme complet, **Dvoretsky''s Endgame Manual** pour les finales (avancé).'
quiz:
- q: Tu as 1 600 Elo. Ton adversaire a 1 800. Quel score est attendu pour toi sur plusieurs parties ?
  options:
  - 50 %
  - Environ 25 %
  - Environ 75 %
  - 0 %
  answer: 1
  explain: 200 points d'écart donnent environ 75 % au plus fort, donc environ 25 % au moins fort.
- q: Tu viens de perdre une partie longue. Quel est le meilleur ordre d'analyse ?
  options:
  - Moteur directement
  - Seul d'abord, puis avec l'adversaire, puis avec le moteur
  - Ne pas l'analyser
  - Rejouer la même ouverture en blitz
  answer: 1
  explain: L'analyse personnelle d'abord force à comprendre ; le moteur vient vérifier.
- q: Au 20ᵉ coup, la position se transforme (tu peux échanger les dames vers une finale). Il te reste 40 minutes. Que faire ?
  options:
  - Jouer vite
  - 'Prendre du temps : c''est un moment critique où une décision change la nature de la partie'
  - Proposer nulle
  - Jouer le premier coup venu
  answer: 1
  explain: Le temps doit être dépensé aux carrefours, pas sur les coups évidents.
- q: Tu enchaînes trois défaites en blitz en ligne et tu es énervé. Que faire ?
  options:
  - Rejouer immédiatement pour te refaire
  - 'Faire une pause : tu joues en état de tilt'
  - Jouer en cadence plus rapide
  - Changer d'ouverture tout de suite
  answer: 1
  explain: Le tilt fait perdre des points et n'apprend rien.
---

Progresser aux échecs demande plus de **méthode** que d'heures. Les joueurs qui progressent le plus vite combinent exercices ciblés, parties lentes **analysées**, et une bonne gestion du temps et des émotions. Cette fiche donne une méthode d'entraînement et les repères de la compétition.

## Le classement Elo

Le système Elo (Arpad Elo, adopté par la FIDE en 1970) estime la force relative des joueurs.

| Écart de classement | Score attendu du plus fort |
| --- | --- |
| 0 | 50 % |
| 100 | environ 64 % |
| 200 | environ 76 % |
| 400 | environ 91 % |

Repères FIDE : débutant 1 000 à 1 200, joueur de club 1 400 à 1 800, joueur fort 2 000 et plus, maître international 2 400, grand maître 2 500. Les classements en ligne (Lichess, Chess.com) utilisent d'autres systèmes (Glicko) et ne sont **pas directement comparables** aux classements FIDE ou fédéraux.

## Que travailler, selon son niveau

| Niveau | Priorités |
| --- | --- |
| **Jusqu'à 1 400** | tactique de base, mats élémentaires, ne pas laisser de pièce en prise, principes d'ouverture |
| **1 400 à 1 800** | tactique plus profonde, calcul, finales de pions et de tours, plans de milieu de partie |
| **1 800 et plus** | stratégie fine, répertoire approfondi, finales techniques, préparation |

Une semaine type pour un joueur de club : exercices tactiques **chaque jour** (15 à 30 minutes), une ou deux **parties lentes** (30 minutes et plus par joueur) analysées, une séance de **finales**, et un peu d'ouverture.

## Analyser ses parties

1. **Juste après la partie**, noter les moments où l'on a hésité et ce qu'on pensait.
2. **Seul, sans moteur** : chercher les erreurs, les plans manqués, les moments critiques.
3. Avec l'**adversaire** (l'analyse d'après-partie, tradition en tournoi) : il a vu d'autres choses.
4. Avec le **moteur** : repérer les **grosses variations d'évaluation** et comprendre pourquoi.
5. **Retenir une ou deux leçons** et les noter (« je n'ai pas regardé ses échecs après mon coup »).

Les parties **perdues** apprennent le plus. Repérer les erreurs **récurrentes** (gaffes en zeitnot, finales mal jouées, ouverture mal comprise) dit quoi travailler ensuite.

## Bien utiliser le moteur

- un moteur (Stockfish, Leela) joue bien mieux que n'importe quel humain : ses coups ne sont pas toujours **humainement** compréhensibles ;
- les petites différences (±0,3) n'ont pas de sens pratique ; seules comptent les **chutes** d'évaluation ;
- demander « pourquoi ce coup ? » et jouer la suite contre le moteur pour comprendre ;
- ne jamais l'utiliser **pendant** une partie : c'est de la triche, détectée et sanctionnée.

## La gestion du temps

| Moment | Temps |
| --- | --- |
| ouverture connue | rapide |
| coups évidents (reprises forcées) | rapide |
| **moments critiques** (structure qui change, sacrifice, passage en finale) | investir |
| fin de partie | garder une réserve |

Le **zeitnot** (manque de temps) provoque une large part des gaffes. Avec un incrément, garder au moins quelques minutes pour les phases techniques.

## La psychologie

- **Tilt** : après une défaite rageante, faire une pause plutôt que d'enchaîner ;
- **Peur du classement** : jouer le coup, pas le classement de l'adversaire ;
- **Position gagnante** : rester concentré, la partie n'est pas finie ; vérifier encore plus les tactiques adverses ;
- **Position perdante** : se battre, poser des problèmes, chercher une forteresse.

## Les ressources

- **Lichess** (gratuit) : exercices, études, explorateur d'ouvertures, analyse ;
- **Chess.com** : leçons, exercices, parties ;
- **Livres** : *Logical Chess Move by Move* (Chernev), *Mon système* (Nimzowitsch), *Reassess Your Chess* (Silman), la série Yusupov, *Dvoretsky's Endgame Manual* ;
- **Club** : parties longues, analyse avec des joueurs plus forts, compétitions par équipes (interclubs FFE).

> **À retenir.** Elo : 200 points d'écart donnent environ 75 % au plus fort. Entraîne-toi surtout en tactique, en finales et en parties lentes analysées. Analyse seul, puis avec l'adversaire, puis avec le moteur, et retiens une ou deux leçons. Dépense ton temps aux moments critiques. Fais une pause en cas de tilt.
