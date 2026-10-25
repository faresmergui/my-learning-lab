---
title: Sécuriser la supply chain
chapter: 5
order: 1
duration: 10
level: intermédiaire
tags:
- DevSecOps
cards:
- q: Qu'est-ce qu'une attaque de la supply chain logicielle ?
  a: 'Une attaque qui vise ce qui **produit** ou **compose** le logiciel : dépendance piégée, pipeline CI compromis, image modifiée dans le registre. Exemples connus : SolarWinds, xz-utils, Codecov.'
- q: Qu'est-ce qu'un SBOM ?
  a: 'Une **nomenclature logicielle** : la liste de tous les composants et versions d''une appli ou d''une image (formats SPDX ou CycloneDX). Indispensable pour savoir si on est touché par une nouvelle CVE.'
- q: À quoi sert la signature d'images avec cosign ?
  a: À prouver qu'une image vient bien de **ta CI** et n'a pas été modifiée. Le cluster peut refuser les images non signées, avec Kyverno par exemple.
- q: Qu'est-ce que SLSA ?
  a: 'Un cadre de niveaux de maturité pour la chaîne de build : build scripté, provenance générée, build isolé et non modifiable.'
- q: Pourquoi épingler les dépendances et les actions CI par empreinte ?
  a: Un tag (`v4`, `latest`) peut être **déplacé** vers un contenu malveillant. Une empreinte (`@sha256:…` ou un SHA de commit) désigne un contenu précis et immuable.
- q: Qu'est-ce qu'un SBOM et à quoi sert-il ?
  a: La liste des composants d'un artefact (bibliothèques, versions, licences). Quand une CVE majeure sort, il permet de savoir immédiatement quelles images sont concernées.
- q: Que garantit la signature keyless avec cosign ?
  a: Que l'image a été signée par une identité précise (par exemple le workflow de release d'un dépôt), via un certificat éphémère obtenu par OIDC et inscrit dans un journal de transparence.
- q: Différence entre signature et provenance SLSA ?
  a: 'La signature dit **qui** a signé. La provenance décrit **comment** l''artefact a été construit : dépôt, commit, CI, commandes.'
- q: Pourquoi épingler une action GitHub par SHA ?
  a: Un tag (`@v4`) peut être déplacé vers un autre code. Un SHA de commit est immuable. L'action s'exécute avec les secrets du job.
quiz:
- q: Une nouvelle CVE critique touche une bibliothèque de logs. Comment savoir vite quelles images sont concernées ?
  options:
  - Regarder chaque Dockerfile à la main
  - Chercher dans les SBOM générés à chaque build
  - Attendre un incident
  - Scanner le code source seulement
  answer: 1
  explain: Avec un SBOM par image, stocké à côté de l'image, la recherche prend quelques minutes au lieu de quelques jours.
- q: 'Ton workflow CI utilise `uses: une-action/deploy@v2`. Quel risque ?'
  options:
  - Aucun
  - Le tag v2 peut être déplacé vers un code malveillant si le dépôt de l'action est compromis
  - L'action sera trop lente
  - Les secrets seront visibles
  answer: 1
  explain: Épingle par SHA de commit, et limite les permissions du jeton du workflow au strict nécessaire.
- q: Ton équipe signe toutes ses images avec cosign, mais le cluster accepte n'importe quelle image. Que vaut cette signature ?
  options:
  - Elle protège déjà le cluster
  - 'Pas grand-chose : sans vérification à l''admission, une image non signée passe aussi'
  - Elle chiffre l'image
  - Elle remplace le scan de CVE
  answer: 1
  explain: Il faut une politique d'admission (Kyverno, policy-controller) qui refuse les images non signées par ta CI.
- q: Une CVE critique sort sur une bibliothèque de compression. Qu'est-ce qui te permet de savoir en 5 minutes quelles images de prod l'embarquent ?
  options:
  - Les logs applicatifs
  - Les SBOM générés à chaque build
  - Les tags des images
  - Les NetworkPolicies
  answer: 1
  explain: 'Le SBOM liste les composants exacts de chaque image : une recherche dans les SBOM suffit.'
- q: Pourquoi attendre quelques jours avant d'adopter une version de dépendance tout juste publiée (hors correctif critique) ?
  options:
  - Pour économiser de la bande passante
  - Les versions malveillantes sont souvent détectées et retirées dans les 24 à 48 h
  - Les versions récentes sont toujours instables
  - Pour respecter SLSA
  answer: 1
  explain: Ce délai réduit le risque d'embarquer un paquet compromis tout en gardant des mises à jour régulières.
---

Ton code peut être parfait, il passe quand même par des **dépendances** écrites par d'autres, une **CI** qui le construit, un **registre** qui stocke les images et un **cluster** qui les exécute. La **supply chain** (chaîne d'approvisionnement logicielle), c'est tout ce chemin. Chaque maillon peut être attaqué, et un attaquant préfère souvent le maillon faible au code lui-même.


