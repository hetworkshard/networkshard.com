import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.date(),
    tags: z.array(z.string()).optional(),
    readTime: z.string().optional(),
    draft: z.boolean().optional().default(false),
    pinned: z.boolean().optional().default(false),
  }),
});

export const collections = { blog };
