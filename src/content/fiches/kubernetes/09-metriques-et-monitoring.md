---
title: Métriques, logs et autoscaling
chapter: 9
order: 2
duration: 9
level: intermédiaire
tags:
- CKA
cards:
- q: À quoi sert metrics-server ?
  a: À fournir la consommation CPU et mémoire **instantanée** des pods et des nœuds, pour `kubectl top` et pour le HPA. Il ne garde pas d'historique.
- q: Différence entre kube-state-metrics et node-exporter ?
  a: '**kube-state-metrics** expose l''**état des objets** Kubernetes (réplicas voulus, pods en échec…). **node-exporter** expose les métriques **système** des nœuds (CPU, disque, réseau).'
- q: Sur quoi se base le HPA pour un objectif de 70 % de CPU ?
  a: Sur **70 % de la request CPU**, en moyenne sur les pods. Sans request, le HPA ne peut pas calculer l'utilisation.
- q: Où vont les logs écrits sur stdout par un conteneur ?
  a: Le runtime les écrit sur le nœud, dans `/var/log/pods/`. Un agent (Fluent Bit, Promtail, Vector) les envoie ensuite vers un stockage central (Loki, Elasticsearch).
- q: Quelle requête PromQL donne la consommation CPU d'un pod ?
  a: '`sum(rate(container_cpu_usage_seconds_total{pod="api-7d9f"}[5m]))`, en cœurs.'
quiz:
- q: '`kubectl top pods` renvoie `Metrics API not available`. Pourquoi ?'
  options:
  - Prometheus n'est pas installé
  - metrics-server n'est pas installé ou ne fonctionne pas
  - Les pods n'ont pas de limites
  - Le HPA est désactivé
  answer: 1
  explain: '`kubectl top` interroge l''API `metrics.k8s.io`, fournie par metrics-server. Prometheus ne la fournit pas par défaut.'
- q: Ton HPA affiche `<unknown>/70%` comme cible. Quelle est la cause la plus fréquente ?
  options:
  - Les pods n'ont pas de request CPU
  - Le Deployment a trop de réplicas
  - Le cluster n'a pas de LoadBalancer
  - L'image est trop lourde
  answer: 0
  explain: Le pourcentage est calculé par rapport à la request. Sans request, aucun calcul n'est possible.
---

Pour savoir si un cluster va bien, il faut trois choses : des **métriques**, des **logs**, et des **alertes** dessus.

> **Les outils cités dans cette fiche.**
> - **Prometheus** : la base de données de métriques de référence sur Kubernetes. Elle va lire (*scrape*) les métriques des applications toutes les 15 à 30 secondes et les garde sous forme de séries temporelles.
> - **Grafana** : l'outil de tableaux de bord qui affiche ces métriques (et les logs) en graphiques.
> - **Alertmanager** : le composant qui reçoit les alertes de Prometheus, les regroupe et les envoie (Slack, e-mail, PagerDuty).
> - **Exporteur** : un petit programme qui expose des métriques au format Prometheus pour quelque chose qui ne le fait pas tout seul (**node-exporter** pour un serveur, **kube-state-metrics** pour les objets Kubernetes). **metrics-server** est à part : il ne garde que les valeurs instantanées pour `kubectl top` et l'autoscaling.
> - **Fluent Bit** collecte les logs sur chaque nœud et les envoie à **Loki**, qui les stocke pour Grafana.
> - **HPA** : l'autoscaler horizontal, qui ajuste le nombre de pods selon la charge.
> - **JSON** : un format texte de données en paires « clé : valeur », lisible par les humains et les programmes.
> - **réplica** : une copie identique d'un pod, d'une base ou d'une donnée.
> - **file de messages** : un intermédiaire où un programme dépose des messages qu'un autre lit plus tard, à son rythme.

## Qui fournit quoi

| Composant | Fournit | Utilisé par |
| --- | --- | --- |
| metrics-server | CPU et mémoire instantanés | `kubectl top`, HPA |
| cAdvisor (dans le kubelet) | métriques détaillées des conteneurs | Prometheus |
| kube-state-metrics | état des objets Kubernetes | Prometheus, alertes |
| node-exporter | métriques système des nœuds | Prometheus |

La pile la plus courante est **kube-prometheus-stack** : Prometheus, Alertmanager, Grafana et ces exporteurs, installés en un chart Helm.

```promql
# CPU par pod, en cœurs
sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="shop"}[5m]))
# Pods qui redémarrent
increase(kube_pod_container_status_restarts_total[1h]) > 3
```

## Les logs

```
conteneur ─stdout─► /var/log/pods/... (sur le nœud) ─► Fluent Bit (DaemonSet) ─► Loki ─► Grafana
```

