---
title: count, for_each et expressions
chapter: 5
order: 1
duration: 10
level: intermédiaire
tags:
- Terraform Associate
cards:
- q: Pourquoi préférer `for_each` à `count` pour une liste de ressources ?
  a: Avec `count`, les ressources sont indexées par **position** (`[0]`, `[1]`). Retirer un élément du milieu décale les suivants, qui sont détruits et recréés. `for_each` les indexe par **clé**, stable.
- q: Sur quoi peut-on faire un `for_each` ?
  a: 'Sur une **map** ou un **set de chaînes**. Pour une liste, on la convertit : `for_each = toset(var.names)`.'
- q: Comment faire une ressource conditionnelle ?
  a: '`count = var.enable_monitoring ? 1 : 0`, puis on la référence avec `aws_x.this[0]` (ou `one(aws_x.this[*].id)`).'
- q: À quoi sert un bloc `dynamic` ?
  a: À générer des **blocs imbriqués** répétés (par exemple plusieurs `ingress` dans un security group) à partir d'une collection.
- q: 'Que donne `[for s in var.services : s.name if s.public]` ?'
  a: 'La **liste des noms** des services dont `public` est vrai. Avec `{ for … : clé => valeur }`, on obtient une map.'
quiz:
- q: Tu as 3 buckets créés avec `count` à partir de `["a", "b", "c"]`. Tu retires `"b"`. Que prévoit le plan ?
  options:
  - Supprimer seulement le bucket b
  - Supprimer b et c, puis recréer c à l'index 1
  - Ne rien faire
  - Une erreur
  answer: 1
  explain: L'index 1 passe de b à c, l'index 2 disparaît. Avec `for_each = toset(...)`, seul `b` serait supprimé.
- q: 'Pourquoi `for_each = toset([for i in aws_instance.web : i.id])` peut-il échouer au premier plan ?'
  options:
  - Les sets n'acceptent pas les ID
  - Les clés de for_each doivent être connues au moment du plan, et ces ID n'existent pas encore
  - for_each ne marche pas avec les instances
  - Il faut un count
  answer: 1
  explain: Utilise des clés connues à l'avance (noms, clés de map de tes variables) et mets les valeurs inconnues dans les attributs.
---

Quand il faut créer **plusieurs** ressources semblables (un bucket par équipe, une règle par port), on ne copie pas le bloc : on le fait **boucler**. Terraform offre deux méta-arguments pour ça, `count` (par position) et `for_each` (par clé), et un petit langage d'**expressions** pour transformer listes et maps.


> **Les termes et outils cités dans cette fiche.**
> - **bucket** : un conteneur de fichiers dans un stockage objet (S3, Swift).
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **HCL** : le langage de configuration de Terraform.

## count ou for_each

```hcl
# À éviter pour une liste qui peut changer
resource "aws_s3_bucket" "by_index" {
  count  = length(var.buckets)
  bucket = var.buckets[count.index]
}

# Mieux : chaque bucket est identifié par son nom
resource "aws_s3_bucket" "by_name" {
  for_each = toset(var.buckets)
  bucket   = each.value
}
```

| | `count` | `for_each` |
| --- | --- | --- |
| Adresse | `aws_s3_bucket.x[0]` | `aws_s3_bucket.x["logs"]` |
| Retirer un élément du milieu | décale et recrée les suivants | ne touche que cet élément |
| Usage idéal | ressource conditionnelle (0 ou 1) | collection d'objets |

<!-- schema:count-vs-foreach -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Retirer un élément avec count ou avec for_each" style="--minw:560px"><defs><marker id="g11-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g11-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g11-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g11-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="170" y="24" class="dg-at" text-anchor="middle">avec count : indexé par position</text><text x="510" y="24" class="dg-okt" text-anchor="middle">avec for_each : indexé par clé</text><g class="dg-box dg-pop" style="--d:0"><rect x="30" y="46" width="110" height="46" rx="9"/></g><text x="85.0" y="74.0" class="dg-t" text-anchor="middle" style="--d:0">[0] a</text><g class="dg-box dg-pop" style="--d:1"><rect x="200" y="46" width="110" height="46" rx="9"/></g><text x="255.0" y="74.0" class="dg-t" text-anchor="middle" style="--d:1">[0] a</text><path d="M140 69 L198 69" class="dg-l" marker-end="url(#g11-n)"/><g class="dg-box dg-pop" style="--d:1"><rect x="30" y="108" width="110" height="46" rx="9"/></g><text x="85.0" y="136.0" class="dg-t" text-anchor="middle" style="--d:1">[1] b</text><g class="dg-box dg-a dg-pop" style="--d:2"><rect x="200" y="108" width="110" height="46" rx="9"/></g><text x="255.0" y="136.0" class="dg-t" text-anchor="middle" style="--d:2">[1] c</text><path d="M140 131 L198 131" class="dg-l a" marker-end="url(#g11-a)"/><g class="dg-box dg-pop" style="--d:2"><rect x="30" y="170" width="110" height="46" rx="9"/></g><text x="85.0" y="198.0" class="dg-t" text-anchor="middle" style="--d:2">[2] c</text><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="200" y="170" width="110" height="46" rx="9"/></g><text x="255.0" y="198.0" class="dg-t" text-anchor="middle" style="--d:3">✗ détruit</text><path d="M140 193 L198 193" class="dg-l a" marker-end="url(#g11-a)"/><g class="dg-box dg-pop" style="--d:0"><rect x="370" y="46" width="110" height="46" rx="9"/></g><text x="425.0" y="74.0" class="dg-t" text-anchor="middle" style="--d:0">[&quot;a&quot;]</text><g class="dg-box dg-ok dg-pop" style="--d:1"><rect x="540" y="46" width="110" height="46" rx="9"/></g><text x="595.0" y="74.0" class="dg-t" text-anchor="middle" style="--d:1">[&quot;a&quot;]</text><path d="M480 69 L538 69" class="dg-l ok" marker-end="url(#g11-ok)"/><g class="dg-box dg-pop" style="--d:1"><rect x="370" y="108" width="110" height="46" rx="9"/></g><text x="425.0" y="136.0" class="dg-t" text-anchor="middle" style="--d:1">[&quot;b&quot;]</text><g class="dg-box dg-a dg-pop" style="--d:2"><rect x="540" y="108" width="110" height="46" rx="9"/></g><text x="595.0" y="136.0" class="dg-t" text-anchor="middle" style="--d:2">✗ détruit</text><path d="M480 131 L538 131" class="dg-l a" marker-end="url(#g11-a)"/><g class="dg-box dg-pop" style="--d:2"><rect x="370" y="170" width="110" height="46" rx="9"/></g><text x="425.0" y="198.0" class="dg-t" text-anchor="middle" style="--d:2">[&quot;c&quot;]</text><g class="dg-box dg-ok dg-pop" style="--d:3"><rect x="540" y="170" width="110" height="46" rx="9"/></g><text x="595.0" y="198.0" class="dg-t" text-anchor="middle" style="--d:3">[&quot;c&quot;]</text><path d="M480 193 L538 193" class="dg-l ok" marker-end="url(#g11-ok)"/><text x="170" y="242" class="dg-s" text-anchor="middle">retirer &quot;b&quot; : c est recréé, l&#x27;ancien [2] détruit</text><text x="510" y="242" class="dg-s" text-anchor="middle">retirer &quot;b&quot; : seul b est détruit</text><line x1="340" y1="40" x2="340" y2="230" class="dg-grid"/></svg><figcaption>Liste de départ [&quot;a&quot;, &quot;b&quot;, &quot;c&quot;], on retire &quot;b&quot;.</figcaption></figure>
<!-- /schema:count-vs-foreach -->

