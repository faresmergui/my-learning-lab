---
title: 'Git avancé : réécrire, retrouver, déboguer'
chapter: 1
order: 1
duration: 8
level: intermédiaire
tags:
- git
cards:
- q: À quoi sert `git rebase -i HEAD~5` ?
  a: 'À **réécrire les 5 derniers commits** : les réordonner, fusionner (`squash`/`fixup`), renommer (`reword`) ou supprimer (`drop`), avant de les partager.'
- q: Pourquoi préférer `git push --force-with-lease` à `--force` ?
  a: '`--force-with-lease` refuse d''écraser la branche distante si quelqu''un a poussé **depuis ton dernier fetch**. `--force` écrase sans vérifier.'
- q: Tu as perdu des commits après un `reset --hard`. Comment les retrouver ?
  a: Avec `git reflog`, qui garde l'historique local des positions de `HEAD`. Puis `git reset --hard <sha>` ou `git branch sauvetage <sha>`.
- q: Que fait `git bisect` ?
  a: Une **recherche dichotomique** dans l'historique pour trouver le commit qui a introduit un bug. `git bisect run <script>` l'automatise.
- q: Différence entre merge et rebase ?
  a: '**Merge** garde l''historique tel quel et ajoute un commit de fusion. **Rebase** rejoue tes commits sur la nouvelle base : historique linéaire, mais les SHA changent.'
- q: Règle d'or du rebase ?
  a: Ne jamais rebaser des commits **déjà partagés** sur une branche que d'autres utilisent (comme `main`).
- q: À quoi sert `git commit --fixup <sha>` ?
  a: Il crée un commit marqué « fixup! » que `git rebase -i --autosquash` fusionnera automatiquement dans le commit visé.
quiz:
- q: Un bug est apparu entre la v1.4 (OK) et la v1.6 (KO), avec 200 commits entre les deux. Méthode la plus rapide ?
  options:
  - Relire les 200 diffs
  - git bisect start v1.6 v1.4, puis tester à chaque étape
  - git blame sur chaque fichier
  - Revenir à la v1.4
  answer: 1
  explain: Bisect trouve le commit fautif en environ 8 étapes (log2 de 200), et peut même tourner tout seul avec un script de test.
- q: Ta MR contient 12 commits « wip ». Le reviewer demande un historique propre. Que faire ?
  options:
  - git rebase -i main, puis squash/fixup, puis push --force-with-lease
  - Fermer la MR et en recréer une
  - git revert de chaque commit
  - git merge --no-ff
  answer: 0
  explain: Le rebase interactif nettoie l'historique de ta branche. Comme les SHA changent, il faut forcer le push, de préférence avec --force-with-lease.
---

Git est l'outil que tu utilises le plus, et l'un de ceux qu'on maîtrise le moins. Quelques commandes changent tout au quotidien.

## Nettoyer avant de partager

```bash
git rebase -i main            # réordonner, squash, reword
git commit --fixup abc123     # corriger un ancien commit
git rebase -i --autosquash main
git push --force-with-lease   # forcer, mais prudemment
```

## Retrouver ce qu'on croit perdu

```bash
git reflog                    # toutes les positions de HEAD
git branch sauvetage HEAD@{3} # recréer une branche à cet endroit
```

Le reflog est **local** et expire (90 jours par défaut). Un commit n'est presque jamais vraiment perdu.

## Trouver le commit fautif

```bash
git bisect start
git bisect bad                # la version actuelle est cassée
git bisect good v1.4          # celle-ci marchait
git bisect run ./test.sh      # Git teste tout seul
git bisect reset
```

## Merge ou rebase ?

| | Merge | Rebase |
| --- | --- | --- |
| Historique | fidèle, avec commits de fusion | linéaire |
| SHA | inchangés | réécrits |
| Sur une branche partagée | sans risque | à éviter |

