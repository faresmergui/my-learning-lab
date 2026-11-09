---
title: CKA
name: Certified Kubernetes Administrator
org: Linux Foundation / CNCF
order: 1
color: "#4f7cf0"
description: Administrer un cluster Kubernetes en ligne de commande, en conditions réelles.
officialUrl: https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/
checked: 22 octobre 2026
format:
  - { label: Type, value: "Examen pratique : des tâches à réaliser sur de vrais clusters, dans un terminal distant" }
  - { label: Durée, value: "2 heures, pour 15 à 20 tâches" }
  - { label: Score pour réussir, value: "66 %" }
  - { label: Documentation autorisée, value: "kubernetes.io (docs, blog) et les docs des outils cités dans l'énoncé" }
  - { label: Inclus, value: "Une seconde tentative gratuite et deux sessions de simulateur (killer.sh)" }
  - { label: Validité, value: "2 ans" }
domains:
  - name: Troubleshooting
    weight: 30
    fiches: [kubernetes/09-methode-de-debug, kubernetes/02-probes-et-etats, kubernetes/09-metriques-et-monitoring, reseaux/08-reseau-kubernetes-et-cni, linux/07-journald-et-logs]
  - name: Architecture, installation et configuration du cluster
    weight: 25
    fiches: [kubernetes/01-composants-du-cluster, kubernetes/01-trajet-d-une-requete, kubernetes/08-rbac, kubernetes/10-helm, kubernetes/10-kustomize-et-gitops, kubernetes/01-installer-mettre-a-jour-sauvegarder, kubernetes/10-crd-et-operateurs]
  - name: Services et réseau
    weight: 20
    fiches: [kubernetes/04-services, kubernetes/04-ingress-et-gateway-api, kubernetes/08-network-policies, reseaux/03-dns]
  - name: Workloads et scheduling
    weight: 15
    fiches: [kubernetes/03-deployments-et-rolling-updates, kubernetes/03-statefulset-daemonset-job, kubernetes/02-pods-multi-conteneurs, kubernetes/05-injecter-la-configuration, kubernetes/07-requests-limits-qos, kubernetes/07-taints-et-affinites, kubernetes/07-repartir-et-prioriser]
  - name: Stockage
    weight: 10
    fiches: [kubernetes/06-pv-pvc-storageclass, kubernetes/06-volumes-ephemeres]
  - name: Se préparer à l'examen
    fiches: [kubernetes/11-passer-l-examen-cka]