> **Les termes et outils cités dans cette fiche.**
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.
> - **CVE** : l'identifiant public d'une vulnérabilité connue (CVE-2024-3094).
> - **artefact** : un fichier produit par une étape du pipeline (binaire, image, rapport) et transmis aux suivantes.
> - **OIDC** : OpenID Connect, le standard de connexion par un fournisseur d'identité, qui délivre des jetons signés.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **commit** : un instantané enregistré des modifications dans Git, avec un message et un auteur.
> - **branche** : une ligne de développement parallèle dans Git.
> - **runner** : la machine ou le conteneur qui exécute les jobs d'un pipeline CI.

## Pourquoi c'est devenu un sujet majeur

Quelques attaques ont marqué les esprits, et chacune vise un maillon différent :

| Attaque | Maillon | Ce qui s'est passé |
| --- | --- | --- |
| SolarWinds (2020) | build | du code malveillant injecté pendant la compilation, distribué signé à 18 000 clients |
| Codecov (2021) | CI | un script de CI modifié exfiltrait les variables d'environnement (donc les secrets) des clients |
| xz-utils (2024) | dépendance | un mainteneur gagne la confiance du projet pendant 2 ans puis glisse une porte dérobée dans SSH |
| typosquatting npm / PyPI | dépendance | des paquets aux noms proches (`reqeusts`) qui volent des identifiants à l'installation |

Une application moderne a souvent des **centaines** de dépendances, directes et indirectes (les dépendances de tes dépendances). Tu n'en as lu aucune.

