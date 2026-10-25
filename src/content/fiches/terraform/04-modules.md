---
title: Écrire et utiliser des modules
chapter: 4
order: 1
duration: 9
level: intermédiaire
tags:
- Terraform Associate
cards:
- q: Qu'est-ce qu'un module Terraform ?
  a: Un **dossier de fichiers `.tf`**. Le dossier où tu lances Terraform est le module racine. Il peut appeler d'autres modules avec un bloc `module`.
- q: Comment un module communique-t-il avec celui qui l'appelle ?
  a: Il reçoit des **variables** en entrée et expose des **outputs**. L'appelant lit `module.<nom>.<output>`.
- q: Pourquoi épingler la version d'un module ?
  a: Pour qu'une nouvelle version publiée ne change pas ton infra sans prévenir. `version = "~> 5.1"` pour le registre, `?ref=v1.2.0` pour une source Git.
- q: Quelle structure de fichiers pour un module ?
  a: '`main.tf` (ressources), `variables.tf` (entrées), `outputs.tf` (sorties), `versions.tf` (contraintes de version), et un `README.md`.'
- q: Un module doit-il déclarer un bloc `provider` ?
  a: Non. Un module réutilisable déclare seulement `required_providers`. La configuration du provider (région, identifiants) vient du module racine.
quiz:
- q: Tu ajoutes un module dans ton code. Quelle commande faut-il relancer avant le plan ?
  options:
  - terraform init (ou terraform get)
  - terraform validate
  - terraform refresh
  - Aucune
  answer: 0
  explain: Terraform doit télécharger ou lier le nouveau module. Sans `init`, le plan échoue avec `Module not installed`.
- q: Quand vaut-il mieux **ne pas** créer de module ?
  options:
  - Quand le même ensemble de ressources est utilisé à plusieurs endroits
  - Pour envelopper une seule ressource sans rien ajouter
  - Pour imposer des bonnes pratiques à l'équipe
  - Pour un réseau complet (VPC, sous-réseaux, NAT)
  answer: 1
  explain: Un module qui se contente de recopier les paramètres d'une ressource ajoute une couche sans valeur. Un bon module regroupe et impose des choix.
---

Un module regroupe des ressources qui vont ensemble et les expose avec une interface simple.

<!-- schema:modules -->
<figure class="diagram"><svg viewBox="0 0 680 240" role="img" aria-label="Des modules qui se passent des valeurs" style="--minw:560px"><defs><marker id="g10-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g10-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g10-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g10-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="652" height="212" rx="12" class="dg-zone dg-zc"/><text x="26" y="32" class="dg-zl" text-anchor="start">module racine : envs/prod</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="30" y="70" width="170" height="90" rx="9"/></g><text x="115.0" y="105.0" class="dg-t" text-anchor="middle" style="--d:0">module &quot;network&quot;</text><text x="115.0" y="123.0" class="dg-s" text-anchor="middle" style="--d:0"><tspan x="115.0" dy="0">in : cidr</tspan><tspan x="115.0" dy="14">out : subnet_ids</tspan></text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="330" y="70" width="160" height="90" rx="9"/></g><text x="410.0" y="105.0" class="dg-t" text-anchor="middle" style="--d:1">module &quot;eks&quot;</text><text x="410.0" y="123.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="410.0" dy="0">in : subnet_ids</tspan><tspan x="410.0" dy="14">out : endpoint</tspan></text><g class="dg-box dg-pop" style="--d:2"><rect x="530" y="84" width="116" height="62" rx="9"/></g><text x="588.0" y="112.0" class="dg-t" text-anchor="middle" style="--d:2">output</text><text x="588.0" y="130.0" class="dg-s" text-anchor="middle" style="--d:2">cluster_endpoint</text><path d="M200 115 L328 115" class="dg-l c flow" marker-end="url(#g10-c)"/><text x="264" y="100" class="dg-s" text-anchor="middle">module.network</text><text x="264" y="140" class="dg-s" text-anchor="middle">.subnet_ids</text><path d="M490 115 L528 115" class="dg-l" marker-end="url(#g10-n)"/><text x="115" y="190" class="dg-s" text-anchor="middle">source = &quot;../../modules/network&quot;</text><text x="410" y="190" class="dg-s" text-anchor="middle">source = &quot;terraform-aws-modules/eks/aws&quot;</text></svg><figcaption>Un module ne voit que ses variables. Les modules communiquent par leurs outputs.</figcaption></figure>
<!-- /schema:modules -->


