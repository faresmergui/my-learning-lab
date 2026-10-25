---
title: Le state et son verrouillage
chapter: 2
order: 1
duration: 9
level: intermédiaire
tags:
- Terraform Associate
cards:
- q: À quoi sert le fichier de state ?
  a: Il fait le lien entre les ressources de ton code et les objets réels (leurs IDs), garde leurs attributs connus et l'ordre des dépendances. Sans lui, Terraform ne sait pas ce qu'il gère.
- q: À quoi sert `terraform state mv`, et quelle est l'alternative moderne ?
  a: À renommer ou déplacer une ressource dans le state (par exemple vers un module) **sans la recréer**. Depuis Terraform 1.1, on préfère un bloc `moved` dans le code, qui est versionné et relu en revue.
- q: Pourquoi le state ne doit-il jamais être commité dans Git ?
  a: Il contient les valeurs en **clair**, y compris les champs marqués `sensitive` (mots de passe, clés). Il doit vivre dans un backend distant chiffré, avec accès restreint.
- q: À quoi sert le state Terraform ?
  a: Faire le lien **bloc de code ↔ ressource réelle** (ex. `aws_vpc.main` ↔ `vpc-0a1b…`), garder les attributs et accélérer le plan.
- q: Qu'est-ce que la dérive (drift) ?
  a: La réalité ne correspond plus au state, souvent après un **changement manuel**. `plan -refresh-only` la montre.
- q: Pourquoi activer le versioning du bucket de state ?
  a: Pour pouvoir **revenir** à une version précédente si le state est corrompu ou abîmé.
quiz:
- q: Deux personnes lancent `terraform apply` en même temps sur un backend S3. Qu'est-ce qui évite la corruption du state ?
  options:
  - Le versioning du bucket
  - Le verrouillage du state (lockfile S3 natif ou table DynamoDB)
  - Le fichier .terraform.lock.hcl
  - Rien, il faut se coordonner
  answer: 1
  explain: Le verrou bloque le second apply. Attention, `.terraform.lock.hcl` verrouille les **versions des providers**, pas le state.
- q: Une ressource a été créée à la main dans la console AWS. Comment la faire gérer par Terraform sans la recréer ?
  options:
  - '`terraform refresh`'
  - Un bloc `import` (ou `terraform import`), puis aligner le code
  - '`terraform state mv`'
  - '`terraform apply -replace`'
  answer: 1
  explain: Depuis Terraform 1.5, le bloc `import` permet même de générer le code avec `terraform plan -generate-config-out=generated.tf`.
---

Le **state** (état) est un fichier JSON, `terraform.tfstate`, dans lequel Terraform note tout ce qu'il a créé : l'identifiant réel de chaque ressource chez le provider et ses attributs. C'est sa mémoire : sans lui, Terraform ne saurait pas que la machine `web` de ton code correspond à l'instance `i-0a12…` chez AWS. Un **backend** est l'endroit où ce fichier est stocké : en local par défaut, ou à distance (un bucket S3, GitLab, Terraform Cloud) pour qu'une équipe le partage.

Terraform compare trois choses à chaque `plan` : ton **code**, le **state** (ce qu'il croit avoir créé) et la **réalité** (ce que répond l'API du provider).