<!-- schema:chaine -->
<figure class="diagram"><svg viewBox="0 0 680 262" role="img" aria-label="La chaîne d&#x27;approvisionnement logicielle" style="--minw:560px"><defs><marker id="g3-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g3-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g3-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g3-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="14" y="96" width="98" height="52" rx="9"/></g><text x="63.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:0">code</text><text x="63" y="40" class="dg-s" text-anchor="middle" style="--d:0"><tspan x="63" dy="0">revue, commits</tspan><tspan x="63" dy="14">signés</tspan></text><text x="63" y="180" class="dg-at" text-anchor="middle" style="--d:0">⚠</text><text x="63" y="196" class="dg-as" text-anchor="middle" style="--d:0">compte volé</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="125" y="96" width="98" height="52" rx="9"/></g><text x="174.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:1">dépendances</text><path d="M112 122 L124 122" class="dg-l c" marker-end="url(#g3-c)"/><text x="174" y="40" class="dg-s" text-anchor="middle" style="--d:1">lock file, scan</text><text x="174" y="180" class="dg-at" text-anchor="middle" style="--d:1">⚠</text><text x="174" y="196" class="dg-as" text-anchor="middle" style="--d:1">paquet piégé</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="236" y="96" width="98" height="52" rx="9"/></g><text x="285.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:2">CI</text><path d="M223 122 L235 122" class="dg-l c" marker-end="url(#g3-c)"/><text x="285" y="40" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="285" dy="0">OIDC, runners</tspan><tspan x="285" dy="14">isolés</tspan></text><text x="285" y="180" class="dg-at" text-anchor="middle" style="--d:2">⚠</text><text x="285" y="196" class="dg-as" text-anchor="middle" style="--d:2">secrets volés</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="347" y="96" width="98" height="52" rx="9"/></g><text x="396.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:3">image</text><path d="M334 122 L346 122" class="dg-l c" marker-end="url(#g3-c)"/><text x="396" y="40" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="396" dy="0">SBOM, scan,</tspan><tspan x="396" dy="14">signature</tspan></text><text x="396" y="180" class="dg-at" text-anchor="middle" style="--d:3">⚠</text><text x="396" y="196" class="dg-as" text-anchor="middle" style="--d:3">contenu modifié</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="458" y="96" width="98" height="52" rx="9"/></g><text x="507.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:4">registre</text><path d="M445 122 L457 122" class="dg-l c" marker-end="url(#g3-c)"/><text x="507" y="40" class="dg-s" text-anchor="middle" style="--d:4">tags immuables</text><text x="507" y="180" class="dg-at" text-anchor="middle" style="--d:4">⚠</text><text x="507" y="196" class="dg-as" text-anchor="middle" style="--d:4">image remplacée</text><g class="dg-box dg-c dg-pop" style="--d:5"><rect x="569" y="96" width="98" height="52" rx="9"/></g><text x="618.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:5">cluster</text><path d="M556 122 L568 122" class="dg-l c" marker-end="url(#g3-c)"/><text x="618" y="40" class="dg-s" text-anchor="middle" style="--d:5"><tspan x="618" dy="0">admission</tspan><tspan x="618" dy="14">vérifie</tspan></text><text x="618" y="180" class="dg-at" text-anchor="middle" style="--d:5">⚠</text><text x="618" y="196" class="dg-as" text-anchor="middle" style="--d:5">image non signée</text><text x="14" y="20" class="dg-zl" text-anchor="start">protection</text><text x="14" y="222" class="dg-zl" text-anchor="start">attaque possible</text><path d="M14 236 L666 236" class="dg-l dash" marker-end="url(#g3-n)"/><text x="340" y="254" class="dg-s" text-anchor="middle">la confiance doit se vérifier à chaque maillon</text></svg><figcaption>Une signature vérifiée à l&#x27;admission garantit que l&#x27;image vient bien de ta CI.</figcaption></figure>
<!-- /schema:chaine -->

## Les notions clés, une par une

**Le lock file** (`package-lock.json`, `go.sum`, `poetry.lock`) fige la version **exacte** et l'empreinte de chaque dépendance. Sans lui, deux builds du même code peuvent embarquer des versions différentes, dont une piégée publiée entre-temps. Il se commite toujours.

**Le SBOM** (*Software Bill of Materials*) est la **liste des ingrédients** d'une image ou d'un binaire : chaque bibliothèque, sa version, sa licence. Le jour où une CVE comme Log4Shell sort, il permet de répondre en minutes à « sommes-nous concernés, et où ? ».

**La signature** prouve qu'un artefact vient bien de toi et n'a pas été modifié. Avec **cosign** en mode *keyless*, il n'y a même pas de clé à gérer : la CI s'identifie par OIDC (voir la fiche sur les secrets), reçoit un certificat éphémère, signe l'image, et la signature est inscrite dans un **journal public de transparence** (Rekor). Le certificat dit « signé par le workflow `release.yml` du dépôt `fares/shop` ».

**La provenance** (format **SLSA**) va plus loin : une attestation signée qui décrit **comment** l'artefact a été construit (quel dépôt, quel commit, quelle CI, quelles commandes). On peut alors refuser une image qui n'a pas été construite par ta CI officielle, même si elle porte ta signature.

**Le tag contre le digest.** Un tag (`api:2.1`) est une étiquette **mobile** : n'importe qui ayant les droits peut pousser un autre contenu sous le même tag. Un digest (`api@sha256:3f2c…`) est l'**empreinte** du contenu : si un octet change, le digest change. Déployer par digest garantit qu'on exécute exactement ce qui a été testé et signé.

**L'épinglage des actions de CI.** `uses: actions/checkout@v4` suit un tag qui peut être déplacé. `uses: actions/checkout@<SHA du commit>` ne bouge jamais. Les actions tierces s'exécutent avec les droits et les secrets du job : elles méritent la même méfiance qu'une dépendance.

## Les protections, maillon par maillon

| Maillon | Mesures |
| --- | --- |
| Code | revue obligatoire, branches protégées, commits signés |
| Dépendances | lock files, Renovate ou Dependabot pour les mises à jour, scan (Trivy, Grype), sources de confiance |
| CI | runners isolés, OIDC plutôt que des secrets, actions épinglées par SHA, droits minimaux du jeton de CI |
| Image | SBOM, scan, signature cosign, provenance SLSA |
| Registre | accès restreint en écriture, tags immuables |
| Cluster | admission qui vérifie signature et provenance (Kyverno, Sigstore policy-controller) |

Le dernier maillon ferme la boucle : signer ne sert à rien si personne ne **vérifie**. Le contrôleur d'admission du cluster refuse tout pod dont l'image n'est pas signée par ta CI.

## En pratique

```bash
# Générer un SBOM
syft registry.local/api:2.1 -o cyclonedx-json > sbom.json

# Signer en mode keyless depuis la CI (identité OIDC)
cosign sign registry.local/api@sha256:3f2c…

# Vérifier : la signature doit venir de ce dépôt et de cet émetteur OIDC
cosign verify registry.local/api@sha256:3f2c… \
  --certificate-identity-regexp 'https://gitlab.com/fares/.*' \
  --certificate-oidc-issuer https://gitlab.com
```

## Mettre à jour sans se faire piéger

Les mises à jour corrigent des CVE, mais une nouvelle version peut aussi être la version piégée. Un équilibre raisonnable :

- des mises à jour **régulières et automatisées** (Renovate), regroupées, testées par la CI ;
- un **délai** de quelques jours avant d'adopter une version tout juste publiée (les paquets malveillants sont souvent retirés en 24 à 48 h) ;
- les correctifs de sécurité critiques, eux, appliqués vite.

> **À retenir.** Chaque maillon entre ton code et la prod peut être attaqué. Fige tes dépendances (lock files), sache ce que contiennent tes images (SBOM), signe-les depuis la CI, vérifie la signature à l'admission, et déploie par **digest** : `api:2.1` peut changer de contenu, `api@sha256:3f2c…` jamais.
