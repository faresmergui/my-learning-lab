---
title: Principes et modèle de menace
chapter: 1
order: 1
duration: 9
level: intermédiaire
tags:
- fondamentaux
cards:
- q: Que signifie la triade CIA (ou DIC en français) ?
  a: '**Confidentialité** (seules les bonnes personnes lisent), **Intégrité** (personne ne modifie à son insu), **Disponibilité** (le service répond quand on en a besoin).'
- q: Qu'est-ce que le principe du moindre privilège ?
  a: Chaque personne, service ou machine n'a **que les droits nécessaires** à sa tâche, et seulement le temps nécessaire.
- q: Qu'est-ce que la défense en profondeur ?
  a: Empiler **plusieurs protections indépendantes** (réseau, identité, système, appli, données), pour qu'une seule faille ne suffise pas à tout compromettre.
- q: Que veut dire STRIDE ?
  a: 'Une grille pour lister les menaces : **S**poofing (usurpation), **T**ampering (altération), **R**epudiation (nier une action), **I**nformation disclosure (fuite), **D**enial of service, **E**levation of privilege.'
- q: Qu'est-ce que le modèle *zero trust* ?
  a: 'Ne faire confiance à **aucune** requête en fonction de sa position réseau : chaque accès est authentifié, autorisé et chiffré, même à l''intérieur du réseau de l''entreprise.'
- q: Différence entre menace, vulnérabilité et risque ?
  a: La **menace** est ce qui pourrait arriver, la **vulnérabilité** la faiblesse qui le permet, le **risque** combine probabilité et impact.
- q: Différence entre authentification et autorisation ?
  a: '**Authentification** : prouver qui on est. **Autorisation** : vérifier ce qu''on a le droit de faire. HTTP 401 concerne la première, 403 la seconde.'
- q: Qu'est-ce que le mouvement latéral ?
  a: Une fois entré sur une machine, l'attaquant rebondit vers d'autres systèmes du réseau interne. Le zero trust et la segmentation le limitent.
- q: Qu'est-ce qu'une frontière de confiance ?
  a: L'endroit où une donnée ou une requête passe d'une zone à une autre de niveau de confiance différent (Internet → LB, CI → prod). C'est là qu'il faut authentifier et valider.
quiz:
- q: Un pod compromis peut joindre la base de données de toute l'entreprise. Quel principe est le plus en défaut ?
  options:
  - La disponibilité
  - La segmentation et le moindre privilège
  - L'intégrité
  - La non-répudiation
  answer: 1
  explain: 'Un attaquant qui entre quelque part doit trouver le moins de portes ouvertes possible : NetworkPolicies, comptes dédiés, droits minimaux.'
- q: Quelle question pose en premier un modèle de menace ?
  options:
  - Quel pare-feu acheter ?
  - Que protège-t-on, contre qui, et qu'est-ce qui peut mal tourner ?
  - Combien coûte une faille ?
  - Quel est le dernier CVE ?
  answer: 1
  explain: On part des actifs et des scénarios réalistes. Les outils viennent après, pour répondre aux risques identifiés.
- q: Une clé de CI qui ne sert qu'à pousser une image fuit. Elle permettait aussi de supprimer des instances. Quel principe n'a pas été respecté ?
  options:
  - Défense en profondeur
  - Moindre privilège
  - Sécurisé par défaut
  - Traçabilité
  answer: 1
  explain: La clé avait plus de droits que nécessaire. Avec le moindre privilège, la fuite n'aurait permis que de pousser une image.
- q: Un attaquant modifie une image dans ton registre. Dans STRIDE, de quelle menace s'agit-il ?
  options:
  - Spoofing
  - Tampering
  - Information disclosure
  - Denial of service
  answer: 1
  explain: 'Modifier un artefact, c''est une atteinte à l''intégrité : Tampering. La signature des images y répond.'
- q: 'Ton équipe dit : « Pas besoin d''authentifier les appels entre services, ils sont dans le même VPC. » Quel principe contredit ce raisonnement ?'
  options:
  - Zero trust
  - Disponibilité
  - Rotation
  - Secure by default
  answer: 0
  explain: 'Être dans le réseau interne ne doit pas donner confiance : un attaquant qui entre sur une machine du VPC pourrait sinon appeler tous les services.'
---

