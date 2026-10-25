---
title: Synthèse sécurité
description: "Principes, secrets, durcissement Linux, conteneurs, supply chain, Kubernetes, TLS, tests d'intrusion et certifications : les règles et les outils."
---

## Les principes

| Principe | En pratique |
| --- | --- |
| Confidentialité, intégrité, disponibilité | Les trois propriétés à protéger |
| Moindre privilège | Chaque identité n'a que les droits nécessaires, pour le temps nécessaire |
| Défense en profondeur | Plusieurs couches : une seule qui cède ne suffit pas à tout ouvrir |
| Surface d'attaque minimale | Moins de ports, de paquets, de droits, de secrets |
| Sécurité par défaut | Fermé par défaut, ouvert explicitement |
| Traçabilité | Journaliser qui a fait quoi, et le garder hors de portée de l'attaquant |

## Les secrets

| Niveau | Approche |
| --- | --- |
| ✗ | Secret dans le code ou un `.env` commité |
| ~ | Variable de CI masquée, Secret Kubernetes en base64 |
| ✓ | Gestionnaire de secrets (Vault, Secrets Manager) injecté à l'exécution |
| ✓✓ | Identités fédérées (OIDC, IRSA, Workload Identity) et secrets dynamiques |

**En cas de fuite** : 1. révoquer ou faire tourner, 2. vérifier les journaux d'accès, 3. nettoyer la source, 4. ajouter un garde-fou. Un secret supprimé d'un commit reste dans l'historique.

```bash
gitleaks git --pre-commit --staged
trufflehog git file://. --only-verified
vault kv get -field=password secret/shop/prod/db
```

## HashiCorp Vault

| Notion | En bref |
| --- | --- |
| Scellé / descellé | au démarrage Vault ne peut rien lire ; parts de clé (Shamir) ou auto-unseal par KMS |
| Méthode d'authentification | OIDC/LDAP pour un humain ; Kubernetes, AppRole, JWT de CI pour une machine |
| Policy | chemins et actions autorisés (`read`, `create`…), le reste est refusé |
| Secrets engine | KV v2 (statique, versionné), database (dynamique), PKI, transit |
| Lease | durée de vie d'un secret dynamique, supprimé à l'expiration |

Panne après redémarrage : `vault status`, il est sans doute scellé. OpenBao est le fork libre de Vault.

## Durcir un serveur Linux

- SSH : clés uniquement (`PasswordAuthentication no`), pas de connexion root (`PermitRootLogin no`), accès restreint (bastion, VPN).
- Mises à jour de sécurité automatiques (`unattended-upgrades`, `dnf-automatic`).
- Pare-feu : tout refuser par défaut en entrée.
- Services inutiles désactivés : `systemctl list-unit-files --state=enabled`.
- `sudo` nominatif et journalisé, pas de compte partagé.
- Durcissement systemd : `NoNewPrivileges`, `ProtectSystem=strict`, `PrivateTmp`.
- Journaux envoyés vers un serveur central.

## Les conteneurs

- Images minimales (distroless, alpine, `scratch`), multi-stage build.
- Ne pas tourner en **root** : `USER 10001` dans le Dockerfile.
- Système de fichiers en lecture seule, capabilities retirées (`--cap-drop=ALL`).
- Jamais de secret dans une couche d'image : `COPY` puis `rm` ne l'efface pas.
- Scanner les images en CI (`trivy image`, `grype`) et bloquer les vulnérabilités critiques corrigeables.
- Tag immuable ou digest (`@sha256:…`), jamais `latest` en prod.

## La supply chain

| Risque | Parade |
| --- | --- |
| Dépendance compromise ou typosquattée | Lockfiles, registre miroir, revue des nouvelles dépendances |
| Image falsifiée | Signature (`cosign sign`) et vérification à l'admission |
| Pipeline compromis | Runners isolés, jetons à courte durée (OIDC), protection des branches |
| Composants inconnus | SBOM (`syft`), scan continu |
| Action CI tierce modifiée | Épingler par SHA, pas par tag |

Le cadre **SLSA** décrit des niveaux de confiance pour la provenance des artefacts.