## Avec une map d'objets

```hcl
variable "services" {
  type = map(object({ port = number, public = bool }))
}

resource "aws_lb_target_group" "svc" {
  for_each = var.services
  name     = "tg-${each.key}"
  port     = each.value.port
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
}
```

## Expressions utiles

```hcl
locals {
  public_names = [for name, s in var.services : name if s.public]
  ports_by_svc = { for name, s in var.services : name => s.port }
  all_arns     = values(aws_lb_target_group.svc)[*].arn
  env_suffix   = var.environment == "prod" ? "" : "-${var.environment}"
}
```

## Blocs dynamiques

```hcl
resource "aws_security_group" "web" {
  name = "web"
  dynamic "ingress" {
    for_each = var.allowed_ports
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}
```

> **Piège classique.** Passer de `count` à `for_each` sur des ressources existantes change toutes leurs adresses. Sans blocs `moved`, Terraform veut tout détruire et recréer.

## Comprendre le problème de `count`

Avec `count`, Terraform identifie chaque copie par sa **position** dans la liste. Prends `buckets = ["logs", "backup", "assets"]` :

```
aws_s3_bucket.by_index[0] = logs
aws_s3_bucket.by_index[1] = backup
aws_s3_bucket.by_index[2] = assets
```

Tu retires `"backup"`. La liste devient `["logs", "assets"]`, donc `[1]` doit maintenant être `assets`, et `[2]` ne doit plus exister. Terraform va **renommer** le bucket `[1]` (ce qui, pour un bucket S3, veut dire le détruire et le recréer vide) et **détruire** `[2]`. Tu voulais supprimer un bucket, le plan en touche deux.

Avec `for_each`, chaque copie est identifiée par une **clé** (`["logs"]`, `["backup"]`, `["assets"]`). Retirer `"backup"` supprime seulement `["backup"]`. C'est pourquoi `for_each` est la règle pour les collections, et `count` réservé au cas « 0 ou 1 » :

```hcl
resource "aws_cloudwatch_metric_alarm" "cpu" {
  count = var.enable_alarms ? 1 : 0     # la ressource existe, ou non
  # …
}
```

`for_each` accepte une **map** ou un **set** de chaînes, pas une liste (d'où le `toset()`), et ses clés doivent être connues **au moment du plan** : impossible d'utiliser comme clé un ID qui n'existera qu'après la création d'une autre ressource.

## Lire les expressions

Les expressions `for` de HCL se lisent comme une phrase :

```hcl
[for name, s in var.services : name if s.public]
# « pour chaque (nom, service) de var.services, garde le nom si le service est public »  → une liste

{ for name, s in var.services : name => s.port }
# « pour chaque (nom, service), associe le nom au port »  → une map
```

- crochets `[ ]` → le résultat est une **liste** ; accolades `{ }` → une **map** (avec `=>`) ;
- `[*]` (le *splat*) récupère un attribut sur tous les éléments : `values(aws_lb_target_group.svc)[*].arn` ;
- `condition ? a : b` est le seul « if » de HCL.

`terraform console` permet de tester ces expressions en direct, avec les vraies variables du projet : c'est le meilleur moyen de les apprendre.

Le bloc `dynamic` génère des **sous-blocs** répétés (`ingress`, `setting`…) à partir d'une collection. Utile, mais il rend le code plus difficile à lire : réserve-le aux cas où le nombre de blocs varie vraiment.

> **À retenir.** `for_each` (identifié par une clé) pour les collections, `count` seulement pour « 0 ou 1 ». Teste tes expressions `for` dans `terraform console`, et ajoute des blocs `moved` avant de changer la façon dont une ressource est indexée.
