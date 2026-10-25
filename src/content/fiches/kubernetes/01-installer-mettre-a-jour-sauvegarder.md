---
title: Installer, mettre à jour et sauvegarder un cluster
chapter: 1
order: 3
duration: 12
tags:
- CKA
- kubeadm
- etcd
cards:
- q: Quelles sont les deux commandes de base pour monter un cluster avec kubeadm ?
  a: '`kubeadm init` sur le premier nœud du control plane, puis `kubeadm join` sur chaque autre nœud. La commande de join complète s''obtient avec `kubeadm token create --print-join-command`.'
- q: Que faut-il installer juste après `kubeadm init` pour que les nœuds passent `Ready` ?
  a: Un **plugin réseau (CNI)** comme Calico, Cilium ou Flannel. Sans lui, les pods ne peuvent pas recevoir d'adresse et les nœuds restent `NotReady`.
- q: Dans quel ordre met-on à jour un cluster kubeadm ?
  a: 'Une **version mineure à la fois** (1.33 vers 1.34, pas 1.32 vers 1.34). Le control plane d''abord (`kubeadm upgrade apply` sur le premier, `kubeadm upgrade node` sur les autres), puis chaque worker : drain, kubeadm, kubelet, uncordon.'
- q: Le kubelet peut-il être plus récent que l'API server ?
  a: '**Non.** Il peut être plus ancien (jusqu''à trois versions mineures), jamais plus récent. C''est pour ça qu''on met à jour le control plane avant les workers.'
- q: Quelle commande sauvegarde etcd et quels fichiers lui faut-il ?
  a: '`etcdctl snapshot save <fichier>` avec `--endpoints`, `--cacert`, `--cert` et `--key`. Sur un cluster kubeadm, les certificats sont dans `/etc/kubernetes/pki/etcd/`.'
- q: Comment restaure-t-on un snapshot etcd ?
  a: '`etcdutl snapshot restore <fichier> --data-dir <nouveau dossier>`, puis on fait pointer le manifeste statique `/etc/kubernetes/manifests/etcd.yaml` vers ce nouveau dossier. Le kubelet redémarre etcd tout seul.'
- q: Combien de temps durent les certificats créés par kubeadm et comment les renouveler ?
  a: '**Un an.** `kubeadm certs check-expiration` affiche les dates, `kubeadm certs renew all` les renouvelle. Chaque `kubeadm upgrade` les renouvelle aussi.'
quiz:
- q: Ton cluster est en 1.32 et tu veux arriver en 1.34. Que fais-tu ?
  options:
  - '`kubeadm upgrade apply v1.34.x` directement'
  - Passer en 1.33 partout, puis en 1.34
  - Mettre à jour les workers en 1.34 d'abord
  - Réinstaller le cluster
  answer: 1
  explain: kubeadm ne saute pas de version mineure. On fait deux montées successives, control plane puis workers à chaque fois.
- q: Tu as restauré un snapshot dans `/var/lib/etcd-restore` mais le cluster montre toujours les anciennes données. Pourquoi ?
  options:
  - Il faut redémarrer tous les nœuds
  - Le manifeste d'etcd pointe encore sur l'ancien dossier `/var/lib/etcd`
  - Le snapshot est vide
  - Il faut relancer `kubeadm init`
  answer: 1
  explain: La restauration crée un nouveau dossier de données. Il faut modifier le `hostPath` dans `/etc/kubernetes/manifests/etcd.yaml` pour qu'etcd l'utilise.
- q: Avant de mettre à jour le kubelet d'un worker, que fais-tu ?
  options:
  - '`kubectl delete node`'
  - '`kubectl drain <nœud> --ignore-daemonsets`'
  - '`kubeadm reset`'
  - Rien, la mise à jour est transparente
  answer: 1
  explain: Le drain déplace les pods ailleurs et empêche d'en planifier de nouveaux. Après la mise à jour, `kubectl uncordon` remet le nœud en service.
level: intermédiaire
---

Sur un service managé (EKS, GKE, AKS), le fournisseur installe et met à jour le control plane pour toi. À la CKA, et sur un cluster maison, c'est à toi de le faire. L'outil officiel pour ça s'appelle **kubeadm**. Cette fiche couvre les trois gestes que l'examen demande à coup sûr : monter un cluster, le mettre à jour, et sauvegarder puis restaurer etcd.

> **Les outils cités dans cette fiche.**
> - **kubeadm** : l'outil officiel qui installe un cluster (certificats, manifestes du control plane, configuration du kubelet) et le met à jour. Il n'installe ni le réseau des pods ni les applications.
> - **kubelet** : l'agent qui tourne sur chaque nœud et lance les conteneurs. Il est installé comme paquet système, pas comme pod.
> - **CNI** (Container Network Interface) : le plugin qui donne une adresse IP aux pods et les relie entre eux. Exemples : **Calico**, **Cilium**, **Flannel**.
> - **etcd** : la base clé-valeur où le cluster garde tout son état (objets, secrets, configuration).
> - **etcdctl** et **etcdutl** : les commandes d'etcd. `etcdctl` parle à un etcd qui tourne (pour la sauvegarde), `etcdutl` travaille sur les fichiers (pour la restauration).
> - **manifeste statique** : un fichier YAML posé dans `/etc/kubernetes/manifests/`. Le kubelet lance le pod décrit sans passer par l'API server. C'est ainsi que tournent l'API server, etcd, le scheduler et le controller manager.
> - **EKS** : le service Kubernetes managé d'AWS.
> - **GKE** : le service Kubernetes managé de Google Cloud.
> - **AKS** : le service Kubernetes managé d'Azure.

