---
title: Dispositions, groupes, scratchpad et plusieurs écrans
chapter: 4
order: 1
duration: 13
level: Débutant
tags:
- dwindle
- scrolling
- groupes
- scratchpad
- multi-écrans
cards:
- q: Quelles sont les trois dispositions d'Omarchy ?
  a: '**Dwindle** (par défaut) : toutes les fenêtres visibles, chaque nouvelle coupe la place de l''active en deux. **Scrolling** : les fenêtres s''alignent côte à côte et débordent hors de l''écran, on défile. **Floating** : fenêtres libres, comme sous Windows, avec un dock. **Super+L** passe de l''une à l''autre.'
- q: La disposition est-elle globale ?
  a: 'Non : elle se règle **par espace de travail** et elle est conservée au redémarrage. Tu peux avoir l''espace 1 en scrolling et le 2 en dwindle. La disposition par défaut se change dans `looknfeel.lua` (`layout = "scrolling"` sous `general`).'
- q: À quoi servent les groupes ?
  a: À **empiler** plusieurs fenêtres dans une seule case, comme des onglets. **Super+G** crée un groupe (les fenêtres ouvertes ensuite le rejoignent), **Super+Ctrl+gauche/droite** passe d'une fenêtre à l'autre, **Super+Alt+G** en sort une, Super+G à nouveau dissout le groupe.
- q: Qu'est-ce que le scratchpad ?
  a: 'Un **espace caché** qui s''affiche par-dessus l''espace courant. **Super+Alt+S** y envoie une fenêtre, **Super+S** l''affiche ou le cache. Idéal pour une appli qu''on consulte souvent sans lui donner un espace : musique, notes, messagerie.'
- q: Qu'est-ce que la console « quake » ?
  a: Un terminal à mi-hauteur qui descend du haut de l'écran avec **Super+`** (accent grave, touche sous Échap) et remonte de la même façon. **Super+Shift+`** y place une autre fenêtre. Pratique pour une commande rapide sans casser sa mise en page.
- q: Comment déplacer une fenêtre ou un espace vers l'autre écran ?
  a: '**Super+Shift+Ctrl+flèche** envoie la fenêtre active sur l''écran dans cette direction. **Super+Shift+Alt+flèche** déplace **tout l''espace de travail**. **Ctrl+Alt+Tab** passe le focus à l''écran suivant.'
- q: Comment redimensionner une fenêtre en mosaïque ?
  a: 'À la souris : **Super + clic droit** et glisser. Au clavier, les raccourcis de redimensionnement figurent dans Super+K ; **Super+Alt+moins/égal** donne des pas plus fins. Super+J bascule une paire de fenêtres entre empilées et côte à côte.'
quiz:
- q: Tu codes avec un éditeur, un terminal, un navigateur de doc et des logs. En dwindle, tout devient minuscule. Quelle disposition essayer ?
  options:
  - Floating
  - 'Scrolling : chaque fenêtre garde une largeur confortable et tu défiles'
  - Fermer des fenêtres
  - Passer en plein écran en permanence
  answer: 1
  explain: Scrolling aligne les fenêtres en ruban sans les écraser ; tu fais défiler la vue. Dwindle convient mieux à deux ou trois fenêtres.
- q: Tu veux ton lecteur de musique accessible d'un geste, sans lui réserver un espace. Que fais-tu ?
  options:
  - Tu l'ouvres en plein écran
  - Tu l'envoies au scratchpad (Super+Alt+S) et tu l'appelles avec Super+S
  - Tu le mets sur l'espace 10
  - Tu le gardes en flottant partout
  answer: 1
  explain: Le scratchpad apparaît par-dessus n'importe quel espace et disparaît aussi vite.
- q: Tu as quatre terminaux pour le même projet et tu veux qu'ils occupent une seule case. Outil adapté ?
  options:
  - Un groupe (Super+G)
  - Le scratchpad
  - Quatre espaces
  - La console quake
  answer: 0
  explain: Un groupe empile les fenêtres comme des onglets dans une seule case. (Pour des terminaux, tmux est une autre option, fiche 5.)
- q: Tu branches un second écran et veux y déplacer tout ton espace « navigateur » d'un coup. Raccourci ?
  options:
  - Super+Shift+Ctrl+flèche
  - Super+Shift+Alt+flèche
  - Ctrl+Alt+Tab
  - Super+Tab
  answer: 1
  explain: Super+Shift+Alt+flèche déplace l'espace entier ; Super+Shift+Ctrl+flèche ne déplace que la fenêtre active.
---

Une fois les raccourcis de base acquis, Hyprland offre plusieurs façons de ranger les fenêtres. Bien choisir sa disposition et connaître les groupes, le scratchpad et la console quake change vraiment le confort, surtout sur un grand écran de PC fixe. Tout ce qui suit vient du manuel Omarchy 4.

