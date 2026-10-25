---
title: Requests, limits et classes QoS
chapter: 7
order: 2
duration: 9
level: intermédiaire
tags:
- CKA
cards:
- q: À quoi servent les **requests** ?
  a: 'Au **scheduler** : il place le pod sur un nœud qui a assez de ressources non réservées. C''est aussi la part garantie au conteneur.'
- q: Que se passe-t-il quand un conteneur dépasse sa limite **CPU** ? Et sa limite **mémoire** ?
  a: 'CPU : il est **ralenti** (throttling), pas tué. Mémoire : il est **tué** (`OOMKilled`, code 137).'
- q: Quelles sont les trois classes QoS ?
  a: '**Guaranteed** : requests = limits pour le CPU et la mémoire de tous les conteneurs. **Burstable** : au moins une request ou une limite. **BestEffort** : rien du tout.'
- q: Dans quel ordre le kubelet évince-t-il les pods quand un nœud manque de mémoire ?
  a: D'abord les **BestEffort**, puis les **Burstable** qui dépassent leurs requests, et les **Guaranteed** en dernier.
- q: Différence entre LimitRange et ResourceQuota ?
  a: '**LimitRange** : valeurs par défaut et bornes **par conteneur** dans un namespace. **ResourceQuota** : plafond **total** pour tout le namespace (CPU, mémoire, nombre d''objets).'
quiz:
- q: Un pod est `OOMKilled` alors que le nœud a plein de mémoire libre. Pourquoi ?
  options:
  - Le nœud ment sur sa mémoire
  - Le conteneur a dépassé sa propre limite mémoire
  - La request est trop haute
  - La classe QoS est Guaranteed
  answer: 1
  explain: La limite s'applique au conteneur, quelle que soit la mémoire libre du nœud. Regarde la consommation réelle avec `kubectl top pod` avant d'ajuster.
- q: Ton appli est lente alors que le nœud est peu chargé, et ses métriques montrent du throttling. Que faire en priorité ?
  options:
  - Baisser la request CPU
  - Augmenter ou retirer la limite CPU
  - Ajouter une liveness probe
  - Passer en BestEffort
  answer: 1
  explain: Une limite CPU trop basse ralentit le conteneur même quand le nœud a du CPU libre. Beaucoup d'équipes gardent une limite mémoire mais pas de limite CPU.
- q: 'Un pod a `requests: {cpu: 500m, memory: 512Mi}` et `limits: {cpu: 500m, memory: 512Mi}`. Quelle est sa classe QoS ?'
  options:
  - BestEffort
  - Burstable
  - Guaranteed
  - Critical
  answer: 2
  explain: 'Requests et limits égales pour le CPU et la mémoire, dans tous les conteneurs : c''est Guaranteed.'
---

Les requests et les limits sont les réglages qui ont le plus d'impact sur la stabilité d'un cluster. Elles décident où les pods vont, et qui est sacrifié quand un nœud sature.


> **Les termes et outils cités dans cette fiche.**
> - **scheduler** : le composant qui décide où placer une charge de travail (sur quel nœud ou quel hôte).
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **cgroups** : le mécanisme du noyau Linux qui limite et mesure les ressources (CPU, mémoire) d'un groupe de processus.
> - **latence** : le délai entre une demande et sa réponse.

## Requests et limits

```yaml
resources:
  requests:            # réservé, utilisé par le scheduler
    cpu: 250m          # 0,25 cœur
    memory: 256Mi
  limits:              # plafond appliqué par le noyau
    memory: 512Mi
```

| | Request | Limite |
| --- | --- | --- |
| **CPU** | part garantie, utilisée pour le placement | au-delà : ralenti (throttling) |
| **Mémoire** | part garantie, utilisée pour le placement | au-delà : tué (`OOMKilled`) |

> **Piège classique.** Sans requests, le scheduler croit que ton pod ne consomme rien et peut surcharger un nœud. Mets toujours des requests réalistes, mesurées avec `kubectl top`.

## Comprendre les unités

- **CPU** : `1` = un cœur entier, `250m` (millicœurs) = un quart de cœur. Ce n'est pas un cœur physique réservé, mais une **part de temps** de calcul.
- **Mémoire** : `256Mi` = 256 mébioctets (puissance de 2). `256M` (puissance de 10) existe aussi, un peu plus petit : on utilise `Mi` et `Gi` pour éviter la confusion.

## Ce que fait chaque réglage, concrètement

La **request** sert au **placement**. Le scheduler additionne les requests des pods déjà placés sur chaque nœud, et ne place un nouveau pod que là où il reste assez de place. Il ne regarde **pas** la consommation réelle. Un pod qui demande 100m et consomme 2 cœurs fausse tout le calcul.

La **limite** est appliquée par le noyau (via les cgroups), et les deux ressources ne réagissent pas pareil :

- le **CPU** est **compressible** : un conteneur qui atteint sa limite est **ralenti** (*throttling*), il reçoit moins de temps de calcul, mais il continue. Symptôme : latence qui monte, sans erreur visible ;
- la **mémoire** ne l'est pas : on ne peut pas « ralentir » une allocation. Au-delà de la limite, le noyau **tue** le processus (`OOMKilled`, code 137).

