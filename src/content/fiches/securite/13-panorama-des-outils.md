---
title: Panorama des outils de sécurité
chapter: 13
order: 1
duration: 8
level: intermédiaire
tags:
- offensif
- défense
cards:
- q: À quoi sert nmap, et comment limiter ce qu'il révèle ?
  a: "nmap **cartographie** un réseau : quelles machines répondent, quels ports sont ouverts, quels services tournent. On s'en protège en n'exposant que le nécessaire (pare-feu en refus par défaut) et en surveillant les scans dans les logs."
- q: À quoi sert Burp Suite ?
  a: "C'est un **proxy d'interception** web : il se place entre le navigateur et le site pour lire et modifier les requêtes. Il sert à tester la logique d'une appli. La protection, c'est de **tout valider côté serveur**, jamais seulement dans le navigateur."
- q: Quelle famille d'outils représentent Hydra et hashcat ?
  a: "Les outils de **cassage de mots de passe** : Hydra essaie des mots de passe en ligne sur un service, hashcat retrouve des mots de passe à partir de leurs empreintes volées. Parade : MFA, limitation des tentatives, mots de passe longs et hachage lent (Argon2, bcrypt)."
- q: Qu'est-ce que Metasploit ?
  a: "Un **framework d'exploitation** qui regroupe des milliers d'exploits de failles **connues**. Il rappelle qu'une faille publiée devient vite facile à exploiter : la parade principale est d'**appliquer les correctifs** rapidement."
- q: Pourquoi un DevOps devrait-il utiliser lui-même des scanners comme Trivy ou OpenVAS ?
  a: Pour trouver les failles connues de ses images, dépendances et serveurs **avant** un attaquant, qui utilise des outils comparables.
- q: Que fait un IDS comme Suricata ou un outil comme Falco ?
  a: "Ils **détectent** : Suricata repère des attaques dans le trafic réseau, Falco des comportements suspects dans les conteneurs (shell ouvert dans un pod, lecture de fichiers sensibles)."
quiz:
- q: "Les logs montrent des milliers d'échecs de connexion SSH par minute depuis plusieurs IP. Quelle famille d'outil est probablement en cause, et quelle est la meilleure parade ?"
  options:
  - Un scanner de ports ; changer le port SSH
  - Un outil de force brute en ligne ; clés SSH uniquement, mot de passe désactivé, et limitation des tentatives (fail2ban)
  - Un proxy d'interception ; activer HTTPS
  - Un framework d'exploitation ; redémarrer le serveur
  answer: 1
  explain: "Des essais répétés de mots de passe, c'est de la force brute. Sans authentification par mot de passe, elle ne peut plus réussir. Changer le port réduit le bruit mais ne protège pas."
- q: Une base de données a fuité. Les mots de passe y sont hachés en MD5. Quel est le risque ?
  options:
  - Aucun, ils sont chiffrés
  - Élevé, un outil comme hashcat retrouve très vite les mots de passe courants à partir d'empreintes MD5
  - Faible, il faudrait des années
  - Seulement si l'attaquant a aussi la clé de chiffrement
  answer: 1
  explain: "MD5 est conçu pour être rapide, donc on peut tester des milliards de candidats par seconde. Il faut un algorithme lent et salé (Argon2, bcrypt, scrypt), et forcer le changement des mots de passe après une fuite."
- q: Une faille critique est publiée sur ton reverse proxy, avec un module d'exploitation déjà disponible. Quelle est la priorité ?
  options:
  - Attendre le prochain cycle de mise à jour mensuel
  - Appliquer le correctif ou une mesure de contournement au plus vite, puis vérifier les logs
  - Changer le port d'écoute
  - Ajouter une alerte et attendre
  answer: 1
  explain: "Quand un exploit public existe, l'attaque devient accessible à n'importe qui. Le délai entre publication et exploitation massive se compte parfois en heures."
---

Attaquants et défenseurs utilisent largement **les mêmes outils**. Les connaître ne sert pas à attaquer : ça sert à comprendre ce qu'un attaquant voit de ton infrastructure, à reconnaître ses traces dans tes logs, et à choisir les bonnes protections. Cette fiche les range par **catégorie**, avec pour chacune la défense qui va avec. Rappel des fiches précédentes : on ne les utilise que sur ses propres systèmes, un lab ou un périmètre autorisé par écrit.


> **Les termes et outils cités dans cette fiche.**
> - **inventaire** : la liste des machines qu'Ansible gère, rangées en groupes.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **chiffrement** : transformer une donnée pour qu'elle soit illisible sans la clé.
> - **TLS** : le protocole qui chiffre une connexion et prouve l'identité du serveur par un certificat.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).
> - **proxy** : un intermédiaire qui reçoit les requêtes et les transmet à leur place.

## La carte d'ensemble

| Catégorie | Exemples | Ce que fait l'outil | Comment s'en protéger |
| --- | --- | --- | --- |
| Reconnaissance | nmap, Shodan, outils d'OSINT | découvrir ce qui est exposé | exposer le minimum, inventaire à jour |
| Scan de vulnérabilités | OpenVAS, Nessus, Trivy, Nuclei | chercher des failles connues | scanner soi-même en continu, corriger |
| Tests web | Burp Suite, OWASP ZAP | intercepter et modifier les requêtes | valider côté serveur, tests de sécurité en CI |
| Mots de passe | Hydra, hashcat, John the Ripper | deviner ou retrouver des mots de passe | MFA, limitation, hachage lent, gestionnaire |
| Exploitation | Metasploit | exploiter des failles connues | correctifs rapides, moindre privilège |
| Analyse réseau | Wireshark, tcpdump | lire le trafic | chiffrer partout (TLS, mTLS) |
| Détection | Suricata, Falco, Wazuh | repérer les attaques | les déployer et lire leurs alertes |

