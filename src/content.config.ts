// Content definitions for the site.
// Astro reads the Markdown files in src/content/ and validates their header
// (the "frontmatter") against the schemas below. A typo in a note fails the
// build with a clear message instead of silently breaking a page.
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// A module = one subject (Kubernetes, Linux, Japanese...).
// Fichier : src/content/modules/<slug>.md
const modules = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/modules' }),
  schema: z.object({
    title: z.string(),
    universe: z.enum(['tech', 'perso']),
    code: z.string(),               // short text shown in the icon
    color: z.string(),              // module color
    order: z.number(),
    description: z.string(),
    objective: z.string().optional(),
    chapters: z.array(z.string()),  // chapter titles, in order
    // Levels (optional): group consecutive chapters.
    // Example: JLPT N5 for the first 10 chapters, then N4 for the next 5.
    stages: z
      .array(z.object({
        label: z.string(),          // badge court : « N5 », « P12-P10 »
        title: z.string(),          // level name
        description: z.string().optional(),
        chapters: z.number().int().positive(), // number of chapters in this level
      }))
      .optional(),
  }),
});

// A note ("fiche") = one concept, attached to a module and a chapter.
// Fichier : src/content/fiches/<module>/<nom>.md
// The note's flashcards and quiz live in the same file.
const fiches = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/fiches' }),
  schema: z.object({
    title: z.string(),
    chapter: z.number(),            // chapter number (1 = first in the list)
    order: z.number().default(1),   // position of the note within the chapter
    duration: z.number().optional(),// minutes de lecture
    level: z.string().optional(),
    tags: z.array(z.string()).default([]),
    cards: z
      .array(z.object({
        id: z.string().optional(),  // set it to reword a question without losing its progress
        q: z.string(),
        a: z.string(),
      }))
      .default([]),
    quiz: z
      .array(z.object({
        q: z.string(),
        options: z.array(z.string()).min(2),
        answer: z.number(),         // index of the correct answer, starting at 0
        explain: z.string().optional(),
      }))
      .default([]),
  }),
});

// A summary ("synthèse") = a module's one-page cheat sheet.
// File: src/content/syntheses/<module>.md (same name as the module)
const syntheses = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/syntheses' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
  }),
});

// A certification = a target exam, linked to the notes that prepare for it.
// File: src/content/certifications/<slug>.md. The text below the header is the
// exam-day summary (pitfalls, commands to know, strategy).
const certifications = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/certifications' }),
  schema: z.object({
    title: z.string(),                // nom court : CKA, LFCS...
    name: z.string(),                 // nom complet de l'examen
    org: z.string(),                  // organisme
    order: z.number(),                // display order (priority)
    color: z.string(),
    description: z.string(),
    format: z.array(z.object({ label: z.string(), value: z.string() })), // duration, type, passing score...
    officialUrl: z.url(),
    checked: z.string(),              // date the information was last checked
    // Domains of the official curriculum, with their weight and the notes that cover them.
    // `missing`: what the site does not cover yet for that domain.
    domains: z.array(z.object({
      name: z.string(),
      weight: z.number().optional(),  // in %, when the exam body publishes it
      fiches: z.array(z.string()).default([]),  // identifiants : module/fichier
      missing: z.string().optional(),
    })),
  }),
});

export const collections = { modules, fiches, syntheses, certifications };