training:
  start: "2026-11-09"
  rhythm: "4 sessions de 30 min en semaine et 1 h le week-end, environ 3 h par semaine, sans créneau fixe"
  weeks:
    - theme: "Mise en place : alias `k`, autocomplétion, vim. Udemy : architecture du cluster"
      lab: "Monter `cp1`, `w1` et `w2` avec kubeadm"
      fiches: [kubernetes/01-composants-du-cluster, kubernetes/01-trajet-d-une-requete]
    - theme: "Notions de base : pods, ReplicaSets, Deployments, Services, namespaces, YAML généré avec `--dry-run=client -o yaml`"
      lab: "Tout recréer en commandes impératives"
      fiches: [kubernetes/03-deployments-et-rolling-updates, kubernetes/04-services]
    - theme: "Scheduling : labels, taints et tolérations, affinités, ressources, DaemonSets, pods statiques"
      lab: "Un pod statique sur `w1`"
      milestone: "Acheter l'examen si la promo Black Friday est là"
      fiches: [kubernetes/07-taints-et-affinites, kubernetes/07-requests-limits-qos, kubernetes/07-repartir-et-prioriser, kubernetes/03-statefulset-daemonset-job]
    - theme: "Cycle de vie des applications : rolling updates, ConfigMaps, Secrets, multi-conteneurs, autoscaling, monitoring"
      lab: "Rolling update puis rollback"
      fiches: [kubernetes/05-injecter-la-configuration, kubernetes/02-pods-multi-conteneurs, kubernetes/02-probes-et-etats, kubernetes/09-metriques-et-monitoring]
    - theme: "Maintenance : drain et cordon, mise à jour kubeadm, sauvegarde et restauration etcd"
      lab: "Mise à jour d'une version mineure, puis restauration etcd"
      fiches: [kubernetes/01-installer-mettre-a-jour-sauvegarder]
    - theme: "Sécurité 1 : certificats TLS, kubeconfig, RBAC, `kubectl auth can-i`"
      lab: "Un utilisateur limité à un namespace"
      fiches: [kubernetes/08-rbac]
    - theme: "Fêtes : semaine légère, flashcards et deux scénarios Killercoda"
      lab: "Repos"
    - theme: "Sécurité 2 : ServiceAccounts, securityContext, NetworkPolicies"
      lab: "Isoler un namespace avec une NetworkPolicy"
      fiches: [kubernetes/08-network-policies, kubernetes/08-pod-security]
    - theme: "Stockage : PV, PVC, StorageClass, volumes"
      lab: "Un PVC lié à un PV `hostPath`"
      fiches: [kubernetes/06-pv-pvc-storageclass, kubernetes/06-volumes-ephemeres]
    - theme: "Réseau 1 : réseau des pods, CNI, DNS et CoreDNS, Services"
      lab: "Diagnostiquer la résolution DNS d'un pod"
      fiches: [reseaux/08-reseau-kubernetes-et-cni, reseaux/03-dns]
    - theme: "Réseau 2 : Ingress et Gateway API"
      lab: "Exposer une appli avec une HTTPRoute"
      fiches: [kubernetes/04-ingress-et-gateway-api]
    - theme: "Helm, Kustomize, CRD et opérateurs"
      lab: "Installer un chart, puis un overlay Kustomize"
      fiches: [kubernetes/10-helm, kubernetes/10-kustomize-et-gitops, kubernetes/10-crd-et-operateurs]
    - theme: "Installation : reconstruire le cluster de zéro, sans tutoriel, au chrono"
      lab: "Objectif : moins de 45 min"
      fiches: [kubernetes/01-installer-mettre-a-jour-sauvegarder]
    - theme: "Troubleshooting 1 : applications, control plane (`/etc/kubernetes/manifests/`), nœuds (kubelet, `journalctl`)"
      lab: "Casser puis réparer l'apiserver et le kubelet"
      fiches: [kubernetes/09-methode-de-debug, linux/07-journald-et-logs]
    - theme: "Troubleshooting 2 : réseau"
      lab: "killer.sh à la place du homelab"
      milestone: "Week-end : killer.sh, session 1 (environ 2 h, exception au rythme)"
      fiches: [reseaux/08-reseau-kubernetes-et-cni]
    - theme: "Refaire les tâches ratées de killer.sh, travailler les points faibles"
      lab: "Selon les points faibles"
    - theme: "Examens blancs Udemy au chrono"
      lab: "Un examen blanc complet"
      milestone: "Réserver la date d'examen"
      fiches: [kubernetes/11-passer-l-examen-cka]
    - theme: "killer.sh, session 2, puis seulement des révisions légères"
      lab: "Repos"
      milestone: "killer.sh, session 2"
    - theme: "Semaine de l'examen"
      milestone: "Examen CKA"
  tools:
    - name: "Cours Udemy de Mumshad Mannambeth (KodeKloud)"
      role: "La colonne vertébrale : tout le programme, en vidéos courtes, avec des labs dans le navigateur."
      when: "Sessions 1 à 3 de chaque semaine."
    - name: "killer.sh"
      role: "Le simulateur le plus proche de l'examen, en plus dur. Deux sessions incluses avec l'examen, chacune ouverte 36 h."
      when: "Semaines 15 et 18."
      url: https://killer.sh
    - name: "Killercoda"
      role: "Des scénarios CKA gratuits de 10 à 20 min, dans le navigateur."
      when: "Session 4 de chaque semaine, sans regarder la solution."
      url: https://killercoda.com
    - name: "LabEx Pro"
      role: "Des labs guidés pas à pas. Fait doublon avec Udemy et Killercoda."
      when: "Seulement sur un sujet qui bloque. Ne pas renouveler pour la seule CKA."
      url: https://labex.io
    - name: "Homelab kubeadm"
      role: "Le vrai cluster : installation, mise à jour, etcd, dépannage des nœuds."
      when: "Chaque week-end."
    - name: "Documentation kubernetes.io"
      role: "La seule documentation autorisée le jour de l'examen."
      when: "Dans tous les exercices, à la place de Google."
      url: https://kubernetes.io/docs/
    - name: "Ce learning hub"
      role: "Fiches, flashcards et quiz pour réviser."
      when: "Le quiz du chapitre en fin de semaine, les cartes pendant les temps morts."
    - name: "Kubernetes the Hard Way"
      role: "Monter un cluster à la main pour comprendre les rouages. Peu rentable pour l'examen."
      when: "Après la certification."
      url: https://github.com/kelseyhightower/kubernetes-the-hard-way
  checkpoints:
    - "Chaque fin de semaine : au moins 80 % au quiz du chapitre. Sinon, le thème reste une semaine de plus, une seule fois."
    - "Semaine 13 : le cluster est remonté sans tutoriel en moins de 45 min."
    - "killer.sh, session 1 : un score moyen n'est pas grave. Ce qui compte, c'est le nombre de tâches non terminées faute de temps."
    - "Examens blancs Udemy : au moins 80 % avant de réserver (repère, pas un seuil officiel)."
    - "Plus de deux semaines de retard au 1er février : l'examen passe à mi-avril."