## Kubernetes

- RBAC au plus juste, pas de `cluster-admin` pour les applications, `automountServiceAccountToken: false` si inutile.
- **Pod Security Standards** `restricted` sur les namespaces applicatifs.
- `securityContext` : `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`, `seccompProfile: RuntimeDefault`.
- NetworkPolicy **deny all** puis ouvertures explicites.
- Chiffrement d'etcd, accès à l'API restreint, journaux d'audit activés.
- Admission : Kyverno ou OPA Gatekeeper pour imposer les règles (images signées, pas de `latest`, limites obligatoires).
- Runtime : Falco pour détecter les comportements anormaux.

## TLS et PKI

- Le certificat lie une **clé publique** à un **nom**, signé par une autorité de confiance.
- Chaîne : certificat serveur → intermédiaire(s) → racine (dans le magasin de confiance).
- Le nom vérifié est dans le **SAN**, pas dans le CN.
- Renouvellement automatique (ACME, cert-manager) : un certificat expiré est une panne, pas un problème de sécurité.
- Clés privées jamais commitées, jamais partagées entre environnements.

```bash
openssl s_client -connect host:443 -servername host </dev/null | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
openssl req -new -newkey rsa:2048 -nodes -keyout key.pem -out req.csr
```

## Les réflexes en cas d'incident

1. **Contenir** : isoler la machine ou révoquer l'accès, sans tout effacer.
2. **Préserver** les preuves : journaux, image disque, mémoire si possible.
3. **Éradiquer** : corriger la faille, faire tourner tous les secrets exposés.
4. **Restaurer** depuis un état sain connu.
5. **Analyser** sans reproche et ajouter les garde-fous manquants.

## Tester sa sécurité, légalement

| Démarche | Question | Fréquence |
| --- | --- | --- |
| Audit de configuration | Est-ce réglé selon les bonnes pratiques ? | régulière |
| Scan de vulnérabilités | Y a-t-il des failles connues ? | continue (CI, hebdo) |
| Pentest | Que peut réellement faire un attaquant ? | annuelle, avant une mise en prod |
| Red team | Détecterait-on une vraie attaque ? | rare |

- **Seule une autorisation écrite** avec un périmètre précis rend un test légal (Code pénal, art. 323-1 : jusqu'à 3 ans et 100 000 €).
- Faille trouvée hors périmètre : on s'arrête et on signale (à l'organisation, ou à l'ANSSI).
- Bug bounty : uniquement le scope listé, preuve avec le minimum de données, rien de conservé.
- S'entraîner : TryHackMe, Root-Me, Hack The Box, PortSwigger Academy, OverTheWire ; en local, Juice Shop, DVWA, Kubernetes Goat.
- Sur ses services : publier un `/.well-known/security.txt` et une politique de divulgation.

## Les outils d'attaque et leur parade

| Catégorie | Exemples | Parade |
| --- | --- | --- |
| Reconnaissance | nmap, Shodan | exposer le minimum, inventaire à jour |
| Scan de vulnérabilités | OpenVAS, Trivy, Nuclei | scanner soi-même, corriger par gravité |
| Tests web | Burp Suite, OWASP ZAP | validation et droits vérifiés côté serveur |
| Mots de passe | Hydra, hashcat | MFA, clés SSH, fail2ban, Argon2 ou bcrypt |
| Exploitation | Metasploit | correctifs rapides, moindre privilège, segmentation |
| Écoute réseau | Wireshark, tcpdump | chiffrer tous les flux |
| Détection | Suricata, Falco, Wazuh | les déployer et lire les alertes |

## Les certifications utiles

1. **CKS** : la suite de la CKA, la plus rentable pour un DevOps Kubernetes.
2. **Sécurité de ton cloud** : AWS Security Specialty, AZ-500, GCP Security Engineer.
3. **Security+** ou **ISC2 CC** : le socle généraliste. **SecNumacadémie** (ANSSI) : gratuit pour commencer.
4. **eJPT** pour découvrir l'attaque ; OSCP et CISSP seulement pour changer d'orientation ou de niveau.
