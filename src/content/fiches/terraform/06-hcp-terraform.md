---
title: HCP Terraform
chapter: 6
order: 2
duration: 10
tags:
- Terraform Associate
- HCP Terraform
- Sentinel
cards:
- q: Qu'est-ce que HCP Terraform ?
  a: Le service en ligne de HashiCorp (anciennement **Terraform Cloud**) qui stocke le state, lance les plans et les applies sur ses serveurs, gère les variables et les secrets, et ajoute registre privé et politiques. **Terraform Enterprise** est la même chose installée chez soi.
- q: Comment relie-t-on un projet à HCP Terraform ?
  a: Avec un bloc `cloud` dans `terraform { }` (organisation et workspace), puis `terraform login` pour obtenir un jeton et `terraform init`.
- q: Un workspace HCP Terraform est-il la même chose qu'un workspace de la CLI ?
  a: '**Non.** Un workspace HCP a son propre state, ses variables, ses droits et son historique d''exécutions : c''est l''équivalent d''un dossier de configuration par environnement. Les workspaces de la CLI ne sont que plusieurs states pour un même code.'
- q: Quels sont les trois modes de déclenchement d'un run ?
  a: '**VCS** (un push ou une pull request sur le dépôt lié lance un plan), **CLI** (`terraform plan` en local, exécuté à distance avec les logs affichés chez toi) et **API** (un outil externe déclenche le run).'
- q: À quoi servent Sentinel et OPA dans HCP Terraform ?
  a: 'À écrire des **politiques** vérifiées entre le plan et l''apply : « pas de bucket public », « seulement ces types d''instances ». Niveaux : `advisory` (avertit), `soft-mandatory` (bloque, sauf dérogation), `hard-mandatory` (bloque toujours).'
- q: Qu'apporte le registre privé ?
  a: Un catalogue de **modules** (et de providers) internes, versionnés, que les équipes appellent avec `source = "app.terraform.io/<orga>/<nom>/<provider>"` comme ceux du registre public.
quiz:
- q: Une équipe veut qu'un plan soit lancé automatiquement à chaque pull request et affiché dans la PR. Quel mode ?
  options:
  - CLI
  - VCS
  - API
  - Local
  answer: 1
  explain: 'En mode VCS, HCP Terraform suit le dépôt : un plan spéculatif à chaque PR, un apply après fusion sur la branche suivie.'
- q: Une politique `soft-mandatory` échoue. Que se passe-t-il ?
  options:
  - Rien, c'est un avertissement
  - Le run est bloqué, mais une personne autorisée peut passer outre
  - Le run est toujours bloqué
  - Le state est supprimé
  answer: 1
  explain: '`advisory` avertit seulement, `hard-mandatory` ne laisse aucune dérogation.'
- q: Où mets-tu des identifiants AWS utilisés par plusieurs workspaces ?
  options:
  - Dans le code, en clair
  - Dans un variable set, en variables d'environnement sensibles
  - Dans le state
  - Dans un output
  answer: 1
  explain: 'Un variable set s''applique à plusieurs workspaces. Mieux encore : des identifiants dynamiques (OIDC) qui évitent les clés longues durées.'
level: intermédiaire
---

La fiche précédente expliquait comment une équipe partage un state et fait tourner Terraform en CI. **HCP Terraform** (HashiCorp Cloud Platform, anciennement Terraform Cloud) est le service de HashiCorp qui fait tout cela clé en main. L'examen Terraform Associate lui consacre un domaine entier.

