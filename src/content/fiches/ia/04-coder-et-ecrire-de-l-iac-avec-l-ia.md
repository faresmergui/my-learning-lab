---
title: L'IA pour le code, l'IaC et les pipelines
chapter: 4
order: 1
duration: 12
tags:
- IA
- Terraform
- Kubernetes
- CI/CD
cards:
- q: Quels sont les trois grands types d'assistants de code ?
  a: La **complétion dans l'éditeur** (suggestions ligne par ligne, comme GitHub Copilot), le **chat** sur le code (expliquer, modifier un fichier) et les **agents de code** (Claude Code, Codex, Cursor en mode agent…) qui lisent le dépôt, modifient plusieurs fichiers et lancent des commandes (tests, linters) eux-mêmes.
- q: Pourquoi l'IaC générée par IA demande-t-elle une vigilance particulière ?
  a: 'Parce qu''une erreur ne casse pas seulement un programme : elle peut **ouvrir un bucket au public**, donner des droits IAM trop larges, ou détruire une ressource (remplacement forcé). Les modèles connaissent aussi parfois d''anciennes versions des providers. D''où `plan`, lecture du diff, scanners de sécurité et revue.'
- q: Quels garde-fous automatiques mettre derrière du code généré ?
  a: 'Les mêmes que pour tout code : formatage et lint (`terraform fmt`, `tflint`, `ansible-lint`, `yamllint`), validation (`terraform validate`, `kubectl --dry-run=server`, `kubeconform`), scanners de sécurité IaC (Checkov, Trivy, KICS), politiques (OPA/Conftest, Kyverno), tests, et revue humaine de la merge request.'
- q: Où l'IA fait-elle gagner le plus de temps en DevOps ?
  a: Le code répétitif (modules, manifests, pipelines), les **conversions** (bash vers Ansible, Compose vers Helm, Jenkinsfile vers GitLab CI), l'explication de code ou de configurations inconnues, l'écriture de tests et de documentation, et la **revue** de merge requests.
- q: Comment donner à un agent de code les règles du projet ?
  a: 'Par un fichier d''instructions dans le dépôt (par exemple `CLAUDE.md` ou `AGENTS.md`) : conventions de nommage, commandes de test et de lint, ce qu''il ne faut jamais toucher (state, environnements de production), procédure de validation.'
quiz:
- q: 'L''assistant génère une politique IAM avec `"Action": "*"` pour « que ça marche ». Que fais-tu ?'
  options:
  - L'accepter, c'est plus simple
  - 'Refuser : demander les actions minimales nécessaires (moindre privilège), vérifier avec IAM Access Analyzer ou les logs, et faire passer un scanner de sécurité'
  - 'Ajouter `Resource: *` aussi'
  - La déployer en production pour tester
  answer: 1
  explain: Un modèle optimise souvent pour « ça marche » ; c'est à toi d'imposer le moindre privilège, de préférence dès le prompt.
- q: Un agent propose un changement Terraform dont le plan affiche `-/+ destroy and then create replacement` sur la base de données. Que fais-tu ?
  options:
  - Appliquer
  - 'S''arrêter : comprendre quel attribut force le remplacement, corriger (lifecycle, moved, valeur d''origine) et ne pas appliquer tant que le plan détruit une ressource avec des données'
  - Supprimer le state
  - Ajouter -auto-approve
  answer: 1
  explain: La lecture du plan reste la barrière principale, encore plus avec du code généré.
level: intermédiaire
---

L'endroit où l'IA a le plus changé le travail des ingénieurs, c'est l'écriture de code, et l'infrastructure en code n'y échappe pas : modules Terraform, manifests Kubernetes, charts Helm, playbooks Ansible, pipelines GitLab CI. Bien utilisée, elle fait gagner beaucoup de temps sur le répétitif et l'inconnu. Mal utilisée, elle produit vite de l'infrastructure fragile ou dangereuse.

> **Les outils cités dans cette fiche.**
> - **assistant de code** : un outil d'IA intégré à l'éditeur ou au terminal (GitHub Copilot, Cursor, Claude Code, Codex…).
> - **agent de code** : un assistant qui agit lui-même dans le dépôt (lit, modifie, lance des commandes).
> - **IaC** (Infrastructure as Code) : décrire l'infrastructure dans des fichiers versionnés (Terraform, Ansible, Helm…).
> - **tflint**, **ansible-lint**, **yamllint**, **kubeconform** : des vérificateurs de syntaxe et de bonnes pratiques.
> - **Checkov**, **Trivy**, **KICS** : des scanners qui détectent les failles de sécurité dans l'IaC.
> - **OPA/Conftest** et **Kyverno** : des moteurs de politiques qui refusent les configurations non conformes.
> - **manifest** : un fichier YAML qui décrit un objet Kubernetes.
> - **playbook** : un fichier YAML Ansible qui liste les tâches à appliquer à des machines.
> - **pipeline** : une suite d'étapes automatiques (construire, tester, déployer) lancée à chaque modification.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.
> - **provider** : le plugin qui permet à Terraform de piloter une plateforme (AWS, OpenStack, Kubernetes).
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **MR** : merge request : la demande de fusion d'une branche dans GitLab, avec revue de code (pull request sur GitHub).

