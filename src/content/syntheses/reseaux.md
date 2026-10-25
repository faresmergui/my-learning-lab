---
title: Synthèse réseaux
description: "Couches, adressage, ports, DNS, HTTP et TLS, pare-feu, conteneurs et Kubernetes, et les commandes de diagnostic."
---

## Les couches

| Couche (TCP/IP) | Couche OSI | Exemples | Unité |
| --- | --- | --- | --- |
| Application | 7, 6, 5 | HTTP, DNS, SSH, TLS | message |
| Transport | 4 | TCP, UDP | segment / datagramme |
| Internet | 3 | IP, ICMP | paquet |
| Accès réseau | 2, 1 | Ethernet, Wi-Fi, ARP | trame |

Un **load balancer L4** répartit sur IP et port, un **L7** lit le HTTP (chemin, en-têtes, cookies).

## L'adressage et le CIDR

| Masque | Adresses | Usage typique |
| --- | --- | --- |
| /32 | 1 | Une seule machine (règle de pare-feu) |
| /28 | 16 | Petit sous-réseau |
| /24 | 256 | Sous-réseau classique |
| /20 | 4 096 | Sous-réseau de cluster |
| /16 | 65 536 | VPC |

Plages privées : `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`. Adresses perdues par sous-réseau : réseau et broadcast (et souvent 3 de plus chez les clouds). Chaque /1 de moins **double** la taille.

## Les ports à connaître

| Port | Service |
| --- | --- |
| 22 | SSH |
| 53 | DNS (UDP et TCP) |
| 80 / 443 | HTTP / HTTPS |
| 123 | NTP |
| 3306 / 5432 | MySQL / PostgreSQL |
| 6379 | Redis |
| 6443 | API Kubernetes |
| 2379-2380 | etcd |
| 10250 | kubelet |
| 30000-32767 | NodePort Kubernetes |
| 9090 / 3000 | Prometheus / Grafana |

## TCP et UDP

- **TCP** : connexion (SYN, SYN-ACK, ACK), ordre garanti, retransmission. HTTP/1.1, HTTP/2, SSH, bases de données.
- **UDP** : sans connexion, pas de garantie. DNS, NTP, streaming, HTTP/3 (QUIC).
- `connection refused` : la machine répond mais rien n'écoute. `timeout` : un pare-feu filtre ou la machine est injoignable.

## DNS

| Enregistrement | Rôle |
| --- | --- |
| A / AAAA | Nom → IPv4 / IPv6 |
| CNAME | Alias vers un autre nom (pas à l'apex) |
| MX | Serveurs de mail |
| TXT | Vérifications, SPF, DKIM |
| NS | Serveurs faisant autorité |
| SRV | Service, port et cible |

Le **TTL** dit combien de temps une réponse est gardée en cache : le baisser **avant** une migration. Dans Kubernetes : `svc.namespace.svc.cluster.local`, et l'option `ndots:5` multiplie les requêtes pour les noms courts.

## DNS, DHCP et IPAM en entreprise (Infoblox)

- **DDI** = DNS + DHCP + IPAM sur une même base : réserver une IP crée son DNS et l'exclut du DHCP.
- **IPAM** : l'inventaire des réseaux et des adresses (libres, réservées, à qui).
- **Grid** : toutes les appliances Infoblox gérées depuis le **Grid Master**.
- Automatisation : API **WAPI** (`func:nextavailableip:10.0.12.0/24`), provider Terraform `infobloxopen/infoblox`, collection Ansible `infoblox.nios_modules`, ExternalDNS pour Kubernetes.

## HTTP et TLS

| Code | Sens |
| --- | --- |
| 2xx | Succès (200, 201, 204) |
| 3xx | Redirection (301 permanente, 302 / 307 temporaire, 304 non modifié) |
| 4xx | Erreur du client (400, 401 non authentifié, 403 interdit, 404, 429 trop de requêtes) |
| 5xx | Erreur du serveur (500, 502 mauvaise passerelle, 503 indisponible, 504 délai dépassé) |

- **502** : le proxy n'a pas eu de réponse valide du backend. **504** : le backend a répondu trop tard.
- **TLS** : le serveur présente un certificat signé par une autorité, le client vérifie la chaîne et le nom (SAN). TLS 1.3 de préférence.
- **mTLS** : le client présente aussi un certificat (service mesh, API internes).

## Pare-feu et NAT

- **Stateful** : la réponse d'une connexion autorisée passe automatiquement (security groups, nftables avec conntrack).
- **SNAT** : changer la source (sortie vers Internet via une NAT gateway). **DNAT** : changer la destination (redirection de port, Services Kubernetes).
- Bonne pratique : tout refuser par défaut, ouvrir le minimum, journaliser les refus.

```bash
nft list ruleset
iptables -L -n -v
conntrack -L | head
```

## Conteneurs et Kubernetes

- Docker : un **bridge** (`docker0`), une paire **veth** par conteneur, du NAT pour sortir, `-p 8080:80` = DNAT.
- Kubernetes : chaque pod a une IP routable dans le cluster, sans NAT entre pods (modèle CNI).
- **Service ClusterIP** : IP virtuelle, traduite par kube-proxy (iptables, IPVS) ou eBPF (Cilium).
- **NetworkPolicy** : appliquée par le CNI (Calico, Cilium), pas par Kubernetes lui-même.

## Le diagnostic, couche par couche

```bash
ip -br a ; ip r                  # ai-je une IP et une route ?
ping -c3 10.0.0.1                # la passerelle répond-elle ?
dig +short api.exemple.com       # le nom se résout-il ?
nc -zv api.exemple.com 443       # le port est-il ouvert ?
curl -vI https://api.exemple.com # TLS et HTTP répondent-ils ?
mtr api.exemple.com              # où se perd le trafic ?
ss -tlpn                         # qu'est-ce qui écoute ici ?
tcpdump -i any host 10.0.0.5 -nn # que passe-t-il vraiment ?
openssl s_client -connect host:443 -servername host   # détail du certificat
```

Toujours remonter du bas vers le haut : lien, IP, route, DNS, port, TLS, application.