<!-- schema:triangle -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Code, state et réalité" style="--minw:560px"><defs><marker id="g8-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g8-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g8-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g8-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="20" y="30" width="170" height="64" rx="9"/></g><text x="105.0" y="59.0" class="dg-t" text-anchor="middle" style="--d:0">code .tf</text><text x="105.0" y="77.0" class="dg-s" text-anchor="middle" style="--d:0">ce que tu veux</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="255" y="160" width="170" height="64" rx="9"/></g><text x="340.0" y="182.0" class="dg-t" text-anchor="middle" style="--d:1">state</text><text x="340.0" y="200.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="340.0" dy="0">ce que Terraform</tspan><tspan x="340.0" dy="14">pense gérer</tspan></text><g class="dg-box dg-pop" style="--d:2"><rect x="490" y="30" width="170" height="64" rx="9"/></g><text x="575.0" y="59.0" class="dg-t" text-anchor="middle" style="--d:2">infra réelle</text><text x="575.0" y="77.0" class="dg-s" text-anchor="middle" style="--d:2">ce qui existe</text><path d="M190 62 L488 62" class="dg-l dash" marker-end="url(#g8-n)"/><text x="339.0" y="54.0" class="dg-s" text-anchor="middle">plan compare les trois</text><path d="M105 94 L105 192 L253 192" class="dg-l c" marker-end="url(#g8-c)" marker-start="url(#g8-c)"/><path d="M575 94 L575 192 L427 192" class="dg-l" marker-end="url(#g8-n)" marker-start="url(#g8-n)"/><text x="575.0" y="135.0" class="dg-s" text-anchor="middle">refresh</text><text x="340" y="150" class="dg-s" text-anchor="middle">S3 chiffré + verrou</text><text x="340" y="244" class="dg-at" text-anchor="middle">un seul apply à la fois grâce au verrou</text></svg><figcaption>Le state fait le lien entre tes blocs resource et les vrais identifiants dans le cloud.</figcaption></figure>
<!-- /schema:triangle -->


> **Les termes et outils cités dans cette fiche.**
> - **JSON** : un format texte de données en paires « clé : valeur », lisible par les humains et les programmes.
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.
> - **bucket** : un conteneur de fichiers dans un stockage objet (S3, Swift).
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **IAM** : la gestion des identités et des droits (qui peut faire quoi).
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.

## Un backend distant avec verrou

```hcl
terraform {
  backend "s3" {
    bucket       = "fares-tfstate"
    key          = "prod/network.tfstate"
    region       = "eu-west-3"
    encrypt      = true
    use_lockfile = true # verrou natif S3, Terraform 1.10+
  }
}
```

## Les commandes à connaître

```bash
terraform state list                 # ce que Terraform gère
terraform state show aws_vpc.main    # le détail d'une ressource
terraform state rm aws_s3_bucket.old # oublier sans détruire
```

## Refactorer sans rien casser

```hcl
moved {
  from = aws_instance.web
  to   = module.web.aws_instance.this
}
```

## Pourquoi un state ?

L'API d'un cloud ne sait pas quelle ressource correspond à quel bloc de ton code. Le state fait ce lien : `aws_vpc.main` ↔ `vpc-0a1b2c3d`. Il garde aussi les attributs connus (IP, ARN) pour calculer les dépendances, et il rend le `plan` rapide en évitant de tout redécouvrir.

## Local ou distant ?

| State local (`terraform.tfstate`) | State distant (backend) |
| --- | --- |
| Sur ton poste, perdu si le disque l'est | Stocké de façon durable (S3, GCS, Terraform Cloud) |
| Pas de verrou : deux `apply` en même temps le corrompent | Verrou pendant `plan` et `apply` |
| Contient les secrets en clair sur ton disque | Chiffré au repos, accès contrôlé par IAM |

Dès qu'on est deux, ou qu'une CI applique, le backend distant est indispensable. Active aussi le **versioning** du bucket : c'est ton retour arrière si le state est abîmé.

## La dérive

La **dérive** (drift), c'est quand la réalité ne correspond plus au state : quelqu'un a modifié une ressource dans la console. Le `plan` la détecte et propose de **revenir au code**.

```bash
terraform plan -refresh-only      # montre la dérive sans rien proposer d'autre
terraform apply -refresh-only     # accepte la réalité dans le state
```

Si le changement manuel doit rester, il faut le reporter **dans le code**, sinon le prochain `apply` l'annulera.

## Un state par périmètre

Un seul state géant rend chaque `plan` lent et chaque erreur dangereuse. On découpe par **périmètre et environnement** (réseau, base de données, applications, × dev/prod), et on lit les sorties d'un autre state avec `terraform_remote_state` ou, mieux, des data sources.

## Verrou bloqué

Si un `apply` est interrompu, le verrou peut rester. Avant `terraform force-unlock <ID>`, vérifie que personne d'autre n'est vraiment en train d'appliquer.

> **Piège classique.** Renommer une ressource dans le code sans bloc `moved` : Terraform propose de **détruire** l'ancienne et d'en créer une nouvelle. Lis toujours le `plan` avant d'appliquer.

> **À retenir.** Le state relie chaque bloc du code à un objet réel. En équipe, il vit dans un backend distant, chiffré, versionné et verrouillé. Découpe-le par périmètre et environnement, et traite toute dérive en la reportant dans le code ou en laissant le code l'annuler.
