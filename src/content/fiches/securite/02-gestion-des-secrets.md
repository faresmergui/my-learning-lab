---
title: Gérer les secrets
chapter: 2
order: 1
duration: 12
level: intermédiaire
tags:
- DevSecOps
cards:
- q: Où un secret ne doit-il jamais se trouver ?
  a: Dans le **code** ou l'historique **Git**, dans une **image** de conteneur, dans des **logs**, ou en clair dans un ticket ou une messagerie.
- q: Qu'apporte un gestionnaire de secrets comme Vault ?
  a: Un stockage chiffré centralisé, des **droits fins**, un **audit** de chaque lecture, et des **secrets dynamiques** générés à la demande avec une durée de vie courte.
- q: Qu'est-ce qu'un secret dynamique ?
  a: Un identifiant **créé à la demande** (par exemple un compte de base de données) avec une durée de vie courte, puis révoqué automatiquement. Une fuite devient beaucoup moins grave.
- q: Comment une CI peut-elle accéder au cloud sans clé d'accès stockée ?
  a: 'Avec la **fédération OIDC** : la CI présente un jeton signé qui prouve son identité (dépôt, branche), et le cloud lui donne des identifiants temporaires.'
- q: Que faire quand un secret a fuité dans Git ?
  a: 'Le **révoquer et le changer tout de suite**, puis nettoyer l''historique si besoin. Supprimer le commit ne suffit pas : il a pu être copié.'
- q: 'Un secret a été commité puis supprimé : est-il protégé ?'
  a: Non. Il reste dans l'**historique Git**. Il faut le **révoquer** ou le faire tourner.
- q: Première action après la fuite d'un secret ?
  a: '**Révoquer / faire tourner** le secret. Nettoyer la source vient après.'
- q: Un Secret Kubernetes est-il chiffré ?
  a: Non, seulement **encodé en base64**. Il faut chiffrer etcd et restreindre le RBAC.
- q: Qu'apporte OIDC entre une CI et un cloud ?
  a: Chaque job reçoit un jeton signé décrivant son contexte (dépôt, branche). Le cloud le vérifie et délivre des identifiants **temporaires**. Plus aucune clé statique à stocker ni à faire tourner.
- q: Pourquoi préférer un fichier monté à une variable d'environnement pour un secret ?
  a: Les variables d'environnement fuient facilement (logs, dumps d'erreur, `/proc`, processus enfants). Un fichier peut aussi être mis à jour sans redémarrer l'appli.
quiz:
- q: Quel outil détecte des secrets dans le code avant qu'ils soient poussés ?
  options:
  - gitleaks (ou trufflehog) en hook pre-commit et dans la CI
  - terraform fmt
  - kubectl diff
  - shellcheck
  answer: 0
  explain: Mieux vaut bloquer le commit que gérer la fuite. GitHub et GitLab proposent aussi une détection côté serveur.
- q: Ta CI GitLab déploie sur AWS avec une clé d'accès stockée en variable. Quelle amélioration est la plus forte ?
  options:
  - Changer la clé chaque année
  - Passer à la fédération OIDC avec un rôle IAM limité au projet et à la branche
  - Masquer la variable
  - Chiffrer la clé en base64
  answer: 1
  explain: 'Plus de secret longue durée à voler : les identifiants sont temporaires et liés au pipeline.'
- q: Ta CI GitHub déploie sur AWS avec une clé d'accès stockée dans les secrets du dépôt depuis 2 ans. Quelle amélioration a le plus d'impact ?
  options:
  - Faire tourner la clé tous les ans
  - Passer à OIDC avec un rôle limité au dépôt et à la branche main
  - Chiffrer la variable
  - Masquer la variable dans les logs
  answer: 1
  explain: 'OIDC supprime la clé statique : identifiants temporaires, liés au contexte du job. Rien à faire fuir ni à faire tourner.'
---

Un secret, c'est tout ce qui donne un accès : mot de passe, clé d'API, clé privée, token, chaîne de connexion.


> **Les termes et outils cités dans cette fiche.**
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.
> - **commit** : un instantané enregistré des modifications dans Git, avec un message et un auteur.
> - **image** : le modèle figé (système de fichiers et réglages) à partir duquel on lance un conteneur.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **RBAC** : le contrôle d'accès par rôles : on donne des droits à des rôles, puis des rôles aux personnes ou programmes.
> - **CSI** : le standard des pilotes de stockage de Kubernetes.

