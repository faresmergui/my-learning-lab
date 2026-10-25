---
title: Le workflow Terraform
chapter: 1
order: 1
duration: 9
level: intermédiaire
tags:
- Terraform Associate
cards:
- q: Que fait `terraform init` ?
  a: 'Il prépare le dossier : télécharge les **providers** et les **modules**, configure le **backend** du state, et crée ou lit `.terraform.lock.hcl`.'
- q: Pourquoi enregistrer le plan avec `terraform plan -out=tfplan` ?
  a: Pour que `terraform apply tfplan` applique **exactement** ce qui a été relu. Sans fichier de plan, `apply` recalcule tout, et le résultat peut avoir changé entre-temps.
- q: Faut-il commiter `.terraform.lock.hcl` ?
  a: '**Oui.** Il fige les versions exactes des providers et leurs empreintes, pour que toute l''équipe et la CI utilisent les mêmes. Le dossier `.terraform/`, lui, ne se commite pas.'
- q: Que signifient les symboles `+`, `-`, `~` et `-/+` dans un plan ?
  a: '`+` création, `-` destruction, `~` modification sur place, `-/+` **remplacement** (destruction puis recréation). Le dernier mérite toujours un second regard.'
- q: Différence entre `terraform fmt` et `terraform validate` ?
  a: '`fmt` **formate** le code selon le style officiel. `validate` vérifie la **syntaxe et la cohérence** (types, références), sans contacter le cloud.'
- q: Que signifie `# forces replacement` dans un plan ?
  a: 'L''attribut ne peut pas changer sur place : la ressource sera **détruite puis recréée**.'
- q: '`~> 6.2.0` accepte quelles versions ?'
  a: Seulement **6.2.x**.
- q: À quoi sert `create_before_destroy` ?
  a: Créer la **nouvelle** ressource avant de détruire l'ancienne, pour éviter une coupure.
quiz:
- q: Le plan affiche `-/+` sur ta base RDS de prod. Que faire ?
  options:
  - Appliquer, Terraform sait ce qu'il fait
  - S'arrêter et chercher quel attribut force le remplacement (`# forces replacement`)
  - Lancer `terraform refresh`
  - Supprimer le state
  answer: 1
  explain: Certains attributs ne peuvent pas être modifiés sur place. Le plan l'indique avec `# forces replacement`. Sur une base, un remplacement veut dire une perte de données.
- q: Comment obtenir une version plus récente d'un provider en respectant les contraintes `version` ?
  options:
  - terraform init -upgrade
  - terraform apply -upgrade
  - Supprimer `.terraform.lock.hcl` à la main
  - terraform get
  answer: 0
  explain: '`-upgrade` choisit la version la plus récente autorisée par les contraintes et met à jour le lock file, que tu commites ensuite.'
---

**Terraform** est un outil d'**infrastructure as code** (IaC) créé par HashiCorp : tu décris dans des fichiers texte l'infrastructure que tu veux (réseaux, machines virtuelles, bases de données, DNS…), et Terraform la crée, la modifie ou la supprime pour qu'elle corresponde à ta description. Il ne parle pas directement aux clouds : il passe par des **providers**, des plugins qui traduisent ton code en appels à l'API d'AWS, d'OpenStack, de Cloudflare, etc. Le langage des fichiers s'appelle **HCL** (HashiCorp Configuration Language), et les fichiers finissent par `.tf`. **OpenTofu** est un fork libre de Terraform, compatible, né en 2023 après un changement de licence.

Terraform suit toujours le même cycle : **écrire**, **planifier**, **appliquer**.

