// Définition du contenu du site.
// Astro lit les fichiers Markdown de src/content/ et vérifie leur en-tête
// (le "frontmatter") avec les schémas ci-dessous. Une faute de frappe dans
// une fiche fait échouer le build avec un message clair, au lieu de casser
// une page en silence.
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Un module = un sujet (Kubernetes, Linux, Japonais...).
// Fichier : src/content/modules/<slug>.md
const modules = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/modules' }),
  schema: z.object({
    title: z.string(),
    universe: z.enum(['tech', 'perso']),
    code: z.string(),               // texte court affiché dans l'icône
    color: z.string(),              // couleur du module
    order: z.number(),
    description: z.string(),
    objective: z.string().optional(),
    chapters: z.array(z.string()),  // titres des chapitres, dans l'ordre
    // Niveaux (facultatif) : regroupent les chapitres qui se suivent.
    // Exemple : JLPT N5 pour les 10 premiers chapitres, puis N4 pour les 5 suivants.
    stages: z
      .array(z.object({
        label: z.string(),          // badge court : « N5 », « P12-P10 »
        title: z.string(),          // nom du niveau
        description: z.string().optional(),
        chapters: z.number().int().positive(), // nombre de chapitres dans ce niveau
      }))
      .optional(),
  }),
});

// Une fiche = une notion, rattachée à un module et à un chapitre.
// Fichier : src/content/fiches/<module>/<nom>.md
// Les flashcards et le quiz de la fiche vivent dans le même fichier.
const fiches = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/fiches' }),
  schema: z.object({
    title: z.string(),
    chapter: z.number(),            // numéro du chapitre (1 = premier de la liste)
    order: z.number().default(1),   // position de la fiche dans le chapitre
    duration: z.number().optional(),// minutes de lecture
    level: z.string().optional(),
    tags: z.array(z.string()).default([]),
    cards: z
      .array(z.object({
        id: z.string().optional(),  // à fixer si tu veux reformuler une question sans perdre sa progression
        q: z.string(),
        a: z.string(),
      }))
      .default([]),
    quiz: z
      .array(z.object({
        q: z.string(),
        options: z.array(z.string()).min(2),
        answer: z.number(),         // index de la bonne réponse, à partir de 0
        explain: z.string().optional(),
      }))
      .default([]),
  }),
});

// Une synthèse = la page récapitulative d'un module (aide-mémoire).
// Fichier : src/content/syntheses/<module>.md (même nom que le module)
const syntheses = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/syntheses' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
  }),
});

// Une certification = un examen visé, relié aux fiches qui le préparent.
// Fichier : src/content/certifications/<slug>.md. Le texte sous l'en-tête est
// la synthèse « jour J » (pièges, commandes à connaître, stratégie).
const certifications = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/certifications' }),
  schema: z.object({
    title: z.string(),                // nom court : CKA, LFCS...
    name: z.string(),                 // nom complet de l'examen
    org: z.string(),                  // organisme
    order: z.number(),                // ordre d'affichage (ta priorité)
    color: z.string(),
    description: z.string(),
    format: z.array(z.object({ label: z.string(), value: z.string() })), // durée, type, seuil...
    officialUrl: z.url(),
    checked: z.string(),              // date à laquelle les infos ont été vérifiées
    // Les domaines du programme officiel, avec leur poids et les fiches qui les couvrent.
    // `missing` : ce que le site ne couvre pas encore pour ce domaine.
    domains: z.array(z.object({
      name: z.string(),
      weight: z.number().optional(),  // en %, quand l'organisme le publie
      fiches: z.array(z.string()).default([]),  // identifiants : module/fichier
      missing: z.string().optional(),
    })),
  }),
});

export const collections = { modules, fiches, syntheses, certifications };
