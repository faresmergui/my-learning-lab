---
title: Synthèse Terraform
description: "Le cycle, les blocs du langage, le state, les modules et les pièges du plan."
---

## Le cycle

```bash
terraform init               # providers, modules, backend, .terraform.lock.hcl
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
terraform destroy            # avec prudence
```

| Symbole du plan | Action |
| --- | --- |
| `+` | création |
| `~` | modification sur place |
| `-/+` | remplacement (`# forces replacement`) |
| `-` | destruction |

## Les blocs du langage

| Bloc | Rôle |
| --- | --- |
| `terraform {}` | Version requise, providers, backend |
| `provider` | Connexion à une API (région, identifiants, tags par défaut) |
| `resource` | Une ressource gérée |
| `data` | Lire une ressource existante sans la gérer |
| `variable` | Entrée du module |
| `locals` | Valeurs calculées |
| `output` | Sortie du module |
| `module` | Appeler un module |
| `moved`, `import`, `removed` | Refactoriser, importer, oublier une ressource sans la détruire |

## Data sources et fonctions

- Un objet est **géré** par un seul projet (`resource`) et **lu** par les autres (`data`, référence `data.<type>.<nom>.<attr>`).
- Fonctions à connaître : `merge`, `lookup`, `try`, `coalesce`, `cidrsubnet`, `templatefile`, `jsonencode`, `toset`. On les essaie dans `terraform console`.
- `sensitive = true` masque l'affichage et se propage, mais la valeur reste **en clair dans le state** : backend chiffré, ou `ephemeral` et arguments write-only (Terraform 1.10 et plus).

## Les méta-arguments

| Méta-argument | Usage |
| --- | --- |
| `count` | N copies identiques, indexées par numéro |
| `for_each` | Une copie par clé d'une map ou d'un set : préférable, les clés restent stables |
| `depends_on` | Dépendance explicite, quand aucune référence ne la crée |
| `provider` | Choisir un alias de provider (autre région, autre compte) |
| `lifecycle` | `create_before_destroy`, `prevent_destroy`, `ignore_changes`, `replace_triggered_by` |

## Les expressions utiles

```hcl
name   = "${local.prefix}-api"
size   = var.env == "prod" ? "large" : "small"
ids    = [for s in var.subnets : s.id]
by_az  = { for s in var.subnets : s.az => s.id }
tags   = merge(local.common_tags, { role = "api" })
first  = try(var.list[0], null)
dynamic "ingress" {
  for_each = var.ports
  content {
    from_port = ingress.value
    to_port   = ingress.value
    protocol  = "tcp"
  }
}
```

Fonctions fréquentes : `lookup`, `coalesce`, `flatten`, `toset`, `jsonencode`, `templatefile`, `cidrsubnet`, `format`.

## Les variables

Priorité, de la plus faible à la plus forte :

```
défaut < TF_VAR_x < terraform.tfvars < *.auto.tfvars < -var / -var-file
```

Typer (`object`, `list`, `map`, `optional()`), valider (`validation`), et marquer `sensitive` (masque l'affichage, **pas** le stockage dans le state).

## Le state

- Le lien **code ↔ ressource réelle**. Distant (S3, GCS, Terraform Cloud), chiffré, versionné, avec **verrou**.
- Un state par périmètre et par environnement.
- Contient des secrets en clair : accès restreint.

```bash
terraform state list
terraform state show aws_vpc.main
terraform state rm aws_s3_bucket.old       # oublier sans détruire
terraform plan -refresh-only               # voir la dérive
terraform force-unlock ID                  # seulement si personne n'applique
```

## Refactoriser sans casser

```hcl
moved {
  from = aws_instance.web
  to   = module.web.aws_instance.this
}

import {
  to = aws_s3_bucket.logs
  id = "fares-logs-prod"
}
```

`terraform plan -generate-config-out=generated.tf` écrit le code des ressources importées.

## Déboguer

```bash
TF_LOG=DEBUG terraform plan                          # TRACE, DEBUG, INFO, WARN, ERROR
TF_LOG=TRACE TF_LOG_PATH=./terraform.log terraform apply
```

Les journaux peuvent contenir des secrets : ne pas les partager tels quels.

## Les modules

- Un module = un dossier avec ses variables, ressources et outputs.
- Versionner les modules (tag Git ou registre) et fixer la version à l'appel.
- Peu de variables, des valeurs par défaut sensées, des outputs pour tout ce qu'un autre module peut utiliser.
- Ne pas mettre de bloc `provider` dans un module réutilisable.

## Contraintes de version

| Écriture | Accepte |
| --- | --- |
| `= 6.2.0` | exactement 6.2.0 |
| `~> 6.2` | 6.2 et plus, pas 7.0 |
| `~> 6.2.0` | 6.2.x seulement |

## Tester et valider

- `terraform validate`, `tflint`, `checkov` ou `trivy config` en CI.
- `terraform test` avec des fichiers `.tftest.hcl`.
- Blocs `check` et `precondition` / `postcondition` pour les vérifications à l'exécution.
- Le plan en commentaire de la merge request, l'apply seulement après revue.

## HCP Terraform

- Bloc `cloud { organization = "…" workspaces { name = "…" } }`, puis `terraform login` et `terraform init`.
- Un workspace HCP (state, variables, droits, historique) n'est **pas** un workspace de la CLI.
- Runs déclenchés par **VCS** (plan spéculatif sur PR), **CLI** ou **API** ; exécution `remote`, `local` ou `agent`.
- Variables Terraform ou d'environnement, marquées sensibles ; **variable sets** partagés entre workspaces.
- Registre privé : `source = "app.terraform.io/<orga>/<nom>/<provider>"`.
- Politiques Sentinel ou OPA entre plan et apply : `advisory`, `soft-mandatory`, `hard-mandatory`.

## Les pièges classiques

1. Renommer une ressource sans `moved` : destruction puis recréation.
2. `count` sur une liste qui change d'ordre : les ressources sont décalées et recréées. Préférer `for_each`.
3. `-auto-approve` en local : plus aucune chance de voir un remplacement.
4. Modifier à la main dans la console : dérive, annulée au prochain apply.
5. Secrets dans les `.tfvars` commités.
