---
title: Variables, outputs et locals
chapter: 3
order: 1
duration: 8
level: intermédiaire
tags:
- Terraform Associate
cards:
- q: Quelle est la différence entre une variable, un local et un output ?
  a: La **variable** est une entrée (fournie de l'extérieur). Le **local** est une valeur calculée à l'intérieur, pour éviter de se répéter. L'**output** est une sortie, lisible par l'appelant ou par `terraform output`.
- q: Dans quel ordre Terraform lit-il les valeurs des variables ?
  a: 'Du plus faible au plus fort : valeur par défaut, `TF_VAR_nom`, `terraform.tfvars`, fichiers `*.auto.tfvars`, puis `-var` et `-var-file` sur la ligne de commande. Le dernier gagne.'
- q: Que fait `sensitive = true` sur une variable ou un output ?
  a: Il **masque** la valeur dans le plan et les sorties. Mais elle reste **en clair dans le state**.
- q: Comment refuser une valeur invalide dès le plan ?
  a: 'Avec un bloc `validation` dans la variable : une `condition` et un `error_message`.'
- q: Comment déclarer une variable qui est une liste d'objets ?
  a: '`type = list(object({ name = string, port = number }))`. Les attributs facultatifs s''écrivent `optional(number, 80)`.'
- q: 'Variable ou local : comment choisir ?'
  a: Si personne d'extérieur ne doit la changer, c'est un **local**. Une variable est une entrée du module.
- q: Comment un module parent lit-il une valeur d'un module enfant ?
  a: 'Par un **output** de l''enfant : `module.network.vpc_id`.'
quiz:
- q: La variable `region` vaut `eu-west-1` dans `terraform.tfvars` et `eu-west-3` dans `prod.auto.tfvars`. Quelle valeur est utilisée ?
  options:
  - eu-west-1
  - eu-west-3
  - Terraform renvoie une erreur
  - La valeur par défaut
  answer: 1
  explain: Les fichiers `*.auto.tfvars` sont lus **après** `terraform.tfvars`, donc ils l'emportent. Un `-var` en ligne de commande passerait encore devant.
- q: Ton output `db_password` est marqué `sensitive`. Comment lire sa valeur ?
  options:
  - C'est impossible
  - '`terraform output -raw db_password`'
  - '`terraform show -sensitive`'
  - Retirer `sensitive` temporairement
  answer: 1
  explain: '`terraform output` masque la valeur, mais `-raw` ou `-json` sur un output précis l''affichent. D''où l''importance de protéger l''accès au state.'
---

Un module Terraform fonctionne comme une fonction : il reçoit des **variables** (ses paramètres d'entrée), calcule des valeurs intermédiaires avec des **locals** (des variables internes, pour éviter de répéter une expression), et renvoie des **outputs** (ses valeurs de sortie, par exemple l'adresse IP d'un serveur créé). Cette fiche montre les trois, et comment les valeurs circulent de l'un à l'autre.

<!-- schema:flux -->
<figure class="diagram"><svg viewBox="0 0 680 230" role="img" aria-label="D&#x27;où viennent les valeurs et où elles vont" style="--minw:560px"><defs><marker id="g9-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g9-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g9-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g9-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="178" height="202" rx="12" class="dg-zone "/><text x="26" y="32" class="dg-zl" text-anchor="start">entrées</text><g class="dg-box dg-pop" style="--d:0"><rect x="28" y="42" width="150" height="46" rx="9"/></g><text x="103.0" y="62.0" class="dg-t" text-anchor="middle" style="--d:0">default</text><text x="103.0" y="80.0" class="dg-s" text-anchor="middle" style="--d:0">dans variable {}</text><g class="dg-box dg-pop" style="--d:1"><rect x="28" y="100" width="150" height="46" rx="9"/></g><text x="103.0" y="120.0" class="dg-t" text-anchor="middle" style="--d:1">*.tfvars</text><text x="103.0" y="138.0" class="dg-s" text-anchor="middle" style="--d:1">par environnement</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="28" y="158" width="150" height="46" rx="9"/></g><text x="103.0" y="178.0" class="dg-t" text-anchor="middle" style="--d:2">-var / TF_VAR_</text><text x="103.0" y="196.0" class="dg-s" text-anchor="middle" style="--d:2">gagne sur le reste</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="236" y="82" width="120" height="56" rx="9"/></g><text x="296.0" y="107.0" class="dg-t" text-anchor="middle" style="--d:3">variables</text><text x="296.0" y="125.0" class="dg-s" text-anchor="middle" style="--d:3">var.env</text><g class="dg-box dg-pop" style="--d:4"><rect x="392" y="82" width="120" height="56" rx="9"/></g><text x="452.0" y="107.0" class="dg-t" text-anchor="middle" style="--d:4">locals</text><text x="452.0" y="125.0" class="dg-s" text-anchor="middle" style="--d:4">calculs, noms</text><g class="dg-box dg-pop" style="--d:5"><rect x="548" y="30" width="118" height="56" rx="9"/></g><text x="607.0" y="55.0" class="dg-t" text-anchor="middle" style="--d:5">resources</text><text x="607.0" y="73.0" class="dg-s" text-anchor="middle" style="--d:5">utilisent var et local</text><g class="dg-box dg-c dg-pop" style="--d:6"><rect x="548" y="134" width="118" height="56" rx="9"/></g><text x="607.0" y="159.0" class="dg-t" text-anchor="middle" style="--d:6">outputs</text><text x="607.0" y="177.0" class="dg-s" text-anchor="middle" style="--d:6">ce que tu exposes</text><path d="M192 110 L234 110" class="dg-l c" marker-end="url(#g9-c)"/><path d="M356 110 L390 110" class="dg-l" marker-end="url(#g9-n)"/><path d="M512 100 L530 100 L530 58 L546 58" class="dg-l" marker-end="url(#g9-n)"/><path d="M607 86 L607 132" class="dg-l" marker-end="url(#g9-n)"/></svg><figcaption>Les variables sont les entrées, les locals les calculs internes, les outputs les sorties.</figcaption></figure>
<!-- /schema:flux -->


> **Les termes et outils cités dans cette fiche.**
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.

## Les variables : les entrées

```hcl
variable "environment" {
  type        = string
  description = "Nom de l'environnement"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment doit valoir dev, staging ou prod."
  }
}

variable "services" {
  type = list(object({
    name = string
    port = optional(number, 80)
  }))
  default = []
}

variable "db_password" {
  type      = string
  sensitive = true
}
```

## Les locals : les valeurs calculées

```hcl
locals {
  name_prefix = "shop-${var.environment}"
  common_tags = {
    environment = var.environment
    project     = "shop"
  }
}
```

## Les outputs : les sorties

```hcl
output "bucket_arn" {
  value       = aws_s3_bucket.logs.arn
  description = "ARN du bucket de logs"
}
```

## Qui l'emporte ?

```
défaut  <  TF_VAR_x  <  terraform.tfvars  <  *.auto.tfvars  <  -var / -var-file
```

## Quand utiliser quoi ?

| Besoin | Outil |
| --- | --- |
| Une valeur qui **change selon l'environnement ou l'utilisateur** du module | `variable` |
| Une valeur **calculée** ou répétée plusieurs fois dans le code | `local` |
| Une valeur à **exposer** à un autre module, à la CI ou à l'humain | `output` |

Une règle simple : si personne d'extérieur ne doit pouvoir la changer, ce n'est pas une variable, c'est un local. Trop de variables rendent un module difficile à utiliser.

## Bien typer

Les types (`string`, `number`, `bool`, `list(...)`, `map(...)`, `object({...})`) servent de **documentation exécutable** : une erreur de saisie est signalée au `plan`, pas après dix minutes d'`apply`. `optional()` dans un `object` permet des attributs facultatifs avec une valeur par défaut, et `validation` impose des règles métier.

## Les outputs entre modules

Dans un module enfant, un output est la seule façon d'exposer une valeur au parent : `module.network.vpc_id`. Ce sont les outputs qui créent les **dépendances** entre modules : Terraform sait qu'il faut créer le réseau avant les instances qui utilisent `vpc_id`.

## Les tfvars par environnement

```
envs/
├── dev.tfvars
└── prod.tfvars
```

```bash
terraform plan -var-file=envs/prod.tfvars
```

Les fichiers `.tfvars` ne devraient pas contenir de secrets : passe-les par `TF_VAR_db_password` depuis la CI, ou mieux, lis-les dans le gestionnaire de secrets avec une data source.

> **À retenir.** `sensitive` masque l'affichage, pas le stockage. Les secrets restent lisibles dans le state : protège-le, ou va chercher les secrets à l'exécution (Vault, Secrets Manager).
