---
title: Registres, tags et distribution
chapter: 8
order: 1
duration: 10
tags:
- Docker
- registre
- tags
cards:
- q: Comment se décompose un nom d'image complet ?
  a: '`registre/espace/dépôt:tag@digest`, par exemple `registry.shop.fr/equipe/api:2.4.1@sha256:ab…`. Sans registre, Docker suppose `docker.io` ; sans espace, `library/` ; sans tag, `latest`.'
- q: Différence entre un tag et un digest ?
  a: 'Un **tag** est une étiquette **déplaçable** : `api:2.4` peut désigner une autre image demain. Un **digest** (`@sha256:…`) est l''empreinte du contenu : il désigne **toujours** exactement la même image.'
- q: Pourquoi éviter `latest` en production ?
  a: Il ne dit pas **quelle version** tourne, change sans prévenir et empêche un retour arrière fiable. On déploie un tag immuable (version, ou SHA du commit) et idéalement le digest.
- q: Quelle stratégie de tags pour une CI ?
  a: Un tag **immuable par build** (`api:git-3f2a9c1`), un tag de **version** à la publication (`api:2.4.1`), éventuellement des tags flottants pour les humains (`api:2.4`, `api:2`). On active l'**immuabilité des tags** dans le registre quand c'est possible.
- q: Quels registres sont courants en entreprise ?
  a: '**Harbor** (open source, scan, signature, réplication), **GitLab Container Registry**, **GitHub Container Registry** (ghcr.io), et ceux des clouds : **ECR** (AWS), **Artifact Registry** (Google), **ACR** (Azure), **Quay** (Red Hat).'
- q: Pourquoi Docker Hub peut-il bloquer une CI ?
  a: 'Il **limite le nombre de téléchargements** pour les utilisateurs anonymes et gratuits. Une CI qui tire beaucoup d''images échoue alors (`toomanyrequests`). Solution : s''authentifier, ou passer par un **cache** (proxy) de registre comme Harbor ou ECR pull-through.'
quiz:
- q: La production tourne `api:2.4`. Un collègue republie `api:2.4` avec un bug. Que se passe-t-il au prochain redémarrage d'un nœud ?
  options:
  - Rien, l'ancienne image reste
  - Le nœud peut tirer la nouvelle image sous le même tag et lancer la version boguée
  - Docker refuse le tag
  - Kubernetes détecte le problème
  answer: 1
  explain: Un tag est déplaçable. Déployer par tag immuable ou par digest évite qu'un même nom change de contenu.
- q: Comment vérifier, avant de déployer, qu'une image a bien été construite par ta CI et pas modifiée ?
  options:
  - Regarder sa taille
  - Vérifier sa signature (cosign) et son digest
  - Lire son tag
  - La lancer en local
  answer: 1
  explain: La signature lie l'image (son digest) à l'identité de la CI ; un contrôle d'admission peut l'exiger dans Kubernetes.
level: intermédiaire
---

Une image construite sur une machine doit arriver sur d'autres : les serveurs de production, les nœuds Kubernetes, les postes des collègues. C'est le rôle des **registres**. Bien nommer et étiqueter les images est ce qui rend un déploiement traçable et un retour arrière possible.

> **Les outils cités dans cette fiche.**
> - **registre** (registry) : un serveur qui stocke et distribue des images, selon le standard de distribution OCI.
> - **tag** : une étiquette lisible sur une image (`2.4.1`) ; **digest** : son empreinte `sha256` unique.
> - **Docker Hub** : le registre public par défaut.
> - **Harbor** : un registre open source d'entreprise (droits par projet, scan, signature, réplication, cache).
> - **ECR**, **GHCR**, **GitLab Registry**, **Quay** : des registres hébergés.
> - **cosign** (projet Sigstore) : signe et vérifie des images.
> - **SBOM** (Software Bill of Materials) : la liste des composants d'une image.
> - **nœud** : une machine (physique ou virtuelle) membre d'un cluster.
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.
> - **commit** : un instantané enregistré des modifications dans Git, avec un message et un auteur.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **CD** : le déploiement (ou la livraison) continu : ce qui a passé la CI est déployé automatiquement.
> - **IAM** : la gestion des identités et des droits (qui peut faire quoi).

