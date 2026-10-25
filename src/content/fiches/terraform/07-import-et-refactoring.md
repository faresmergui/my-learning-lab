---
title: Importer, refactorer et protéger
chapter: 7
order: 1
duration: 9
level: intermédiaire
tags:
- Terraform Associate
cards:
- q: Comment voir en détail ce que fait Terraform quand une commande échoue sans explication ?
  a: 'Avec la variable `TF_LOG` (`TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`) : `TF_LOG=DEBUG terraform plan`. `TF_LOG_PATH=terraform.log` écrit ces journaux dans un fichier, `TF_LOG_CORE` et `TF_LOG_PROVIDER` séparent Terraform et le provider.'
- q: Comment importer une ressource existante avec un bloc `import` ?
  a: Un bloc `import` avec `to` (l'adresse dans le code) et `id` (l'identifiant réel), puis `terraform plan`. Avec `-generate-config-out=generated.tf`, Terraform écrit même le code de la ressource.
- q: À quoi sert un bloc `removed` ?
  a: À **sortir une ressource du state sans la détruire**, de façon déclarative et relue en revue. C'est la version moderne de `terraform state rm`.
- q: Que fait `lifecycle { prevent_destroy = true }` ?
  a: Il fait **échouer** tout plan qui détruirait la ressource. Une protection pour les bases de données ou les buckets critiques.
- q: À quoi sert `ignore_changes` ?
  a: À ignorer les écarts sur certains attributs gérés ailleurs, par exemple `desired_count` piloté par un autoscaler, ou des tags ajoutés par un outil externe.
- q: Que fait `create_before_destroy` ?
  a: En cas de remplacement, il crée la **nouvelle** ressource avant de détruire l'ancienne. Pour éviter une coupure, par exemple sur un certificat ou un launch template.
- q: Comment forcer le remplacement d'une seule ressource ?
  a: '`terraform apply -replace=aws_instance.bastion`. C''est le remplaçant de l''ancien `terraform taint`.'
quiz:
- q: Tu déplaces `aws_instance.web` dans un module `web`. Comment éviter sa destruction ?
  options:
  - Un bloc `moved` de `aws_instance.web` vers `module.web.aws_instance.this`
  - '`ignore_changes = all`'
  - '`prevent_destroy = true`'
  - Relancer `terraform init`
  answer: 0
  explain: Le bloc `moved` dit à Terraform qu'il s'agit de la même ressource à une nouvelle adresse. `prevent_destroy` ferait seulement échouer le plan.
- q: Une équipe veut arrêter de gérer un bucket avec Terraform, sans le supprimer. Que faire ?
  options:
  - Supprimer la ressource du code et lancer apply
  - Utiliser un bloc `removed` avec `lifecycle { destroy = false }`
  - Supprimer le state
  - Mettre `count = 0`
  answer: 1
  explain: Retirer simplement le code détruirait le bucket. Le bloc `removed` le retire du state et laisse la ressource intacte.
---

Deux situations arrivent vite dans un vrai projet : des ressources **créées à la main** qu'on veut confier à Terraform (l'**import**), et du code qu'on veut **réorganiser** (renommer, déplacer dans un module) sans que Terraform détruise et recrée tout (le **refactoring**).


> **Les termes et outils cités dans cette fiche.**
> - **bucket** : un conteneur de fichiers dans un stockage objet (S3, Swift).
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **jeton** : une chaîne secrète qui prouve qu'on est authentifié, à durée limitée.

## Importer l'existant

```hcl
import {
  to = aws_s3_bucket.logs
  id = "fares-logs-prod"
}
```

```bash
terraform plan -generate-config-out=generated.tf   # écrit le code pour toi
# relire, nettoyer generated.tf, le renommer, puis :
terraform apply
```

## Refactorer sans rien casser

```hcl
moved {
  from = aws_instance.web
  to   = module.web.aws_instance.this
}

moved {
  from = aws_s3_bucket.by_index[0]
  to   = aws_s3_bucket.by_name["logs"]
}

removed {
  from = aws_s3_bucket.legacy
  lifecycle { destroy = false }
}
```

<!-- schema:moved -->
<figure class="diagram"><svg viewBox="0 0 680 210" role="img" aria-label="Ce que change un bloc moved" style="--minw:560px"><defs><marker id="g13-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g13-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g13-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g13-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="170" y="22" class="dg-at" text-anchor="middle">renommer sans moved</text><text x="510" y="22" class="dg-okt" text-anchor="middle">renommer avec un bloc moved</text><g class="dg-box dg-a dg-pop" style="--d:0"><rect x="30" y="40" width="280" height="44" rx="9"/></g><text x="170.0" y="59.0" class="dg-t" text-anchor="middle" style="--d:0">- aws_instance.web</text><text x="170.0" y="77.0" class="dg-s" text-anchor="middle" style="--d:0">destroy</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="30" y="100" width="280" height="44" rx="9"/></g><text x="170.0" y="119.0" class="dg-t" text-anchor="middle" style="--d:1">+ aws_instance.app</text><text x="170.0" y="137.0" class="dg-s" text-anchor="middle" style="--d:1">create : nouvelle IP, coupure</text><g class="dg-box dg-ok dg-pop" style="--d:1"><rect x="370" y="40" width="280" height="104" rx="9"/></g><text x="510.0" y="74.0" class="dg-t" text-anchor="middle" style="--d:1"><tspan x="510.0" dy="0">aws_instance.web</tspan><tspan x="510.0" dy="16">→ aws_instance.app</tspan></text><text x="510.0" y="108.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="510.0" dy="0">même objet, nouvelle adresse</tspan><tspan x="510.0" dy="14">0 to add, 0 to destroy</tspan></text><text x="510" y="186" class="dg-s" text-anchor="middle">moved { from = aws_instance.web  to = aws_instance.app }</text><line x1="340" y1="36" x2="340" y2="196" class="dg-grid"/></svg><figcaption>Sans moved, Terraform voit une ressource supprimée et une autre ajoutée.</figcaption></figure>
<!-- /schema:moved -->

