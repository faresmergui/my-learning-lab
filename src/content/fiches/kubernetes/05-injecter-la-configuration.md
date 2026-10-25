---
title: Injecter la configuration
chapter: 5
order: 1
duration: 8
level: intermédiaire
tags:
- CKA
- CKAD
cards:
- q: Quelles sont les deux façons d'utiliser un ConfigMap dans un pod ?
  a: En **variables d'environnement** (`env` avec `valueFrom`, ou `envFrom` pour tout importer) ou en **fichiers** via un volume.
- q: Tu modifies un ConfigMap. Les pods voient-ils le changement ?
  a: 'En **variables d''environnement** : non, il faut redémarrer les pods. En **volume** : oui, après un délai d''environ une minute, **sauf** avec `subPath`.'
- q: Quelle est la taille maximale d'un ConfigMap ou d'un Secret ?
  a: '**1 Mio**. Au-delà, il faut un volume ou un stockage externe.'
- q: 'À quoi sert `immutable: true` sur un ConfigMap ?'
  a: Il empêche toute modification (il faudra en créer un nouveau) et soulage l'API server, qui n'a plus à surveiller ses changements.
- q: Comment créer un ConfigMap à partir d'un fichier ?
  a: '`kubectl create configmap nginx-conf --from-file=nginx.conf`. Avec `--from-literal=CLE=valeur` pour une simple valeur.'
quiz:
- q: Tu montes un fichier de ConfigMap avec `subPath` pour ne pas écraser le dossier. Tu modifies le ConfigMap. Que se passe-t-il ?
  options:
  - Le fichier est mis à jour en quelques secondes
  - Le fichier n'est jamais mis à jour tant que le pod n'est pas recréé
  - Le pod redémarre automatiquement
  - Le ConfigMap est refusé
  answer: 1
  explain: Les montages en `subPath` ne reçoivent pas les mises à jour. C'est une source classique de « j'ai changé la config, rien ne bouge ».
- q: Comment forcer un Deployment à prendre en compte un nouveau ConfigMap injecté en variables ?
  options:
  - '`kubectl apply` sur le ConfigMap suffit'
  - '`kubectl rollout restart deployment/app`'
  - Supprimer le ConfigMap
  - Attendre une minute
  answer: 1
  explain: Les variables d'environnement sont lues au démarrage du conteneur. Helm et Kustomize règlent ce problème en ajoutant un hash du ConfigMap dans le template, ce qui déclenche un rollout.
---

Séparer la configuration de l'image permet d'utiliser la même image en dev, en recette et en prod.


> **Les termes et outils cités dans cette fiche.**
> - **RBAC** : le contrôle d'accès par rôles : on donne des droits à des rôles, puis des rôles aux personnes ou programmes.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **hachage** : calculer une empreinte d'un contenu ; impossible de revenir au contenu à partir de l'empreinte.

## En variables d'environnement

```yaml
env:
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef: { name: app-config, key: log_level }
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef: { name: db-credentials, key: password }
envFrom:
  - configMapRef: { name: app-config }   # toutes les clés d'un coup
```

## En fichiers

```yaml
volumes:
  - name: config
    configMap: { name: nginx-conf }
containers:
  - name: nginx
    volumeMounts:
      - name: config
        mountPath: /etc/nginx/conf.d   # chaque clé devient un fichier
```