## Le cycle de vie d'un secret

<!-- schema:cycle -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Le cycle de vie d&#x27;un secret" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="40" width="118" height="64" rx="9"/></g><text x="73.0" y="69.0" class="dg-t" text-anchor="middle" style="--d:0">création</text><text x="73.0" y="87.0" class="dg-s" text-anchor="middle" style="--d:0">généré, fort</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="148" y="40" width="118" height="64" rx="9"/></g><text x="207.0" y="69.0" class="dg-t" text-anchor="middle" style="--d:1">stockage</text><text x="207.0" y="87.0" class="dg-s" text-anchor="middle" style="--d:1">coffre chiffré</text><path d="M132 72 L146 72" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="282" y="40" width="118" height="64" rx="9"/></g><text x="341.0" y="69.0" class="dg-t" text-anchor="middle" style="--d:2">distribution</text><text x="341.0" y="87.0" class="dg-s" text-anchor="middle" style="--d:2">à l&#x27;exécution</text><path d="M266 72 L280 72" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-pop" style="--d:3"><rect x="416" y="40" width="118" height="64" rx="9"/></g><text x="475.0" y="62.0" class="dg-t" text-anchor="middle" style="--d:3">utilisation</text><text x="475.0" y="80.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="475.0" dy="0">en mémoire,</tspan><tspan x="475.0" dy="14">pas dans les logs</tspan></text><path d="M400 72 L414 72" class="dg-l c" marker-end="url(#g2-c)"/><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="550" y="40" width="118" height="64" rx="9"/></g><text x="609.0" y="69.0" class="dg-t" text-anchor="middle" style="--d:4">rotation</text><text x="609.0" y="87.0" class="dg-s" text-anchor="middle" style="--d:4">régulière ou auto</text><path d="M534 72 L548 72" class="dg-l c" marker-end="url(#g2-c)"/><path d="M610 106 C 610 170, 140 170, 140 108" class="dg-l c dash" marker-end="url(#g2-c)"/><text x="300" y="176" class="dg-s" text-anchor="middle">nouvelle version, l&#x27;ancienne expire</text><g class="dg-box dg-a dg-pop" style="--d:5"><rect x="470" y="186" width="196" height="50" rx="9"/></g><text x="568.0" y="208.0" class="dg-t" text-anchor="middle" style="--d:5">révocation</text><text x="568.0" y="226.0" class="dg-s" text-anchor="middle" style="--d:5">immédiate en cas de fuite</text><path d="M475 104 L475 150 L560 150 L560 184" class="dg-l a" marker-end="url(#g2-a)"/><text x="14" y="220" class="dg-at" text-anchor="start">jamais : dans Git, dans l&#x27;image, en clair dans une variable de CI</text></svg><figcaption>Un bon système rend la rotation banale : si changer un secret fait peur, il ne sera jamais changé.</figcaption></figure>
<!-- /schema:cycle -->

## Du moins bien au mieux

| Niveau | Approche |
| --- | --- |
| ✗ | secret dans le code ou dans un `.env` commité |
| ~ | variable de CI masquée, Secret Kubernetes en clair dans etcd |
| ✓ | gestionnaire de secrets (Vault, AWS Secrets Manager), injecté à l'exécution |
| ✓✓ | identités fédérées (OIDC, IRSA, Workload Identity) et secrets dynamiques |

## Exemples

```bash
# Détecter avant de pousser
gitleaks git --pre-commit --staged

# Lire un secret dans Vault
vault kv get -field=password secret/shop/prod/db

# Identifiants de base dynamiques, valables 1 h
vault read database/creds/shop-readonly
```

## Pourquoi les secrets fuient

La plupart des fuites ne viennent pas d'attaques sophistiquées mais d'endroits banals :