## Comprendre : trois niveaux d'assistance

| Niveau | Ce qu'il fait | Ce que tu fais |
| --- | --- | --- |
| complétion | propose la suite de la ligne ou du bloc | accepter ou ignorer, au fil de l'eau |
| chat | explique, modifie le fichier qu'on lui donne | copier, relire, intégrer |
| agent | explore le dépôt, modifie plusieurs fichiers, lance tests et lint, itère | définir la tâche et les limites, relire le diff, valider |

Plus l'outil est autonome, plus le **cadre** compte : un agent doit savoir quelles commandes il peut lancer, ce qu'il ne doit pas toucher, et comment prouver que son travail est correct.

## Les usages qui rapportent

- **Le répétitif** : un nouveau module Terraform sur le modèle des autres, dix manifests similaires, les variables et outputs.
- **Les conversions** : un script bash en rôle Ansible, un `docker-compose.yml` en chart Helm, un Jenkinsfile en `.gitlab-ci.yml`.
- **Comprendre l'inconnu** : « explique ce module hérité », « que fait ce filtre jq », « pourquoi cette regex ».
- **Les tests et la doc** : tests Terratest ou `terraform test`, README de module, commentaires.
- **La revue** : faire relire une merge request (« cherche les problèmes de sécurité et les changements destructifs »), en complément d'une revue humaine.
- **Le débogage** : donner l'erreur, le fichier et le contexte, demander des hypothèses et des vérifications.

## La chaîne de garde-fous

```
code généré ─► fmt / lint ─► validate / dry-run ─► scanner sécurité ─► politique ─► plan relu ─► revue MR ─► apply
              terraform fmt   terraform validate     Checkov, Trivy     OPA, Kyverno   terraform plan
              tflint          kubectl --dry-run=server                                 helm diff
              ansible-lint    ansible --check
```

Cette chaîne existe déjà dans une équipe DevOps mature ; l'IA la rend simplement **indispensable**. Un agent de code bien configuré lance lui-même ces commandes et corrige jusqu'à ce qu'elles passent, ce qui fait gagner des allers-retours.

## Les pièges propres à l'IaC

| Piège | Exemple | Parade |
| --- | --- | --- |
| droits trop larges | `Action: "*"`, `0.0.0.0/0` sur SSH | demander le moindre privilège, scanner |
| syntaxe d'une ancienne version | argument déprécié d'un provider, API Kubernetes retirée | donner la version, `validate`, `kubeconform` |
| remplacement destructif | changement d'un attribut qui recrée la base | lire le plan, `prevent_destroy` |
| secrets en clair | mot de passe dans une variable par défaut | coffre à secrets, revue |
| options inventées | annotation Ingress qui n'existe pas | doc officielle, dry-run serveur |
| cohérence perdue | conventions de nommage, tags oubliés | fichier d'instructions du projet, exemples |

## Donner les règles du projet

```markdown
# CLAUDE.md (ou AGENTS.md)
- Terraform >= 1.9, provider AWS 5.x. Toujours lancer `terraform fmt -recursive` et `tflint`.
- Ne jamais lancer `terraform apply` ni modifier `envs/prod/`.
- Kubernetes : valider avec `kubeconform -strict` et `kubectl apply --dry-run=server` sur le cluster de dev.
- Nommage : <équipe>-<env>-<composant>, tags obligatoires owner et cost-center.
```

Ce fichier sert à la fois à l'IA et aux nouveaux arrivants de l'équipe.

> **À retenir.** Complétion, chat et agents de code : plus l'outil agit seul, plus il faut un cadre (règles du projet, commandes autorisées, interdits). L'IA brille sur le répétitif, les conversions, l'explication, les tests et la revue. Derrière, toujours la même chaîne : lint, validate ou dry-run, scanner de sécurité, politique, plan relu, revue de MR. Surveiller les droits trop larges, les versions dépassées, les remplacements destructifs et les secrets.