## Protéger avec `lifecycle`

```hcl
resource "aws_db_instance" "main" {
  # …
  lifecycle {
    prevent_destroy = true
    ignore_changes  = [password]   # changé par la rotation automatique
  }
}

resource "aws_launch_template" "web" {
  # …
  lifecycle { create_before_destroy = true }
}
```

| Option | Effet |
| --- | --- |
| `prevent_destroy` | le plan échoue s'il détruit la ressource |
| `ignore_changes` | ignore les écarts sur ces attributs |
| `create_before_destroy` | crée la remplaçante avant de supprimer l'ancienne |
| `replace_triggered_by` | remplace si une autre ressource change |

> **Piège classique.** `prevent_destroy` ne protège pas si on supprime le bloc de ressource du code : la protection disparaît avec lui. Pour les données critiques, ajoute aussi la protection côté cloud (deletion protection, versioning, sauvegardes).

## Comprendre : le code, le state et le réel

Terraform travaille avec trois choses :

1. le **code** (`.tf`) : ce que tu veux ;
2. le **state** : la liste des objets que Terraform **gère**, avec leur adresse dans le code (`aws_s3_bucket.logs`) et leur ID réel (`fares-logs-prod`) ;
3. le **réel** : ce qui existe dans le cloud.

**Importer**, c'est ajouter au state une ligne « l'adresse `aws_s3_bucket.logs` correspond à l'objet réel `fares-logs-prod` », pour une ressource créée à la main. Rien n'est créé ni modifié dans le cloud. Après l'import, le plan doit être **vide** (ou presque) : s'il propose des changements, c'est que ton code ne décrit pas encore fidèlement la ressource. On ajuste le code jusqu'à obtenir « No changes ».

**Refactorer**, c'est changer l'**adresse** d'une ressource dans le code (la renommer, la déplacer dans un module, passer de `count` à `for_each`) sans toucher au réel. Sans aide, Terraform voit une adresse qui disparaît et une nouvelle qui apparaît, et conclut : détruire l'ancienne, créer la nouvelle. Le bloc **`moved`** lui dit « c'est le même objet, il a seulement changé d'adresse ».

**Retirer** sans détruire (`removed` avec `destroy = false`) fait l'inverse de l'import : Terraform oublie la ressource, qui continue d'exister dans le cloud. Utile pour la confier à un autre projet.

Les blocs `import`, `moved` et `removed` sont écrits dans le code, donc **relus en revue** et visibles dans le plan. C'est leur avantage sur les anciennes commandes `terraform import` et `terraform state mv`, qui modifiaient le state directement, sans trace.

## Lire un plan avant de valider

Les symboles d'un plan disent ce qui va arriver :

| Symbole | Signification | Vigilance |
| --- | --- | --- |
| `+` | création | faible |
| `~` | modification sur place | moyenne |
| `-/+` | **destruction puis recréation** | élevée : regarde l'attribut marqué `# forces replacement` |
| `-` | destruction | élevée |

Un `-/+` sur une base de données ou un bucket signifie une perte de données. C'est exactement ce que `moved`, `prevent_destroy` et `create_before_destroy` servent à éviter.

## Activer les journaux pour déboguer

Quand une commande échoue avec un message trop court (erreur d'API du provider, blocage sans explication), Terraform peut raconter tout ce qu'il fait grâce à la variable d'environnement **`TF_LOG`**.

```bash
TF_LOG=DEBUG terraform plan                         # niveaux : TRACE, DEBUG, INFO, WARN, ERROR
TF_LOG=TRACE TF_LOG_PATH=./terraform.log terraform apply   # dans un fichier plutôt qu'à l'écran
TF_LOG_PROVIDER=DEBUG terraform plan                # seulement le provider (les appels à l'API du cloud)
unset TF_LOG                                        # revenir à la normale
```

`TRACE` est le plus bavard : on y voit chaque requête envoyée à l'API du cloud et sa réponse, ce qui suffit souvent à comprendre un refus de droits. Ces journaux peuvent contenir des **secrets** (jetons, mots de passe dans les requêtes) : on ne les colle pas tels quels dans un ticket ou une discussion publique, et on supprime le fichier après usage. Pour un crash de Terraform lui-même, il écrit un fichier `crash.log` dans le dossier courant.

> **À retenir.** `import` fait entrer une ressource existante dans le state, `moved` change son adresse sans la recréer, `removed` la fait oublier sans la détruire. Ces blocs passent en revue de code comme le reste. Après chaque opération, le plan doit être vide ou ne montrer que ce que tu attends. Pour déboguer, `TF_LOG=DEBUG` (ou `TRACE`) et `TF_LOG_PATH` pour garder les journaux dans un fichier.