<!-- schema:merge-rebase -->
<figure class="diagram"><svg viewBox="0 0 680 210" role="img" aria-label="Merge et rebase" style="--minw:560px"><defs><marker id="g17-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g17-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g17-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g17-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="170" y="22" class="dg-t" text-anchor="middle">merge</text><line x1="40" y1="70" x2="300" y2="70" class="dg-court"/><circle cx="50" cy="70" r="9" class="dg-dot  dg-pop" style="--d:0"/><text x="50" y="96" class="dg-s" text-anchor="middle">A</text><circle cx="100" cy="70" r="9" class="dg-dot  dg-pop" style="--d:1"/><text x="100" y="96" class="dg-s" text-anchor="middle">B</text><circle cx="150" cy="70" r="9" class="dg-dot  dg-pop" style="--d:2"/><text x="150" y="96" class="dg-s" text-anchor="middle">C</text><path d="M100 70 C 120 130, 140 130, 160 130" class="dg-l" marker-end="url(#g17-n)"/><circle cx="170" cy="130" r="9" class="dg-dot dg-c dg-pop" style="--d:1"/><text x="170" y="156" class="dg-s" text-anchor="middle">D</text><circle cx="220" cy="130" r="9" class="dg-dot dg-c dg-pop" style="--d:2"/><text x="220" y="156" class="dg-s" text-anchor="middle">E</text><path d="M220 130 C 240 130, 250 70, 262 70" class="dg-l c" marker-end="url(#g17-c)"/><circle cx="270" cy="70" r="11" class="dg-dot dg-a dg-pop" style="--d:3"/><text x="270" y="48" class="dg-at" text-anchor="middle">M</text><text x="170" y="186" class="dg-s" text-anchor="middle">historique fidèle, un commit de fusion</text><line x1="340" y1="30" x2="340" y2="220" class="dg-grid"/><text x="510" y="22" class="dg-t" text-anchor="middle">rebase</text><line x1="380" y1="70" x2="660" y2="70" class="dg-court"/><circle cx="390" cy="70" r="9" class="dg-dot  dg-pop" style="--d:0"/><text x="390" y="96" class="dg-s" text-anchor="middle">A</text><circle cx="440" cy="70" r="9" class="dg-dot  dg-pop" style="--d:1"/><text x="440" y="96" class="dg-s" text-anchor="middle">B</text><circle cx="490" cy="70" r="9" class="dg-dot  dg-pop" style="--d:2"/><text x="490" y="96" class="dg-s" text-anchor="middle">C</text><circle cx="550" cy="70" r="9" class="dg-dot dg-c dg-pop" style="--d:1"/><text x="550" y="96" class="dg-s" text-anchor="middle">D&#x27;</text><circle cx="600" cy="70" r="9" class="dg-dot dg-c dg-pop" style="--d:2"/><text x="600" y="96" class="dg-s" text-anchor="middle">E&#x27;</text><circle cx="480" cy="130" r="9" class="dg-dot  dg-pop" style="--d:0"/><circle cx="530" cy="130" r="9" class="dg-dot  dg-pop" style="--d:1"/><circle cx="480" cy="130" r="9" class="dg-dot" style="opacity:.35"/><circle cx="530" cy="130" r="9" class="dg-dot" style="opacity:.35"/><text x="505" y="160" class="dg-s" text-anchor="middle">D et E abandonnés</text><text x="510" y="186" class="dg-s" text-anchor="middle">historique linéaire, nouveaux SHA</text></svg><figcaption>Le rebase rejoue D et E sur C : ce sont de nouveaux commits, d&#x27;où le push forcé.</figcaption></figure>
<!-- /schema:merge-rebase -->

## Comprendre le modèle de Git

La plupart des commandes « avancées » deviennent simples une fois qu'on a ces trois idées en tête.

**Un commit est une photo complète**, identifiée par son **SHA** (une empreinte calculée à partir de son contenu, de son message, de son auteur **et de son parent**). Changer quoi que ce soit, même le message, produit un autre SHA : c'est donc un **nouveau** commit, pas une modification.

**Une branche n'est qu'une étiquette** qui pointe vers un commit. `main` n'est pas un dossier ni une copie : c'est un pointeur de 40 caractères dans `.git/refs/heads/main`. Créer une branche ne coûte rien. `HEAD` est le pointeur qui dit « où tu es ».

**Les commits forment une chaîne** : chacun connaît son parent. L'historique, c'est la chaîne qu'on obtient en remontant de parent en parent depuis une branche.

## Ce que fait vraiment un rebase

`git rebase main` sur ta branche `feature` :

1. met de côté tes commits qui ne sont pas dans `main` ;
2. place `feature` sur le dernier commit de `main` ;
3. **rejoue** tes changements un par un, ce qui crée de **nouveaux** commits (nouveaux SHA, puisque le parent a changé).

Les anciens commits existent toujours, simplement plus aucune branche ne pointe dessus. C'est pour ça que le **reflog** permet de revenir en arrière après un rebase raté : il garde la trace de toutes les positions où HEAD est passé.

C'est aussi pour ça qu'on ne rebase pas une branche **partagée** : tes collègues ont les anciens commits, toi les nouveaux. Leurs prochains `pull` mélangeront les deux versions, avec des doublons et des conflits.

## Pourquoi `--force-with-lease`

Après un rebase, ta branche locale et la branche distante ont divergé : `git push` refuse. `--force` écrase la branche distante, **y compris** les commits qu'un collègue y aurait poussés entre-temps. `--force-with-lease` vérifie d'abord que la branche distante est toujours là où tu l'as vue la dernière fois ; sinon, il refuse, et tu ne détruis le travail de personne.

## Comment bisect trouve le coupable

`git bisect` fait une **recherche dichotomique** : il te place au milieu entre le « bon » et le « mauvais » commit, tu dis si ça marche, il coupe l'intervalle en deux, et ainsi de suite. Sur 1 000 commits, il trouve le fautif en une dizaine d'étapes. Avec `bisect run`, un script qui renvoie 0 (bon) ou autre chose (mauvais) fait tout le travail.

> **À retenir.** Rebase sur ta branche, merge sur les branches partagées. Et `--force-with-lease`, jamais `--force`.
