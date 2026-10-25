---
title: Environnements et travail en équipe
chapter: 6
order: 1
duration: 9
level: intermédiaire
tags:
- Terraform Associate
cards:
- q: Que sont les workspaces Terraform (CLI) ?
  a: Plusieurs **states** pour le même code et le même backend. `terraform workspace new staging`, et `terraform.workspace` dans le code.
- q: Pourquoi les workspaces ne suffisent-ils pas toujours pour séparer dev et prod ?
  a: 'Ils partagent le **même backend** et les **mêmes droits** : impossible de restreindre l''accès au state de prod. On préfère souvent un dossier par environnement, avec son propre backend.'
- q: Comment lire les outputs d'un autre projet Terraform ?
  a: Avec la data source `terraform_remote_state`, ou mieux, avec des data sources du provider (`data "aws_vpc"`), qui évitent de dépendre du state d'un autre.
- q: Quel workflow CI pour Terraform en équipe ?
  a: 'Sur la merge request : `fmt -check`, `validate`, `plan`, et le plan est publié en commentaire. Après la fusion : `apply` du plan relu, sur la branche principale uniquement.'
- q: Qu'est-ce que la dérive (*drift*) ?
  a: Un écart entre le state et la réalité, souvent dû à une modif manuelle dans la console. `terraform plan -refresh-only` la met en évidence sans rien changer.
quiz:
- q: Un collègue modifie un security group à la main dans la console. Que montrera ton prochain `terraform plan` ?
  options:
  - Rien
  - Une modification pour revenir à ce que décrit le code
  - Une erreur de state
  - La suppression du security group
  answer: 1
  explain: Terraform rafraîchit l'état réel et propose de revenir à ce que dit le code. Si la modif manuelle doit rester, il faut la reporter dans le code.
- q: Comment s'assurer que seule la CI peut appliquer en prod ?
  options:
  - Mettre un mot de passe dans le code
  - Restreindre les droits du rôle de prod et du backend à l'identité de la CI
  - Utiliser un workspace nommé prod
  - Mettre `prevent_destroy` partout
  answer: 1
  explain: 'La séparation des environnements passe par les droits : un rôle IAM et un backend propres à la prod, que seule la CI peut utiliser.'
---

Un seul développeur qui lance `terraform apply` depuis son poste, ça marche pour un essai. Dès qu'il y a plusieurs environnements (dev, recette, prod) et plusieurs personnes, il faut répondre à trois questions : comment **séparer** les environnements, comment **partager** le state sans se marcher dessus, et **qui applique** les changements.


> **Les termes et outils cités dans cette fiche.**
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **branche** : une ligne de développement parallèle dans Git.
> - **réplica** : une copie identique d'un pod, d'une base ou d'une donnée.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **VPC** : un réseau privé virtuel dans le cloud, isolé des autres clients.
> - **artefact** : un fichier produit par une étape du pipeline (binaire, image, rapport) et transmis aux suivantes.

## Séparer les environnements

Deux approches courantes :

```
# 1. Un dossier par environnement            # 2. Des workspaces
envs/                                         main.tf
├── dev/      main.tf  backend.tf             terraform workspace select prod
├── staging/  main.tf  backend.tf
└── prod/     main.tf  backend.tf
modules/
└── app/      (le code partagé)
```

| | Dossiers séparés | Workspaces |
| --- | --- | --- |
| Backend et droits | propres à chaque env | partagés |
| Différences entre envs | explicites | via `terraform.workspace` |
| Risque d'erreur | faible | appliquer sur le mauvais workspace |
| Idéal pour | dev / staging / prod | copies identiques (environnements éphémères) |