## Comprendre ce que fait kubeadm

Un control plane, c'est quatre programmes (API server, etcd, scheduler, controller manager) qui doivent se faire confiance grâce à des **certificats**. kubeadm automatise la partie pénible :

1. il crée une petite autorité de certification dans `/etc/kubernetes/pki/` et signe tous les certificats ;
2. il écrit les manifestes statiques du control plane, que le kubelet démarre ;
3. il crée les fichiers kubeconfig (`admin.conf` pour toi, d'autres pour les composants) ;
4. il génère un **jeton** qui permet aux autres nœuds de rejoindre le cluster.

Le reste n'est pas son travail : installer le runtime de conteneurs (containerd), le kubelet, et ensuite le CNI.

## Monter un cluster

```bash
# Sur chaque nœud : containerd, kubelet, kubeadm et kubectl installés, swap géré, modules réseau chargés
# Sur le premier nœud du control plane :
kubeadm init --pod-network-cidr=10.244.0.0/16
mkdir -p ~/.kube && cp /etc/kubernetes/admin.conf ~/.kube/config

# Installer un CNI (exemple : appliquer le manifeste fourni par Calico ou Flannel)
kubectl apply -f <manifeste-du-cni>.yaml

# Obtenir la commande à lancer sur chaque worker
kubeadm token create --print-join-command
# Sur le worker :
kubeadm join 10.0.0.10:6443 --token <jeton> --discovery-token-ca-cert-hash sha256:<empreinte>
```

Le `--discovery-token-ca-cert-hash` est une protection : le worker vérifie qu'il parle au bon control plane avant de lui faire confiance.

## Mettre à jour un cluster

Deux règles guident tout le reste :

- **Une version mineure à la fois** : 1.33 vers 1.34, jamais 1.32 vers 1.34 d'un coup.
- **Le control plane d'abord** : un kubelet peut être plus ancien que l'API server, jamais plus récent.

```bash
# 1. Premier nœud du control plane
apt-get install -y kubeadm=1.34.1-*        # d'abord le binaire kubeadm
kubeadm upgrade plan                        # vérifie et affiche ce qui va changer
kubeadm upgrade apply v1.34.1
kubectl drain cp1 --ignore-daemonsets
apt-get install -y kubelet=1.34.1-* kubectl=1.34.1-*
systemctl daemon-reload && systemctl restart kubelet
kubectl uncordon cp1

# 2. Autres nœuds du control plane, puis chaque worker
apt-get install -y kubeadm=1.34.1-*
kubeadm upgrade node
kubectl drain worker1 --ignore-daemonsets   # lancé depuis une machine qui a kubectl
apt-get install -y kubelet=1.34.1-* kubectl=1.34.1-*
systemctl daemon-reload && systemctl restart kubelet
kubectl uncordon worker1
```

Sur les distributions où les paquets sont figés (`apt-mark hold`), il faut les libérer avec `apt-mark unhold` avant et les refiger après. Le **drain** vide le nœud proprement : il déplace les pods ailleurs en respectant les PodDisruptionBudgets.

## Sauvegarder et restaurer etcd

Tout l'état du cluster est dans etcd. Perdre etcd sans sauvegarde, c'est perdre le cluster entier, même si les conteneurs tournent encore.

```bash
# Sauvegarde (etcd tourne, on lui parle en TLS)
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

etcdutl snapshot status /backup/etcd.db -w table   # vérifier le fichier

# Restauration : on crée un NOUVEAU dossier de données
etcdutl snapshot restore /backup/etcd.db --data-dir /var/lib/etcd-restore
# Puis dans /etc/kubernetes/manifests/etcd.yaml, faire pointer le volume hostPath vers /var/lib/etcd-restore
```

Les chemins des certificats ne s'apprennent pas par cœur : ils sont écrits dans le manifeste `etcd.yaml` lui-même (`--cert-file`, `--key-file`, `--trusted-ca-file`). À l'examen, ouvre ce fichier et recopie-les.

## Les certificats qui expirent

kubeadm crée des certificats valables **un an**. Un cluster qui n'a pas été mis à jour depuis un an tombe en panne d'un coup, avec des erreurs `x509: certificate has expired`.

```bash
kubeadm certs check-expiration
kubeadm certs renew all       # puis redémarrer les pods du control plane
```

Chaque `kubeadm upgrade` renouvelle les certificats au passage : mettre à jour régulièrement évite donc aussi ce piège.

> **À retenir.** kubeadm installe le control plane mais pas le réseau des pods. Une mise à jour se fait une version mineure à la fois, control plane d'abord, avec un drain avant de toucher au kubelet. Une sauvegarde etcd se prend avec `etcdctl snapshot save` et les certificats lus dans `etcd.yaml` ; une restauration crée un nouveau dossier qu'il faut déclarer dans ce même manifeste.
