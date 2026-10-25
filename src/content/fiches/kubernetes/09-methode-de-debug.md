---
title: Une méthode de debug
chapter: 9
order: 1
duration: 8
level: intermédiaire
tags:
- CKA
cards:
- q: Quelles sont les trois premières commandes face à un pod qui ne va pas ?
  a: '`kubectl get pod -o wide` (état, nœud), `kubectl describe pod` (événements, raisons), `kubectl logs` (et `--previous` si le conteneur a redémarré).'
- q: Comment lire les logs d'un conteneur qui a planté et redémarré ?
  a: '`kubectl logs <pod> --previous` (ou `-p`). Sans cette option, tu vois les logs du conteneur actuel, souvent vides.'
- q: Comment déboguer un conteneur basé sur une image *distroless*, sans shell ?
  a: 'Avec un **conteneur éphémère** : `kubectl debug -it <pod> --image=busybox:1.36 --target=<conteneur>`. `--target` donne accès à ses processus.'
- q: Comment obtenir un shell sur un nœud sans SSH ?
  a: '`kubectl debug node/<nœud> -it --image=ubuntu`. Le système de fichiers du nœud est monté dans `/host`.'
- q: Un nœud est `NotReady`. Où regarder ?
  a: '`kubectl describe node` (conditions : mémoire, disque, PID, réseau), puis sur le nœud : `systemctl status kubelet`, `journalctl -u kubelet` et `crictl ps`.'
- q: Comment tester un Service depuis l'intérieur du cluster ?
  a: '`kubectl run tmp --rm -it --image=busybox:1.36 -- sh`, puis `nslookup api` et `wget -qO- http://api`. Ou `kubectl port-forward svc/api 8080:80` depuis ton poste.'
quiz:
- q: Un pod est en `Pending` depuis 10 minutes. Quelle commande donne la raison le plus vite ?
  options:
  - kubectl logs
  - kubectl describe pod
  - kubectl exec
  - kubectl top pod
  answer: 1
  explain: 'Un pod Pending n''a pas encore démarré, il n''a donc pas de logs. Les événements de `describe` affichent par exemple `0/3 nodes are available: insufficient memory`.'
- q: '`kubectl logs` renvoie `container not found` sur un pod à plusieurs conteneurs. Que faire ?'
  options:
  - Préciser le conteneur avec `-c <nom>` ou utiliser `--all-containers`
  - Redémarrer le pod
  - Utiliser `kubectl describe`
  - Le pod n'a pas de logs
  answer: 0
  explain: '`kubectl get pod <pod> -o jsonpath=''{.spec.containers[*].name}''` liste les noms des conteneurs.'
- q: Ton appli répond via `kubectl port-forward pod/...` mais pas via le Service. Où est le problème ?
  options:
  - Dans l'appli
  - 'Entre le Service et les pods : selector, targetPort ou readiness'
  - Dans le DNS du poste
  - Dans l'image
  answer: 1
  explain: 'Le port-forward vers le pod prouve que l''appli fonctionne. Il reste le Service : ses EndpointSlices, son `targetPort` et l''état Ready des pods.'
---

Déboguer Kubernetes, c'est surtout savoir **dans quel ordre** regarder. Cette méthode couvre la grande majorité des cas.

