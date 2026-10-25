---
title: Sécuriser un cluster Kubernetes
chapter: 6
order: 1
duration: 11
level: intermédiaire
tags:
- CKS
cards:
- q: Pourquoi ne pas exposer l'API server Kubernetes sur Internet ?
  a: C'est la clé de tout le cluster. Une faille, un token volé ou une mauvaise config RBAC suffit alors. On le limite à un réseau privé, un VPN ou une liste d'IP.
- q: À quoi servent les audit logs de l'API server ?
  a: 'À savoir **qui a fait quoi, quand** : création de pods, lecture de Secrets, changements RBAC. Indispensables pour détecter et enquêter.'
- q: Que fait Falco ?
  a: 'De la **détection à l''exécution** : il observe les appels système et alerte sur les comportements suspects (shell ouvert dans un conteneur, lecture de `/etc/shadow`, connexion inattendue).'
- q: Quel outil vérifie un cluster par rapport au CIS Benchmark Kubernetes ?
  a: '**kube-bench**. Il contrôle la configuration de l''API server, du kubelet, d''etcd, etc.'
- q: Qu'est-ce qu'un policy engine comme Kyverno ou Gatekeeper ?
  a: 'Un admission controller qui applique **tes propres règles** : images signées obligatoires, registres autorisés, labels requis, interdiction de `latest`…'
- q: Quels réglages du kubelet sont importants ?
  a: Désactiver l'authentification anonyme (`--anonymous-auth=false`), utiliser l'autorisation `Webhook`, et ne pas exposer le port en lecture seule (10255).
- q: Pourquoi le droit `create pods` est-il presque équivalent à admin d'un namespace ?
  a: Un pod créé peut monter n'importe quel Secret et n'importe quelle ServiceAccount du namespace, et, sans Pod Security, être privilégié pour sortir vers le nœud.
- q: 'À quoi sert `automountServiceAccountToken: false` ?'
  a: 'À ne pas monter le jeton d''API dans un pod qui n''en a pas besoin : un attaquant qui le compromet n''a aucun jeton à réutiliser.'
- q: Pourquoi bloquer l'accès des pods à `169.254.169.254` ?
  a: 'C''est l''API de métadonnées du cloud : elle peut délivrer les identifiants IAM du nœud à n''importe quel pod.'
quiz:
- q: Quelle combinaison couvre à la fois la prévention et la détection ?
  options:
  - RBAC seul
  - Pod Security + NetworkPolicies + Kyverno pour prévenir, Falco + audit logs pour détecter
  - Un antivirus sur les nœuds
  - Un seul namespace par équipe
  answer: 1
  explain: La prévention réduit les risques, la détection repère ce qui passe quand même. Il faut les deux.
- q: Un développeur a besoin de débugger en prod. Quelle option est la plus sûre ?
  options:
  - Lui donner cluster-admin
  - Un accès temporaire, limité au namespace, avec `pods/exec` journalisé
  - Partager le kubeconfig admin
  - Désactiver l'audit pendant ce temps
  answer: 1
  explain: 'Accès juste à temps, limité et tracé : c''est le moindre privilège appliqué au debug.'
