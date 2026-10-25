---
title: Une feuille de route IA pour un ingénieur cloud
chapter: 12
order: 1
duration: 11
tags:
- IA
- DevOps
- Carrière
cards:
- q: Comment l'IA change-t-elle le métier d'ingénieur DevOps/cloud ?
  a: 'Sur trois plans. **Utilisateur** : l''IA accélère l''écriture de code et d''IaC, le diagnostic et la documentation. **Intégrateur** : on branche l''IA dans les outils de l''équipe (MR, CI, astreinte, ChatOps). **Fournisseur** : l''équipe plateforme héberge et exploite des modèles, des GPU et des passerelles pour les autres équipes.'
- q: Par quoi commencer pour intégrer l'IA dans une équipe ?
  a: 'Par des usages à **fort gain et faible risque** : explication de code et d''erreurs, brouillons de documentation et de postmortems, traduction en PromQL ou en requêtes de logs, relecture de MR. Ensuite seulement : agents de code avec garde-fous, assistant d''astreinte en lecture seule, puis automatisations.'
- q: Comment mesurer si l'IA aide vraiment l'équipe ?
  a: 'Avec des indicateurs existants plutôt que des impressions : délai entre ouverture et merge des MR, **MTTR** des incidents, temps passé sur les tâches répétitives, nombre de runbooks à jour, taux de défauts trouvés en revue, plus un retour régulier des ingénieurs. Comparer avant et après, sur quelques semaines.'
- q: Quelles compétences développer en priorité ?
  a: 'Savoir **briefer et vérifier** (prompts, revue critique), **cadrer des agents** (droits, outils, MCP), construire un **RAG** simple sur la doc de l''équipe, et côté plateforme : **inférence sur GPU** (vLLM, KServe, GPU Operator, PCI/vGPU sur OpenStack), passerelle LLM, observabilité et coûts.'
- q: Quelles erreurs éviter lors de l'adoption ?
  a: Automatiser des actions en production avant d'avoir des garde-fous, laisser chacun utiliser n'importe quel outil avec des données sensibles, mesurer le succès au nombre de lignes générées, ne pas relire, et négliger la documentation qui nourrit le RAG.