La sécurité n'est pas une liste d'outils à installer. C'est une façon de raisonner : **qu'est-ce qu'on protège**, **contre qui**, et **qu'est-ce qui peut mal tourner**. Les outils viennent après, pour répondre à des risques identifiés. Cette fiche pose le vocabulaire qu'on retrouve dans tout le module.


> **Les termes et outils cités dans cette fiche.**
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **image** : le modèle figé (système de fichiers et réglages) à partir duquel on lance un conteneur.
> - **bucket** : un conteneur de fichiers dans un stockage objet (S3, Swift).
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **HTTP** : le protocole du web : un client envoie une requête (GET, POST…) et reçoit une réponse avec un code (200, 404, 500…).
> - **RBAC** : le contrôle d'accès par rôles : on donne des droits à des rôles, puis des rôles aux personnes ou programmes.
> - **IAM** : la gestion des identités et des droits (qui peut faire quoi).
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.

## Le vocabulaire de base

| Mot | Sens | Exemple |
| --- | --- | --- |
| **Actif** | ce qui a de la valeur et qu'on protège | la base clients, les clés de prod, la disponibilité du site |
| **Menace** | ce qui pourrait arriver | un attaquant vole la base |
| **Vulnérabilité** | la faiblesse qui le permet | un port de base de données ouvert sur Internet |
| **Risque** | probabilité × impact | élevé si la base est exposée **et** contient des données sensibles |
| **Surface d'attaque** | tout ce qu'un attaquant peut atteindre | ports ouverts, API, comptes, dépendances |
| **CVE** | identifiant public d'une vulnérabilité connue | `CVE-2024-3094` (xz) |

On ne supprime jamais tous les risques. On les **réduit** là où c'est rentable, on en **accepte** certains en connaissance de cause, et on s'organise pour **détecter** et **réagir** quand ça arrive.

## Les trois propriétés à protéger

| Propriété | Question | Exemple d'atteinte |
| --- | --- | --- |
| Confidentialité | qui peut lire ? | fuite d'une base clients |
| Intégrité | qui peut modifier ? | image Docker piégée, données altérées |
| Disponibilité | le service répond-il ? | DDoS, ransomware, suppression d'un bucket |

<!-- schema:cia -->
<figure class="diagram"><svg viewBox="0 0 680 280" role="img" aria-label="La triade CIA" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><path d="M340 40 L130 236 L550 236 Z" class="dg-zone dg-zc"/><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="250" y="16" width="180" height="58" rx="9"/></g><text x="340.0" y="42.0" class="dg-t" text-anchor="middle" style="--d:0">Confidentialité</text><text x="340.0" y="60.0" class="dg-s" text-anchor="middle" style="--d:0">seuls les bons lisent</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="40" y="212" width="180" height="58" rx="9"/></g><text x="130.0" y="231.0" class="dg-t" text-anchor="middle" style="--d:1">Intégrité</text><text x="130.0" y="249.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="130.0" dy="0">personne ne modifie</tspan><tspan x="130.0" dy="14">en douce</tspan></text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="460" y="212" width="180" height="58" rx="9"/></g><text x="550.0" y="231.0" class="dg-t" text-anchor="middle" style="--d:2">Disponibilité</text><text x="550.0" y="249.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="550.0" dy="0">accessible quand</tspan><tspan x="550.0" dy="14">on en a besoin</tspan></text><text x="340" y="150" class="dg-zl" text-anchor="middle">ce qu&#x27;on protège</text><text x="150" y="120" class="dg-s" text-anchor="middle"><tspan x="150" dy="0">chiffrement, IAM,</tspan><tspan x="150" dy="14">moindre privilège</tspan></text><text x="530" y="120" class="dg-s" text-anchor="middle"><tspan x="530" dy="0">redondance, sauvegardes,</tspan><tspan x="530" dy="14">limites de débit</tspan></text><text x="340" y="254" class="dg-s" text-anchor="middle">hash, signatures, journaux</text></svg><figcaption>Chaque mesure de sécurité protège au moins un des trois sommets.</figcaption></figure>
<!-- /schema:cia -->

Chaque mesure de sécurité protège au moins une de ces trois propriétés. Le chiffrement protège la confidentialité ; les signatures, l'intégrité ; les sauvegardes et la redondance, la disponibilité. Se demander laquelle est en jeu aide à choisir la bonne réponse.