---

## Ce que l'examen vérifie vraiment

La CKA ne pose aucune question de cours : elle te donne un cluster et une tâche (« le pod `api` ne démarre pas, répare-le », « crée un utilisateur qui ne peut lire que les pods du namespace `dev` »). Elle vérifie que tu sais **faire**, **vite**, avec `kubectl` et la documentation. Le troubleshooting pèse presque un tiers de la note : c'est là qu'il faut être le plus à l'aise.

## Les pièges

- **Le mauvais contexte.** Chaque tâche indique sur quel cluster travailler. Une tâche parfaite faite sur le mauvais cluster rapporte zéro point. Lance la commande `kubectl config use-context …` (ou le `ssh`) donnée en tête de tâche, à chaque fois.
- **Le mauvais namespace.** Ajoute `-n <ns>` partout, ou change le namespace par défaut du contexte. Un objet créé dans `default` au lieu de `dev` ne compte pas.
- **Rester bloqué.** Toutes les tâches ne valent pas autant de points. Au-delà de 6 à 8 minutes sur une tâche, note-la et passe à la suivante.
- **Écrire le YAML à la main.** C'est lent et source de fautes d'indentation. Génère-le, puis modifie-le.
- **Oublier de vérifier.** Après chaque tâche, un `kubectl get` ou un `describe` confirme que l'objet est bien là et dans l'état voulu.

## À connaître par cœur

```bash
# Générer du YAML au lieu de l'écrire
kubectl create deployment api --image=nginx --replicas=3 --dry-run=client -o yaml > api.yaml
kubectl run tmp --image=busybox:1.36 --restart=Never --dry-run=client -o yaml -- sleep 3600
kubectl expose deployment api --port=80 --target-port=8080 --dry-run=client -o yaml

# Trouver un champ sans quitter le terminal
kubectl explain pod.spec.containers.securityContext

# RBAC
kubectl create role ... ; kubectl create rolebinding ...
kubectl auth can-i list pods -n dev --as=jane

# Diagnostic
kubectl describe pod <pod> ; kubectl logs <pod> --previous
kubectl get events -n <ns> --sort-by=.lastTimestamp
journalctl -u kubelet -n 50     # sur le nœud
```

Côté cluster, sache aussi retrouver les manifestes des composants du control plane (`/etc/kubernetes/manifests/`, ce sont des pods statiques), la configuration du kubelet (`/var/lib/kubelet/config.yaml`) et les certificats (`/etc/kubernetes/pki/`).

## Stratégie le jour J

1. **Premier tour rapide** : fais toutes les tâches courtes et sûres, saute les longues.
2. **Deuxième tour** : reviens sur les tâches notées, de la plus rentable à la moins rentable.
3. **Dix dernières minutes** : relis les tâches faites, vérifie contexte et namespace.

Prépare-toi avec la fiche « Passer l'examen CKA » et les deux sessions du simulateur : la première tôt, pour mesurer l'écart, la seconde quelques jours avant l'examen.
