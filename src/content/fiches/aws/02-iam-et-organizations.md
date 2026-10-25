---
title: IAM, rôles et organisation des comptes
chapter: 2
order: 1
duration: 13
tags:
- AWS SAA
- IAM
- sécurité
cards:
- q: Différence entre un utilisateur IAM et un rôle IAM ?
  a: 'Un **utilisateur** a des identifiants permanents (mot de passe, clés d''accès). Un **rôle** n''a pas d''identifiants : on l''**endosse** pour obtenir des identifiants temporaires via STS. On préfère les rôles partout (instances, Lambda, humains via SSO).'
- q: Comment AWS évalue-t-il une requête face aux politiques ?
  a: Tout est **refusé par défaut**. Un `Allow` explicite autorise, mais un `Deny` explicite l'emporte **toujours**, où qu'il soit (politique d'identité, de ressource, SCP, limite de permissions).
- q: Quels sont les éléments d'une déclaration de politique IAM ?
  a: '`Effect` (Allow ou Deny), `Action` (`s3:GetObject`), `Resource` (l''ARN visé) et éventuellement `Condition` (IP source, MFA, tag, région…). Pour une politique de ressource, `Principal` indique qui est concerné.'
- q: Comment une instance EC2 obtient-elle des droits sur S3 sans clé stockée ?
  a: Avec un **rôle IAM** attaché via un **profil d'instance**. Le SDK récupère automatiquement des identifiants temporaires renouvelés depuis le service de métadonnées.
- q: Qu'est-ce qu'une SCP ?
  a: 'Une **Service Control Policy** d''AWS Organizations : elle fixe le **maximum** de ce qui est permis dans un compte ou une unité d''organisation. Elle n''accorde aucun droit, elle en retire. Même le root du compte membre est limité.'
- q: Comment donner à un compte A l'accès à un bucket du compte B ?
  a: Soit une **politique de bucket** dans B qui autorise le principal de A, soit un **rôle** dans B que A peut endosser (`sts:AssumeRole`). Dans les deux cas, A doit aussi avoir le droit de son côté.
- q: Que faire du compte root ?
  a: MFA activé, aucune clé d'accès, ne l'utiliser que pour les quelques tâches qui l'exigent (changer le support, fermer le compte). Le quotidien passe par IAM Identity Center ou des rôles.
quiz:
- q: Une politique d'identité autorise `s3:*` mais une SCP refuse `s3:DeleteBucket`. L'utilisateur peut-il supprimer un bucket ?
  options:
  - Oui, son Allow suffit
  - Non, le Deny de la SCP l'emporte
  - Seulement en root
  - Oui si le bucket est vide
  answer: 1
  explain: Un Deny explicite gagne toujours, et la SCP limite tous les principaux du compte.
- q: Une application sur EC2 a des clés d'accès écrites dans son fichier de configuration. Que recommandes-tu ?
  options:
  - Les chiffrer dans le fichier
  - Les remplacer par un rôle IAM attaché à l'instance
  - Les mettre en variable d'environnement
  - Les faire tourner chaque année
  answer: 1
  explain: 'Un rôle donne des identifiants temporaires et automatiques : plus rien à stocker ni à faire fuiter.'
- q: Les développeurs doivent pouvoir créer des rôles pour leurs Lambda sans pouvoir se donner plus de droits qu'eux. Quel mécanisme ?
  options:
  - Une SCP
  - Une limite de permissions (permissions boundary) imposée aux rôles créés
  - Un groupe IAM
  - CloudTrail
  answer: 1
  explain: La limite de permissions plafonne les droits d'un rôle ou utilisateur, quels que soient ceux qu'on lui attache.
level: intermédiaire
---

**IAM** (Identity and Access Management) décide qui peut faire quoi sur quelles ressources. C'est le service le plus important de toute la sécurité AWS, et le domaine le plus lourd de la certification (30 % de la note sur la sécurité). La plupart des incidents réels viennent d'un droit trop large ou d'une clé qui a fuité.

> **Les outils cités dans cette fiche.**
> - **IAM** : le service qui gère les identités (utilisateurs, groupes, rôles) et leurs droits (politiques).
> - **politique** (policy) : un document JSON qui autorise ou refuse des actions sur des ressources.
> - **STS** (Security Token Service) : délivre des identifiants **temporaires** quand on endosse un rôle.
> - **MFA** (authentification multifacteur) : un second facteur (application, clé physique) en plus du mot de passe.
> - **IAM Identity Center** (ex-AWS SSO) : connecte l'annuaire de l'entreprise (Entra ID, Okta, Google) à tous les comptes AWS.
> - **AWS Organizations** : regroupe plusieurs comptes AWS sous une organisation, avec facturation unique et règles communes.
> - **SCP** (Service Control Policy) : une politique d'Organizations qui plafonne ce qui est permis dans des comptes.
> - **S3** : le stockage objet d'AWS : des fichiers rangés dans des buckets, accessibles par HTTP.
> - **SQS** : le service de files de messages d'AWS.
> - **KMS** : le service de gestion des clés de chiffrement.
> - **SDK** : une bibliothèque de code fournie pour utiliser un service depuis un langage de programmation.

## Comprendre : identités et politiques

| Identité | Identifiants | Usage |
| --- | --- | --- |
| compte root | email + mot de passe | presque jamais (MFA, aucune clé) |
| utilisateur IAM | mot de passe, clés d'accès **permanentes** | à éviter ; cas historiques |
| groupe | (aucun) | regrouper des utilisateurs pour leur attacher des politiques |
| rôle | identifiants **temporaires** via STS | instances, Lambda, accès entre comptes, humains via SSO |

Une politique ressemble à ceci :

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::shop-factures/*",
      "Condition": { "Bool": { "aws:SecureTransport": "true" } }
    }
  ]
}
```

## Comment AWS décide

<!-- schema:decision -->
<figure class="diagram"><svg viewBox="0 0 680 390" role="img" aria-label="Comment AWS décide d&#x27;autoriser une requête" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="40" y="44" class="dg-ct" text-anchor="middle">requête</text><path d="M70 40 L108 40" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="110" y="16" width="330" height="48" rx="9"/></g><text x="275.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:0">Un Deny explicite quelque part ?</text><g class="dg-box dg-a dg-pop" style="--d:0"><rect x="520" y="22" width="146" height="36" rx="9"/></g><text x="593.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:0">REFUS</text><path d="M440 40 L518 40" class="dg-l a" marker-end="url(#g1-a)"/><text x="479.0" y="33.0" class="dg-s" text-anchor="middle">oui</text><path d="M275 64 L275 96" class="dg-l c" marker-end="url(#g1-c)" style="--d:0"/><text x="285" y="84" class="dg-s" text-anchor="start">non</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="110" y="98" width="330" height="48" rx="9"/></g><text x="275.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:1">Une SCP de l&#x27;organisation l&#x27;autorise ?</text><g class="dg-box dg-a dg-pop" style="--d:1"><rect x="520" y="104" width="146" height="36" rx="9"/></g><text x="593.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:1">REFUS</text><path d="M440 122 L518 122" class="dg-l a" marker-end="url(#g1-a)"/><text x="479.0" y="115.0" class="dg-s" text-anchor="middle">non</text><path d="M275 146 L275 178" class="dg-l c" marker-end="url(#g1-c)" style="--d:1"/><text x="285" y="166" class="dg-s" text-anchor="start">oui</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="110" y="180" width="330" height="48" rx="9"/></g><text x="275.0" y="209.0" class="dg-t" text-anchor="middle" style="--d:2">Un Allow (identité ou ressource) ?</text><g class="dg-box dg-a dg-pop" style="--d:2"><rect x="520" y="186" width="146" height="36" rx="9"/></g><text x="593.0" y="209.0" class="dg-t" text-anchor="middle" style="--d:2">REFUS par défaut</text><path d="M440 204 L518 204" class="dg-l a" marker-end="url(#g1-a)"/><text x="479.0" y="197.0" class="dg-s" text-anchor="middle">non</text><path d="M275 228 L275 260" class="dg-l c" marker-end="url(#g1-c)" style="--d:2"/><text x="285" y="248" class="dg-s" text-anchor="start">oui</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="110" y="262" width="330" height="48" rx="9"/></g><text x="275.0" y="291.0" class="dg-t" text-anchor="middle" style="--d:3">Limite de permissions et session OK ?</text><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="520" y="268" width="146" height="36" rx="9"/></g><text x="593.0" y="291.0" class="dg-t" text-anchor="middle" style="--d:3">REFUS</text><path d="M440 286 L518 286" class="dg-l a" marker-end="url(#g1-a)"/><text x="479.0" y="279.0" class="dg-s" text-anchor="middle">non</text><path d="M275 310 L275 342" class="dg-l ok" marker-end="url(#g1-ok)" style="--d:3"/><text x="285" y="330" class="dg-s" text-anchor="start">oui</text><g class="dg-box dg-ok dg-pop" style="--d:4"><rect x="185" y="344" width="180" height="38" rx="9"/></g><text x="275.0" y="368.0" class="dg-t" text-anchor="middle" style="--d:4">AUTORISÉ</text><path d="M275 312 L275 342" class="dg-l ok" marker-end="url(#g1-ok)"/></svg><figcaption>Un seul Deny suffit à refuser ; sans Allow explicite, la réponse est non.</figcaption></figure>
<!-- /schema:decision -->

Trois règles suffisent pour la plupart des questions : **refus par défaut**, **un Allow ouvre**, **un Deny explicite gagne toujours**.

## Les types de politiques

| Type | Attachée à | Effet |
| --- | --- | --- |
| politique d'identité | utilisateur, groupe, rôle | ce que cette identité peut faire |
| politique de ressource | bucket S3, file SQS, clé KMS… | qui peut agir sur cette ressource (contient un `Principal`) |
| politique d'approbation (trust policy) | rôle | qui a le droit d'**endosser** ce rôle |
| limite de permissions | utilisateur ou rôle | plafond de ses droits |
| SCP | compte ou unité d'organisation | plafond pour tout le compte |

On parle de **politiques gérées par AWS** (prêtes à l'emploi, souvent larges), **gérées par le client** (réutilisables) et **inline** (collées à une seule identité).

## Les rôles en pratique

- **Une instance EC2** reçoit un rôle par un **profil d'instance**. Le SDK trouve tout seul les identifiants temporaires.
- **Une Lambda** a un **rôle d'exécution**.
- **Un pod EKS** endosse un rôle par **IRSA** ou **EKS Pod Identity**.
- **Un autre compte** endosse un rôle si la trust policy l'autorise (`sts:AssumeRole`), souvent avec une condition `ExternalId` pour un fournisseur tiers.
- **Une CI** (GitLab, GitHub) endosse un rôle par **OIDC**, sans aucune clé stockée.

```bash
aws sts assume-role --role-arn arn:aws:iam::222222222222:role/lecture-factures \
  --role-session-name fares
```

## Organiser plusieurs comptes

Une entreprise n'a pas un compte AWS mais des dizaines : un par environnement et par équipe. Un compte est la **frontière d'isolation** la plus forte d'AWS.

```
Organisation (compte de gestion : facturation, rien d'autre)
├── UO Sécurité      : compte journaux (CloudTrail), compte audit
├── UO Infrastructure: compte réseau partagé
├── UO Production    : shop-prod, paiement-prod      ← SCP « régions UE seulement »
└── UO Développement : shop-dev, sandbox             ← SCP plus souples
```

Exemples de SCP utiles : interdire de quitter l'organisation, interdire de désactiver CloudTrail, limiter les régions utilisables. **AWS Control Tower** met en place cette structure avec des règles prêtes à l'emploi.

## Les bonnes pratiques

1. Root : MFA, aucune clé, enfermé.
2. Humains : **IAM Identity Center** (SSO) avec des jeux de permissions, pas d'utilisateurs IAM.
3. Machines : **rôles**, jamais de clés dans le code.
4. **Moindre privilège** : partir de peu, élargir selon le besoin ; **IAM Access Analyzer** propose des politiques à partir de l'activité réelle et signale les ressources partagées hors du compte.
5. Conditions : exiger MFA pour les actions sensibles, limiter par IP ou par tag.

> **À retenir.** Refus par défaut, un Allow ouvre, un Deny explicite gagne toujours. Les rôles donnent des identifiants temporaires : on les préfère partout aux utilisateurs et aux clés. Une SCP n'accorde rien, elle plafonne tout un compte, root compris. Plusieurs comptes sous Organizations, c'est la base d'une organisation saine.