## Comprendre : un nom d'image

```
registry.shop.fr / equipe / api : 2.4.1 @ sha256:3f2a…
└── registre ──┘   └espace┘ └dépôt┘ └tag┘   └── digest (contenu exact)

nginx            =  docker.io/library/nginx:latest
fares/outil:1.0  =  docker.io/fares/outil:1.0
```

Une image publiée est composée d'un **manifeste** (la liste des couches et la configuration) et des **couches**, chacune identifiée par son empreinte. Pour plusieurs architectures, un **index** pointe vers un manifeste par plateforme.

## Publier

```bash
docker login registry.shop.fr                     # (ou un jeton de CI)
docker build -t registry.shop.fr/equipe/api:2.4.1 .
docker push registry.shop.fr/equipe/api:2.4.1
docker buildx imagetools inspect registry.shop.fr/equipe/api:2.4.1   # digest et plateformes
docker pull registry.shop.fr/equipe/api@sha256:3f2a…                 # tirer par digest
```

Sur AWS : `aws ecr get-login-password | docker login --username AWS --password-stdin <compte>.dkr.ecr.<région>.amazonaws.com`.

## Tags mobiles, tags immuables

| Tag | Mobile ? | Usage |
| --- | --- | --- |
| `latest` | oui | jamais en production |
| `2`, `2.4` | oui | confort humain, suivre les correctifs |
| `2.4.1` | devrait être fixe | version publiée |
| `git-3f2a9c1` | fixe | traçabilité : quel commit tourne |
| `@sha256:…` | **toujours fixe** | ce qu'on déploie réellement |

Une bonne CI produit à chaque build un tag lié au commit, ajoute le tag de version à la publication, et le déploiement (manifeste Kubernetes, Helm, Argo CD) référence une version immuable. Beaucoup de registres proposent l'**immuabilité des tags** : impossible de republier `2.4.1`.

## Les registres en entreprise

| Besoin | Réponse |
| --- | --- |
| droits par équipe, audit | projets et rôles du registre (Harbor, ECR + IAM) |
| limiter les téléchargements depuis Internet | **cache proxy** (Harbor proxy cache, ECR pull-through, registry mirror) |
| plusieurs sites ou régions | **réplication** entre registres |
| maîtriser l'espace | **règles de rétention** (garder les 20 derniers tags, supprimer les images non taguées) |
| sécurité | scan automatique à l'envoi, signature, blocage des images vulnérables |

Docker Hub limite les téléchargements anonymes et gratuits : une CI qui tire beaucoup d'images de base doit s'authentifier ou passer par un cache.

## Signer et décrire

```bash
cosign sign registry.shop.fr/equipe/api@sha256:3f2a…        # signature (souvent « keyless », liée à l'identité OIDC de la CI)
cosign verify --certificate-identity-regexp '.*gitlab.*' \
  --certificate-oidc-issuer https://gitlab.com registry.shop.fr/equipe/api@sha256:3f2a…
docker buildx build --sbom=true --provenance=true -t … --push .   # SBOM et provenance attachées
```

La **signature** prouve qui a construit l'image ; la **provenance** dit comment ; le **SBOM** dit ce qu'elle contient. Dans Kubernetes, un contrôleur d'admission (Kyverno, policy-controller de Sigstore) peut refuser les images non signées. La fiche Sécurité sur la supply chain développe ces notions.

> **À retenir.** Un nom d'image complet : registre, espace, dépôt, tag, digest. Les tags se déplacent, le digest jamais : on déploie une version immuable, pas `latest`. En entreprise, un registre avec droits, cache proxy, rétention, scan et signature. Docker Hub limite les téléchargements : authentifier la CI ou passer par un cache.