D'où une pratique répandue : des requests CPU réalistes **sans** limite CPU (pour profiter du CPU libre du nœud sans throttling), et une limite mémoire égale ou proche de la request mémoire (pour un comportement prévisible).

## Pourquoi la QoS compte

Quand un **nœud** manque de mémoire (et non plus un conteneur), le kubelet doit **évincer** des pods pour se protéger. Il choisit d'abord ceux qui consomment le plus **au-delà de leur request**, en commençant par les `BestEffort`. Un pod `Guaranteed` qui reste dans ses limites est le dernier sacrifié. Mettre des requests, c'est donc aussi dire « voici ce qu'il me faut pour vivre ».

## Les classes QoS

| Classe | Condition | Évincé |
| --- | --- | --- |
| `Guaranteed` | requests = limits (CPU et mémoire) partout | en dernier |
| `Burstable` | au moins une request ou une limite | ensuite |
| `BestEffort` | aucune request ni limite | en premier |

```bash
kubectl get pod api-7d9f -o jsonpath='{.status.qosClass}'
```

<!-- schema:qos -->
<figure class="diagram"><svg viewBox="0 0 680 256" role="img" aria-label="Les trois classes QoS" style="--minw:560px"><defs><marker id="g9-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g9-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g9-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g9-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-a dg-pop" style="--d:0"><rect x="30" y="16" width="186" height="52" rx="9"/></g><text x="123.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:0">BestEffort</text><text x="123.0" y="57.0" class="dg-s" text-anchor="middle" style="--d:0">ni request ni limit</text><rect x="93" y="84" width="60" height="110" rx="6" class="dg-floor"/><text x="123" y="144" class="dg-s" text-anchor="middle">aucune garantie</text><text x="123" y="214" class="dg-at" text-anchor="middle" style="--d:0">évincé en premier</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="246" y="16" width="186" height="52" rx="9"/></g><text x="339.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:1">Burstable</text><text x="339.0" y="57.0" class="dg-s" text-anchor="middle" style="--d:1">request &lt; limit</text><rect x="309" y="84" width="60" height="110" rx="6" class="dg-floor"/><rect x="309" y="100.5" width="60" height="93.5" rx="6" class="dg-fill"/><line x1="301" y1="100.5" x2="377" y2="100.5" class="dg-court"/><text x="383" y="104.5" class="dg-s" text-anchor="start">limit</text><line x1="301" y1="150.0" x2="377" y2="150.0" class="dg-court"/><text x="383" y="154.0" class="dg-s" text-anchor="start">request</text><text x="339" y="214" class="dg-ct" text-anchor="middle" style="--d:1">ensuite</text><g class="dg-box dg-ok dg-pop" style="--d:2"><rect x="462" y="16" width="186" height="52" rx="9"/></g><text x="555.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:2">Guaranteed</text><text x="555.0" y="57.0" class="dg-s" text-anchor="middle" style="--d:2">request = limit</text><rect x="525" y="84" width="60" height="110" rx="6" class="dg-floor"/><rect x="525" y="117.0" width="60" height="77.0" rx="6" class="dg-fill"/><line x1="517" y1="117.0" x2="593" y2="117.0" class="dg-court"/><text x="599" y="121.0" class="dg-s" text-anchor="start">limit</text><line x1="517" y1="117.0" x2="593" y2="117.0" class="dg-court"/><text x="599" y="133.0" class="dg-s" text-anchor="start">request</text><text x="555" y="214" class="dg-okt" text-anchor="middle" style="--d:2">en dernier</text><path d="M30 234 L650 234" class="dg-l dash" marker-end="url(#g9-n)"/><text x="340" y="248" class="dg-s" text-anchor="middle">ordre d&#x27;éviction quand le nœud manque de mémoire</text></svg><figcaption>La classe dépend uniquement de la façon dont tu remplis requests et limits.</figcaption></figure>
<!-- /schema:qos -->

## Encadrer un namespace

```yaml
apiVersion: v1
kind: LimitRange
metadata: { name: defaults, namespace: team-a }
spec:
  limits:
    - type: Container
      defaultRequest: { cpu: 100m, memory: 128Mi }
      default: { memory: 256Mi }
---
apiVersion: v1
kind: ResourceQuota
metadata: { name: quota, namespace: team-a }
spec:
  hard:
    requests.cpu: "8"
    requests.memory: 16Gi
    pods: "50"
```

Avec une ResourceQuota sur le CPU ou la mémoire, tout pod **sans** requests est refusé. Le LimitRange évite ce problème en ajoutant des valeurs par défaut.

> **À retenir.** La request sert au placement et à la protection en cas de manque, la limite est un plafond : dépasser la limite CPU ralentit, dépasser la limite mémoire tue. Mets toujours des requests mesurées ; la classe QoS qui en découle décide qui est évincé en premier.