- q: Un pod web est compromis. Il a le jeton de la ServiceAccount `default`, qui a `get secrets` dans le namespace. Quelle est la prochaine étape probable de l'attaquant ?
  options:
  - Redémarrer le pod
  - Lire tous les Secrets du namespace (mots de passe de base, clés d'API)
  - Supprimer le cluster
  - Modifier le DNS
  answer: 1
  explain: Le jeton monté par défaut lui donne les droits de la SA. D'où une SA par appli, sans droits inutiles, et pas de jeton monté si l'appli n'appelle pas l'API.
- q: Ton cluster a des NetworkPolicies, Pod Security restricted et un RBAC propre, mais l'API server est ouvert sur Internet avec l'authentification par certificat. Quelle couche reste la plus exposée ?
  options:
  - Le code
  - Le plan de contrôle
  - Les conteneurs
  - etcd
  answer: 1
  explain: L'API server est la porte de tout le cluster. Une CVE ou un kubeconfig volé suffit. Restreins son accès réseau.
---

Les fiches Kubernetes couvrent RBAC, Pod Security, NetworkPolicies et Secrets un par un. Celle-ci prend du recul : comment un attaquant voit un cluster, et comment protéger **l'ensemble**.


> **Les termes et outils cités dans cette fiche.**
> - **RBAC** : le contrôle d'accès par rôles : on donne des droits à des rôles, puis des rôles aux personnes ou programmes.
> - **jeton** : une chaîne secrète qui prouve qu'on est authentifié, à durée limitée.
> - **nœud** : une machine (physique ou virtuelle) membre d'un cluster.
> - **namespace** : un espace de noms : dans Kubernetes, une partition du cluster ; sous Linux, une isolation du noyau.
> - **OIDC** : OpenID Connect, le standard de connexion par un fournisseur d'identité, qui délivre des jetons signés.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **webhook** : un appel HTTP automatique envoyé par un outil quand un événement se produit.
> - **SIEM** : un outil qui centralise les logs de sécurité et détecte les attaques.

## Comment un attaquant voit ton cluster

Un cluster Kubernetes est une **API** qui pilote des machines. Quiconque obtient assez de droits sur cette API contrôle tout ce qui tourne dessus. Les scénarios réels ressemblent à ça :

1. **Entrer** : une appli vulnérable exposée sur Internet, un API server ouvert, un kubeconfig qui traîne dans un dépôt, une image piégée.
2. **Regarder autour** : depuis un pod compromis, lire le jeton de la ServiceAccount (monté par défaut dans `/var/run/secrets/kubernetes.io/serviceaccount/`), interroger l'API, scanner le réseau du cluster.
3. **Monter en droits** : une ServiceAccount trop permissive qui peut créer des pods, lire des Secrets, ou un pod privilégié qui permet de sortir vers le nœud.
4. **S'étendre** : récupérer les identifiants cloud du nœud, les Secrets des autres namespaces, et rebondir vers le compte cloud.

Chaque mesure de cette fiche casse une de ces étapes.

## Les 4C de la sécurité cloud native

<!-- schema:4c -->
<figure class="diagram"><svg viewBox="0 0 680 290" role="img" aria-label="Les 4C de la sécurité cloud native" style="--minw:560px"><defs><marker id="g4-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g4-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g4-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g4-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="652" height="262" rx="12" class="dg-zone dg-zc"/><text x="26" y="32" class="dg-zl" text-anchor="start">cloud</text><text x="654" y="32" class="dg-s" text-anchor="end" style="--d:0">compte, réseau, IAM</text><rect x="60" y="52" width="560" height="196" rx="12" class="dg-zone "/><text x="72" y="70" class="dg-zl" text-anchor="start">cluster</text><text x="608" y="70" class="dg-s" text-anchor="end" style="--d:1">API server, RBAC, etcd, admission</text><rect x="106" y="90" width="468" height="130" rx="12" class="dg-zone dg-zc"/><text x="118" y="108" class="dg-zl" text-anchor="start">conteneur</text><text x="562" y="108" class="dg-s" text-anchor="end" style="--d:2">image, runtime, securityContext</text><rect x="152" y="128" width="376" height="64" rx="12" class="dg-zone "/><text x="164" y="146" class="dg-zl" text-anchor="start">code</text><text x="516" y="146" class="dg-s" text-anchor="end" style="--d:3">dépendances, secrets, failles</text><text x="340" y="166" class="dg-ct" text-anchor="middle">ton application</text></svg><figcaption>Chaque couche dépend de celle qui l&#x27;entoure : un code parfait ne sauve pas un cluster ouvert.</figcaption></figure>
<!-- /schema:4c -->

Les quatre couches s'emboîtent : **Cloud** (le compte, le réseau), **Cluster** (l'API, les nœuds), **Conteneur** (l'image, ses droits), **Code** (l'application). Chaque couche dépend de celle qui l'entoure : un cluster parfait sur un compte cloud mal protégé reste vulnérable, et une appli impeccable dans un pod privilégié aussi.

