---
title: HashiCorp Vault en pratique
chapter: 2
order: 2
duration: 12
level: intermédiaire
tags:
- Vault
- secrets
- HashiCorp
cards:
- q: Qu'est-ce que HashiCorp Vault ?
  a: 'Un **gestionnaire de secrets** qui tourne comme un service : il stocke les secrets chiffrés, décide qui peut lire quoi, journalise chaque accès et peut générer des identifiants temporaires à la demande.'
- q: Que veut dire « sceller » et « desceller » Vault ?
  a: 'Au démarrage, Vault est **scellé** : ses données sont chiffrées et il ne peut pas les lire. Le **descellement** (*unseal*) lui fournit de quoi reconstituer sa clé maîtresse, avec plusieurs parts de clé (Shamir) ou automatiquement via un KMS cloud (*auto-unseal*).'
- q: Qu'est-ce qu'un secrets engine ?
  a: 'Un module de Vault qui gère un type de secret : **KV** (clé-valeur, secrets statiques), **database** (identifiants de base générés à la demande), **PKI** (certificats), **transit** (chiffrement à la volée)…'
- q: Qu'est-ce qu'une méthode d'authentification dans Vault ?
  a: 'La façon dont un client prouve son identité pour obtenir un **jeton** : utilisateur LDAP/OIDC pour un humain, **AppRole**, **Kubernetes** (jeton de ServiceAccount), JWT d''une CI ou identité cloud pour une machine.'
- q: Que contient une policy Vault ?
  a: Les chemins accessibles et les actions permises (`read`, `create`, `update`, `delete`, `list`). Tout ce qui n'est pas autorisé est refusé.
- q: Quel avantage d'un secret dynamique de base de données ?
  a: Chaque application reçoit son propre utilisateur, valable peu de temps, supprimé à l'expiration (le **lease**). Une fuite est limitée dans le temps et traçable.
- q: Qu'est-ce qu'OpenBao ?
  a: Un fork libre de Vault, maintenu par la Linux Foundation depuis le changement de licence de HashiCorp en 2023. Il reste très proche de Vault à l'usage.
