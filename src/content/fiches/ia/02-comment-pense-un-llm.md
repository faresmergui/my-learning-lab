---
title: 'Comment pense un LLM : contexte, température, limites'
chapter: 2
order: 1
duration: 11
tags:
- IA
- LLM
cards:
- q: Qu'est-ce que la fenêtre de contexte ?
  a: 'La quantité de tokens que le modèle peut prendre en compte à la fois : instructions, conversation, fichiers collés et sa propre réponse. Elle va de quelques milliers à plus d''un million de tokens selon les modèles. Au-delà, il faut résumer, découper ou chercher les passages utiles (RAG).'
- q: Un LLM se souvient-il de tes conversations précédentes ?
  a: 'Non, pas de lui-même : le modèle est **sans état**. À chaque requête, l''application lui renvoie tout l''historique utile. Les « mémoires » des assistants sont des notes que l''application stocke et réinjecte dans le contexte.'
- q: Que règle la température ?
  a: 'Le degré de hasard dans le choix du token suivant. Basse (0 à 0,3) : réponses stables et prévisibles, adaptées au code, à l''extraction, au classement. Plus haute : réponses plus variées, utiles pour proposer des idées. Elle ne rend pas le modèle plus « intelligent ».'
- q: Qu'est-ce qu'une hallucination et comment la limiter ?
  a: Une réponse **fausse mais présentée avec assurance** (option inexistante, citation inventée, chiffre faux). On la limite en fournissant les sources dans le contexte, en demandant de citer ou de dire « je ne sais pas », en donnant des outils (recherche, exécution) et en **vérifiant** ce qui compte.
- q: Qu'est-ce que le prompt système ?
  a: Les instructions de fond données au modèle avant la conversation (rôle, règles, format, contexte de l'entreprise). Les applications et les agents s'en servent pour fixer le comportement ; l'utilisateur ne le voit pas forcément.
- q: Pourquoi un modèle peut-il « oublier » une consigne dans un long contexte ?
  a: 'Parce que l''attention se dilue : dans un contexte très long et touffu, les informations au milieu sont moins bien prises en compte. Mieux vaut un contexte **court et pertinent**, les consignes importantes au début ou rappelées à la fin, et des documents bien séparés.'
quiz:
- q: Tu demandes au même modèle, deux fois, de générer un script, et tu obtiens deux versions différentes. Est-ce un bug ?
  options:
  - Oui, il faut le signaler
  - 'Non : la génération est probabiliste ; une température basse et une consigne précise réduisent la variation, sans la supprimer'
  - Oui, le cache est corrompu
  - Non, il apprend entre les deux requêtes
  answer: 1
  explain: Pour un résultat reproductible (pipeline), on fixe une température basse, une consigne précise et on valide la sortie (tests, linter).
- q: Tu colles 3 000 lignes de logs et demandes la cause d'un incident. La réponse est vague. Que changes-tu ?
  options:
  - Coller encore plus de logs
  - Filtrer d'abord (fenêtre de temps, service, niveau ERROR), donner le contexte (ce qui a changé, l'architecture) et poser une question précise
  - Monter la température
  - Changer de langue
  answer: 1
  explain: Un contexte réduit et pertinent donne de bien meilleures réponses qu'un contexte énorme et bruité.
level: intermédiaire
---

Comprendre trois ou quatre mécanismes du fonctionnement d'un LLM suffit pour éviter la plupart des déceptions : pourquoi il « oublie », pourquoi il invente, pourquoi deux réponses diffèrent, pourquoi il ne connaît pas ton cluster. Cette fiche donne ce modèle mental, utile aussi bien pour utiliser un assistant que pour en construire un.

> **Les outils cités dans cette fiche.**
> - **fenêtre de contexte** : la quantité de texte que le modèle voit à la fois.
> - **prompt système** : les instructions de fond qui fixent le comportement du modèle.
> - **température** : le réglage du hasard dans la génération.
> - **RAG** (Retrieval-Augmented Generation) : chercher des documents pertinents et les mettre dans le contexte (voir la fiche dédiée).
> - **API** : l'interface par laquelle un programme envoie des requêtes au modèle.
> - **cluster** : un groupe de machines qui travaillent ensemble comme un seul système.
> - **JSON** : un format texte de données en paires « clé : valeur », lisible par les humains et les programmes.
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…
> - **manifest** : un fichier YAML qui décrit un objet Kubernetes.

## Comprendre : un modèle sans mémoire

