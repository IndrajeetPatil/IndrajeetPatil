import { defineCollection, z } from "astro:content";
import { file } from "astro/loaders";

const publications = defineCollection({
  loader: file("src/content/publications.yaml"),
  schema: z.object({
    id: z.string(),
    title: z.string(),
    authors: z.string(),
    journal: z.string(),
    year: z.number(),
    doi: z.string().optional(),
    pdf: z.string().optional(),
    supplementary_pdf: z.string().optional(),
    supplementary_url: z.string().optional(),
    data_url: z.string().optional(),
    neuroimaging_url: z.string().optional(),
    tags: z.array(z.string()),
    type: z.enum(["article", "thesis", "preprint"]).default("article"),
    thesis_type: z.string().optional(),
  }),
});

const presentations = defineCollection({
  loader: file("src/content/presentations.yaml"),
  schema: z.object({
    id: z.string(),
    title: z.string(),
    description: z.string(),
    url: z.string(),
    category: z.enum(["language-agnostic-se", "r-programming", "career-advice"]),
    image: z.string().optional(),
  }),
});

const software = defineCollection({
  loader: file("src/content/packages.yaml"),
  schema: z.object({
    id: z.string(),
    name: z.string(),
    description: z.string(),
    role: z.enum(["creator", "author"]),
    language: z.enum(["R", "Python"]).default("R"),
    category: z.enum([
      "data-visualization",
      "data-analysis",
      "statistical-reporting",
      "developer-tools",
      "utilities",
    ]),
    hex_sticker: z.string().optional(),
    cran_url: z.string().optional(),
    pypi_url: z.string().optional(),
    github_url: z.string(),
    docs_url: z.string().optional(),
  }),
});

export const collections = { publications, presentations, software };