## Authentification et autorisation

Deux mots qu'on confond souvent, et que tu retrouveras partout (HTTP 401 / 403, RBAC Kubernetes, IAM cloud) :

- **Authentification** (*authn*) : **qui es-tu ?** Prouver son identité avec un mot de passe, une clé SSH, un certificat, un jeton, un second facteur (MFA).
- **Autorisation** (*authz*) : **qu'as-tu le droit de faire ?** Une fois l'identité connue, vérifier les permissions.

Une identité peut être humaine (toi) ou machine (une CI, un pod, un serveur). Les identités machine sont aujourd'hui les plus nombreuses et les plus souvent oubliées.

## Les principes qui reviennent partout

- **Moindre privilège** : chaque identité a le strict nécessaire, pour la durée nécessaire. Si une clé de CI fuit, elle ne doit pouvoir déployer qu'une appli, pas supprimer le compte cloud.
- **Défense en profondeur** : plusieurs couches indépendantes, comme les remparts d'un château. Si le pare-feu laisse passer, l'authentification arrête ; si l'authentification cède, le moindre privilège limite les dégâts ; si tout cède, les journaux permettent de comprendre.
- **Sécurisé par défaut** (*secure by default*) : la configuration de départ est la plus sûre ; on ouvre explicitement ce qu'il faut. L'inverse (tout ouvert, on ferme ce qu'on pense) laisse toujours des oublis.
- **Zero trust** : être « dans le réseau interne » ne donne aucune confiance. Chaque requête est authentifiée et autorisée, même entre deux services du même cluster. L'idée vient du constat qu'un attaquant finit souvent par entrer quelque part, et se déplace ensuite librement (*mouvement latéral*).
- **Traçabilité** : chaque action importante est journalisée, attribuée à une identité, et les journaux sont stockés hors de portée de l'attaquant.

## Qui attaque, et comment

Il n'y a pas besoin d'imaginer un service secret. Les attaques réelles les plus fréquentes sont banales et automatisées :

| Vecteur | Exemple |
| --- | --- |
| identifiants volés ou faibles | clé d'API dans un dépôt public, mot de passe réutilisé |
| service exposé et non corrigé | un panneau d'admin ou une base ouverte sur Internet, une CVE connue |
| mauvaise configuration | bucket public, security group `0.0.0.0/0`, Dashboard Kubernetes sans authentification |
| dépendance piégée | paquet npm ou PyPI malveillant, image Docker compromise |
| hameçonnage | un humain donne ses identifiants ou approuve une demande MFA |

Des robots scannent Internet en continu : un port SSH ou une base exposés reçoivent des tentatives dans les **minutes** qui suivent leur ouverture.

## Un modèle de menace en 4 questions

Modéliser les menaces, c'est faire cet exercice avant d'être attaqué :

1. **Sur quoi travaille-t-on ?** Un schéma simple des flux de données : qui parle à qui, et où passent les données sensibles.
2. **Qu'est-ce qui peut mal tourner ?** Pour chaque flux, on passe en revue les six familles de **STRIDE** :

| Lettre | Menace | Propriété touchée | Exemple |
| --- | --- | --- | --- |
| S | usurpation (*Spoofing*) | authentification | un pod se fait passer pour un autre |
| T | altération (*Tampering*) | intégrité | modifier une image dans le registre |
| R | répudiation | traçabilité | impossible de savoir qui a supprimé la base |
| I | fuite d'information | confidentialité | des logs contenant des jetons |
| D | déni de service | disponibilité | saturer l'API |
| E | élévation de privilèges | autorisation | sortir d'un conteneur vers l'hôte |

3. **Que fait-on contre ?** Des mesures, priorisées par risque.
4. **A-t-on fait du bon travail ?** Revue, tests, exercices.

Les points les plus intéressants sont les **frontières de confiance** : l'endroit où une donnée passe d'une zone qu'on contrôle à une zone qu'on contrôle moins (Internet → load balancer, CI → production, pod → API du cloud).

> **À retenir.** Identifie ce que tu protèges et les flux qui traversent une frontière de confiance, puis applique moindre privilège et défense en profondeur. La plupart des incidents viennent d'identifiants qui fuient, de services exposés non corrigés et de mauvaises configurations, pas d'attaques exotiques.
