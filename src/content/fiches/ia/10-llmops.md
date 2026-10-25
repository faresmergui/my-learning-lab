---
title: 'LLMOps : exploiter des applications IA'
chapter: 10
order: 1
duration: 11
tags:
- IA
- LLMOps
- Observabilité
cards:
- q: Qu'est-ce que le LLMOps ?
  a: 'L''ensemble des pratiques pour mettre en production et exploiter des applications à base de LLM : **passerelle** d''accès aux modèles, **versionnage** des prompts et des modèles, **évaluation** automatique, **observabilité** (traces, coûts, qualité), garde-fous, et maîtrise des coûts. C''est le DevOps appliqué aux applications IA.'
- q: À quoi sert une passerelle LLM (AI gateway) ?
  a: 'À centraliser l''accès aux modèles, internes et externes, derrière une seule API : authentification et quotas par équipe, routage et repli entre fournisseurs, journalisation, masquage de données sensibles, cache et suivi des coûts. Exemples : LiteLLM, Envoy AI Gateway, Kong AI Gateway, les passerelles des clouds.'
- q: Pourquoi faut-il évaluer une application IA comme on teste du code ?
  a: Parce qu'un changement de prompt, de modèle ou de documents peut **dégrader** les réponses sans aucune erreur visible. On garde un **jeu d'évaluation** (questions et réponses attendues ou critères), on le rejoue à chaque changement en CI, avec des vérifications automatiques et parfois un LLM juge, et on compare aux scores précédents.
- q: Que tracer dans une application à base de LLM ?
  a: 'Pour chaque requête : le prompt et la réponse (masqués si sensibles), le modèle et sa version, les tokens en entrée et en sortie, la **latence**, le **coût**, les appels d''outils et les documents récupérés (RAG), les erreurs, et les retours des utilisateurs. OpenTelemetry a des conventions dédiées (GenAI) ; Langfuse et des outils similaires les affichent.'
- q: Comment maîtriser les coûts d'une application IA ?
  a: Choisir le **plus petit modèle suffisant** pour chaque tâche (routage), réduire le contexte (moins de documents, résumés), utiliser le **cache de prompt** des fournisseurs pour les préfixes répétés, limiter la longueur des réponses, mettre des **quotas** par équipe dans la passerelle, et suivre le coût par fonctionnalité.
quiz:
- q: Après un changement de prompt, le bot de support répond moins bien, mais aucune alerte ne s'est déclenchée. Qu'est-ce qui manquait ?
  options:
  - Plus de GPU
  - Une évaluation automatique en CI sur un jeu de questions types, qui aurait détecté la baisse avant la mise en production
  - Une température plus haute
  - Un autre fournisseur
  answer: 1
  explain: 'Les régressions de qualité sont silencieuses : seules des évaluations les révèlent.'
- q: Trois équipes appellent directement le même fournisseur avec leurs propres clés. Quel est le problème ?
  options:
  - Aucun
  - 'Pas de vue sur les coûts, pas de quotas, des clés dispersées, pas de journal commun ni de repli : une passerelle LLM centralise tout cela'
  - Les réponses sont plus lentes
  - Le modèle est surchargé
  answer: 1
  explain: 'La passerelle joue pour les LLM le rôle d''un API gateway : sécurité, quotas, observabilité, routage.'
level: intermédiaire
---

Mettre un assistant en production, ce n'est pas seulement appeler une API. Il faut gérer les accès, les coûts, les versions de prompts et de modèles, mesurer la **qualité** (qui peut baisser sans aucune erreur), et tout observer. Le **LLMOps** reprend les réflexes DevOps (CI, observabilité, déploiement progressif) et les adapte à ces applications.