> **Les outils cités dans cette fiche.**
> - **disposition** (layout) : la règle qui décide comment Hyprland répartit les fenêtres d'un espace.
> - **dwindle** : disposition par découpes successives (chaque fenêtre coupe la place de la précédente en deux).
> - **scrolling** : disposition en ruban horizontal qui déborde de l'écran, qu'on fait défiler.
> - **floating** : fenêtres libres, superposables, comme sous Windows.
> - **groupe** : plusieurs fenêtres empilées dans une seule case, comme des onglets.
> - **scratchpad** : un espace caché qui s'affiche par-dessus l'espace courant.
> - **looknfeel.lua** : le fichier de réglages visuels de Hyprland dans ton dossier personnel (fiche 8).

## Comprendre : trois façons de ranger

<!-- schema:dispositions -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Dwindle, scrolling, floating" style="--minw:560px"><defs><marker id="g3-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g3-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g3-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g3-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="204" height="170" rx="12" class="dg-zone dg-zc"/><text x="26" y="32" class="dg-zl" text-anchor="start">dwindle</text><text x="116" y="206" class="dg-s" text-anchor="middle">tout reste visible</text><rect x="238" y="14" width="204" height="170" rx="12" class="dg-zone "/><text x="250" y="32" class="dg-zl" text-anchor="start">scrolling</text><text x="340" y="206" class="dg-s" text-anchor="middle">un ruban qui déborde</text><rect x="462" y="14" width="204" height="170" rx="12" class="dg-zone "/><text x="474" y="32" class="dg-zl" text-anchor="start">floating</text><text x="564" y="206" class="dg-s" text-anchor="middle">fenêtres libres</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="24" y="40" width="90" height="134" rx="9"/></g><text x="69.0" y="112.0" class="dg-t" text-anchor="middle" style="--d:0">1</text><g class="dg-box dg-pop" style="--d:1"><rect x="120" y="40" width="88" height="64" rx="9"/></g><text x="164.0" y="77.0" class="dg-t" text-anchor="middle" style="--d:1">2</text><g class="dg-box dg-pop" style="--d:2"><rect x="120" y="110" width="42" height="64" rx="9"/></g><text x="141.0" y="147.0" class="dg-t" text-anchor="middle" style="--d:2">3</text><g class="dg-box dg-pop" style="--d:3"><rect x="168" y="110" width="40" height="64" rx="9"/></g><text x="188.0" y="147.0" class="dg-t" text-anchor="middle" style="--d:3">4</text><g class="dg-box dg-pop" style="--d:0"><rect x="248" y="40" width="58" height="134" rx="9"/></g><text x="277.0" y="112.0" class="dg-t" text-anchor="middle" style="--d:0">1</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="312" y="40" width="58" height="134" rx="9"/></g><text x="341.0" y="112.0" class="dg-t" text-anchor="middle" style="--d:1">2</text><g class="dg-box dg-pop" style="--d:2"><rect x="376" y="40" width="58" height="134" rx="9"/></g><text x="405.0" y="112.0" class="dg-t" text-anchor="middle" style="--d:2">3</text><text x="434" y="112" class="dg-ct" text-anchor="middle">→</text><g class="dg-box dg-pop" style="--d:0"><rect x="472" y="46" width="110" height="76" rx="9"/></g><text x="527.0" y="89.0" class="dg-t" text-anchor="middle" style="--d:0">1</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="532" y="84" width="110" height="76" rx="9"/></g><text x="587.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:1">2</text><g class="dg-box dg-pop" style="--d:2"><rect x="492" y="128" width="70" height="42" rx="9"/></g><text x="527.0" y="154.0" class="dg-t" text-anchor="middle" style="--d:2">3</text><text x="340" y="238" class="dg-s" text-anchor="middle">Super+L change la disposition de l&#x27;espace courant (mémorisée par espace)</text></svg><figcaption>Chaque espace de travail garde sa propre disposition, même après un redémarrage.</figcaption></figure>
<!-- /schema:dispositions -->

| Disposition | Fonctionnement | Bien pour |
| --- | --- | --- |
| **Dwindle** (défaut) | chaque nouvelle fenêtre prend la moitié de l'active ; tout reste visible | 2 à 4 fenêtres, un écran 1440p ou 4K |
| **Scrolling** | les fenêtres s'alignent côte à côte et débordent ; on fait défiler | beaucoup de fenêtres, écran ultra-large |
| **Floating** | fenêtres libres, superposables, avec un dock | applis à fenêtres multiples, jeux, retouche d'image |

