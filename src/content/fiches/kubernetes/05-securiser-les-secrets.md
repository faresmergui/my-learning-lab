---
title: Sécuriser les Secrets
chapter: 5
order: 2
duration: 7
level: intermédiaire
tags:
- CKA
- CKS
cards:
- q: Un Secret Kubernetes est-il chiffré ?
  a: Pas par défaut. Ses valeurs sont seulement encodées en **base64**, et stockées en clair dans etcd tant que le chiffrement au repos n'est pas activé.
- q: Comment active-t-on le chiffrement des Secrets dans etcd ?
  a: Avec une `EncryptionConfiguration` passée à l'API server (`--encryption-config`), idéalement avec un fournisseur **KMS v2** relié à un gestionnaire de clés externe.
- q: Pourquoi le droit `list` sur les Secrets est-il aussi dangereux que `get` ?
  a: Parce que `list` renvoie les objets **complets**, valeurs comprises. Donner `list` revient à donner tous les secrets du namespace.
- q: Comment stocker des secrets dans Git pour faire du GitOps ?
  a: Jamais en clair. Soit on chiffre (Sealed Secrets, SOPS), soit on ne stocke qu'une **référence** et un opérateur va chercher la valeur (External Secrets Operator avec Vault ou AWS Secrets Manager).
- q: Pourquoi préférer un Secret monté en fichier plutôt qu'en variable d'environnement ?
  a: 'Les variables fuient plus facilement : processus enfants, dumps d''erreur, outils de debug qui affichent l''environnement. Et un fichier peut être mis à jour sans redémarrer.'
quiz:
- q: 'Un collègue dit : « nos secrets sont en base64, donc ils sont protégés ». Que lui réponds-tu ?'
  options:
  - Il a raison
  - Le base64 est un encodage, n'importe qui le décode avec `base64 -d`
  - C'est vrai uniquement dans etcd
  - C'est vrai si le namespace est privé
  answer: 1
  explain: La protection vient du RBAC, du chiffrement au repos et de l'usage d'un gestionnaire de secrets externe, pas de l'encodage.
- q: Quel outil synchronise des secrets depuis Vault ou AWS Secrets Manager vers des Secrets Kubernetes ?
  options:
  - Sealed Secrets
  - External Secrets Operator
  - Kustomize
  - cert-manager
  answer: 1
  explain: External Secrets Operator lit un `ExternalSecret` (qui ne contient qu'une référence) et crée le Secret à partir du gestionnaire externe. Sealed Secrets, lui, chiffre le secret pour le stocker dans Git.
---

Le nom est trompeur : un Secret Kubernetes n'est pas secret par défaut. C'est un objet qu'on peut protéger, à condition de le faire volontairement.

> **Les outils cités dans cette fiche.**
> - **Vault** (HashiCorp) : un coffre-fort à secrets qui tourne comme un service, avec des droits par application, un journal d'accès et des secrets qui expirent. **AWS Secrets Manager** et **Azure Key Vault** sont les équivalents gérés par les clouds.
> - **Sealed Secrets** : un contrôleur installé dans le cluster, avec une paire de clés. Tu chiffres ton Secret avec sa clé publique, tu peux commiter le résultat, et seul le contrôleur sait le déchiffrer.
> - **SOPS** : un outil en ligne de commande qui chiffre les valeurs d'un fichier YAML ou JSON (les clés restent lisibles), avec une clé **age** (un outil de chiffrement moderne et simple), PGP ou un **KMS** cloud (un service qui garde les clés de chiffrement).
> - **External Secrets Operator** : un contrôleur qui lit les secrets dans Vault ou un gestionnaire cloud et crée les Secrets Kubernetes à partir d'eux.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).

## Ce qu'un Secret n'est pas

```bash
kubectl get secret db-credentials -o jsonpath='{.data.password}' | base64 -d
# s3cr3t
```

Le base64 est un **encodage**, pas un chiffrement. Sans configuration, les valeurs sont en clair dans etcd et dans ses sauvegardes.

## Les quatre protections

1. **RBAC strict** : peu de personnes ont `get`, `list` ou `watch` sur les Secrets. N'oublie pas que pouvoir créer un pod dans un namespace permet de monter n'importe lequel de ses Secrets.
2. **Chiffrement au repos** dans etcd, avec KMS v2 si possible.
3. **Un gestionnaire externe** (Vault, AWS Secrets Manager, Azure Key Vault) qui reste la source de vérité.
4. **Le moins d'exposition possible** : montage en fichier, `automountServiceAccountToken: false` quand le pod n'a pas besoin de l'API.

## Les secrets et le GitOps

| Outil | Principe | Dans Git |
| --- | --- | --- |
| Sealed Secrets | Chiffré avec la clé publique du contrôleur | Le secret chiffré |
| SOPS | Fichier chiffré avec age, PGP ou KMS | Le fichier chiffré |
| External Secrets Operator | Référence vers un gestionnaire externe | Seulement la référence |

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata: { name: db-credentials }
spec:
  refreshInterval: 1h
  secretStoreRef: { name: vault, kind: ClusterSecretStore }
  target: { name: db-credentials }
  data:
    - secretKey: password
      remoteRef: { key: prod/db, property: password }
```

> **À retenir.** Un Secret supprimé de Git reste dans l'historique. Si un secret a été commité en clair, considère-le comme compromis et change-le.