## Le plan de contrôle

| Élément | Mesure | Pourquoi |
| --- | --- | --- |
| API server | réseau privé ou liste d'IP, OIDC pour les humains, audit logs activés | c'est la porte d'entrée de tout ; on veut savoir qui l'a utilisée |
| etcd | accès limité à l'API server, chiffrement des Secrets, sauvegardes chiffrées | il contient **tout** l'état du cluster, Secrets compris |
| kubelet | `anonymous-auth=false`, autorisation Webhook | un kubelet ouvert permet d'exécuter des commandes dans les pods du nœud |
| Mises à jour | rester sur une version supportée (les 3 dernières mineures) | les correctifs de sécurité ne sont publiés que pour elles |

## RBAC : les droits qui donnent tout

RBAC dit qui peut faire quoi sur quelles ressources. Certains droits paraissent anodins mais équivalent à devenir administrateur :

| Droit | Pourquoi c'est sensible |
| --- | --- |
| `get`/`list` sur `secrets` | lire tous les mots de passe et jetons du namespace (ou du cluster) |
| `create` sur `pods` | lancer un pod qui monte n'importe quel Secret ou ServiceAccount du namespace, voire un pod privilégié |
| `pods/exec` | exécuter des commandes dans les pods existants |
| `escalate`, `bind`, `impersonate` | s'attribuer d'autres rôles ou se faire passer pour quelqu'un d'autre |
| `*` sur `*` | évidemment |

Réflexes : une ServiceAccount **par application**, sans droits si elle n'appelle pas l'API, et `automountServiceAccountToken: false` sur les pods qui n'en ont pas besoin. Ainsi, un pod compromis ne trouve même pas de jeton à voler.

## Les charges de travail

| Prévenir | Détecter |
| --- | --- |
| Pod Security `restricted` | Falco (comportements suspects à l'exécution) |
| NetworkPolicies en refus par défaut | audit logs vers un SIEM |
| Kyverno : images signées, registres autorisés | scans réguliers (Trivy Operator) |
| RBAC minimal, une ServiceAccount par appli | alertes sur les changements RBAC |

**Pod Security** impose au niveau d'un namespace les réglages vus dans la fiche sur les conteneurs : pas de privilèges, pas de root, pas de montage de l'hôte. Les **NetworkPolicies** limitent le mouvement latéral : un pod compromis ne peut joindre que ce qui lui est explicitement autorisé. Pense aussi à bloquer l'accès des pods à l'**API de métadonnées du cloud** (`169.254.169.254`), qui délivre les identifiants du nœud.

**Falco** surveille les appels système et alerte sur des comportements anormaux : un shell lancé dans un conteneur de prod, une lecture de `/etc/shadow`, une connexion sortante inattendue.

Un **contrôleur d'admission** comme Kyverno intercepte chaque création de ressource et peut la refuser ou la modifier. Exemple :

```yaml
# Kyverno : interdire le tag latest
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: disallow-latest-tag }
spec:
  rules:
    - name: require-tag
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        failureAction: Enforce            # refuser (Audit = seulement signaler)
        message: "Le tag latest est interdit."
        pattern:
          spec:
            containers:
              - image: "!*:latest"
```

## Vérifier

```bash
kube-bench run --targets node,policies                 # conformité au CIS Benchmark
kubectl auth can-i --list --as=system:serviceaccount:shop:default -n shop   # que peut faire cette SA ?
kubectl auth can-i create pods --as=system:serviceaccount:shop:api -n shop
```

> **À retenir.** L'API Kubernetes est la cible : qui la contrôle contrôle tout. Ne l'expose pas, revois RBAC (lire les Secrets et créer des pods valent presque admin), retire les jetons de ServiceAccount inutiles, applique Pod Security `baseline` partout et `restricted` sur tes applis, et des NetworkPolicies en refus par défaut.