quiz:
- q: Ton responsable veut « mettre de l'IA partout » ce trimestre. Quelle proposition est la plus solide ?
  options:
  - Un agent qui applique seul les changements Terraform en production
  - Deux ou trois usages mesurables à faible risque (revue de MR, postmortems, assistant d'astreinte en lecture seule sur les runbooks), une passerelle commune et une politique d'usage, avec des indicateurs avant/après
  - Acheter le plus gros modèle
  - Interdire l'IA
  answer: 1
  explain: On démontre la valeur sur des usages sûrs et mesurés, puis on étend.
- q: L'équipe data demande à la plateforme de servir un modèle ouvert pour un usage interne. Quel est le rôle naturel d'un ingénieur cloud ?
  options:
  - Entraîner le modèle
  - 'Fournir l''infrastructure : nœuds ou VM GPU, serveur d''inférence (vLLM, KServe), authentification et quotas via la passerelle, supervision (DCGM, métriques d''inférence), coûts et mises à jour'
  - Écrire les prompts de l'équipe data
  - Refuser
  answer: 1
  explain: L'IA devient une charge de travail de la plateforme, comme une base de données ou un cluster.
level: intermédiaire
---

Cette dernière fiche relie tout le module à ton quotidien d'ingénieur cloud qui travaille avec Kubernetes, OpenStack, Terraform, Ansible et GitLab CI. L'IA ne remplace pas ces compétences : elle les rend plus rapides à exercer, et elle crée de nouvelles responsabilités pour les équipes plateforme. L'objectif est d'avoir une feuille de route concrète, progressive et mesurable.

> **Les outils cités dans cette fiche.**
> - **MR** (merge request) : la demande de fusion de GitLab, l'équivalent de la pull request de GitHub.
> - **ChatOps** : piloter l'exploitation depuis la messagerie de l'équipe avec des bots.
> - **MTTR** : le temps moyen de rétablissement après un incident.
> - **DORA** : quatre indicateurs de performance des équipes de livraison (fréquence de déploiement, délai de mise en production, taux d'échec des changements, temps de rétablissement).
> - **passerelle LLM** : le point d'accès commun aux modèles (voir la fiche LLMOps).
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **VM** : une machine virtuelle : un ordinateur complet simulé sur un serveur physique par un hyperviseur.

## Comprendre : trois rôles

```
UTILISATEUR             INTÉGRATEUR                     FOURNISSEUR
l'IA t'aide             tu branches l'IA dans           tu héberges l'IA
à faire ton travail     les outils de l'équipe          pour les autres
───────────────         ──────────────────────          ─────────────────────
code, IaC, debug        revue de MR en CI               GPU (K8s, OpenStack, Ironic)
explications, doc       bot d'astreinte (RAG + MCP)     vLLM, KServe, passerelle
requêtes PromQL         ChatOps, résumés d'incident     quotas, coûts, observabilité
```

Un ingénieur cloud passe naturellement par les trois : il commence par utiliser, puis il outille son équipe, et la plateforme finit par devoir servir des modèles.

## Ce qui change dans les tâches quotidiennes

| Tâche | Avant | Avec l'IA bien utilisée |
| --- | --- | --- |
| nouveau module Terraform | copier un module, adapter | décrire, générer sur le modèle des autres, `plan` et scanners |
| comprendre un dépôt hérité | lire pendant des heures | demander une carte du dépôt, puis vérifier dans le code |
| erreur Kubernetes ou OpenStack inconnue | chercher sur le web | donner l'erreur et le contexte, obtenir des hypothèses et les commandes de vérification |
| requête Prometheus ou Loki | tâtonner | décrire en français, relire la requête proposée |
| postmortem | une heure de rédaction | relire et corriger un brouillon |
| revue de MR | humaine seulement | pré-revue automatique, humain sur l'essentiel |
| documentation | souvent repoussée | générée à partir du code, relue |

## Une feuille de route en quatre étapes

**1. Pour toi (tout de suite)**
- Un assistant approuvé par l'entreprise et un agent de code dans le terminal, avec un fichier d'instructions dans chaque dépôt.
- L'habitude de briefer (contexte, entrées, format) et de vérifier (lint, validate, dry-run, plan).

**2. Pour l'équipe (quelques semaines)**
- Une **pré-revue IA** des MR dans GitLab CI (sécurité IaC, changements destructifs), en commentaire.
- Des **prompts partagés** pour les postmortems, l'explication d'alertes et les passations d'astreinte.
- Une **politique d'usage** et la liste des outils approuvés.

**3. L'assistant d'équipe (un trimestre)**
- Un **RAG** sur les runbooks, postmortems et la doc d'architecture (pgvector suffit pour commencer).
- Des **serveurs MCP** en lecture sur Kubernetes, Prometheus, Loki, GitLab et OpenStack.
- Un bot d'astreinte qui résume, propose des hypothèses et retrouve le runbook ; les actions restent humaines.

**4. La plateforme IA (selon les besoins)**
- Une **passerelle LLM** commune (accès, quotas, coûts, journal).
- Des **GPU** : VM ou bare metal sur OpenStack, GPU Operator sur Kubernetes.
- Un service d'**inférence** (vLLM, KServe) pour les modèles ouverts, avec supervision et évaluation.

## Mesurer

- Délais des MR et indicateurs **DORA** avant et après.
- **MTTR** et temps de diagnostic des incidents.
- Part des runbooks à jour, temps gagné sur les postmortems.
- Coûts (tokens, GPU) rapportés à l'usage.
- Retours des ingénieurs, tous les mois.

## Les compétences à développer

1. **Briefer et vérifier** : la compétence de base, qui ne s'automatise pas.
2. **Cadrer des agents** : droits, outils, MCP, garde-fous.
3. **RAG et données** : rendre la documentation exploitable.
4. **Inférence et GPU** : le prolongement naturel de Kubernetes et d'OpenStack.
5. **LLMOps** : passerelle, évaluation, observabilité, coûts.
6. **Sécurité de l'IA** : injection, fuites, chaîne d'approvisionnement.

> **À retenir.** Trois rôles : utiliser l'IA pour ton travail, l'intégrer dans les outils de l'équipe, l'héberger comme fournisseur de plateforme. Avancer par étapes : toi, l'équipe (pré-revue de MR, prompts partagés, politique), l'assistant d'équipe (RAG, MCP en lecture, bot d'astreinte), puis la plateforme (passerelle, GPU, inférence). Commencer par les usages à fort gain et faible risque, mesurer avec les indicateurs existants (DORA, MTTR), et garder la décision humaine sur tout ce qui touche la production.