<!-- schema:cycle -->
<figure class="diagram"><svg viewBox="0 0 680 220" role="img" aria-label="Le cycle de travail Terraform" style="--minw:560px"><defs><marker id="g7-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g7-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g7-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g7-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="60" width="118" height="70" rx="9"/></g><text x="73.0" y="92.0" class="dg-t" text-anchor="middle" style="--d:0">code .tf</text><text x="73.0" y="110.0" class="dg-s" text-anchor="middle" style="--d:0">tu écris</text><g class="dg-box dg-pop" style="--d:1"><rect x="148" y="60" width="118" height="70" rx="9"/></g><text x="207.0" y="85.0" class="dg-t" text-anchor="middle" style="--d:1">init</text><text x="207.0" y="103.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="207.0" dy="0">providers, modules,</tspan><tspan x="207.0" dy="14">backend</tspan></text><path d="M132 95 L146 95" class="dg-l c" marker-end="url(#g7-c)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="282" y="60" width="118" height="70" rx="9"/></g><text x="341.0" y="85.0" class="dg-t" text-anchor="middle" style="--d:2">plan</text><text x="341.0" y="103.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="341.0" dy="0">diff code / state /</tspan><tspan x="341.0" dy="14">réalité</tspan></text><path d="M266 95 L280 95" class="dg-l c" marker-end="url(#g7-c)"/><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="416" y="60" width="118" height="70" rx="9"/></g><text x="475.0" y="92.0" class="dg-t" text-anchor="middle" style="--d:3">relecture</text><text x="475.0" y="110.0" class="dg-s" text-anchor="middle" style="--d:3">surtout les -/+</text><path d="M400 95 L414 95" class="dg-l c" marker-end="url(#g7-c)"/><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="550" y="60" width="118" height="70" rx="9"/></g><text x="609.0" y="85.0" class="dg-t" text-anchor="middle" style="--d:4">apply</text><text x="609.0" y="103.0" class="dg-s" text-anchor="middle" style="--d:4"><tspan x="609.0" dy="0">applique le plan,</tspan><tspan x="609.0" dy="14">met à jour le state</tspan></text><path d="M534 95 L548 95" class="dg-l c" marker-end="url(#g7-c)"/><path d="M550 132 C 520 200, 120 200, 73 132" class="dg-l dash" marker-end="url(#g7-n)"/><text x="310" y="196" class="dg-s" text-anchor="middle">chaque changement repart du code</text><text x="240" y="40" class="dg-s" text-anchor="middle">terraform plan -out=tfplan</text><text x="560" y="40" class="dg-s" text-anchor="middle">terraform apply tfplan</text></svg><figcaption>Le plan enregistré est exactement ce qui sera appliqué.</figcaption></figure>
<!-- /schema:cycle -->


> **Les termes et outils cités dans cette fiche.**
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.
> - **déclaratif** : on décrit l'état voulu et l'outil se charge d'y arriver (par opposition à une liste de commandes).
> - **bucket** : un conteneur de fichiers dans un stockage objet (S3, Swift).
> - **idempotent** : qui donne le même résultat qu'on l'exécute une ou dix fois.
> - **AMI** : l'image de disque à partir de laquelle on démarre une instance EC2.

## Un premier projet

```hcl
terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"     # 6.x, mais pas 7.0
    }
  }
}

provider "aws" {
  region = "eu-west-3"
  default_tags {
    tags = { owner = "fares", managed-by = "terraform" }
  }
}

resource "aws_s3_bucket" "logs" {
  bucket = "fares-logs-prod"
}
```

## Les commandes

```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
terraform destroy          # avec prudence
```

| Symbole | Action |
| --- | --- |
| `+` | création |
| `~` | modification sur place |
| `-/+` | remplacement (destruction puis recréation) |
| `-` | destruction |

## Ce que fait vraiment chaque commande

- **`init`** télécharge les providers et les modules, configure le backend, et écrit `.terraform.lock.hcl`, qui fige les versions exactes des providers. Ce fichier se **commite**.
- **`validate`** vérifie la syntaxe et la cohérence interne, sans appeler le cloud.
- **`plan`** lit le state, interroge le cloud (refresh) et calcule la différence entre le code et la réalité.
- **`apply`** exécute le plan, puis met à jour le state.

## Déclaratif, pas impératif

Tu ne décris pas des **actions** (« crée un bucket »), tu décris un **état** (« il existe un bucket nommé fares-logs-prod »). Terraform calcule lui-même les actions. Conséquences :

- Relancer `apply` sans changement ne fait **rien** : c'est l'idempotence.
- Supprimer un bloc du code signifie « cette ressource ne doit plus exister » : Terraform la **détruit**.
- L'ordre des blocs dans les fichiers ne compte pas : Terraform construit un **graphe de dépendances** à partir des références (`aws_s3_bucket.logs.arn`).

## Pourquoi un remplacement ?

Certains attributs ne peuvent pas être modifiés sur place par l'API : changer le nom d'un bucket, la zone d'un disque, l'AMI d'une instance. Terraform propose alors `-/+` : **détruire puis recréer**. Le plan l'indique avec `# forces replacement`. C'est la ligne à chercher en priorité dans un plan.

Pour éviter un trou de service, `lifecycle { create_before_destroy = true }` crée la nouvelle ressource avant de détruire l'ancienne. Pour les ressources critiques, `prevent_destroy = true` bloque toute destruction.

## Les contraintes de version

| Écriture | Accepte |
| --- | --- |
| `= 6.2.0` | exactement 6.2.0 |
| `~> 6.2` | 6.2 et plus, mais pas 7.0 |
| `~> 6.2.0` | 6.2.x seulement |
| `>= 6.0, < 7.0` | même chose que `~> 6.0` |

> **Piège classique.** `terraform apply -auto-approve` en local « pour aller vite ». Le plan est ta seule chance de voir un remplacement ou une destruction avant qu'il ne soit trop tard.

> **À retenir.** Tu décris un état, Terraform calcule les actions. Le cycle est toujours `init`, `plan`, `apply`, et le plan est le moment où tu repères un `-/+` (remplacement) ou un `-` (destruction). Fige les versions des providers et commite `.terraform.lock.hcl`.
