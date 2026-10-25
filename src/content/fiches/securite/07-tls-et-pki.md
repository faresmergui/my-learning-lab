---
title: TLS et PKI
chapter: 7
order: 1
duration: 10
level: intermédiaire
tags:
- fondamentaux
cards:
- q: Que garantit TLS ?
  a: La **confidentialité** (chiffrement), l'**intégrité** (pas de modification en route) et l'**authentification** du serveur, et du client aussi en mTLS.
- q: Qu'est-ce qu'une chaîne de certificats ?
  a: Le certificat du serveur est signé par une **autorité intermédiaire**, elle-même signée par une **autorité racine** de confiance installée sur le client. Le serveur doit envoyer les intermédiaires.
- q: Qu'est-ce que le SAN d'un certificat ?
  a: 'Le *Subject Alternative Name* : la liste des **noms DNS ou IP** valides pour ce certificat. Les clients modernes ignorent le CN et ne regardent que le SAN.'
- q: Qu'est-ce que le mTLS ?
  a: 'TLS **mutuel** : le client présente aussi un certificat. Chaque côté vérifie l''autre. Utilisé entre microservices (service mesh) ou pour des API sensibles.'
- q: Comment voir le certificat présenté par un serveur ?
  a: '`openssl s_client -connect site:443 -servername site </dev/null | openssl x509 -noout -subject -issuer -dates -ext subjectAltName`.'
