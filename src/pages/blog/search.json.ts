import { getCollection } from 'astro:content';

export async function GET() {
  const posts = (await getCollection('blog'))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());

  const payload = posts.map((post) => ({
    slug: post.slug,
    title: post.data.title,
    description: post.data.description,
    date: post.data.date.toISOString(),
    readTime: post.data.readTime ?? null,
  }));

  return new Response(JSON.stringify(payload), {
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=60',
    },
  });
}

