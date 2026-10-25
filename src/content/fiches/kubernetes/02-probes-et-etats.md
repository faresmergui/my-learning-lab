---
title: Probes et états d'un pod
chapter: 2
order: 2
duration: 9
level: intermédiaire
tags:
- CKA
- CKAD
cards:
- q: Que se passe-t-il quand une **liveness** probe échoue ?
  a: Le kubelet **redémarre** le conteneur.
- q: Que se passe-t-il quand une **readiness** probe échoue ?
  a: 'Le pod est **retiré des endpoints** du Service : il ne reçoit plus de trafic, mais il n''est pas redémarré.'
- q: À quoi sert une **startup** probe ?
  a: À laisser du temps à une appli lente à démarrer. Tant qu'elle n'a pas réussi, les probes liveness et readiness sont suspendues.
- q: Un conteneur s'est terminé avec le code 137. Qu'est-ce que ça veut dire ?
  a: '128 + 9 : il a reçu **SIGKILL**. Le plus souvent un `OOMKilled` (limite mémoire dépassée), à vérifier dans `kubectl describe pod`.'
- q: Que fait Kubernetes quand il arrête un pod ?
  a: Il lance le hook `preStop` s'il existe, envoie **SIGTERM**, attend `terminationGracePeriodSeconds` (30 s par défaut), puis envoie **SIGKILL**.
- q: Différence entre `ImagePullBackOff` et `CrashLoopBackOff` ?
  a: '`ImagePullBackOff` : l''image ne peut pas être téléchargée (nom, tag, accès au registre). `CrashLoopBackOff` : l''image démarre mais le conteneur s''arrête en erreur, encore et encore.'
quiz:
- q: Un pod affiche `CrashLoopBackOff`. Que se passe-t-il ?
  options:
  - L'image est introuvable dans le registre
  - Le conteneur démarre puis s'arrête en erreur, et le kubelet le relance avec un délai croissant
  - Aucun nœud n'a assez de ressources
  - Le nœud est NotReady
  answer: 1
  explain: Le délai double à chaque échec, jusqu'à 5 minutes. Regarde `kubectl logs <pod> --previous` pour voir pourquoi le conteneur précédent s'est arrêté.
- q: Ta liveness probe vérifie la connexion à la base de données. La base tombe. Que va-t-il se passer ?
  options:
  - Rien de grave
  - Tous les pods redémarrent en boucle, alors que redémarrer ne répare rien
  - Les pods sont seulement retirés du Service
  - Le Deployment est supprimé
  answer: 1
  explain: Une liveness probe ne doit tester que le processus lui-même. Les dépendances externes relèvent de la readiness probe.
- q: Un pod affiche `CreateContainerConfigError`. Quelle est la cause la plus probable ?
  options:
  - Un Secret ou un ConfigMap référencé n'existe pas
  - La limite CPU est trop basse
  - La readiness probe échoue
  - Le scheduler est arrêté
  answer: 0
  explain: Le kubelet ne peut pas construire la configuration du conteneur. `kubectl describe pod` indique quelle référence manque.
---

Les probes disent au kubelet comment savoir si ton appli va bien. Bien réglées, elles évitent les coupures. Mal réglées, elles en provoquent.