<!-- schema:propagation -->
<figure class="diagram"><svg viewBox="0 0 680 220" role="img" aria-label="Ce qui se passe quand une ConfigMap change" style="--minw:560px"><defs><marker id="g19-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g19-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g19-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g19-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="14" y="80" width="150" height="60" rx="9"/></g><text x="89.0" y="107.0" class="dg-t" text-anchor="middle" style="--d:0">ConfigMap</text><text x="89.0" y="125.0" class="dg-s" text-anchor="middle" style="--d:0">LOG_LEVEL=debug</text><g class="dg-box dg-pop" style="--d:1"><rect x="250" y="14" width="200" height="64" rx="9"/></g><text x="350.0" y="43.0" class="dg-t" text-anchor="middle" style="--d:1">en variable d&#x27;env</text><text x="350.0" y="61.0" class="dg-s" text-anchor="middle" style="--d:1">lue au démarrage</text><g class="dg-box dg-pop" style="--d:2"><rect x="250" y="142" width="200" height="64" rx="9"/></g><text x="350.0" y="171.0" class="dg-t" text-anchor="middle" style="--d:2">en fichier (volume)</text><text x="350.0" y="189.0" class="dg-s" text-anchor="middle" style="--d:2">mis à jour en ~1 min</text><path d="M164 100 L206 100 L206 46 L248 46" class="dg-l c" marker-end="url(#g19-c)"/><path d="M164 120 L206 120 L206 174 L248 174" class="dg-l c" marker-end="url(#g19-c)"/><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="500" y="14" width="166" height="64" rx="9"/></g><text x="583.0" y="43.0" class="dg-t" text-anchor="middle" style="--d:3">il faut redémarrer</text><text x="583.0" y="61.0" class="dg-s" text-anchor="middle" style="--d:3">rollout restart</text><g class="dg-box dg-ok dg-pop" style="--d:4"><rect x="500" y="142" width="166" height="64" rx="9"/></g><text x="583.0" y="171.0" class="dg-t" text-anchor="middle" style="--d:4">l&#x27;appli doit relire</text><text x="583.0" y="189.0" class="dg-s" text-anchor="middle" style="--d:4">sauf avec subPath</text><path d="M450 46 L498 46" class="dg-l" marker-end="url(#g19-n)"/><path d="M450 174 L498 174" class="dg-l" marker-end="url(#g19-n)"/></svg><figcaption>Les variables d&#x27;environnement sont figées au démarrage du conteneur.</figcaption></figure>
<!-- /schema:propagation -->

## Comprendre : pourquoi séparer config et image

Le principe vient des *12-factor apps* : une image est **construite une fois**, puis promue de dev à prod **sans être reconstruite**. Ce qui change d'un environnement à l'autre (l'URL de la base, le niveau de log, les clés) doit donc venir de **l'extérieur** de l'image. Si l'image de prod est différente de celle testée en recette, les tests ne prouvent plus rien.

Kubernetes fournit deux objets pour ça :

- le **ConfigMap** pour la configuration non sensible ;
- le **Secret** pour ce qui donne un accès. Techniquement presque identique (des paires clé-valeur), mais traité à part : droits RBAC distincts, possibilité de chiffrement dans etcd, jamais affiché par `kubectl describe` (fiche suivante).

## Variable ou fichier ?

Une **variable d'environnement** est lue une fois, au démarrage du processus : c'est le noyau qui la fige. Kubernetes ne peut pas la changer dans un processus en cours, d'où l'absence de mise à jour automatique.

Un **volume** est un vrai dossier dans le conteneur. Le kubelet le resynchronise périodiquement (environ une minute) : l'appli voit les nouveaux fichiers si elle les **relit** (certaines surveillent le dossier, d'autres rechargent sur signal, beaucoup ne relisent jamais). Avec `subPath`, on monte un **seul** fichier à un emplacement précis, mais ce montage n'est plus mis à jour.

En pratique : des variables pour les réglages simples, des fichiers pour les configurations complètes (nginx, certificats) et pour les secrets.

## Ce qui se passe quand la config change

| Mode d'injection | Mise à jour automatique ? |
| --- | --- |
| Variable d'environnement | Non, il faut redémarrer le pod |
| Volume | Oui, après environ une minute |
| Volume avec `subPath` | Non |

> **Piège classique.** Mettre à jour un ConfigMap ne redémarre jamais rien. Avec Helm ou Kustomize, on ajoute un hash de la config dans le template du pod pour déclencher un rollout à chaque changement.

```bash
kubectl create configmap app-config --from-literal=log_level=info --dry-run=client -o yaml
kubectl create secret generic db-credentials --from-literal=password='s3cr3t'
```

> **À retenir.** Une même image pour tous les environnements, la configuration injectée depuis un ConfigMap ou un Secret. Les variables d'environnement sont figées au démarrage ; les volumes se mettent à jour (sauf avec `subPath`), mais seulement si l'appli relit ses fichiers.
