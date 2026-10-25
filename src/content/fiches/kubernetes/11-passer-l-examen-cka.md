---
title: Passer l'examen CKA
chapter: 11
order: 1
duration: 6
level: tous niveaux
tags: [CKA]
cards:
  - id: cka-format
    q: Quel est le format de l'examen CKA ?
    a: "**2 heures** pour **15 à 20 tâches** pratiques en ligne de commande, surveillé à distance. Il faut **66 %** pour réussir."
  - id: cka-hotes
    q: À l'examen CKA, où se fait chaque tâche ?
    a: Sur un **hôte dédié**, joint avec la commande `ssh` donnée dans l'énoncé. On revient sur `base` avec `exit` avant la tâche suivante (pas de SSH imbriqué).
  - id: cka-outils
    q: Quels outils sont prêts sur les hôtes de l'examen, et lesquels manquent sur `base` ?
    a: Les hôtes ont `kubectl` avec l'alias `k` et l'autocomplétion, plus `yq`, `curl`, `wget` et `man`. La machine `base` n'a **aucun** de ces outils.
  - id: cka-simulateur
    q: Que contient le simulateur inclus avec la CKA ?
    a: "**2 sessions** de **36 h** chacune, à partir de l'activation. Les questions sont **les mêmes** dans les deux sessions : garder la seconde pour la fin de la préparation."
  - id: cka-copier-coller
    q: Comment copier et coller dans le terminal de l'examen ?
    a: "`Ctrl+Shift+C` et `Ctrl+Shift+V` (ou clic droit). Et `Ctrl+Alt+W` à la place de `Ctrl+W`, qui fermerait l'onglet du navigateur."
  - id: cka-lancement
    q: Combien de temps avant l'heure prévue peut-on lancer l'examen ?
    a: Le bouton « Take Exam » s'active **30 minutes** avant l'heure prévue. Ce temps sert au check-in avec le surveillant.
  - id: cka-dry-run
    q: Comment générer un manifeste YAML sans rien créer ?
    a: "`k run web --image=nginx --dry-run=client -o yaml > pod.yaml`, puis on édite le fichier. Avec `export do=\"--dry-run=client -o yaml\"`, ça devient `k run web --image=nginx $do`."
  - id: cka-question-inconnue
    q: Une tâche porte sur un sujet que tu ne maîtrises pas. Que faire ?
    a: La **marquer** et passer à la suivante. On y revient après un premier tour complet, en commençant par celles qui rapportent le plus pour le moins de temps.
  - id: cka-validite
    q: Combien de temps la CKA reste-t-elle valable ?
    a: "**2 ans** (3 ans pour celles obtenues avant le 1er avril 2024)."
quiz:
  - q: Tu as fini une tâche sur l'hôte `cka-node1`. Que fais-tu avant la suivante ?
    options:
      - J'enchaîne avec `ssh` vers le prochain hôte depuis `cka-node1`
      - Je tape `exit` pour revenir sur `base`, puis je lance le `ssh` de la tâche suivante
      - Je redémarre `base` pour repartir propre
    answer: 1
    explain: Le SSH imbriqué n'est pas supporté. Et redémarrer `base` ne remet pas l'environnement d'examen à zéro.
  - q: Ta seconde session de simulateur te donne 95 % alors que la première t'en donnait 60 %. Qu'en conclure ?
    options:
      - Je suis prêt, mon niveau a fortement progressé
      - Pas grand-chose, ce sont les mêmes questions que la première session
      - Le simulateur est plus facile que l'examen
    answer: 1
    explain: Les deux sessions ont exactement les mêmes questions. Pour mesurer ta progression, refais plutôt des labs que tu n'as jamais vus.
---

L'examen ne vérifie pas seulement ce que tu sais, mais ta vitesse dans un terminal distant. Une bonne partie des points se gagne avant le jour J.


> **Les termes et outils cités dans cette fiche.**
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…

## Le format

| | |
| --- | --- |
| Durée | 2 heures |
| Tâches | 15 à 20, toutes pratiques |
| Score pour réussir | 66 % |
| Version | Kubernetes v1.37 |
| Validité | 2 ans |
| Résultats | Par e-mail, 24 h après |

## L'environnement

Tu travailles sur un bureau Linux à distance. Chaque tâche indique un hôte et la commande `ssh` pour s'y connecter. Sur ces hôtes, `k`, l'autocomplétion, `yq` et `curl` sont prêts, et `sudo -i` donne les droits root.

```bash
ssh cka-node1        # la commande donnée dans l'énoncé
k get nodes          # l'alias est déjà là
exit                 # retour sur base avant la tâche suivante
```

> **Piège classique.** `Ctrl+W` efface un mot dans un terminal, mais ferme l'onglet du navigateur à l'examen. Utilise `Ctrl+Alt+W`.

## Gagner du temps

- Générer le YAML au lieu de l'écrire : `--dry-run=client -o yaml`.
- Retrouver un champ sans quitter le terminal : `k explain pod.spec.containers --recursive`.
- Lire une sortie longue avec `less` plutôt qu'à la souris, qui répond mal à distance.
- Marquer une tâche bloquante, finir le premier tour, puis revenir.

## Préparer le jour J

- Le simulateur inclus offre 2 sessions de 36 h avec les mêmes questions : fais la première tôt pour voir l'écart, la seconde à quelques jours de l'examen.
- Teste ta webcam, ton micro et le logiciel de surveillance avant le jour J.
- Sur un clavier non américain, repère les caractères spéciaux (`|`, `\`, guillemets) et le clavier virtuel du bureau distant.

Sources : [FAQ CKA/CKAD/CKS](https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks), [instructions CKA/CKAD](https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad), [simulateurs](https://training.linuxfoundation.org/blog/exam-simulators/), consultés le 22 octobre 2026.

> **À retenir.** La CKA se joue autant sur la vitesse que sur les connaissances : génère le YAML avec `--dry-run=client -o yaml`, cherche les champs avec `kubectl explain`, saute les tâches bloquantes et reviens-y. Fais une session de simulateur tôt et une juste avant l'examen.