<!-- schema:timeline -->
<figure class="diagram"><svg viewBox="0 0 680 230" role="img" aria-label="Les trois probes dans la vie d&#x27;un conteneur" style="--minw:560px"><defs><marker id="g4-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g4-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g4-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g4-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="20" y="59" class="dg-t" text-anchor="start">startupProbe</text><line x1="150" y1="54" x2="660" y2="54" class="dg-grid"/><text x="20" y="115" class="dg-t" text-anchor="start">readinessProbe</text><line x1="150" y1="110" x2="660" y2="110" class="dg-grid"/><text x="20" y="171" class="dg-t" text-anchor="start">livenessProbe</text><line x1="150" y1="166" x2="660" y2="166" class="dg-grid"/><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="150" y="40" width="150" height="28" rx="6"/></g><text x="225.0" y="59.0" class="dg-s" text-anchor="middle" style="--d:0">démarrage lent toléré</text><text x="306" y="59" class="dg-s" text-anchor="start">réussie : passe la main</text><g class="dg-box dg-ok dg-pop" style="--d:1"><rect x="300" y="96" width="150" height="28" rx="6"/></g><text x="375.0" y="115.0" class="dg-s" text-anchor="middle" style="--d:1">reçoit du trafic</text><g class="dg-box dg-a dg-pop" style="--d:2"><rect x="450" y="96" width="110" height="28" rx="6"/></g><text x="505.0" y="115.0" class="dg-s" text-anchor="middle" style="--d:2">retiré du Service</text><g class="dg-box dg-ok dg-pop" style="--d:3"><rect x="560" y="96" width="100" height="28" rx="6"/></g><text x="610.0" y="115.0" class="dg-s" text-anchor="middle" style="--d:3">trafic</text><g class="dg-box dg-ok dg-pop" style="--d:1"><rect x="300" y="152" width="290" height="28" rx="6"/></g><text x="445.0" y="171.0" class="dg-s" text-anchor="middle" style="--d:1">vivant</text><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="590" y="152" width="70" height="28" rx="6"/></g><text x="625.0" y="171.0" class="dg-s" text-anchor="middle" style="--d:4">restart</text><line x1="300" y1="30" x2="300" y2="190" class="dg-grid"/><path d="M150 204 L660 204" class="dg-l" marker-end="url(#g4-n)"/><text x="150" y="222" class="dg-s" text-anchor="start">démarrage</text><text x="660" y="222" class="dg-s" text-anchor="end">temps</text></svg><figcaption>readiness décide du trafic, liveness décide du redémarrage. startup protège les démarrages lents.</figcaption></figure>
<!-- /schema:timeline -->


> **Les termes et outils cités dans cette fiche.**
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **OOM** : out of memory : la mémoire est épuisée, le noyau tue un processus pour en libérer.
> - **SIGTERM** : le signal qui demande poliment à un processus de s'arrêter.
> - **registre** : le serveur qui stocke et distribue les images de conteneurs (Docker Hub, GitLab, Harbor).

## Les trois probes

| Probe | Question posée | Si elle échoue |
| --- | --- | --- |
| `startupProbe` | L'appli a-t-elle fini de démarrer ? | Les autres probes attendent, puis le conteneur est redémarré |
| `livenessProbe` | Le processus est-il bloqué ? | Le conteneur est **redémarré** |
| `readinessProbe` | Peut-il recevoir du trafic ? | Le pod est **retiré du Service** |

```yaml
startupProbe:
  httpGet: { path: /healthz, port: 8080 }
  failureThreshold: 30   # 30 × 5 s = 2 min 30 pour démarrer
  periodSeconds: 5
livenessProbe:
  httpGet: { path: /healthz, port: 8080 }
  periodSeconds: 10
readinessProbe:
  httpGet: { path: /ready, port: 8080 }
  periodSeconds: 5
```

> **Piège classique.** Ne teste jamais une dépendance externe (base, API) dans la liveness probe. Si elle tombe, tous tes pods redémarrent en boucle pour rien.

## Comprendre la différence liveness / readiness

Les deux probes posent des questions différentes, et leurs conséquences n'ont rien à voir :

- **readiness** = « es-tu **disponible** maintenant ? ». En cas d'échec, le pod est simplement **retiré** des endpoints du Service : il ne reçoit plus de requêtes, mais il continue de tourner. Dès que la probe repasse, il est remis. C'est un retrait **temporaire et sans casse** : parfait pour un pod surchargé, en train de se réchauffer, ou dont une dépendance indispensable est indisponible.
- **liveness** = « es-tu **bloqué** au point qu'il faut te redémarrer ? ». En cas d'échec, le kubelet **tue** le conteneur. C'est une mesure brutale, réservée aux blocages que seul un redémarrage peut résoudre (un interblocage, une boucle infinie).

D'où le piège : si la liveness vérifie la base de données et que la base ralentit, **tous** les pods redémarrent en même temps. Le redémarrage ne répare pas la base, et pendant ce temps plus rien ne répond.

La **startup** protège les applis lentes à démarrer : tant qu'elle n'a pas réussi, la liveness ne s'exécute pas, ce qui évite de tuer une appli Java qui met 90 s à se lancer.

## Les réglages d'une probe

| Champ | Rôle | Défaut |
| --- | --- | --- |
| `periodSeconds` | intervalle entre deux tests | 10 |
| `timeoutSeconds` | délai max de réponse | 1 |
| `failureThreshold` | échecs consécutifs avant d'agir | 3 |
| `successThreshold` | succès pour être de nouveau considéré OK | 1 |
| `initialDelaySeconds` | attente avant le premier test | 0 |

Avec les défauts, une liveness déclare l'échec après environ 30 s (3 × 10 s). Un `timeoutSeconds: 1` trop court sur une appli chargée provoque des redémarrages au pire moment : quand elle est déjà sous pression.

## Lire « CrashLoopBackOff »

Ce n'est pas une erreur en soi : c'est le kubelet qui **espace** les redémarrages (10 s, 20 s, 40 s… jusqu'à 5 min) d'un conteneur qui s'arrête sans cesse. La vraie cause est dans les logs du conteneur **précédent** (`--previous`) et dans son code de sortie : `1` = erreur de l'appli, `137` = tué (souvent OOM), `143` = arrêt par SIGTERM.

## Lire l'état d'un pod

- **Phase** du pod : `Pending`, `Running`, `Succeeded`, `Failed`, `Unknown`.
- **État** de chaque conteneur : `Waiting`, `Running` ou `Terminated`, avec une raison.

| Raison | Ce que ça veut dire | Premier réflexe |
| --- | --- | --- |
| `ImagePullBackOff` | Image introuvable ou registre inaccessible | Vérifier le nom, le tag, `imagePullSecrets` |
| `CrashLoopBackOff` | Le conteneur plante en boucle | `kubectl logs --previous` |
| `OOMKilled` (code 137) | Limite mémoire dépassée | Augmenter la limite ou corriger la fuite |
| `CreateContainerConfigError` | Secret ou ConfigMap manquant | `kubectl describe pod` |

## Un arrêt propre

À l'arrêt, Kubernetes exécute `preStop`, envoie `SIGTERM`, attend `terminationGracePeriodSeconds` (30 s par défaut), puis envoie `SIGKILL`. Ton appli doit intercepter `SIGTERM` pour finir ses requêtes en cours.

> **À retenir.** Readiness retire le pod du trafic sans le tuer, liveness le redémarre, startup laisse le temps de démarrer. Ne mets jamais une dépendance externe dans la liveness, et cherche la cause d'un `CrashLoopBackOff` dans `kubectl logs --previous` et le code de sortie.
