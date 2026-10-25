---
title: Écrire de bons prompts
chapter: 3
order: 1
duration: 10
tags:
- IA
- Prompt
cards:
- q: Quels sont les éléments d'une bonne demande à un assistant ?
  a: Le **contexte** (environnement, versions, contraintes), la **tâche** précise, les **entrées** réelles (fichier, erreur, log filtré), le **format** attendu (un fichier complet, un diff, un tableau) et les **critères de réussite** (« doit passer `terraform validate` », « sans droits root »).
- q: Pourquoi donner des exemples dans un prompt ?
  a: 'Un ou deux exemples (*few-shot*) montrent le format et le niveau attendus bien mieux qu''une description : par exemple deux alertes déjà classées avant de demander de classer la troisième.'
- q: Qu'est-ce que demander au modèle de poser des questions d'abord ?
  a: 'Pour une tâche floue, lui dire « avant de répondre, pose-moi les questions qui te manquent » : il fait apparaître les hypothèses (cloud, version, contraintes de sécurité) au lieu de les inventer.'
- q: Comment découper une tâche complexe ?
  a: 'En étapes vérifiables : d''abord un **plan** que tu valides, puis chaque partie, avec un test à chaque étape. Un « fais-moi toute la migration » d''un coup donne un résultat difficile à relire et souvent faux quelque part.'
- q: Que ne faut-il jamais coller dans un assistant externe ?
  a: Des **secrets** (mots de passe, jetons, clés privées, kubeconfig avec certificats, fichiers `.tfstate` qui contiennent souvent des secrets), des données personnelles de clients, et tout ce que la politique de l'entreprise interdit. Masquer avant de coller.
quiz:
- q: Quel prompt donnera la meilleure réponse ?
  options:
  - « Pourquoi mon pod plante ? »
  - « Pod en CrashLoopBackOff sur EKS 1.31. Voici `kubectl describe` et les 50 dernières lignes de logs. Le déploiement a changé l'image hier. Donne les 3 causes les plus probables et la commande pour vérifier chacune. »
  - « Répare Kubernetes »
  - « Explique Kubernetes »
  answer: 1
  explain: 'Contexte, entrées réelles, changement récent, format de réponse : chaque élément réduit l''invention.'
- q: Le modèle propose une commande `rm -rf` dans un script de nettoyage. Que fais-tu ?
  options:
  - L'exécuter, il sait ce qu'il fait
  - Lire et comprendre chaque commande, tester en dry-run ou sur un environnement jetable avant la production
  - Demander une autre réponse et exécuter sans lire
  - Monter la température
  answer: 1
  explain: 'Une commande générée a le statut d''un code proposé par un inconnu : relue et testée avant d''être appliquée.'
level: intermédiaire
---

La qualité d'une réponse dépend d'abord de la qualité de la demande. Un assistant n'a ni ton écran, ni ton cluster, ni ton historique : il ne sait que ce que tu lui dis. Écrire un bon prompt, c'est surtout bien **briefer**, comme on le ferait pour un collègue compétent qui arrive sur le projet.

> **Les outils cités dans cette fiche.**
> - **prompt** : le texte qu'on envoie au modèle (consigne, contexte, données).
> - **few-shot** : donner quelques exemples résolus dans le prompt.
> - **dry-run** : exécuter une commande en mode simulation, sans rien modifier (`kubectl apply --dry-run=server`, `terraform plan`, `ansible-playbook --check`).
> - **cluster** : un groupe de machines qui travaillent ensemble comme un seul système.
> - **EKS** : le service Kubernetes managé d'AWS.
> - **nœud** : une machine (physique ou virtuelle) membre d'un cluster.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **manifest** : un fichier YAML qui décrit un objet Kubernetes.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…
> - **namespace** : un espace de noms : dans Kubernetes, une partition du cluster ; sous Linux, une isolation du noyau.

## Comprendre : briefer un collègue

Un bon prompt répond à cinq questions :

| Question | Exemple |
| --- | --- |
| où ? (contexte) | « cluster EKS 1.31, ArgoCD, charts Helm maison, pas d'accès Internet depuis les nœuds » |
| quoi ? (tâche) | « écrire une NetworkPolicy qui n'autorise que le front vers l'API sur le port 8080 » |
| avec quoi ? (entrées) | le manifest actuel, les labels des pods, l'erreur exacte |
| sous quelle forme ? | « un seul fichier YAML complet, commenté » |
| comment juger ? | « doit passer `kubectl apply --dry-run=server` ; ne pas toucher au namespace monitoring » |

## Des modèles de prompts utiles

```text
Contexte : module Terraform AWS (provider 5.x), state dans S3, CI GitLab.
Tâche : ajoute un bucket S3 pour les logs, chiffré KMS, sans accès public,
avec une règle de cycle de vie à 90 jours.
Contraintes : reprends les conventions de nommage du fichier ci-dessous.
Réponds avec le fichier complet, puis une liste de ce que je dois vérifier dans le plan.

<fichier main.tf>
…
</fichier>
```

```text
Voici une erreur et ce que j'ai déjà vérifié. Ne me donne pas de solution tout de suite :
liste les hypothèses par ordre de probabilité et, pour chacune, la commande qui la confirme
ou l'élimine.
```

```text
Explique ce script ligne par ligne comme à quelqu'un qui connaît Linux mais pas awk,
puis signale ce qui pourrait casser en production.
```

## Les bonnes habitudes

- **Itérer** : la première réponse est un brouillon. Corriger (« non, on n'a pas de NAT Gateway »), préciser, demander une version plus simple.
- **Demander le raisonnement ou des alternatives** : « propose deux approches et leurs compromis » évite de foncer sur la première idée.
- **Faire vérifier** : « relis ta réponse et cherche les erreurs », ou mieux, le faire relire par un outil (linter, plan, tests).
- **Garder ses prompts** : les bons prompts récurrents (revue de MR, postmortem, explication d'alerte) deviennent des modèles partagés dans l'équipe.

## Les erreurs fréquentes

| Erreur | Conséquence | À la place |
| --- | --- | --- |
| question vague | réponse générique | contexte et entrées réelles |
| coller tout le dépôt ou 10 000 lignes de logs | réponse noyée, coûteuse | filtrer, donner l'essentiel |
| accepter sans relire | bug ou incident en production | relire, dry-run, tests |
| coller un secret ou un tfstate | fuite de données | masquer, utiliser des valeurs factices |
| tout demander d'un coup | résultat faux quelque part et difficile à relire | plan validé, puis étapes |

## Ce qui reste ta responsabilité

L'assistant propose, tu décides. Une commande, un manifest ou une politique IAM générés ont le statut d'une **proposition** : on les comprend, on les teste, on les fait passer par la même revue et la même CI que le reste. Une règle simple : ne jamais appliquer ce qu'on ne saurait pas expliquer.

> **À retenir.** Briefer comme pour un collègue : contexte, tâche, entrées réelles, format, critères de réussite. Donner des exemples, faire poser les questions manquantes, découper en étapes avec un plan validé. Itérer, demander des alternatives, faire vérifier par des outils. Jamais de secrets ni de tfstate dans un assistant externe. Ce qui est généré se relit et se teste comme le code d'un autre.
