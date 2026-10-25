---
title: TLS et certificats, pas à pas
chapter: 4
order: 2
duration: 10
level: intermédiaire
tags:
- fondamentaux
- sécurité
cards:
- q: Quelles sont les trois garanties de TLS ?
  a: '**Confidentialité** (chiffrement), **intégrité** (rien n''a été modifié en route) et **authenticité** (tu parles bien au serveur que tu crois, grâce au certificat).'
- q: Différence entre chiffrement symétrique et asymétrique ?
  a: '**Symétrique** : une même clé chiffre et déchiffre, très rapide (AES). **Asymétrique** : une paire clé publique / clé privée ; ce que l''une fait, seule l''autre le défait. Plus lent, il sert à s''authentifier et à s''échanger une clé symétrique.'
- q: Que contient un certificat ?
  a: Le **nom** (ou les noms, dans le SAN) du serveur, sa **clé publique**, une **date d'expiration**, et la **signature** de l'autorité (CA) qui garantit le tout.
- q: Qu'est-ce qu'une chaîne de certificats ?
  a: Certificat du serveur → signé par une CA **intermédiaire** → signée par une CA **racine** présente dans le magasin de confiance du système. Le serveur doit envoyer son certificat **et** l'intermédiaire.
- q: Pourquoi la clé privée ne doit jamais sortir du serveur ?
  a: Elle prouve que le serveur est bien le titulaire du certificat. Quiconque la possède peut se faire passer pour lui.
- q: À quoi sert le SNI ?
  a: Le client annonce en clair, dès le début de TLS, le nom du site qu'il veut joindre. Le serveur (ou proxy) peut ainsi choisir le bon certificat parmi plusieurs sur la même IP.
quiz:
- q: '`curl` renvoie « unable to get local issuer certificate » alors que le navigateur affiche le site sans erreur. Cause la plus probable ?'
  options:
  - Le certificat a expiré
  - Le serveur n'envoie pas le certificat intermédiaire
  - Le nom ne correspond pas
  - TLS 1.3 n'est pas supporté
  answer: 1
  explain: Les navigateurs complètent souvent la chaîne tout seuls, `curl` et les applis non. Le serveur doit envoyer la chaîne complète (fullchain).