<!-- schema:separation -->
<figure class="diagram"><svg viewBox="0 0 680 230" role="img" aria-label="Un dossier et un state par environnement" style="--minw:560px"><defs><marker id="g12-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g12-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g12-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g12-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="20" y="20" width="200" height="56" rx="9"/></g><text x="120.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:0">modules/app</text><text x="120.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:0">le code partagé</text><g class="dg-box dg-pop" style="--d:1"><rect x="260" y="20" width="124" height="56" rx="9"/></g><text x="322.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:1">envs/dev</text><text x="322.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:1">main.tf</text><g class="dg-box dg-pop" style="--d:2"><rect x="260" y="130" width="124" height="56" rx="9"/></g><text x="322.0" y="155.0" class="dg-t" text-anchor="middle" style="--d:2">dev.tfstate</text><text x="322.0" y="173.0" class="dg-s" text-anchor="middle" style="--d:2">son propre state</text><path d="M322 76 L322 128" class="dg-l" marker-end="url(#g12-n)"/><g class="dg-box dg-pop" style="--d:2"><rect x="400" y="20" width="124" height="56" rx="9"/></g><text x="462.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:2">envs/staging</text><text x="462.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:2">main.tf</text><g class="dg-box dg-pop" style="--d:3"><rect x="400" y="130" width="124" height="56" rx="9"/></g><text x="462.0" y="155.0" class="dg-t" text-anchor="middle" style="--d:3">staging.tfstate</text><text x="462.0" y="173.0" class="dg-s" text-anchor="middle" style="--d:3">son propre state</text><path d="M462 76 L462 128" class="dg-l" marker-end="url(#g12-n)"/><g class="dg-box dg-pop" style="--d:3"><rect x="540" y="20" width="124" height="56" rx="9"/></g><text x="602.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:3">envs/prod</text><text x="602.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:3">main.tf</text><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="540" y="130" width="124" height="56" rx="9"/></g><text x="602.0" y="155.0" class="dg-t" text-anchor="middle" style="--d:4">prod.tfstate</text><text x="602.0" y="173.0" class="dg-s" text-anchor="middle" style="--d:4">son propre state</text><path d="M602 76 L602 128" class="dg-l" marker-end="url(#g12-n)"/><path d="M220 48 L258 48" class="dg-l c" marker-end="url(#g12-c)"/><text x="470" y="214" class="dg-s" text-anchor="middle">une erreur en dev ne peut pas toucher le state de prod</text></svg><figcaption>Le code commun vit dans un module, chaque environnement l&#x27;appelle avec ses valeurs.</figcaption></figure>
<!-- /schema:separation -->

## Partager des informations entre projets

```hcl
# Plutôt que de lire le state du projet réseau…
data "aws_vpc" "main" {
  tags = { Name = "shop-prod" }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
  tags = { tier = "private" }
}
```

## La CI

```yaml
# .gitlab-ci.yml (extrait)
plan:
  script:
    - terraform init -input=false
    - terraform fmt -check -recursive
    - terraform validate
    - terraform plan -out=tfplan -input=false
  artifacts: { paths: [tfplan] }

apply:
  script:
    - terraform init -input=false
    - terraform apply -input=false tfplan
  when: manual
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Pourquoi séparer les environnements

Le but est de pouvoir casser `dev` sans **aucun** risque pour `prod`. Ça veut dire trois séparations :

- **des states séparés** : un `apply` en dev ne peut physiquement pas toucher une ressource de prod, puisqu'elle n'est pas dans son state ;
- **des droits séparés** : idéalement des comptes cloud différents, et une CI qui n'a les droits de prod que sur la branche principale ;
- **des différences visibles** : ce qui change entre dev et prod (taille des instances, nombre de réplicas) doit se lire dans le code, pas se deviner.

Les **dossiers séparés** remplissent les trois : chaque dossier a son backend (donc son state), peut utiliser d'autres identifiants, et ses valeurs sont écrites noir sur blanc. Le code commun vit dans `modules/`, et chaque environnement ne fait que l'appeler avec ses paramètres. On accepte un peu de duplication (quelques fichiers `main.tf` presque identiques) en échange de la sécurité.

Les **workspaces** gardent un seul code et plusieurs states dans le même backend. C'est pratique pour des copies identiques et temporaires (un environnement par branche de fonctionnalité), mais le workspace actif est un état **invisible** de ton terminal : un `apply` lancé en pensant être en dev, alors qu'on est resté en prod, est l'accident classique.

## Pourquoi `data` plutôt que lire le state voisin

Un projet peut lire les outputs d'un autre via `terraform_remote_state`. Mais il lui faut alors un accès **en lecture au state entier** de l'autre projet, avec tout ce qu'il contient (parfois des mots de passe). Les sources `data` interrogent directement l'API du cloud, par tags ou par nom : les projets ne dépendent que de conventions (« le VPC s'appelle `shop-prod` »), pas de l'organisation interne de l'autre équipe.

## Pourquoi le plan en artefact

Dans la CI ci-dessus, le job `plan` enregistre le plan dans un fichier (`-out=tfplan`) et le job `apply` applique **ce fichier**. Ainsi, ce qui est appliqué est exactement ce qui a été relu. Si l'infrastructure a changé entre les deux (quelqu'un d'autre a appliqué), Terraform refuse le plan périmé au lieu d'appliquer autre chose que ce qui a été validé. Le `when: manual` ajoute une validation humaine avant la prod.

> **À retenir.** Une fois Terraform en place, plus aucune modif à la main dans la console. Chaque exception crée de la dérive, et la dérive finit toujours par surprendre quelqu'un.
