---
title: 'Méthodologie : le fil conducteur'
chapter: 10
order: 1
duration: 12
level: intermédiaire
tags:
- méthodologie
- CTF
- pentest
- cadre légal
- organisation
cards:
- q: Pourquoi suivre une méthode plutôt que de « bidouiller » ?
  a: Parce qu'un challenge ou une machine se résout rarement par chance. Une **méthode** garantit qu'on n'oublie aucune piste, qu'on ne tourne pas en rond, et qu'on sait toujours **quoi essayer ensuite**. C'est ce qui distingue un débutant qui bloque d'un joueur régulier.
- q: Sur quoi a-t-on le droit de s'entraîner ?
  a: 'Uniquement sur des cibles **faites pour ça** : plateformes de CTF (Root Me, Hack The Box, TryHackMe, picoCTF), labs qu''on héberge soi-même (DVWA, Juice Shop), ou un système dont on a l''**autorisation écrite**. Tester une machine tierce sans accord est un délit (articles 323-1 et suivants du Code pénal). Voir la fiche [Audit, pentest et hacking éthique](../08-audit-pentest-hacking-ethique/).'
- q: Quelle est la première chose à faire, avant même de toucher la cible ?
  a: '**Ouvrir un fichier de notes.** Tout y va : l''objectif, ce qu''on découvre, les commandes essayées, les pistes à creuser, les identifiants trouvés. Sans notes, on refait dix fois la même chose et on perd les détails qui débloquent tout.'
- q: Quelles sont les grandes phases d'un CTF ou d'un pentest ?
  a: 1) **Reconnaissance** (que vise-t-on ?). 2) **Énumération** (qu'est-ce qui tourne, qu'est-ce qui est exposé ?). 3) **Recherche de vecteurs** (quelle faiblesse exploiter ?). 4) **Exploitation** (obtenir un accès ou le flag). 5) **Post-exploitation / élévation de privilèges** (aller plus loin). 6) **Documentation**.
- q: Quelle est la phase la plus importante, et la plus négligée ?
  a: 'L''**énumération**. « Enumerate harder » est le proverbe des CTF : la plupart des blocages viennent d''un détail qu''on n''a pas cherché (un sous-répertoire, un port, un commentaire, une version). On exploite rarement ce qu''on n''a pas d''abord patiemment listé.'
- q: Qu'est-ce qu'un flag ?
  a: 'La **preuve** qu''on a réussi une étape : une chaîne de caractères à récupérer et à soumettre (souvent un format comme `FLAG{...}` ou un hash). Sur les machines, il y a typiquement un flag « utilisateur » puis un flag « root/administrateur », qui valident chaque niveau d''accès.'
- q: Que faire quand on est complètement bloqué ?
  a: 'Revenir à ses notes, **relister** ce qu''on a trouvé et ce qu''on n''a pas encore testé, changer d''angle, prendre une pause. Puis, dans l''ordre : relire un write-up d''une étape précédente, demander un **indice** (beaucoup de plateformes en proposent), et seulement en dernier recours lire la solution — puis **refaire sans elle**.'
quiz:
- q: Tu veux t'entraîner au pentest ce week-end. Quelle cible est légale ?
  options:
  - Le site de ton ancienne école, « pour voir »
  - Une machine Hack The Box ou une salle TryHackMe
  - Le wifi de ton voisin
  - Une entreprise au hasard qui a un formulaire de contact
  answer: 1
  explain: Seules les plateformes conçues pour l'entraînement (ou un système autorisé par écrit) sont légales. « Juste pour voir » sur un système tiers est déjà un accès frauduleux.
- q: Tu lances un scan, tu trouves un service, tu l'exploites… et tu bloques. Qu'as-tu probablement sauté ?
  options:
  - Rien, c'est juste difficile
  - 'Une énumération complète : d''autres ports, répertoires, versions ou fichiers que tu n''as pas listés'
  - Il fallait exploiter plus vite
  - La cible est cassée
  answer: 1
  explain: 'Le réflexe CTF : « enumerate harder ». On revient énumérer avant de forcer l''exploitation.'
