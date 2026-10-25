---
title: Tester et valider
chapter: 8
order: 1
duration: 9
level: intermédiaire
tags:
- Terraform Associate
cards:
- q: Quels contrôles automatiques avant même le plan ?
  a: '`terraform fmt -check`, `terraform validate`, **TFLint** (erreurs propres à chaque provider, conventions) et un scanner de sécurité comme **Trivy** ou **Checkov**.'
- q: Où écrit-on les tests natifs de Terraform ?
  a: Dans des fichiers `*.tftest.hcl` (dossier `tests/`), lancés avec `terraform test`. Chaque bloc `run` fait un plan ou un apply puis vérifie des `assert`.
- q: Différence entre `precondition`, `postcondition` et un bloc `check` ?
  a: '`precondition` et `postcondition` (dans `lifecycle`) **bloquent** le plan ou l''apply si elles échouent. Un bloc `check` signale seulement un **avertissement**, sans bloquer.'
- q: Que vérifie un scanner comme Trivy ou Checkov sur du Terraform ?
  a: 'Les **mauvaises configurations** de sécurité : bucket public, chiffrement absent, security group ouvert sur `0.0.0.0/0`, logs désactivés…'
- q: À quoi servent les `mock_provider` dans `terraform test` ?
  a: 'À tester un module **sans créer de vraies ressources** ni d''identifiants cloud : le provider renvoie des valeurs simulées.'
quiz:
- q: Tu veux empêcher un apply si l'AMI choisie n'est pas en architecture arm64. Quel outil ?
  options:
  - Un bloc `check`
  - Une `precondition` dans le `lifecycle` de l'instance
  - Un output sensible
  - TFLint
  answer: 1
  explain: La précondition bloque l'exécution avec ton message d'erreur. Un bloc `check` aurait seulement affiché un avertissement.
- q: '`terraform test` avec `command = plan` crée-t-il des ressources ?'
  options:
  - Oui, toujours
  - Non, il s'arrête au plan
  - Seulement avec un mock
  - Seulement en CI
  answer: 1
  explain: Avec `command = apply` (le défaut), il crée les ressources puis les détruit à la fin du test.
---

L'infrastructure as code se teste comme du code : du plus rapide au plus coûteux.

```
fmt / validate  ──►  TFLint  ──►  Trivy / Checkov  ──►  terraform test  ──►  plan relu
   secondes          secondes      secondes             minutes             humain
```


> **Les termes et outils cités dans cette fiche.**
> - **bucket** : un conteneur de fichiers dans un stockage objet (S3, Swift).
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **KMS** : le service de gestion des clés de chiffrement.
> - **AMI** : l'image de disque à partir de laquelle on démarre une instance EC2.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.

## Lint et sécurité

```bash
terraform fmt -check -recursive
terraform validate
tflint --recursive
trivy config .            # ou : checkov -d .
```

## Les tests natifs

```hcl
# tests/bucket.tftest.hcl
variables {
  name = "test-bucket-fares"
}

run "chiffrement_active" {
  command = plan
  assert {
    condition     = aws_s3_bucket_server_side_encryption_configuration.this.rule[0].apply_server_side_encryption_by_default[0].sse_algorithm == "aws:kms"
    error_message = "Le bucket doit être chiffré avec KMS."
  }
}
```

```bash
terraform test
```

## Les gardes-fous dans le code

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.app.id
  instance_type = var.instance_type
  lifecycle {
    precondition {
      condition     = data.aws_ami.app.architecture == "arm64"
      error_message = "L'AMI doit être en arm64."
    }
  }
}

check "site_repond" {
  data "http" "health" { url = "https://shop.example.com/health" }
  assert {
    condition     = data.http.health.status_code == 200
    error_message = "Le site ne répond pas 200."
  }
}
```

## Ce que chaque étage attrape

| Étape | Ce qu'elle vérifie | Exemple d'erreur attrapée |
| --- | --- | --- |
| `fmt` | la mise en forme | indentation (évite les diffs inutiles en revue) |
| `validate` | la syntaxe et la cohérence interne | variable non déclarée, attribut inexistant |
| TFLint | les erreurs propres au fournisseur | type d'instance `t3.mediun` qui n'existe pas |
| Trivy / Checkov | les mauvaises pratiques de sécurité | bucket public, port 22 ouvert à `0.0.0.0/0`, disque non chiffré |
| `terraform test` | le comportement de **tes** modules | « ce module chiffre toujours en KMS » |
| plan relu | ce qui va vraiment changer | un `-/+` imprévu sur la base |

`validate` ne contacte pas le cloud : il ne sait pas si l'AMI existe ou si tu as les droits. Le **plan**, lui, interroge le cloud ; c'est la vérification la plus réaliste avant `apply`.

## Les tests natifs, expliqués

Un fichier `.tftest.hcl` contient des blocs `run`. Chaque `run` exécute un `plan` (rapide, rien n'est créé) ou un `apply` (crée de vraies ressources, puis les détruit à la fin) et vérifie des `assert`. On teste surtout ses **modules** : leurs choix imposés (chiffrement, tags, noms) doivent tenir, quelles que soient les variables passées.

## Précondition, postcondition, check : quelle différence ?

| Bloc | Quand | Si la condition est fausse |
| --- | --- | --- |
| `validation` (dans une `variable`) | avant tout, sur une valeur d'entrée | erreur : la valeur est refusée |
| `precondition` | avant de créer ou modifier la ressource | erreur : le plan ou l'apply s'arrête |
| `postcondition` | après, sur la ressource obtenue | erreur |
| `check` | à la fin de chaque plan et apply | simple **avertissement**, rien n'est bloqué |

Le bloc `check` sert donc de petite sonde : « après ce déploiement, le site répond-il ? ». Il prévient sans empêcher.

> **À retenir.** Un scanner de sécurité dans la CI attrape en quelques secondes ce qu'une revue humaine laisse passer : le bucket public, le port 22 ouvert au monde.