- un commit avec un `.env` ou une clé, même supprimé ensuite (il reste dans l'**historique** Git) ;
- des **logs** qui affichent une variable d'environnement ou un en-tête `Authorization` ;
- une image Docker qui contient le secret dans une **couche** (un `COPY` puis `rm` ne l'efface pas) ;
- un ticket, un message ou une capture d'écran partagés pour déboguer.

## Un secret a fui : que faire ?

1. **Révoquer ou faire tourner** le secret immédiatement. C'est la seule action qui compte vraiment.
2. Vérifier les **journaux d'accès** du service concerné sur la période.
3. Nettoyer la source (historique Git avec `git filter-repo`, image, log), en sachant que la copie peut déjà exister ailleurs.
4. Comprendre comment c'est arrivé et ajouter un garde-fou (scan pre-commit, scan en CI).

Réécrire l'historique Git sans révoquer le secret ne sert à rien : il faut considérer qu'il est déjà copié.

## La rotation

Un secret qui ne change jamais a toute sa durée de vie pour fuir. La **rotation** régulière limite la fenêtre d'exposition. Elle n'est réaliste que si l'application lit le secret à l'exécution, sans redéploiement : d'où l'intérêt d'un gestionnaire de secrets et des secrets dynamiques à durée de vie courte.

## Les secrets dans Kubernetes

Un Secret Kubernetes est seulement **encodé en base64**, pas chiffré. Pour le protéger : chiffrement d'etcd au repos, RBAC strict sur `get secrets`, et de préférence une source externe (External Secrets Operator, CSI Secrets Store) plutôt que des Secrets écrits à la main.

## Le moindre privilège

Chaque secret doit donner **le moins de droits possible** : une clé par application et par environnement, en lecture seule si l'application ne fait que lire. Une fuite n'expose alors qu'un périmètre limité.

## Les identités fédérées, expliquées

La ligne ✓✓ du tableau mérite une explication, car c'est le changement le plus important de ces dernières années.

**Le problème des clés statiques.** Pour qu'une CI déploie sur AWS, la méthode historique consiste à créer une clé d'accès (`AWS_ACCESS_KEY_ID` + secret) et à la stocker dans les variables de la CI. Cette clé est valable **indéfiniment**, fonctionne **depuis n'importe où**, et il faut penser à la faire tourner. Si elle fuit, l'attaquant l'utilise tranquillement.

**La solution : prouver qui on est, à chaque fois.** Avec **OIDC** (OpenID Connect), la CI (GitHub Actions, GitLab) délivre à chaque job un **jeton signé** qui dit en substance : « ce job tourne pour le dépôt `fares/shop`, sur la branche `main` ». Le cloud a été configuré pour faire confiance à ce fournisseur, avec une règle du type « un jeton du dépôt `fares/shop` sur `main` peut prendre le rôle `deploy-shop` ». Il vérifie la signature et délivre des identifiants **temporaires** (une heure, par exemple).

```
job CI ──jeton OIDC signé──► cloud (vérifie : bon émetteur ? bon dépôt ? bonne branche ?)
       ◄──identifiants valables 1 h──
```

Aucun secret à stocker, rien à faire tourner, et un jeton volé expire vite et ne vaut que pour ce rôle.

Le même principe existe pour les **pods** : **IRSA** et **EKS Pod Identity** sur AWS, **Workload Identity** sur GCP et Azure. La ServiceAccount Kubernetes du pod sert d'identité, échangée contre des droits cloud temporaires. Plus besoin de mettre une clé cloud dans un Secret.

## Les secrets dynamiques

Un **secret dynamique** est créé **à la demande**, pour un demandeur précis, avec une **durée de vie courte**. Exemple avec Vault et une base de données : quand l'appli démarre, Vault crée un utilisateur PostgreSQL dédié, valable une heure, et le supprime à l'expiration. Chaque instance a ses propres identifiants : une fuite est limitée dans le temps, et les journaux de la base disent exactement quelle instance a fait quoi.

## Comment l'appli reçoit son secret

| Méthode | Avantage | Limite |
| --- | --- | --- |
| variable d'environnement | simple, universel | visible dans `/proc`, souvent affichée par erreur dans les logs ou les dumps d'erreur |
| fichier monté (volume, tmpfs) | pas dans l'environnement, peut être mis à jour à chaud | l'appli doit relire le fichier |
| appel direct au gestionnaire (SDK Vault, AWS) | secret toujours à jour, secrets dynamiques possibles | dépendance de l'appli au gestionnaire |

Le fichier monté est un bon compromis par défaut, en particulier dans Kubernetes.

> **À retenir.** Le meilleur secret est celui qui n'existe pas. Chaque fois qu'une identité fédérée peut remplacer une clé statique (CI vers cloud, pod vers cloud), fais-le.