- q: Tu as trouvé un identifiant dans une page. Où le notes-tu ?
  options:
  - Nulle part, tu t'en souviendras
  - Dans ton fichier de notes, avec l'endroit où tu l'as trouvé
  - Tu le tapes directement et tu l'oublies
  - Dans l'historique du terminal seulement
  answer: 1
  explain: Les identifiants et indices se réutilisent souvent plus tard (sur un autre service, pour l'élévation de privilèges). Les noter avec leur contexte fait gagner un temps énorme.
- q: Tu as fini par lire la solution d'un challenge. Quelle est la bonne suite ?
  options:
  - Passer au suivant, c'est réglé
  - Refaire le challenge toi-même, sans la solution, pour ancrer la méthode
  - Copier la solution dans tes notes et l'oublier
  - Considérer que tu as triché et abandonner
  answer: 1
  explain: On apprend en refaisant. Lire une solution n'ancre rien ; la rejouer de mémoire transforme l'astuce en réflexe.
---

Entrer dans une machine d'entraînement ou résoudre un challenge Root Me n'est pas affaire de chance ni de « coup de génie ». C'est une **démarche ordonnée** : on observe, on liste, on raisonne, on essaie, on note. Cette fiche donne le fil conducteur commun à tous les exercices ; les deux suivantes l'appliquent aux **machines** et aux **challenges par catégorie**.

> **Les termes cités dans cette fiche.**
> - **CTF** (*Capture The Flag*) : un jeu de sécurité où l'on récupère des « flags » en résolvant des épreuves, sur des cibles prévues pour ça.
> - **Flag** : la chaîne de caractères qui prouve qu'on a réussi une étape.
> - **Reconnaissance** : la collecte d'informations sur la cible, avant toute action.
> - **Énumération** : l'inventaire détaillé de tout ce que la cible expose (services, versions, fichiers, utilisateurs).
> - **Exploitation** : le fait de tirer parti d'une faiblesse pour obtenir un accès ou une information.
> - **Élévation de privilèges** (*privesc*) : passer d'un accès limité à un accès administrateur.
> - **Write-up** : le compte rendu détaillé de la résolution d'un challenge, publié après coup.

## La règle d'or : un cadre légal

Tout ce qui suit ne vaut que sur des cibles **faites pour être attaquées** :

| Terrain autorisé | Exemple |
| --- | --- |
| Plateformes de CTF | Root Me, Hack The Box, TryHackMe, picoCTF, OverTheWire |
| Labs hébergés par toi | DVWA, OWASP Juice Shop, VulnHub en machine virtuelle isolée |
| Système avec autorisation écrite | une mission de pentest, avec périmètre et dates |

Attaquer tout autre système, « juste pour voir », est un **délit**. La fiche [Audit, pentest et hacking éthique](../08-audit-pentest-hacking-ethique/) détaille le cadre ; la fiche [Bug bounty et CTF](../09-bug-bounty-et-ctf/) liste les plateformes.

## Avant de commencer : les notes

Le meilleur outil d'un joueur de CTF n'est pas un exploit, c'est son **fichier de notes**. Ouvre-le en premier (un simple fichier Markdown, ou un outil comme CherryTree, Obsidian, Notion). On y consigne :

- l'**objectif** (quel flag, quel accès) ;
- chaque **découverte**, avec sa source (« port 8080 : page de login admin ») ;
- les **commandes** qui ont marché (pour les rejouer) ;
- les **identifiants**, hashes, noms d'utilisateurs trouvés ;
- les **pistes à creuser** et celles déjà écartées.

Prendre des notes n'est pas une perte de temps : c'est ce qui évite de tourner en rond et ce qui, plus tard, permet d'écrire un write-up.

## Les six phases

Tout exercice suit, en gros, la même progression. Ce n'est pas une ligne droite : on **revient** souvent en arrière (une découverte en phase 5 relance l'énumération).

<!-- schema:phases -->
<figure class="diagram"><svg viewBox="0 0 680 230" role="img" aria-label="Les six phases, et la boucle du retour" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="8" y="50" width="98" height="56" rx="9"/></g><text x="57.0" y="75.0" class="dg-s" text-anchor="middle" style="--d:0">1 · Recon</text><text x="57.0" y="93.0" class="dg-s" text-anchor="middle" style="--d:0">cadrer</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="120" y="50" width="98" height="56" rx="9"/></g><text x="169.0" y="75.0" class="dg-s" text-anchor="middle" style="--d:1">2 · Énumérer</text><text x="169.0" y="93.0" class="dg-s" text-anchor="middle" style="--d:1">tout lister</text><path d="M106 78 L118 78" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="232" y="50" width="98" height="56" rx="9"/></g><text x="281.0" y="75.0" class="dg-s" text-anchor="middle" style="--d:2">3 · Vecteurs</text><text x="281.0" y="93.0" class="dg-s" text-anchor="middle" style="--d:2">quelle faille</text><path d="M218 78 L230 78" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:3"><rect x="344" y="50" width="98" height="56" rx="9"/></g><text x="393.0" y="75.0" class="dg-s" text-anchor="middle" style="--d:3">4 · Exploiter</text><text x="393.0" y="93.0" class="dg-s" text-anchor="middle" style="--d:3">l&#x27;accès</text><path d="M330 78 L342 78" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="456" y="50" width="98" height="56" rx="9"/></g><text x="505.0" y="75.0" class="dg-s" text-anchor="middle" style="--d:4">5 · Privesc</text><text x="505.0" y="93.0" class="dg-s" text-anchor="middle" style="--d:4">aller + loin</text><path d="M442 78 L454 78" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:5"><rect x="568" y="50" width="98" height="56" rx="9"/></g><text x="617.0" y="75.0" class="dg-s" text-anchor="middle" style="--d:5">6 · Doc</text><text x="617.0" y="93.0" class="dg-s" text-anchor="middle" style="--d:5">write-up</text><path d="M554 78 L566 78" class="dg-l c" marker-end="url(#g1-c)"/><path d="M505.0 108 L505.0 150 L169.0 150 L169.0 108" class="dg-l a dash" marker-end="url(#g1-a)"/><text x="340.0" y="170" class="dg-s" text-anchor="middle">une découverte tardive → on revient énumérer</text></svg><figcaption>On avance de la reconnaissance à la documentation, mais chaque nouvelle information renvoie à l&#x27;énumération : le trajet n&#x27;est jamais une ligne droite.</figcaption></figure>
<!-- /schema:phases -->