Écris tes logs sur stdout, si possible en JSON : pas de fichier à gérer, et ils sont faciles à filtrer.

<!-- schema:hpa -->
<figure class="diagram"><svg viewBox="0 0 680 240" role="img" aria-label="La boucle de l&#x27;autoscaling horizontal" style="--minw:560px"><defs><marker id="g14-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g14-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g14-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g14-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="20" y="92" width="140" height="56" rx="9"/></g><text x="90.0" y="117.0" class="dg-t" text-anchor="middle" style="--d:0">pods</text><text x="90.0" y="135.0" class="dg-s" text-anchor="middle" style="--d:0">CPU utilisé</text><g class="dg-box dg-pop" style="--d:1"><rect x="200" y="14" width="160" height="56" rx="9"/></g><text x="280.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:1">kubelet</text><text x="280.0" y="57.0" class="dg-s" text-anchor="middle" style="--d:1">mesure (cAdvisor)</text><g class="dg-box dg-pop" style="--d:2"><rect x="400" y="14" width="160" height="56" rx="9"/></g><text x="480.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:2">metrics-server</text><text x="480.0" y="57.0" class="dg-s" text-anchor="middle" style="--d:2">agrège</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="470" y="120" width="190" height="64" rx="9"/></g><text x="565.0" y="142.0" class="dg-t" text-anchor="middle" style="--d:3">HPA</text><text x="565.0" y="160.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="565.0" dy="0">veut 60 % de CPU</tspan><tspan x="565.0" dy="14">en moyenne</tspan></text><g class="dg-box dg-pop" style="--d:4"><rect x="200" y="170" width="190" height="56" rx="9"/></g><text x="295.0" y="195.0" class="dg-t" text-anchor="middle" style="--d:4">Deployment</text><text x="295.0" y="213.0" class="dg-s" text-anchor="middle" style="--d:4">replicas : 3 → 5</text><path d="M90 90 L90 42 L198 42" class="dg-l" marker-end="url(#g14-n)"/><path d="M360 42 L398 42" class="dg-l" marker-end="url(#g14-n)"/><path d="M480 70 L530 118" class="dg-l" marker-end="url(#g14-n)"/><text x="516" y="92" class="dg-s" text-anchor="start">toutes les 15 s</text><path d="M470 170 L440 198 L392 198" class="dg-l c" marker-end="url(#g14-c)"/><path d="M200 198 L90 198 L90 150" class="dg-l c" marker-end="url(#g14-c)"/><text x="286" y="130" class="dg-s" text-anchor="middle">replicas = actuel × utilisation / cible</text><text x="286" y="146" class="dg-ct" text-anchor="middle">3 × 100 % / 60 % = 5</text></svg><figcaption>Sans requests CPU sur les pods, le pourcentage n&#x27;a pas de sens et le HPA ne fait rien.</figcaption></figure>
<!-- /schema:hpa -->

## Comprendre le calcul du HPA

Le HPA applique une règle de trois, toutes les 15 secondes environ :

```
réplicas voulus = réplicas actuels × (utilisation actuelle / cible)
```

Avec 4 pods à 105 % de leur request CPU en moyenne et une cible de 70 % : `4 × 105 / 70 = 6` réplicas. Le pourcentage est calculé **par rapport à la request**. Si la request est de 100m et que l'appli en consomme 300m, le HPA voit 300 % ; si la request est de 2 cœurs pour une appli qui en consomme 300m, il voit 15 % et ne scalera jamais.

Le HPA attend aussi avant de **réduire** (5 minutes de stabilisation par défaut), pour ne pas supprimer des pods à chaque creux passager.

Le HPA ajoute des pods ; il faut encore des **nœuds** pour les accueillir. C'est le rôle du **Cluster Autoscaler** ou de **Karpenter**, qui ajoutent des nœuds quand des pods restent `Pending` faute de place.

## metrics-server et Prometheus : pourquoi les deux

- **metrics-server** garde seulement la **dernière** valeur de CPU et de mémoire de chaque pod. Il est léger et sert aux décisions immédiates : `kubectl top`, le HPA.
- **Prometheus** garde l'**historique** de milliers de métriques, pour les graphiques, l'analyse et les alertes.

**kube-state-metrics** comble un manque : il traduit l'**état des objets** Kubernetes en métriques (« ce Deployment veut 4 réplicas, 3 sont disponibles », « ce pod a redémarré 7 fois »). C'est la source de la plupart des alertes de cluster.

## L'autoscaling horizontal

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: api }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 70 }
```

> **À retenir.** Le HPA raisonne en pourcentage de la **request**. Des requests mal réglées donnent un autoscaling absurde. Pour scaler sur une file de messages ou une métrique métier, regarde KEDA.