<!-- schema:contexte -->
<figure class="diagram"><svg viewBox="0 0 680 290" role="img" aria-label="Un modèle sans mémoire" style="--minw:560px"><defs><marker id="g7-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g7-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g7-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g7-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="420" height="262" rx="12" class="dg-zone dg-zc"/><text x="26" y="32" class="dg-zl" text-anchor="start">requête n°3 envoyée au modèle</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="30" y="44" width="388" height="36" rx="9"/></g><text x="224.0" y="67.0" class="dg-s" text-anchor="middle" style="--d:0">prompt système (rôle, règles)</text><g class="dg-box dg-pop" style="--d:1"><rect x="30" y="88" width="388" height="36" rx="9"/></g><text x="224.0" y="111.0" class="dg-s" text-anchor="middle" style="--d:1">message 1 + réponse 1</text><g class="dg-box dg-pop" style="--d:2"><rect x="30" y="132" width="388" height="36" rx="9"/></g><text x="224.0" y="155.0" class="dg-s" text-anchor="middle" style="--d:2">message 2 + réponse 2</text><g class="dg-box dg-pop" style="--d:3"><rect x="30" y="176" width="388" height="36" rx="9"/></g><text x="224.0" y="199.0" class="dg-s" text-anchor="middle" style="--d:3">fichiers, résultats d&#x27;outils</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="30" y="220" width="388" height="36" rx="9"/></g><text x="224.0" y="243.0" class="dg-s" text-anchor="middle" style="--d:4">message 3</text><g class="dg-box dg-a dg-pop" style="--d:5"><rect x="480" y="80" width="180" height="50" rx="9"/></g><text x="570.0" y="102.0" class="dg-t" text-anchor="middle" style="--d:5">le modèle</text><text x="570.0" y="120.0" class="dg-s" text-anchor="middle" style="--d:5">ne se souvient de rien</text><path d="M434 145 L456 145 L456 105 L478 105" class="dg-l a" marker-end="url(#g7-a)"/><g class="dg-box dg-pop" style="--d:6"><rect x="480" y="190" width="180" height="56" rx="9"/></g><text x="570.0" y="208.0" class="dg-t" text-anchor="middle" style="--d:6">réponse 3</text><text x="570.0" y="226.0" class="dg-s" text-anchor="middle" style="--d:6"><tspan x="570.0" dy="0">comptée aussi</tspan><tspan x="570.0" dy="14">dans la fenêtre</tspan></text><path d="M570 130 L570 188" class="dg-l a" marker-end="url(#g7-a)"/><text x="456" y="32" class="dg-s" text-anchor="start">tout est renvoyé à chaque fois</text></svg><figcaption>Chaque requête renvoie toute la conversation : plus elle est longue, plus elle coûte et plus le modèle se disperse.</figcaption></figure>
<!-- /schema:contexte -->

Le modèle lui-même n'apprend rien de ta conversation : ses poids ne changent pas. Tout ce qu'il « sait » de ta situation est ce qui se trouve **dans le contexte** de la requête en cours. D'où trois conséquences :

- s'il ne voit pas ton fichier `values.yaml`, il le devine ;
- une nouvelle conversation repart de zéro (sauf mémoire gérée par l'application) ;
- plus le contexte est long, plus la requête coûte cher et prend du temps.

## Les réglages de génération

| Réglage | Effet | Pour du DevOps |
| --- | --- | --- |
| température | hasard du choix des tokens | basse pour le code, l'extraction, les classements |
| longueur maximale | coupe la réponse | assez haute pour un fichier complet |
| raisonnement étendu (selon le modèle) | réfléchit avant de répondre | utile pour déboguer, planifier, relire |
| format imposé (JSON, schéma) | sortie structurée | indispensable pour l'automatisation |

## Les hallucinations

Le modèle choisit ce qui est **plausible** au vu de son entraînement. Quand il ne sait pas, le plausible ressemble au vrai : un flag `--force-sync` qui n'existe pas, un champ YAML d'une ancienne version, une référence à une RFC inventée. Les situations les plus risquées :

- les versions récentes ou peu documentées d'un outil ;
- les détails exacts (numéros de port, limites, noms d'options) ;
- les questions sur **ton** système, qu'il ne voit pas.

Les parades, de la plus simple à la plus solide :

1. demander de signaler l'incertitude et de citer la source ;
2. fournir la documentation ou le fichier réel dans le contexte ;
3. donner un outil pour vérifier : `terraform validate`, `kubectl --dry-run=server`, `ansible-lint`, une recherche web ;
4. relire et tester avant d'appliquer, comme pour le code d'un collègue.

## Le contexte : moins mais mieux

Un contexte de 200 000 tokens ne veut pas dire qu'il faut le remplir. Les informations noyées au milieu d'un long texte sont moins bien utilisées. En pratique :

- filtrer les logs avant de les donner (fenêtre de temps, service, niveau) ;
- donner les fichiers concernés, pas tout le dépôt ;
- séparer clairement les éléments (balises, titres : « Voici le manifest », « Voici l'erreur ») ;
- rappeler la consigne importante à la fin d'un long message.

## Le coût et la vitesse

Les API facturent au **token** en entrée et en sortie (la sortie coûte en général plusieurs fois plus cher). La vitesse se mesure en temps jusqu'au premier token et en tokens par seconde. Pour une automatisation qui tourne des milliers de fois par jour (classer des alertes, résumer des tickets), un **petit modèle** rapide est souvent suffisant ; on garde le plus gros pour les tâches difficiles.

> **À retenir.** Le modèle est sans état : il ne connaît que ce qui est dans le contexte de la requête, qu'on lui renvoie en entier à chaque fois. Température basse pour du code et de l'automatisation. Il hallucine sur ce qu'il ne sait pas, surtout les détails précis, les versions récentes et ton infrastructure : fournir les sources, donner des outils de vérification, relire. Un contexte court et pertinent vaut mieux qu'un contexte énorme. Le coût et la vitesse se comptent en tokens.