| Phase | Question à se poser | Esprit |
| --- | --- | --- |
| 1. **Reconnaissance** | Que suis-je en train d'attaquer ? | large, passif d'abord |
| 2. **Énumération** | Qu'est-ce qui est exposé, et dans quelle version ? | exhaustif, patient |
| 3. **Recherche de vecteurs** | Quelle faiblesse puis-je exploiter ? | créatif, documenté |
| 4. **Exploitation** | Comment obtenir un accès ou le flag ? | méthodique, un pas à la fois |
| 5. **Post-exploitation / privesc** | Où suis-je, et comment aller plus loin ? | ré-énumérer |
| 6. **Documentation** | Comment ai-je fait, et qu'ai-je appris ? | pour la prochaine fois |

## La boucle « énumérer → raisonner → essayer »

À l'intérieur de chaque phase, on tourne en boucle :

1. **énumérer** : lister ce qui est là, sans a priori ;
2. **raisonner** : « qu'est-ce que ça m'apprend ? qu'est-ce que ça permet ? » ;
3. **essayer** une hypothèse à la fois ;
4. **noter** le résultat, succès ou échec.

Le piège du débutant est de sauter la phase 2 pour « attaquer » tout de suite. Le proverbe des CTF est clair : **« enumerate harder »**. Neuf blocages sur dix se règlent en revenant chercher un détail oublié : un port de plus, un sous-répertoire, un commentaire dans le code source d'une page, un numéro de version.

## Quand on bloque

C'est normal, et ça fait partie du jeu. Dans l'ordre :

1. **relire ses notes** : qu'est-ce que je n'ai pas encore testé ?
2. **changer d'angle** : une autre catégorie de faiblesse, un autre service ;
3. **ré-énumérer** plus finement (options plus agressives, listes de mots plus grandes) ;
4. faire une **pause** : beaucoup de solutions arrivent en revenant l'esprit clair ;
5. demander un **indice** (la plupart des plateformes en vendent ou en offrent) ;
6. en dernier recours, lire un **write-up**, puis **refaire sans lui**.

Lire la solution n'est pas tricher si on la rejoue ensuite de mémoire. Ce qui fait progresser, ce n'est pas d'avoir vu la réponse, c'est de pouvoir la **reproduire seul**.

## Se construire une base d'outils et de réflexes

Au fil des exercices, on se constitue :

- un **fichier de notes maître** : les commandes types, les listes de contrôle par catégorie ;
- des **antisèches** : par exemple le site GTFOBins (binaires Linux détournables), HackTricks (méthodologie détaillée), les *cheat sheets* de PayloadsAllTheThings ;
- des **réflexes** : toujours regarder le code source d'une page, toujours tester les identifiants trouvés ailleurs, toujours relire la sortie complète d'un scan.

La fiche [Panorama des outils](../13-panorama-des-outils/) classe les outils par usage ; les deux fiches suivantes montrent **quand** les sortir.

> **À retenir.** Entraîne-toi uniquement sur des cibles prévues pour (Root Me, HTB, TryHackMe, labs locaux) ou autorisées par écrit. Ouvre un fichier de notes **avant** de commencer. Suis les phases : reconnaissance, énumération, recherche de vecteurs, exploitation, élévation de privilèges, documentation — en revenant en arrière dès qu'une découverte le justifie. Dans chaque phase, boucle « énumérer → raisonner → essayer → noter ». Quand tu bloques : ré-énumère, change d'angle, prends une pause, puis un indice, puis un write-up que tu **referas seul**.