**Super+L** fait tourner les dispositions (scrolling, floating, dwindle) et **Super+Alt+L** dans l'autre sens. Le choix est **mémorisé par espace**, même après redémarrage. Si tu préfères scrolling partout, mets-le par défaut dans `~/.config/hypr/looknfeel.lua` :

```lua
hl.config({
  general = {
    layout = "scrolling",
  },
})
```

Pour une fenêtre isolée qui doit flotter (une calculatrice, une boîte de dialogue), pas besoin de changer tout l'espace : **Super+T** la sort de la mosaïque, Super+T la remet.

## Les gestes de mise en page

| Action | Raccourci |
| --- | --- |
| Empilées ou côte à côte (paire de fenêtres) | **Super+J** |
| Plein écran | **Super+F** |
| Pleine largeur | **Super+Alt+F** |
| Minimiser | **Super+M** |
| Sortir une fenêtre en « pop-out » flottant | **Super+O** |
| Redimensionner à la souris | **Super + clic droit** |
| Pas de redimensionnement plus fins | **Super+Alt+moins / égal** |
| Mémoriser la largeur d'une fenêtre | **Super+Alt+Origine** |

## Les groupes : des onglets de fenêtres

Un **groupe** empile plusieurs fenêtres dans une seule case, avec une barre d'onglets. Utile quand tu as plusieurs fenêtres du même type (plusieurs terminaux, plusieurs documents) et pas la place de toutes les afficher.

| Action | Raccourci |
| --- | --- |
| Démarrer un groupe (les fenêtres ouvertes ensuite le rejoignent) | **Super+G** |
| Fenêtre suivante / précédente du groupe | **Super+Ctrl+gauche / droite** |
| Aller à la 1ʳᵉ, 2ᵉ, 3ᵉ… fenêtre du groupe | **Super+Alt+1/2/3/4** |
| Faire entrer une fenêtre voisine dans le groupe | **Super+Alt+flèche** |
| Sortir la fenêtre active du groupe | **Super+Alt+G** |
| Dissoudre le groupe | **Super+G** à nouveau |

## Le scratchpad et la console quake

Deux espaces « cachés » pour ce qu'on consulte souvent :

- **Le scratchpad** : un espace plein écran en surimpression. **Super+Alt+S** y envoie la fenêtre active, **Super+S** l'affiche ou le cache. Parfait pour la musique, une messagerie, un gestionnaire de mots de passe.
- **La console quake** : un terminal à mi-hauteur qui descend du haut de l'écran avec **Super+`** (la touche sous Échap ; sur un clavier AZERTY, celle du « ² »). **Super+Shift+`** y place une autre fenêtre. Le manuel la présente aussi comme un bon endroit pour un agent IA (fiche 16).

Le nom vient du jeu *Quake*, dont la console descendait du haut de l'écran avec la même touche.

## Plusieurs écrans

Chaque écran a **ses propres espaces 1 à 10**. Les raccourcis Super+chiffre agissent sur l'écran où se trouve le focus.

| Action | Raccourci |
| --- | --- |
| Focus sur l'écran suivant | **Ctrl+Alt+Tab** |
| Envoyer la fenêtre sur l'écran dans une direction | **Super+Shift+Ctrl+flèche** |
| Envoyer tout l'espace sur l'écran dans une direction | **Super+Shift+Alt+flèche** |

La position et l'échelle des écrans se règlent dans `monitors.lua` (fiche 9). Un écran ultra-large se prête très bien à scrolling ; un écran 4K en 27 pouces à dwindle avec mise à l'échelle.

## Organiser un poste de travail type

Un exemple sur un PC fixe à deux écrans :

| Écran | Espace | Disposition | Contenu |
| --- | --- | --- | --- |
| principal | 1 | dwindle | navigateur + doc |
| principal | 2 | scrolling | éditeur, terminaux, logs |
| principal | 3 | floating | applis qui gèrent mal la mosaïque |
| secondaire | 1 | dwindle | messagerie, musique |
| partout | scratchpad | — | notes, gestionnaire de mots de passe |
| partout | console quake | — | commandes rapides |

La règle générale : **une activité par espace**, une disposition adaptée à cette activité, et les outils de consultation rapide en surimpression plutôt que dans la mosaïque.

> **À retenir.** Dwindle pour peu de fenêtres, scrolling pour beaucoup, floating pour les applis récalcitrantes, le tout réglé par espace avec Super+L. Les groupes (Super+G) empilent des fenêtres comme des onglets, le scratchpad (Super+S) et la console quake (Super+`) gardent sous la main ce qu'on consulte souvent. Avec deux écrans, Super+Shift+Ctrl+flèche déplace une fenêtre et Super+Shift+Alt+flèche un espace entier.