- q: Que fait cert-manager dans Kubernetes ?
  a: Il **demande et renouvelle** automatiquement des certificats (Let's Encrypt, Vault, CA interne) et les stocke dans des Secrets TLS.
- q: Quand utiliser une CA interne plutôt qu'une CA publique ?
  a: Pour les services internes, le mTLS ou des noms non publics (`*.svc`, `.internal`). Il faut alors distribuer sa racine à tous les clients.
- q: Différence entre les défis ACME HTTP-01 et DNS-01 ?
  a: '**HTTP-01** : servir un fichier sur le port 80 du domaine. **DNS-01** : publier un enregistrement TXT. Seul DNS-01 permet les wildcards et les services non exposés.'
- q: Qu'est-ce qu'une CSR ?
  a: 'Une demande de signature de certificat : la clé publique et les noms souhaités, signés par la clé privée du demandeur. La CA la vérifie et renvoie le certificat.'
- q: Pourquoi préfère-t-on des certificats courts à la révocation ?
  a: Les clients vérifient mal la révocation (CRL, OCSP). Un certificat de quelques jours ou semaines limite naturellement l'usage d'une clé volée.
quiz:
- q: Le navigateur accepte ton site, mais `curl` dans un conteneur répond `unable to get local issuer certificate`. Cause probable ?
  options:
  - Le certificat a expiré
  - Le serveur n'envoie pas le certificat intermédiaire, ou le conteneur n'a pas les CA racines
  - Le DNS est faux
  - TLS 1.3 n'est pas supporté
  answer: 1
  explain: Les navigateurs complètent parfois la chaîne tout seuls, les autres clients non. Vérifie la chaîne envoyée avec `openssl s_client -showcerts`, et le paquet `ca-certificates` de l'image.
- q: Un certificat pour `example.com` est-il valide pour `api.example.com` ?
  options:
  - Oui, toujours
  - Non, sauf si `api.example.com` ou `*.example.com` figure dans le SAN
  - Oui, si le CN est example.com
  - Seulement en HTTP/2
  answer: 1
  explain: 'Un joker `*.example.com` couvre un seul niveau : `api.example.com` oui, `v1.api.example.com` non, et `example.com` lui-même non plus.'
- q: Tu veux un certificat `*.shop.fr` via Let's Encrypt. Quel défi ACME utiliser ?
  options:
  - HTTP-01
  - DNS-01
  - TLS-ALPN-01
  - Aucun, les wildcards sont interdits
  answer: 1
  explain: 'Les certificats wildcard exigent le défi DNS-01 : il faut publier un enregistrement TXT, donc donner à cert-manager un accès à la zone DNS.'
- q: Tes pods appellent un service interne signé par ta CA interne et échouent avec « unable to get local issuer certificate ». Que faire ?
  options:
  - Ajouter `-k` dans le code
  - Installer la racine de la CA interne dans le magasin de confiance des images (ou la monter et la référencer)
  - Passer à HTTP
  - Renouveler le certificat
  answer: 1
  explain: Le client ne connaît pas ta CA. Désactiver la vérification supprimerait toute protection.
- q: cert-manager est installé, mais un certificat a expiré en prod. Quel contrôle aurait permis de l'éviter ?
  options:
  - Un certificat de 2 ans
  - Une alerte sur la date d'expiration réellement servie par l'endpoint
  - Passer en HTTP/3
  - Une CA interne
  answer: 1
  explain: L'automatisation peut échouer silencieusement (défi DNS cassé, quota). Une sonde externe sur le certificat servi détecte le problème avant l'expiration.
---

La fiche réseau « TLS et certificats, pas à pas » explique comment TLS chiffre une connexion et vérifie un certificat. Celle-ci regarde l'autre côté : **qui délivre** les certificats, comment on les **gère** dans une infra, et comment éviter qu'ils deviennent une source de pannes.


> **Les termes et outils cités dans cette fiche.**
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **VPN** : un tunnel chiffré qui relie un poste ou un site à un réseau privé à travers Internet.
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.
> - **proxy** : un intermédiaire qui reçoit les requêtes et les transmet à leur place.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.

## Le principe, en rappel

<!-- schema:handshake -->
<figure class="diagram"><svg viewBox="0 0 680 300" role="img" aria-label="La poignée de main TLS et la chaîne de certificats" style="--minw:560px"><defs><marker id="g5-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g5-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g5-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g5-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="20" y="14" width="110" height="40" rx="9"/></g><text x="75.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:0">client</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="300" y="14" width="110" height="40" rx="9"/></g><text x="355.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:0">serveur</text><line x1="75" y1="54" x2="75" y2="280" class="dg-grid"/><line x1="355" y1="54" x2="355" y2="280" class="dg-grid"/><path d="M77 80 L353 80" class="dg-l c" marker-end="url(#g5-c)" style="--d:1"/><text x="215.0" y="73.0" class="dg-s" text-anchor="middle" style="--d:1">ClientHello : versions, SNI</text><path d="M353 124 L77 124" class="dg-l c" marker-end="url(#g5-c)" style="--d:2"/><text x="215.0" y="117.0" class="dg-s" text-anchor="middle" style="--d:2">ServerHello + certificat + chaîne</text><path d="M77 214 L353 214" class="dg-l c" marker-end="url(#g5-c)" marker-start="url(#g5-c)" style="--d:3"/><text x="215.0" y="207.0" class="dg-s" text-anchor="middle" style="--d:3">échange de clés</text><path d="M77 256 L353 256" class="dg-l ok thick" marker-end="url(#g5-ok)" marker-start="url(#g5-ok)" style="--d:4"/><text x="215.0" y="249.0" class="dg-s" text-anchor="middle" style="--d:4">trafic chiffré</text><g class="dg-box dg-ghost dg-pop" style="--d:3"><rect x="86" y="140" width="258" height="40" rx="9"/></g><text x="215.0" y="165.0" class="dg-s" text-anchor="middle" style="--d:3">vérifie : CA connue ? nom dans le SAN ? date ?</text><rect x="452" y="14" width="214" height="270" rx="12" class="dg-zone "/><text x="464" y="32" class="dg-zl" text-anchor="start">chaîne de confiance</text><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="470" y="46" width="178" height="52" rx="9"/></g><text x="559.0" y="69.0" class="dg-t" text-anchor="middle" style="--d:4">CA racine</text><text x="559.0" y="87.0" class="dg-s" text-anchor="middle" style="--d:4">dans le magasin du système</text><g class="dg-box dg-pop" style="--d:5"><rect x="470" y="132" width="178" height="52" rx="9"/></g><text x="559.0" y="155.0" class="dg-t" text-anchor="middle" style="--d:5">CA intermédiaire</text><text x="559.0" y="173.0" class="dg-s" text-anchor="middle" style="--d:5">envoyée par le serveur</text><g class="dg-box dg-c dg-pop" style="--d:6"><rect x="470" y="218" width="178" height="52" rx="9"/></g><text x="559.0" y="241.0" class="dg-t" text-anchor="middle" style="--d:6">shop.example.com</text><text x="559.0" y="259.0" class="dg-s" text-anchor="middle" style="--d:6">certificat du site</text><path d="M559 98 L559 130" class="dg-l" marker-end="url(#g5-n)" style="--d:5"/><path d="M559 184 L559 216" class="dg-l" marker-end="url(#g5-n)" style="--d:6"/><text x="566" y="118" class="dg-s" text-anchor="start">signe</text><text x="566" y="204" class="dg-s" text-anchor="start">signe</text></svg><figcaption>L&#x27;erreur la plus fréquente : le serveur oublie d&#x27;envoyer le certificat intermédiaire.</figcaption></figure>
<!-- /schema:handshake -->

Le serveur présente un **certificat** qui lie son nom à sa clé publique, signé par une **autorité de certification** (CA). Le client vérifie la signature en remontant jusqu'à une CA racine qu'il connaît déjà. La **PKI** (infrastructure à clé publique) désigne l'ensemble : les autorités, les certificats, les règles de délivrance et de révocation.

## CA publique ou CA interne

| | CA publique (Let's Encrypt, DigiCert…) | CA interne (la tienne) |
| --- | --- | --- |
| Reconnue par | tous les navigateurs et systèmes | seulement les clients où tu l'installes |
| Noms possibles | domaines publics que tu contrôles | n'importe quoi : `api.shop.svc`, `db.internal` |
| Usage | sites et API exposés sur Internet | services internes, mTLS, VPN |
| Outils | ACME : certbot, cert-manager | Vault PKI, step-ca, cert-manager (issuer CA), service mesh |

Le piège d'une CA interne : il faut **distribuer sa racine** à tous les clients (images de conteneurs, postes, outils de CI). Sinon : `unable to get local issuer certificate`.

La clé privée de la **racine** est l'objet le plus sensible de la PKI : avec elle, on peut fabriquer un certificat valide pour n'importe quel nom. On la garde hors ligne et on signe le quotidien avec une **intermédiaire**, qu'on pourra révoquer et remplacer si elle est compromise.

## Comment une CA publique vérifie que le domaine est à toi : ACME

Let's Encrypt délivre des certificats gratuitement et automatiquement grâce au protocole **ACME**. Avant de signer, il lance un **défi** pour prouver que tu contrôles le domaine :

| Défi | Ce que tu dois faire | Quand l'utiliser |
| --- | --- | --- |
| HTTP-01 | servir un fichier précis sur `http://ton-domaine/.well-known/acme-challenge/…` | site joignable sur le port 80 |
| DNS-01 | publier un enregistrement `TXT` `_acme-challenge.ton-domaine` | wildcard (`*.shop.fr`), services non exposés |

## Le cycle de vie d'un certificat

1. **Générer** une clé privée (sur le serveur, elle n'en sort pas).
2. **Demander** un certificat avec une CSR (*Certificate Signing Request*) : « voici ma clé publique et les noms que je veux ».
3. La CA **vérifie** (défi ACME, ou politique interne) et **signe**.
4. **Déployer** le certificat et la chaîne sur le serveur ou le proxy.
5. **Renouveler** avant l'expiration ; recommencer.
6. **Révoquer** si la clé privée a fui.

Les durées de validité raccourcissent : 90 jours chez Let's Encrypt, et l'industrie se dirige vers des certificats publics de 47 jours d'ici 2029. Le renouvellement **manuel** n'est plus tenable : il doit être automatique.

**La révocation** reste imparfaite : les clients vérifient mal les listes de révocation (CRL, OCSP). En pratique, la meilleure protection contre une clé volée est une **durée de vie courte**.

## Lire un certificat

```bash
# ce que présente le serveur
openssl s_client -connect shop.example.com:443 -servername shop.example.com </dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName

openssl x509 -in tls.crt -noout -text | less        # tout le détail
openssl verify -CAfile chain.pem tls.crt            # la chaîne est-elle valide ?
```

Ce qu'il faut regarder : **subject** et **SAN** (les noms couverts), **issuer** (qui a signé), **notBefore / notAfter** (la période de validité).

## Les erreurs classiques

| Erreur | Cause |
| --- | --- |
| `certificate has expired` | renouvellement oublié ou cassé |
| `hostname mismatch` | nom absent du SAN |
| `unable to get local issuer certificate` | intermédiaire manquant, ou CA interne absente du client |
| `self-signed certificate` | CA interne non installée sur le client |

## Automatiser avec cert-manager

Dans Kubernetes, **cert-manager** fait tout le cycle de vie. Tu décris le certificat voulu ; il génère la clé, passe le défi ACME, stocke le résultat dans un Secret, et renouvelle tout seul (par défaut 30 jours avant l'expiration).

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata: { name: shop-tls, namespace: shop }
spec:
  secretName: shop-tls                 # le Secret où il range clé et certificat
  dnsNames: [shop.example.com, www.shop.example.com]
  issuerRef: { name: letsencrypt, kind: ClusterIssuer }   # qui signe
```

Un **Issuer** (ou ClusterIssuer) décrit la CA à utiliser : Let's Encrypt via ACME, une CA interne, Vault. L'Ingress n'a plus qu'à référencer le Secret `shop-tls`.

## mTLS entre services

Avec le **TLS mutuel**, le client présente aussi un certificat : chaque service prouve son identité à l'autre. C'est la base du **zero trust** entre services. Le faire à la main pour des dizaines de services est lourd ; un **service mesh** (Istio, Linkerd) s'en charge : il délivre à chaque pod un certificat lié à sa ServiceAccount, valable quelques heures, et chiffre automatiquement tout le trafic interne.

> **À retenir.** Une CA publique pour ce qui est exposé, une CA interne (avec une racine bien gardée) pour l'interne. Automatise tout le cycle de vie (cert-manager, ACME), préfère des certificats courts à la révocation, et surveille quand même la date d'expiration avec une alerte (`probe_ssl_earliest_cert_expiry` avec le blackbox exporter) : un certificat expiré reste l'une des pannes les plus bêtes et les plus fréquentes.
