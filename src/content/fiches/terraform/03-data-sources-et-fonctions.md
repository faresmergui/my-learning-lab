---
title: Data sources, fonctions et valeurs sensibles
chapter: 3
order: 2
duration: 11
tags:
- Terraform Associate
- data
- fonctions
cards:
- q: Différence entre un bloc `resource` et un bloc `data` ?
  a: Un `resource` **crée et gère** un objet. Un `data` **lit** un objet qui existe déjà (créé ailleurs, à la main ou par un autre projet) sans jamais le modifier. On y accède avec `data.<type>.<nom>.<attribut>`.
- q: Quand une data source est-elle lue ?
  a: Pendant le **plan** en général. Si ses arguments dépendent d'une ressource pas encore créée, sa lecture est reportée à l'apply et ses valeurs s'affichent `(known after apply)`.
- q: Comment essayer une fonction Terraform sans rien déployer ?
  a: '`terraform console` : on tape `upper("shop")` ou `cidrsubnet("10.0.0.0/16", 8, 2)` et on voit le résultat, avec accès aux variables et au state du projet.'
- q: Que renvoie `cidrsubnet("10.0.0.0/16", 8, 2)` ?
  a: '`10.0.2.0/24` : on ajoute 8 bits au masque (/16 vers /24) et on prend le sous-réseau numéro 2.'
- q: Différence entre `lookup(map, cle, defaut)` et `try(expr, defaut)` ?
  a: '`lookup` lit une clé dans une map avec une valeur de repli. `try` évalue une expression et renvoie la première qui ne produit **pas d''erreur** : utile pour des attributs facultatifs dans des objets imbriqués.'
- q: Une valeur `sensitive` est-elle protégée dans le state ?
  a: '**Non.** `sensitive` la masque seulement dans le plan et les sorties. Elle reste en clair dans le state, qu''il faut donc chiffrer et protéger. Les attributs **éphémères** et `write-only` (Terraform 1.10 et plus) évitent, eux, de l''y écrire.'
quiz:
- q: Tu dois créer une instance dans un VPC créé par une autre équipe. Comment récupérer son ID ?
  options:
  - L'écrire en dur
  - Un bloc `data "aws_vpc"` filtré par ses tags
  - Un bloc `resource "aws_vpc"` avec le même nom
  - '`terraform import` du VPC dans ton projet'
  answer: 1
  explain: La data source lit le VPC sans le gérer. L'importer le ferait gérer par deux projets, qui se battraient pour lui.
- q: Quelle fonction fusionne deux maps de tags, la seconde l'emportant ?
  options:
  - '`concat`'
  - '`merge`'
  - '`flatten`'
  - '`zipmap`'
  answer: 1
  explain: '`merge(local.tags_communs, var.tags)` : en cas de clé commune, la dernière map gagne. `concat` sert aux listes.'
- q: Une variable `sensitive` est utilisée dans un output non marqué `sensitive`. Que se passe-t-il ?
  options:
  - La valeur s'affiche
  - Terraform refuse le plan avec une erreur
  - L'output est vide
  - Rien de spécial
  answer: 1
  explain: 'Terraform protège contre les fuites : il faut marquer l''output `sensitive = true` (ou utiliser `nonsensitive()` en connaissance de cause).'
level: intermédiaire
---

La fiche précédente présentait les entrées (variables), les valeurs calculées (locals) et les sorties (outputs). L'examen Terraform Associate demande trois notions de plus : **lire** ce qui existe déjà avec les data sources, **transformer** des valeurs avec les fonctions intégrées, et bien comprendre ce que protège, ou non, une valeur sensible.

> **Les outils cités dans cette fiche.**
> - **data source** (bloc `data`) : une lecture, faite par le provider, d'un objet qui existe déjà (un VPC, une image, un secret, une zone DNS).
> - **fonctions intégrées** : des fonctions fournies par Terraform (`merge`, `lookup`, `cidrsubnet`…). On ne peut pas en écrire soi-même, mais certains providers en ajoutent.
> - **terraform console** : une invite interactive pour essayer des expressions et des fonctions.
> - **AMI** (Amazon Machine Image) : l'image disque à partir de laquelle AWS démarre une instance.
> - **valeur éphémère** : une valeur que Terraform utilise pendant l'exécution sans jamais l'écrire dans le plan ni dans le state.
> - **IAM** : la gestion des identités et des droits (qui peut faire quoi).
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.