quiz:
- q: Ton cluster Vault redémarre après une coupure. Les applications reçoivent des erreurs. Quelle est la cause la plus probable ?
  options:
  - Les secrets ont expiré
  - Vault est scellé et attend d'être descellé
  - Le réseau est coupé
  - Les policies ont été supprimées
  answer: 1
  explain: Après un redémarrage, Vault est scellé tant que personne (ou l'auto-unseal) ne lui a rendu sa clé.
- q: Un pod Kubernetes doit lire un secret dans Vault sans mot de passe stocké nulle part. Quelle méthode d'authentification ?
  options:
  - userpass
  - La méthode Kubernetes, avec le jeton du ServiceAccount
  - Un token root dans une variable d'environnement
  - LDAP
  answer: 1
  explain: Vault vérifie le jeton de ServiceAccount auprès de l'API Kubernetes et donne un jeton Vault limité par une policy.
- q: Une policy donne `read` sur `secret/data/shop/*`. L'appli tente d'écrire dans `secret/data/shop/db`. Résultat ?
  options:
  - L'écriture réussit
  - 'Refus : seul read est autorisé'
  - Vault crée une nouvelle version
  - Vault se scelle
  answer: 1
  explain: Une policy n'accorde que ce qu'elle liste ; le reste est refusé par défaut.
---

La fiche précédente explique **pourquoi** un gestionnaire de secrets vaut mieux qu'un fichier `.env`. Celle-ci présente le plus répandu en entreprise : **HashiCorp Vault**. C'est un service (un binaire écrit en Go, souvent déployé en cluster de trois ou cinq nœuds) que les humains et les applications interrogent par API pour obtenir des secrets. Il garde tout chiffré, vérifie l'identité de chaque demandeur, applique des règles d'accès fines et note chaque lecture dans un journal d'audit.

## Les briques de Vault

| Brique | Rôle |
| --- | --- |
| **Stockage** | où les données chiffrées sont écrites ; aujourd'hui surtout le stockage intégré (Raft) répliqué entre les nœuds |
| **Méthodes d'authentification** | comment un client prouve qui il est : OIDC/LDAP pour un humain, Kubernetes, AppRole, JWT de CI, identité AWS… |
| **Jetons** | ce que Vault remet après authentification ; chaque requête suivante le présente |
| **Policies** | quels chemins un jeton peut lire ou écrire |
| **Secrets engines** | les types de secrets gérés : KV, database, PKI, transit, AWS… |
| **Audit** | le journal de toutes les requêtes, avec les valeurs sensibles hachées |

Le principe ressemble à RBAC dans Kubernetes : une identité, des règles, et tout ce qui n'est pas autorisé est refusé.

## Sceller et desceller

Vault chiffre tout avec une clé interne, elle-même protégée par une **clé racine**. Au démarrage, il ne connaît pas cette clé : il est **scellé** et refuse toute requête. Pour le **desceller**, il faut soit fournir plusieurs **parts de clé** (par défaut 3 sur 5, distribuées à des personnes différentes, selon le partage de Shamir), soit utiliser l'**auto-unseal**, où un KMS cloud ou un HSM fournit la clé automatiquement.

C'est une sécurité : voler les disques d'un serveur Vault ne donne rien. Mais c'est aussi le premier réflexe de dépannage : après un redémarrage, `vault status` dit si le nœud est scellé.

## Les secrets engines les plus utilisés

- **KV v2** : des paires clé-valeur versionnées. On peut revenir à une version précédente d'un mot de passe.
- **database** : Vault crée un utilisateur PostgreSQL, MySQL… à la demande, avec une durée de vie (un **lease**), puis le supprime. Chaque instance d'appli a ses propres identifiants.
- **PKI** : Vault devient une autorité de certification interne et délivre des certificats de courte durée (pratique pour le mTLS entre services).
- **transit** : Vault chiffre et déchiffre des données pour l'application sans jamais lui donner la clé (*encryption as a service*).

## Un exemple de bout en bout

```bash
# Un humain se connecte avec le SSO de l'entreprise
vault login -method=oidc

# Écrire puis lire un secret statique
vault kv put secret/shop/prod/api key=s3cr3t
vault kv get -field=key secret/shop/prod/api
```

La policy qui autorise l'application à lire, et seulement lire, ses propres secrets :

```hcl
path "secret/data/shop/prod/*" {
  capabilities = ["read"]
}
```

## Vault et Kubernetes

Une appli dans Kubernetes ne doit pas avoir de mot de passe Vault en dur. La méthode **Kubernetes** règle ça : le pod présente le jeton de son ServiceAccount, Vault le fait vérifier par l'API du cluster et rend un jeton Vault limité par une policy. Ensuite, trois façons courantes d'amener le secret à l'appli :

| Méthode | Principe |
| --- | --- |
| **Vault Agent Injector** | un conteneur sidecar récupère les secrets et les écrit dans un fichier partagé du pod |
| **Vault Secrets Operator** ou **External Secrets Operator** | un contrôleur crée et met à jour des Secrets Kubernetes à partir de Vault |
| **Secrets Store CSI Driver** | les secrets sont montés comme un volume |

Côté CI (GitLab CI, GitHub Actions), la méthode **JWT** suit la même logique : le jeton signé du job sert d'identité, sans secret stocké dans la CI.

## Vault ou OpenBao

En 2023, HashiCorp est passé à une licence non libre (BSL), puis a été racheté par IBM. La communauté a créé **OpenBao**, un fork libre sous la Linux Foundation, compatible à l'usage. Les concepts de cette fiche s'appliquent aux deux. Les clouds proposent aussi leurs gestionnaires (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager), plus simples mais liés à un fournisseur.

> **À retenir.** Vault vérifie l'identité de chaque demandeur, applique des policies par chemin et journalise tout. Il démarre scellé, et c'est la première chose à vérifier en cas de panne. Ses vrais atouts sont les secrets dynamiques et l'authentification des machines par leur identité (Kubernetes, CI, cloud), sans aucun mot de passe stocké.