> **Les outils cités dans cette fiche.**
> - **LLMOps** : le DevOps des applications à base de LLM (proche du **MLOps**, qui couvre l'entraînement et le déploiement de modèles).
> - **passerelle LLM** (AI gateway) : un point d'accès unique aux modèles (LiteLLM, Envoy AI Gateway, Kong AI Gateway…).
> - **LLM juge** : un modèle utilisé pour noter les réponses d'un autre selon des critères.
> - **OpenTelemetry** : le standard de traces, métriques et logs ; **Langfuse** : un outil open source d'observabilité des applications LLM.
> - **cache de prompt** : la réutilisation par le fournisseur d'un début de prompt identique, moins cher et plus rapide.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **MR** : merge request : la demande de fusion d'une branche dans GitLab, avec revue de code (pull request sur GitHub).
> - **rollback** : le retour à la version précédente après un déploiement raté.
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…
> - **latence** : le délai entre une demande et sa réponse.
> - **GPU** : le processeur graphique, qui fait énormément de calculs en parallèle (IA, rendu).

## Comprendre : l'architecture type

```
applications (bot d'astreinte, assistant interne, outil de revue)
        │ API compatible OpenAI
        ▼
passerelle LLM ── auth, quotas par équipe, masquage, cache, journal, coûts
   ├──► fournisseurs externes (Claude, GPT, Gemini…)
   └──► modèles internes (vLLM / KServe sur les GPU de la plateforme)
        │
        ▼
observabilité : traces (prompts, outils, documents), latence, tokens, coût, retours utilisateurs
évaluation    : jeux de tests rejoués en CI à chaque changement
```

## Versionner tout ce qui change le comportement

| Élément | Comment le gérer |
| --- | --- |
| prompts | dans Git, revus en MR, testés par l'évaluation |
| modèle et version | épinglés (pas « le dernier » sans le savoir) |
| documents du RAG | ingestion versionnée, date de mise à jour |
| outils (MCP, fonctions) | versionnés comme une API |
| paramètres | température, longueur, nombre de documents |

Une nouvelle version passe par la même chaîne qu'un déploiement : MR, évaluation en CI, déploiement progressif (une partie du trafic), surveillance, rollback possible.

## Évaluer

- Un **jeu d'évaluation** : 50 à 200 questions réelles représentatives, avec la réponse attendue ou des critères (« cite le bon runbook », « ne propose jamais de commande destructive »).
- Des **vérifications automatiques** : format, présence de la source, mots interdits, exécution du code produit (le YAML passe-t-il `kubeconform` ?).
- Un **LLM juge** pour les critères plus subtils, calibré sur quelques notes humaines.
- Les **retours** des utilisateurs (pouce haut ou bas) pour enrichir le jeu de tests.

## Observer

Les métriques classiques (latence, erreurs, débit) ne suffisent pas. Il faut aussi :

- les **tokens** et le **coût** par requête, par fonctionnalité, par équipe ;
- les **traces** complètes d'un échange : prompt, documents récupérés, appels d'outils, réponse ;
- la **qualité** dans le temps (scores d'évaluation, retours) ;
- les **refus** et les déclenchements de garde-fous.

Attention : les traces contiennent des données potentiellement sensibles. Masquer, limiter la rétention et restreindre l'accès, comme pour des logs applicatifs.

## Maîtriser les coûts

1. **Router** : un petit modèle pour classer, extraire ou résumer, un grand pour raisonner.
2. **Réduire le contexte** : moins de documents mais mieux choisis, résumés des longues conversations.
3. **Cache de prompt** : un prompt système et des documents stables en tête de requête sont facturés moins cher quand ils se répètent.
4. **Traitement par lots** : les API batch des fournisseurs coûtent moins cher pour ce qui n'est pas urgent.
5. **Quotas et alertes** par équipe dans la passerelle.
6. **Interne ou externe** : à fort volume et charge stable, un modèle ouvert sur ses GPU peut revenir moins cher ; à faible volume, l'API externe l'emporte presque toujours.

> **À retenir.** Le LLMOps applique le DevOps aux applications IA. Une passerelle LLM centralise accès, quotas, masquage, journal et coûts devant les modèles internes et externes. On versionne prompts, modèles, documents et outils, et on évalue chaque changement en CI sur un jeu de questions types, car la qualité peut baisser silencieusement. On observe tokens, coûts, traces et qualité, et on réduit les coûts par le routage, un contexte plus court, le cache de prompt et des quotas.
