---
title: StatefulSet, DaemonSet, Job et CronJob
chapter: 3
order: 2
duration: 8
level: intermédiaire
tags:
- CKA
- CKAD
cards:
- q: Qu'apporte un StatefulSet par rapport à un Deployment ?
  a: Des pods avec une **identité stable** (`db-0`, `db-1`), un **nom DNS** stable via un Service headless, un **volume dédié** par pod, et un démarrage dans l'ordre.
- q: Que deviennent les PVC d'un StatefulSet quand on réduit le nombre de réplicas ?
  a: Ils sont **conservés** par défaut, pour ne pas perdre de données. Le comportement se règle avec `persistentVolumeClaimRetentionPolicy`.
- q: Quel Service faut-il pour un StatefulSet ?
  a: 'Un Service **headless** (`clusterIP: None`), référencé dans `serviceName`. Il donne à chaque pod un nom comme `db-0.db.default.svc.cluster.local`.'
- q: À quoi sert un DaemonSet ?
  a: 'À faire tourner **un pod par nœud** : agent de logs, de monitoring, CNI, CSI… Il ajoute automatiquement un pod quand un nœud rejoint le cluster.'
- q: Quelles `restartPolicy` sont autorisées pour un Job ?
  a: '`OnFailure` ou `Never`. `Always` est refusé, car un Job doit pouvoir se terminer.'
- q: 'Que fait `concurrencyPolicy: Forbid` sur un CronJob ?'
  a: Si l'exécution précédente tourne encore, la nouvelle est **sautée**. `Allow` (défaut) les lance en parallèle, `Replace` arrête l'ancienne.
quiz:
- q: Tu veux un agent de monitoring sur chaque nœud, y compris le control plane. Que faut-il ?
  options:
  - Un Deployment avec autant de réplicas que de nœuds
  - Un DaemonSet avec une toleration pour le taint du control plane
  - Un StatefulSet
  - Un CronJob
  answer: 1
  explain: Le DaemonSet place un pod par nœud, mais il respecte les taints. Sans toleration, le control plane est ignoré.
- q: Un Job échoue à chaque essai. Combien de fois Kubernetes le relance-t-il par défaut ?
  options:
  - Jamais
  - 3 fois
  - 6 fois
  - À l'infini
  answer: 2
  explain: '`backoffLimit` vaut 6 par défaut, avec un délai croissant entre les essais. `activeDeadlineSeconds` limite aussi sa durée totale.'
- q: Tu supprimes le pod `db-1` d'un StatefulSet. Que se passe-t-il ?
  options:
  - Il est recréé avec un nouveau nom aléatoire
  - Il est recréé sous le nom `db-1`, avec le même volume
  - Le StatefulSet passe à 2 réplicas
  - Les données de `db-1` sont perdues
  answer: 1
  explain: 'C''est tout l''intérêt du StatefulSet : même nom, même identité réseau et même PVC.'
---

Le Deployment ne convient pas à tout. Kubernetes propose d'autres contrôleurs selon la nature de la charge.

| Contrôleur | Pour quoi | Exemple |
| --- | --- | --- |
| `Deployment` | Appli sans état, pods interchangeables | API, front web |
| `StatefulSet` | Appli avec état, identité stable | PostgreSQL, Kafka, Elasticsearch |
| `DaemonSet` | Un pod par nœud | Fluent Bit, node-exporter, CNI |
| `Job` | Tâche qui doit se terminer | Migration, import, batch |
| `CronJob` | Job planifié | Sauvegarde nocturne |


> **Les termes et outils cités dans cette fiche.**
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **CNI** : le standard des plugins réseau de Kubernetes (Calico, Cilium…), qui donnent une adresse IP à chaque pod.
> - **PVC** : une demande de volume persistant faite par un pod.
> - **DNS** : le service qui traduit un nom (api.example.com) en adresse IP.

## StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: db }
spec:
  serviceName: db          # Service headless (clusterIP: None)
  replicas: 3
  selector: { matchLabels: { app: db } }
  template:
    metadata: { labels: { app: db } }
    spec:
      containers:
        - name: postgres
          image: postgres:17
          volumeMounts: [{ name: data, mountPath: /var/lib/postgresql/data }]
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        resources: { requests: { storage: 20Gi } }
```

Les pods s'appellent `db-0`, `db-1`, `db-2` et démarrent dans l'ordre. Chacun a son PVC (`data-db-0`…), conservé même si le pod est supprimé.

<!-- schema:statefulset -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Les garanties d&#x27;un StatefulSet" style="--minw:560px"><defs><marker id="g17-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g17-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g17-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g17-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="14" y="20" width="190" height="56" rx="9"/></g><text x="109.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:0">StatefulSet db</text><text x="109.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:0">serviceName: db</text><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="100" width="190" height="56" rx="9"/></g><text x="109.0" y="125.0" class="dg-t" text-anchor="middle" style="--d:0">Service headless db</text><text x="109.0" y="143.0" class="dg-s" text-anchor="middle" style="--d:0">clusterIP: None</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="250" y="20" width="126" height="56" rx="9"/></g><text x="313.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:1">db-0</text><text x="313.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:1">db-0.db.ns.svc</text><g class="dg-box dg-pop" style="--d:2"><rect x="250" y="120" width="126" height="50" rx="9"/></g><text x="313.0" y="142.0" class="dg-t" text-anchor="middle" style="--d:2">data-db-0</text><text x="313.0" y="160.0" class="dg-s" text-anchor="middle" style="--d:2">son propre PVC</text><path d="M313 76 L313 118" class="dg-l" marker-end="url(#g17-n)" marker-start="url(#g17-n)"/><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="392" y="20" width="126" height="56" rx="9"/></g><text x="455.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:3">db-1</text><text x="455.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:3">db-1.db.ns.svc</text><g class="dg-box dg-pop" style="--d:4"><rect x="392" y="120" width="126" height="50" rx="9"/></g><text x="455.0" y="142.0" class="dg-t" text-anchor="middle" style="--d:4">data-db-1</text><text x="455.0" y="160.0" class="dg-s" text-anchor="middle" style="--d:4">son propre PVC</text><path d="M455 76 L455 118" class="dg-l" marker-end="url(#g17-n)" marker-start="url(#g17-n)"/><path d="M376 48 L390 48" class="dg-l c" marker-end="url(#g17-c)"/><g class="dg-box dg-c dg-pop" style="--d:5"><rect x="534" y="20" width="126" height="56" rx="9"/></g><text x="597.0" y="45.0" class="dg-t" text-anchor="middle" style="--d:5">db-2</text><text x="597.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:5">db-2.db.ns.svc</text><g class="dg-box dg-pop" style="--d:6"><rect x="534" y="120" width="126" height="50" rx="9"/></g><text x="597.0" y="142.0" class="dg-t" text-anchor="middle" style="--d:6">data-db-2</text><text x="597.0" y="160.0" class="dg-s" text-anchor="middle" style="--d:6">son propre PVC</text><path d="M597 76 L597 118" class="dg-l" marker-end="url(#g17-n)" marker-start="url(#g17-n)"/><path d="M518 48 L532 48" class="dg-l c" marker-end="url(#g17-c)"/><path d="M204 48 L248 48" class="dg-l c" marker-end="url(#g17-c)"/><text x="450" y="200" class="dg-s" text-anchor="middle">créés dans l&#x27;ordre 0, 1, 2 · supprimés dans l&#x27;ordre inverse</text><text x="450" y="218" class="dg-ct" text-anchor="middle">un pod recréé garde son nom et son volume</text></svg><figcaption>Nom stable, DNS stable, volume dédié : c&#x27;est ce qui permet d&#x27;y faire tourner une base de données.</figcaption></figure>
<!-- /schema:statefulset -->

## Job et CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata: { name: backup }
spec:
  schedule: "0 3 * * *"
  timeZone: Europe/Paris
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      backoffLimit: 2
      ttlSecondsAfterFinished: 86400
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: registry.local/backup:1.0
```

> **À retenir.** Sans `ttlSecondsAfterFinished`, les Jobs terminés et leurs pods restent dans le cluster. Sur un CronJob, `successfulJobsHistoryLimit` (3) et `failedJobsHistoryLimit` (1) limitent l'historique.