> **Les outils cités dans cette fiche.**
> - **HCP Terraform** : le service en ligne qui garde le state, exécute les runs, stocke les variables et applique des politiques. Version installée chez soi : **Terraform Enterprise**.
> - **run** : une exécution de Terraform (un plan, suivi ou non d'un apply) faite par HCP Terraform.
> - **VCS** (Version Control System) : le système de gestion de versions, ici un dépôt GitHub ou GitLab relié au workspace.
> - **Sentinel** : le langage de politiques de HashiCorp. **OPA** (Open Policy Agent) est un moteur de politiques open source, avec le langage **Rego**.
> - **OIDC** : un protocole qui permet à HCP Terraform d'obtenir des identifiants cloud temporaires, sans clé stockée.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **bucket** : un conteneur de fichiers dans un stockage objet (S3, Swift).
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **artefact** : un fichier produit par une étape du pipeline (binaire, image, rapport) et transmis aux suivantes.
> - **branche** : une ligne de développement parallèle dans Git.
> - **pipeline** : une suite d'étapes automatiques (construire, tester, déployer) lancée à chaque modification.

## Comprendre : ce que le service ajoute

| Besoin d'une équipe | Sans HCP Terraform | Avec HCP Terraform |
| --- | --- | --- |
| state partagé et verrouillé | bucket S3 et verrou | inclus, avec l'historique des versions |
| où tourne `apply` | poste du développeur ou CI | serveurs de HCP (ou un agent chez toi) |
| secrets du provider | variables de la CI | variables sensibles par workspace |
| relire avant d'appliquer | plan en artefact de CI | plan affiché, bouton « Confirm & apply » |
| règles d'entreprise | revue humaine | politiques Sentinel ou OPA |
| modules partagés | dépôts Git | registre privé |

## L'organisation

```
Organisation (shop)
└── Projet (paiement)
    ├── Workspace paiement-dev    ← state, variables, droits, historique
    └── Workspace paiement-prod
```

Un **workspace HCP** n'est pas un workspace de la CLI : il a son propre state, ses propres variables, ses droits et son historique de runs. On en fait un par composant et par environnement.

## Relier un projet

```hcl
terraform {
  cloud {
    organization = "shop"
    workspaces {
      name = "paiement-prod"      # ou tags = ["paiement"] pour plusieurs
    }
  }
}
```

```bash
terraform login        # ouvre le navigateur et enregistre un jeton
terraform init         # propose de migrer un state local existant
terraform plan         # s'exécute chez HCP, les logs s'affichent chez toi
```

## Les trois façons de lancer un run

- **VCS** : le workspace suit une branche du dépôt. Une pull request déclenche un **plan spéculatif** (qui ne peut pas être appliqué) affiché dans la PR ; une fusion déclenche un vrai run.
- **CLI** : `terraform plan` et `apply` depuis ton poste, mais exécutés à distance avec les variables du workspace.
- **API** : un outil (pipeline, portail interne) déclenche les runs.

Le **mode d'exécution** se choisit par workspace : `remote` (sur les serveurs de HCP), `local` (HCP ne garde que le state) ou `agent` (un agent installé dans ton réseau, pour atteindre des ressources privées).

## Variables et variable sets

Chaque workspace a deux sortes de variables : **Terraform** (l'équivalent d'un `.tfvars`) et **environnement** (comme `AWS_REGION`). Chacune peut être marquée **sensitive** : elle n'est plus lisible, ni dans l'interface ni par l'API. Un **variable set** partage les mêmes variables entre plusieurs workspaces, par exemple les accès au compte cloud. Le mieux reste les **identifiants dynamiques** (OIDC) : aucun secret long à stocker.

## Le registre privé

```hcl
module "vpc" {
  source  = "app.terraform.io/shop/vpc/aws"
  version = "~> 2.1"
}
```

Les modules y sont publiés depuis un dépôt Git, à chaque tag de version.

## Les politiques

Entre le plan et l'apply, HCP Terraform peut vérifier des **politiques** écrites en Sentinel ou en OPA.

| Niveau | Si la politique échoue |
| --- | --- |
| `advisory` | avertissement, le run continue |
| `soft-mandatory` | run bloqué, une personne autorisée peut passer outre |
| `hard-mandatory` | run bloqué, sans exception |

Autres options vues à l'examen : l'**estimation des coûts** du plan, les **run tasks** (appeler un outil externe, comme un scanner, pendant le run) et la **détection de dérive**, qui lance régulièrement un plan pour signaler les changements faits hors de Terraform.

> **À retenir.** HCP Terraform garde le state, exécute les runs (VCS, CLI ou API) et stocke les variables sensibles. On s'y relie avec un bloc `cloud` et `terraform login`. Un workspace HCP n'est pas un workspace de la CLI. Les politiques Sentinel ou OPA tombent entre plan et apply, en `advisory`, `soft-mandatory` ou `hard-mandatory`.
