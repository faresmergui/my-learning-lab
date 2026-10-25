---
title: TF Associate
name: HashiCorp Certified Terraform Associate
org: HashiCorp (IBM)
order: 5
color: "#8b5cf6"
description: Connaître Terraform, son workflow, le state et les modules, au niveau d'un usage professionnel.
officialUrl: https://developer.hashicorp.com/certifications/infrastructure-automation
checked: 22 octobre 2026
format:
  - { label: Type, value: "QCM en ligne surveillé (choix unique, choix multiples, vrai ou faux, texte à compléter)" }
  - { label: Durée, value: "1 heure" }
  - { label: Questions, value: "Environ 57" }
  - { label: Version, value: "Vérifie sur la page officielle la version en vigueur de l'examen et la version de Terraform qu'il couvre" }
  - { label: Validité, value: "2 ans" }
domains:
  - name: Comprendre l'infrastructure as code et le rôle de Terraform
    fiches: [terraform/01-le-workflow]
  - name: Le workflow (init, validate, plan, apply, destroy, fmt)
    fiches: [terraform/01-le-workflow, terraform/08-tester-et-valider]
  - name: Configuration (providers, variables, outputs, expressions, fonctions)
    fiches: [terraform/03-variables-outputs-locals, terraform/05-count-for-each-expressions, terraform/03-data-sources-et-fonctions]
  - name: Les modules (sources, versions, entrées et sorties)
    fiches: [terraform/04-modules]
  - name: Le state (backends, verrou, dérive)
    fiches: [terraform/02-le-state]
  - name: Hors du workflow de base (import, state, refactoring, journaux)
    fiches: [terraform/07-import-et-refactoring]
  - name: Travailler en équipe et HCP Terraform
    fiches: [terraform/06-environnements-et-equipe, terraform/06-hcp-terraform]
---

## Ce que l'examen vérifie vraiment

C'est un QCM court (une heure) sur la **compréhension** de Terraform, pas sur un cloud en particulier. Les questions portent sur ce que fait chaque commande, ce que contient le state, comment les versions sont contraintes, ce qu'apporte HCP Terraform. HashiCorp ne publie pas le poids de chaque domaine : il faut les couvrir tous. Pour un DevOps qui utilise Terraform au quotidien, c'est la certification la plus accessible de ta liste.

## Les pièges

- **Les commandes proches.** `terraform plan -refresh-only` contre `terraform refresh` (ancienne commande), `state rm` contre `destroy`, `taint` (ancien) contre `apply -replace`. Les questions aiment ces nuances.
- **Les contraintes de version.** `~> 1.2` et `~> 1.2.0` n'acceptent pas les mêmes versions (fiche « Le workflow »).
- **Ce qui va dans le state.** Les valeurs sensibles y sont **en clair**, même marquées `sensitive` : `sensitive` ne fait que les masquer à l'affichage.
- **HCP Terraform.** C'est la partie qu'on pratique le moins si on utilise un backend S3 : workspaces, exécutions à distance, registre privé, politiques. Lis la documentation officielle dessus.

## À connaître par cœur

| Question | Réponse |
| --- | --- |
| Qu'écrit `terraform init` ? | le dossier `.terraform` et le fichier de verrou `.terraform.lock.hcl` |
| Où se déclare le backend ? | dans le bloc `terraform { backend "…" {} }`, sans variables |
| Ordre de priorité des variables | défaut < variables d'environnement `TF_VAR_…` < `terraform.tfvars` < `*.auto.tfvars` < `-var-file` et `-var` (le dernier donné gagne) |
| Forcer le remplacement d'une ressource | `terraform apply -replace=ADRESSE` |
| Renommer sans recréer | un bloc `moved` |
| Reprendre une ressource existante | un bloc `import` (ou `terraform import`) |
| Déboguer | `TF_LOG=DEBUG terraform plan` |

## Stratégie le jour J

Une heure pour une soixantaine de questions, soit un peu moins d'une minute chacune. Réponds d'abord à ce qui est évident, marque le reste, et garde 10 minutes pour la relecture. La documentation officielle propose un guide d'étude et des questions d'exemple : fais-les en dernier pour repérer tes trous.