> **Les outils et termes cités dans cette fiche.**
> - **kubectl describe** et **kubectl get events** : affichent l'historique récent d'un objet (planification, téléchargement d'image, échecs de probe). C'est souvent là que se trouve la réponse.
> - **CrashLoopBackOff** et **ImagePullBackOff** : des états où Kubernetes réessaie en attendant de plus en plus longtemps (*back-off*), respectivement après un plantage de l'appli ou un échec de téléchargement de l'image.
> - **Conteneur éphémère** (`kubectl debug`) : un conteneur temporaire ajouté à un pod en marche, avec des outils de diagnostic, quand l'image de l'appli n'a même pas de shell.
> - **busybox** : une image minuscule qui regroupe les commandes Unix de base (`sh`, `wget`, `nslookup`).
> - **port-forward** : relie un port de ta machine à un pod ou un Service, pour le tester sans l'exposer.
> - **crictl** : l'équivalent de `docker ps` côté nœud, qui parle directement au runtime de conteneurs (containerd, CRI-O).
> - **chroot /host** : dans un pod de debug de nœud, bascule à la racine du système du nœud pour utiliser ses commandes (`journalctl`, etc.).
> - **PVC** : une demande de volume persistant faite par un pod.
> - **registre** : le serveur qui stocke et distribue les images de conteneurs (Docker Hub, GitLab, Harbor).

<!-- schema:arbre -->
<figure class="diagram"><svg viewBox="0 0 680 270" role="img" aria-label="Par où commencer selon l&#x27;état du pod" style="--minw:560px"><defs><marker id="g13-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g13-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g13-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g13-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="240" y="12" width="200" height="48" rx="9"/></g><text x="340.0" y="33.0" class="dg-t" text-anchor="middle" style="--d:0">kubectl get pod</text><text x="340.0" y="51.0" class="dg-s" text-anchor="middle" style="--d:0">quel état ?</text><path d="M340 60 L340 80 L88 80 L88 100" class="dg-l c" marker-end="url(#g13-c)" style="--d:0"/><g class="dg-box dg-pop" style="--d:1"><rect x="14" y="102" width="148" height="44" rx="9"/></g><text x="88.0" y="129.0" class="dg-t" text-anchor="middle" style="--d:1">Pending</text><g class="dg-box dg-ghost dg-pop" style="--d:1"><rect x="14" y="162" width="148" height="40" rx="9"/></g><text x="88.0" y="187.0" class="dg-s" text-anchor="middle" style="--d:1">describe : events</text><path d="M88 146 L88 160" class="dg-l" marker-end="url(#g13-n)"/><text x="88" y="222" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="88" dy="0">ressources, PVC,</tspan><tspan x="88" dy="14">taints, quota</tspan></text><path d="M340 60 L340 80 L254 80 L254 100" class="dg-l c" marker-end="url(#g13-c)" style="--d:1"/><g class="dg-box dg-pop" style="--d:2"><rect x="180" y="102" width="148" height="44" rx="9"/></g><text x="254.0" y="129.0" class="dg-t" text-anchor="middle" style="--d:2">ContainerCreating</text><g class="dg-box dg-ghost dg-pop" style="--d:2"><rect x="180" y="162" width="148" height="40" rx="9"/></g><text x="254.0" y="187.0" class="dg-s" text-anchor="middle" style="--d:2">describe : events</text><path d="M254 146 L254 160" class="dg-l" marker-end="url(#g13-n)"/><text x="254" y="222" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="254" dy="0">image, secret,</tspan><tspan x="254" dy="14">volume</tspan></text><path d="M340 60 L340 80 L420 80 L420 100" class="dg-l c" marker-end="url(#g13-c)" style="--d:2"/><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="346" y="102" width="148" height="44" rx="9"/></g><text x="420.0" y="129.0" class="dg-t" text-anchor="middle" style="--d:3">CrashLoopBackOff</text><g class="dg-box dg-ghost dg-pop" style="--d:3"><rect x="346" y="162" width="148" height="40" rx="9"/></g><text x="420.0" y="187.0" class="dg-s" text-anchor="middle" style="--d:3">logs --previous</text><path d="M420 146 L420 160" class="dg-l" marker-end="url(#g13-n)"/><text x="420" y="222" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="420" dy="0">l&#x27;appli plante</tspan><tspan x="420" dy="14">au démarrage</tspan></text><path d="M340 60 L340 80 L586 80 L586 100" class="dg-l c" marker-end="url(#g13-c)" style="--d:3"/><g class="dg-box dg-pop" style="--d:4"><rect x="512" y="102" width="148" height="44" rx="9"/></g><text x="586.0" y="129.0" class="dg-t" text-anchor="middle" style="--d:4">Running mais KO</text><g class="dg-box dg-ghost dg-pop" style="--d:4"><rect x="512" y="162" width="148" height="40" rx="9"/></g><text x="586.0" y="187.0" class="dg-s" text-anchor="middle" style="--d:4">readiness, endpoints</text><path d="M586 146 L586 160" class="dg-l" marker-end="url(#g13-n)"/><text x="586" y="222" class="dg-s" text-anchor="middle" style="--d:4"><tspan x="586" dy="0">Service, réseau,</tspan><tspan x="586" dy="14">NetworkPolicy</tspan></text></svg><figcaption>L&#x27;état du pod indique la bonne commande. Ne lis pas les logs d&#x27;un pod qui n&#x27;a jamais démarré.</figcaption></figure>
<!-- /schema:arbre -->

## 1. Où en est le pod ?

```bash
kubectl get pod api-7d9f -o wide          # état, redémarrages, nœud, IP
kubectl describe pod api-7d9f             # événements en bas : la réponse est souvent là
kubectl get events -n shop --sort-by=.lastTimestamp
```

| Symptôme | Piste |
| --- | --- |
| `Pending` | scheduling : ressources, taints, affinités, PVC |
| `ImagePullBackOff` | image, tag, registre, `imagePullSecrets` |
| `CrashLoopBackOff` | l'appli plante : logs du conteneur précédent |
| `Running` mais pas Ready | readiness probe, dépendances |
| `Running` et Ready, mais pas joignable | Service, NetworkPolicy, Ingress |

## 2. Que dit l'appli ?

```bash
kubectl logs api-7d9f --previous
kubectl logs deploy/api --all-containers --since=15m
kubectl exec -it api-7d9f -- sh
```

## 3. Pas de shell ? Un conteneur éphémère

```bash
kubectl debug -it api-7d9f --image=busybox:1.36 --target=api
# ou une copie du pod, avec une autre commande de démarrage :
kubectl debug api-7d9f -it --copy-to=api-debug --container=api -- sh
```

## 4. Le réseau

```bash
kubectl run tmp --rm -it --image=busybox:1.36 -- sh
# nslookup api.shop ; wget -qO- http://api.shop
kubectl port-forward svc/api 8080:80
```

## 5. Le nœud

```bash
kubectl describe node node-2       # conditions MemoryPressure, DiskPressure…
kubectl debug node/node-2 -it --image=ubuntu
# chroot /host ; journalctl -u kubelet -n 100 ; crictl ps -a
```

> **À retenir.** Remonte la chaîne dans l'ordre : pod, conteneur, Service, réseau, nœud. Ne saute pas à « c'est le réseau » avant d'avoir lu les événements.
