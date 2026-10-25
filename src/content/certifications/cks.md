---
title: CKS
name: Certified Kubernetes Security Specialist
org: Linux Foundation / CNCF
order: 3
color: "#34d399"
description: Sécuriser un cluster Kubernetes et les applications qui y tournent, en pratique.
officialUrl: https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/
checked: 22 octobre 2026
format:
  - { label: Type, value: "Examen pratique sur de vrais clusters, dans un terminal distant" }
  - { label: Durée, value: "2 heures, pour 15 à 20 tâches" }
  - { label: Score pour réussir, value: "67 %" }
  - { label: Prérequis, value: "Avoir une CKA valide au moment de passer l'examen" }
  - { label: Inclus, value: "Une seconde tentative gratuite et deux sessions de simulateur (killer.sh)" }
  - { label: Validité, value: "2 ans" }
domains:
  - name: Mise en place du cluster
    weight: 15
    fiches: [kubernetes/08-network-policies, kubernetes/04-ingress-et-gateway-api, securite/07-tls-et-pki, securite/06-securite-kubernetes, kubernetes/12-durcir-le-cluster]
  - name: Durcissement du cluster
    weight: 15
    fiches: [kubernetes/08-rbac, kubernetes/01-trajet-d-une-requete, securite/06-securite-kubernetes, kubernetes/12-durcir-le-cluster]
  - name: Durcissement du système
    weight: 10
    fiches: [securite/03-durcissement-linux, linux/02-utilisateurs-sudo-acl, kubernetes/08-pod-security, linux/02-selinux-et-apparmor, kubernetes/12-isoler-les-workloads]
  - name: Réduire les vulnérabilités des microservices
    weight: 20
    fiches: [kubernetes/08-pod-security, kubernetes/05-securiser-les-secrets, securite/02-gestion-des-secrets, securite/04-securite-des-conteneurs, kubernetes/12-isoler-les-workloads]
  - name: Sécurité de la chaîne d'approvisionnement
    weight: 20
    fiches: [securite/05-supply-chain, securite/04-securite-des-conteneurs]
  - name: Surveillance, journalisation et sécurité à l'exécution
    weight: 20
    fiches: [securite/06-securite-kubernetes, kubernetes/09-metriques-et-monitoring, devops/06-observabilite, securite/13-panorama-des-outils, kubernetes/12-detecter-et-auditer]
---

## Ce que l'examen vérifie vraiment

Même format que la CKA (des tâches sur de vrais clusters), mais toutes orientées sécurité : fermer un flux avec une NetworkPolicy, réduire les droits d'un ServiceAccount, imposer un profil de sécurité aux pods, corriger un Dockerfile, analyser une image, trouver avec Falco le pod qui lance un shell. On suppose que l'administration de base (CKA) est acquise : le temps est **plus serré**, parce que chaque tâche ajoute un outil.

## Les pièges

- **Les outils à apprendre en plus.** Trivy, kube-bench, Falco, AppArmor, la politique d'audit de l'API server : il faut les avoir **utilisés**, pas seulement lus. Leur documentation est autorisée, mais la chercher coûte cher en temps.
- **Modifier un composant du control plane.** Activer un plugin d'admission ou les journaux d'audit passe par le manifeste du pod statique `kube-apiserver`. Une faute de frappe et l'API ne redémarre plus : fais une copie du fichier avant, et attends que l'API revienne avant de passer à la suite.
- **Le même piège de contexte que la CKA** : bon cluster, bon namespace, à chaque tâche.

## À connaître par cœur

```bash
# Qui peut faire quoi
kubectl auth can-i --list --as=system:serviceaccount:dev:app -n dev

# Pod Security Admission sur un namespace
kubectl label ns dev pod-security.kubernetes.io/enforce=restricted

# Scanner une image
trivy image --severity HIGH,CRITICAL registry.local/api:2.1

# Composants du control plane (pods statiques)
ls /etc/kubernetes/manifests/
```

Et les réglages d'un conteneur durci (fiche « Pod Security ») : `runAsNonRoot`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem`, `capabilities: drop: [ALL]`, `seccompProfile: RuntimeDefault`.

## Stratégie le jour J

Même méthode que pour la CKA : un premier tour sur les tâches rapides, puis les longues. Pour les tâches qui touchent l'API server, garde-les pour le moment où tu as le temps d'attendre son redémarrage et de vérifier.