- q: Tu te connectes à `https://10.0.0.5` et obtiens une erreur de nom alors que le certificat est valide pour `api.shop.fr`. Pourquoi ?
  options:
  - Le certificat est auto-signé
  - Le nom demandé (l'IP) ne figure pas dans le certificat
  - Le port 443 est fermé
  - Il manque la clé privée
  answer: 1
  explain: Le client vérifie que le nom qu'il a demandé est dans le SAN du certificat. Utilise le nom, ou `--resolve api.shop.fr:443:10.0.0.5` pour tester.
- q: Pourquoi TLS n'utilise-t-il pas le chiffrement asymétrique pour toutes les données ?
  options:
  - Il est moins sûr
  - Il est beaucoup plus lent ; on s'en sert seulement pour s'authentifier et convenir d'une clé symétrique
  - Il ne fonctionne qu'en IPv6
  - Il nécessite une CA par connexion
  answer: 1
  explain: L'asymétrique sert à la poignée de main ; ensuite tout passe en symétrique (AES, ChaCha20), bien plus rapide.
---

Le cadenas du navigateur promet trois choses : personne ne peut **lire** l'échange, personne ne peut le **modifier** sans que ça se voie, et le serveur est bien **celui qu'il prétend être**. C'est le travail de **TLS** (Transport Layer Security, successeur de SSL). Cette fiche explique comment, sans mathématiques.

> **Les outils et sigles cités dans cette fiche.**
> - **AES** et **ChaCha20** : deux algorithmes de chiffrement symétrique, rapides, utilisés pour chiffrer les données une fois la connexion établie.
> - **CA** (Certificate Authority, autorité de certification) : organisme qui signe les certificats et garantit qu'un nom appartient bien à une clé. **Let's Encrypt** est une CA gratuite et automatisée.
> - **SAN** (Subject Alternative Name) : le champ du certificat qui liste les noms couverts. **SNI** (Server Name Indication) : le nom du site que le client annonce au début de la connexion, pour qu'un serveur qui héberge plusieurs sites présente le bon certificat.
> - **ACME** : le protocole qui permet d'obtenir et de renouveler un certificat automatiquement. **certbot** l'implémente sur un serveur classique, **cert-manager** dans Kubernetes.
> - **openssl** : la boîte à outils en ligne de commande pour inspecter certificats et connexions TLS (`s_client` se connecte comme un client, `x509` lit un certificat).
> - **mTLS** (TLS mutuel) : le client présente lui aussi un certificat. **Service mesh** (Istio, Linkerd) : une couche qui gère le trafic entre services d'un cluster et peut activer le mTLS partout sans toucher au code.
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.

## Deux familles de chiffrement

**Le chiffrement symétrique** : une seule clé, qui sert à chiffrer et à déchiffrer, comme un cadenas à code que les deux parties connaissent. C'est très rapide (AES, ChaCha20). Le problème : comment se mettre d'accord sur ce code sans qu'un espion l'entende ?

**Le chiffrement asymétrique** : une **paire** de clés liées entre elles.

- la **clé publique** peut être donnée à tout le monde ;
- la **clé privée** reste secrète, sur le serveur ;
- ce que l'une fait, seule l'autre peut le défaire.

Ça permet deux choses : **signer** (le serveur prouve qu'il possède la clé privée sans la montrer) et **échanger une clé** en toute sécurité devant un espion. Mais c'est lent.

TLS combine les deux : l'asymétrique pendant la **poignée de main** pour s'authentifier et convenir d'une clé, puis le symétrique pour tout le reste.

## Le certificat : une carte d'identité signée

Une clé publique seule ne prouve rien : n'importe qui peut en générer une et prétendre être `banque.fr`. Il faut qu'un tiers de confiance garantisse le lien entre le **nom** et la **clé**. C'est le rôle du **certificat**, délivré par une **autorité de certification** (CA) comme Let's Encrypt.

Un certificat contient :

- le ou les **noms** couverts, dans le champ **SAN** (`api.shop.fr`, `*.shop.fr`) ;
- la **clé publique** du serveur ;
- une période de **validité** (90 jours chez Let's Encrypt) ;
- l'identité de la CA et sa **signature**.

Avant de signer, la CA vérifie que le demandeur contrôle bien le domaine, par exemple en lui faisant publier un enregistrement DNS `TXT` ou un fichier sur le site (c'est le protocole **ACME**, utilisé par cert-manager et certbot).

## La chaîne de confiance

Ton système (ou ton navigateur) contient une liste d'environ 150 **CA racines** de confiance. Les racines ne signent presque jamais directement les certificats de serveurs : elles signent des **CA intermédiaires**, qui signent les certificats.

```
CA racine (dans ton système)        ← fait confiance a priori
  └─ CA intermédiaire               ← signée par la racine
       └─ certificat api.shop.fr    ← signé par l'intermédiaire
```

Le client remonte la chaîne jusqu'à une racine qu'il connaît. Le serveur doit donc envoyer **son certificat et l'intermédiaire** (le fichier « fullchain »). Oublier l'intermédiaire est l'erreur la plus courante : les navigateurs la compensent souvent, mais `curl`, Java ou Python échouent.

## La poignée de main TLS 1.3, simplifiée

1. **Client Hello** : le client propose ses algorithmes, envoie sa part de l'échange de clé, et annonce le nom du site voulu (**SNI**, en clair).
2. **Server Hello** : le serveur choisit les algorithmes, envoie sa part de l'échange de clé. À partir de là, les deux ont calculé la même clé symétrique, sans jamais l'avoir transmise.
3. Le serveur envoie son **certificat** et une **signature** faite avec sa clé privée, qui prouve qu'il en est bien le propriétaire.
4. Le client **vérifie** : la chaîne remonte à une racine connue, le nom demandé est dans le SAN, le certificat n'a pas expiré.
5. Tout le reste circule chiffré en symétrique.

En TLS 1.3, tout ça prend **un seul aller-retour** (deux en TLS 1.2).

## Les erreurs et ce qu'elles veulent dire

| Erreur | Cause | Correction |
| --- | --- | --- |
| `certificate has expired` | date de fin dépassée | renouvellement automatique (cert-manager, certbot) |
| `unable to get local issuer certificate` | chaîne incomplète, ou CA interne inconnue du client | servir la fullchain ; installer la CA interne sur le client |
| `hostname mismatch` / `no alternative certificate subject name matches` | le nom demandé n'est pas dans le SAN | utiliser le bon nom, ou ajouter le nom au certificat |
| `self-signed certificate` | signé par lui-même, aucune CA | normal en dev ; en prod, utiliser une vraie CA |
| `wrong version number` | on parle TLS à un port qui répond en clair (ou l'inverse) | vérifier le port et le protocole |

`curl -k` (ou `--insecure`) désactive toutes ces vérifications. Utile une seconde pour diagnostiquer, dangereux s'il reste dans un script : on perd la garantie d'authenticité, donc toute protection contre l'interception.

## Inspecter un certificat

```bash
# ce que présente le serveur (chaîne, dates, noms)
openssl s_client -connect api.shop.fr:443 -servername api.shop.fr </dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName

# tester une IP précise avec le bon nom
curl -v --resolve api.shop.fr:443:10.0.0.5 https://api.shop.fr/
```

## mTLS : quand le client aussi montre un certificat

En TLS classique, seul le serveur prouve son identité. En **mTLS** (TLS mutuel), le client présente aussi un certificat. On l'utilise entre services internes : un **service mesh** (Istio, Linkerd) le met en place automatiquement entre tous les pods, ce qui garantit que seul le service `front` peut appeler `api`.

> **À retenir.** Le certificat lie un nom à une clé publique, sous la garantie d'une CA. Le client vérifie trois choses : la chaîne, le nom et la date. La clé privée ne quitte jamais le serveur, et le serveur doit envoyer la chaîne complète.