## Reconnaissance : voir ce qui est exposé

**nmap** est le scanner réseau de référence : il dit quelles machines répondent, quels ports sont ouverts et quels logiciels (avec leur version) écoutent derrière. **Shodan** est un moteur de recherche qui scanne Internet en permanence et indexe tout ce qui est exposé : n'importe qui peut y chercher « tel logiciel, telle version ». L'**OSINT** (renseignement en sources ouvertes) complète avec ce qui est public : sous-domaines trouvés dans les journaux de certificats, dépôts Git publics, profils des employés.

**Côté défense** : c'est la première chose à faire sur ta propre infra, pour découvrir ce que tu exposes sans le savoir (une base de données ouverte, un tableau de bord d'admin). Pare-feu en refus par défaut, services internes sur des IP privées, et un inventaire de ce qui doit être public.

## Scanners de vulnérabilités : les failles connues

**OpenVAS** (libre) et **Nessus** (commercial) analysent des serveurs ; **Trivy** et **Grype** des images de conteneurs et des dépendances ; **Nuclei** teste des sites web avec des modèles de failles connues. Tous comparent ce qu'ils trouvent à des bases de **CVE**.

**Côté défense** : ce sont avant tout des outils de défenseur. Intègre un scan d'image en CI (fiche supply chain), planifie un scan régulier de tes serveurs, et traite les résultats par gravité. Attention aux faux positifs : une version détectée n'est pas toujours exploitable.

## Tests d'applications web

**Burp Suite** et **OWASP ZAP** (libre) se placent entre le navigateur et le site, comme un proxy. On y voit chaque requête et on peut la modifier avant qu'elle parte : changer un prix, un identifiant d'utilisateur, un rôle. Ils montrent qu'un contrôle fait **seulement dans le navigateur** (JavaScript, champ caché) ne protège rien.

**Côté défense** : toute vérification de droits et toute validation de données se fait **côté serveur**. ZAP peut tourner en CI contre un environnement de test pour attraper les erreurs les plus courantes (en-têtes de sécurité manquants, cookies mal configurés).

## Mots de passe : deviner ou retrouver

Deux situations différentes :

- **En ligne** : **Hydra** essaie des couples identifiant/mot de passe directement sur un service (SSH, formulaire web). C'est la **force brute** ou le **credential stuffing** (réutiliser des identifiants volés ailleurs).
- **Hors ligne** : **hashcat** et **John the Ripper** retrouvent des mots de passe à partir de leurs **empreintes** (hash), après le vol d'une base. Sur une carte graphique, ils testent des milliards de candidats par seconde pour les algorithmes rapides.

**Côté défense** :

- **MFA** (authentification à plusieurs facteurs) : un mot de passe deviné ne suffit plus ;
- **clés SSH** et désactivation de l'authentification SSH par mot de passe ;
- **limitation des tentatives** : **fail2ban** bloque une IP après plusieurs échecs, un WAF ou le reverse proxy limite le débit ;
- **hachage lent et salé** (Argon2, bcrypt, scrypt), jamais MD5 ou SHA-1 seuls ;
- un **gestionnaire de mots de passe** pour avoir des mots de passe longs et uniques.

## Frameworks d'exploitation

**Metasploit** regroupe des milliers de modules qui exploitent des failles **déjà publiées**, plus des outils pour la suite (garder un accès, rebondir). Son existence illustre un point clé : dès qu'une faille et son exploit sont publics, l'attaque est à la portée de n'importe qui.

**Côté défense** : la **gestion des correctifs**. Une faille critique exposée sur Internet se corrige en heures ou en jours, pas au prochain cycle mensuel. Le **moindre privilège** et la **segmentation** (NetworkPolicies, security groups) limitent ce que l'attaquant peut faire s'il réussit.

## Analyse réseau

**Wireshark** et **tcpdump** (vus dans les modules Linux et Réseaux) lisent le trafic. Sur un réseau partagé, tout ce qui passe en clair (HTTP, mots de passe FTP, Telnet) est lisible.

**Côté défense** : chiffrer **tous** les flux, y compris internes (TLS, mTLS entre services). C'est aussi ton premier outil de diagnostic.

## Détection : l'autre moitié

Aucune protection n'est parfaite, il faut donc **voir** les attaques :

- **Suricata** (ou Snort) : un **IDS** (système de détection d'intrusion) qui reconnaît des attaques dans le trafic réseau ;
- **Falco** : détecte des comportements anormaux dans les conteneurs et Kubernetes (un shell ouvert dans un pod de production, une lecture de `/etc/shadow`) ;
- **Wazuh** : un **SIEM** et outil de surveillance des machines, libre, qui centralise logs et alertes ;
- **fail2ban** : lit les logs et bloque automatiquement les IP qui multiplient les échecs.

Les traces typiques à reconnaître : des connexions sur des dizaines de ports en quelques secondes (scan), des milliers d'échecs d'authentification (force brute), des requêtes web avec des caractères étranges dans les paramètres (tests d'injection), un `User-Agent` qui annonce un outil de scan.

> **À retenir.** Chaque catégorie d'outil d'attaque a sa parade : exposer peu contre la reconnaissance, corriger vite contre les exploits connus, MFA et hachage lent contre le cassage de mots de passe, validation côté serveur contre les tests web, chiffrement contre l'écoute. Et comme rien n'est parfait, il faut aussi détecter.