> **Les termes et outils cités dans cette fiche.**
> - **VPC** : un réseau privé virtuel dans le cloud, isolé des autres clients.
> - **branche** : une ligne de développement parallèle dans Git.
> - **bucket** : un conteneur de fichiers dans un stockage objet (S3, Swift).
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **EKS** : le service Kubernetes managé d'AWS.
> - **RDS** : le service de bases de données relationnelles gérées d'AWS.

## Appeler un module

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name            = "shop-prod"
  cidr            = "10.10.0.0/16"
  azs             = ["eu-west-3a", "eu-west-3b", "eu-west-3c"]
  private_subnets = ["10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]
  public_subnets  = ["10.10.101.0/24", "10.10.102.0/24", "10.10.103.0/24"]
  enable_nat_gateway = true
}

resource "aws_eks_cluster" "main" {
  # …
  vpc_config { subnet_ids = module.vpc.private_subnets }
}
```

## Les sources possibles

| Source | Exemple |
| --- | --- |
| Dossier local | `source = "./modules/bucket"` |
| Registre Terraform | `source = "terraform-aws-modules/vpc/aws"` + `version` |
| Git | `source = "git::https://gitlab.com/fares/tf-modules.git//bucket?ref=v1.2.0"` |

## Écrire le sien

```
modules/bucket/
├── main.tf        # aws_s3_bucket, chiffrement, blocage de l'accès public
├── variables.tf   # name, versioning, tags
├── outputs.tf     # arn, id
└── versions.tf    # required_providers
```

## Comprendre : un module, c'est une fonction

Tout dossier contenant des fichiers `.tf` est un module. Celui où tu lances `terraform apply` est le **module racine**. Quand il appelle un autre dossier avec un bloc `module`, il l'utilise comme une **fonction** :

| Fonction | Module Terraform |
| --- | --- |
| paramètres | `variable` (dans `variables.tf`) |
| corps | les `resource` et `data` (dans `main.tf`) |
| valeur de retour | `output` (dans `outputs.tf`) |
| appel | `module "nom" { source = …, param = … }` |

Le module appelant ne voit **que** les outputs. Pour lire un attribut d'une ressource interne au module, il faut que le module l'expose : `module.vpc.private_subnets` existe parce que le module VPC déclare `output "private_subnets"`.

Les ressources créées par un module ont une adresse préfixée dans le state : `module.vpc.aws_subnet.private[0]`. C'est pourquoi déplacer une ressource dans un module demande un bloc `moved` (fiche sur l'import et le refactoring).

## Pourquoi épingler la version

`version = "~> 6.0"` accepte `6.1`, `6.9`, mais pas `7.0`. Sans contrainte, un `terraform init -upgrade` peut récupérer une version majeure qui renomme des ressources ou change des valeurs par défaut, et ton prochain plan proposera de recréer la moitié du réseau. Pour un module Git, le `?ref=v1.2.0` joue le même rôle : jamais de `ref` sur une branche qui bouge.

## Quand créer un module

- **oui** : un motif qui se répète avec des règles à imposer (un bucket toujours chiffré et privé, un service toujours avec ses alarmes) ;
- **oui** : un bloc cohérent réutilisé par plusieurs environnements (`modules/app` appelé par `envs/dev` et `envs/prod`) ;
- **non** : envelopper une seule ressource en recopiant tous ses paramètres. On ajoute une couche à comprendre sans rien gagner ;
- **non** : des modules qui appellent des modules qui appellent des modules. Au-delà de deux niveaux, plus personne ne sait ce qu'un changement va toucher.

Pour les briques classiques (VPC, EKS, RDS), les modules communautaires `terraform-aws-modules` sont éprouvés : les lire est aussi un excellent moyen d'apprendre.

> **À retenir.** Un bon module impose des choix : chiffrement activé, accès public bloqué, tags obligatoires. S'il se contente de reprendre tous les paramètres de la ressource, il ne sert à rien.