## Comprendre : gérer ou lire

| | `resource` | `data` |
| --- | --- | --- |
| rôle | créer, modifier, supprimer | lire seulement |
| apparaît dans le plan | `+`, `~`, `-` | seulement si la lecture est reportée |
| `terraform destroy` | supprime l'objet | ne touche à rien |
| référence | `aws_vpc.main.id` | `data.aws_vpc.main.id` |

Une règle simple : un objet est **géré par un seul projet**. Tous les autres le lisent avec une data source.

## Les data sources en pratique

```hcl
# La dernière image Ubuntu publiée par Canonical
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

# Un VPC créé par l'équipe réseau
data "aws_vpc" "main" {
  tags = { Name = "prod-main" }
}

# Ses sous-réseaux privés
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
  tags = { Tier = "private" }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.small"
  subnet_id     = data.aws_subnets.private.ids[0]
}
```

Si la data source ne trouve rien (ou trouve plusieurs objets quand elle en attend un), le plan **échoue** : c'est une protection, pas un bug.

## Les fonctions à connaître

| Famille | Fonctions | Exemple |
| --- | --- | --- |
| texte | `upper`, `lower`, `format`, `replace`, `join`, `split` | `format("%s-%s", var.env, "web")` donne `prod-web` |
| listes | `length`, `concat`, `flatten`, `distinct`, `contains`, `element` | `concat(var.a, var.b)` |
| maps | `merge`, `lookup`, `keys`, `values`, `zipmap` | `merge(local.tags, { Role = "web" })` |
| réseau | `cidrsubnet`, `cidrhost` | `cidrsubnet("10.0.0.0/16", 8, 2)` donne `10.0.2.0/24` |
| fichiers | `file`, `templatefile`, `filebase64` | `templatefile("init.sh.tftpl", { port = 8080 })` |
| encodage | `jsonencode`, `yamldecode`, `base64encode` | une politique IAM en `jsonencode({...})` |
| contrôle | `try`, `can`, `coalesce`, `one` | `try(var.config.port, 8080)` |
| types | `tostring`, `tonumber`, `toset`, `tomap` | `toset(var.noms)` pour un `for_each` |

```bash
terraform console
> cidrsubnet("10.0.0.0/16", 8, 2)
"10.0.2.0/24"
> merge({a = 1}, {a = 2, b = 3})
{ "a" = 2, "b" = 3 }
> exit
```

`templatefile` est la plus utile au quotidien : elle remplace les variables d'un fichier modèle (`${port}`) pour produire un script d'initialisation ou un fichier de configuration.

## Les valeurs sensibles

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}

output "connexion" {
  value     = "postgres://app:${var.db_password}@${aws_db_instance.main.address}/shop"
  sensitive = true      # obligatoire : l'output contient une valeur sensible
}
```

Ce que fait `sensitive` :

- la valeur est remplacée par `(sensitive value)` dans le plan et les sorties ;
- la marque **se propage** : toute expression qui l'utilise devient sensible, et un output non marqué provoque une erreur ;
- la valeur reste lisible avec `terraform output -raw connexion` ou `terraform output -json`.

Ce qu'il **ne fait pas** : chiffrer. La valeur est en clair dans le state. D'où les vraies protections :

1. un backend chiffré, avec un accès limité aux personnes et à la CI qui en ont besoin ;
2. ne pas faire transiter le secret par Terraform du tout : le laisser au gestionnaire de secrets (Vault, AWS Secrets Manager) et ne passer que sa **référence** ;
3. depuis Terraform 1.10 et 1.11, les variables `ephemeral = true` et les arguments **write-only** de certains providers (par exemple `password_wo`), que Terraform transmet sans jamais les écrire dans le state.

> **À retenir.** `resource` gère, `data` lit ce qui existe déjà ; chaque objet n'est géré que par un projet. Les fonctions s'essaient dans `terraform console` ; retiens `merge`, `lookup`, `try`, `cidrsubnet`, `templatefile`, `jsonencode`. `sensitive` masque l'affichage mais la valeur reste en clair dans le state.
