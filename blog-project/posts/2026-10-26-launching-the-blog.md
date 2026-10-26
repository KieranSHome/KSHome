---
title: "Launching Kiwiii.Stream/blog: Building a Blog with GitHub and Cloudflare"
date: "2026-10-26"
description: "How I set up a small technical blog using Markdown, GitHub, a Python build script and Cloudflare, with a custom subdomain."
category: "Website & Projects"
published: true
---

## A new home for my technical notes

I've started **[Kiwiii.Stream/blog](https://kiwiii.stream/blog)** as a place to document the technical projects I'm working on: home lab infrastructure, self-hosting, automation, smart-home experiments and the lessons that come from troubleshooting real systems.

The aim is to publish regularly, explain what I tried and what I learned, and build a useful record of projects as they develop.

## Keeping the site simple

I wanted a lightweight site that I could maintain without needing a full content-management system. The content is stored as Markdown files in the [GitHub repository](https://github.com/KieranSHome/KSHome/tree/main/blog-project), so articles can be edited, reviewed and versioned alongside the code that builds the site.

The repository includes a small Python build script. It reads the Markdown posts and their metadata, then generates the static website files, including an article list, individual article pages, styling and a JSON feed. This keeps the published site lightweight and means the writing remains portable plain text.

Each post has a few metadata fields, such as its title, date, summary, category and publication status. Drafts can stay in the repository with `published: false`; changing that field to `true` makes the post eligible for the next build.

## Connecting the domain

The site is available at **[kiwiii.stream/blog](https://kiwiii.stream/blog)**, using a subdomain of my existing `kiwiii.stream` domain managed through Cloudflare.

Setting up a subdomain meant adding a separate `blog` DNS entry and connecting it to the site's Cloudflare-hosted destination. The important lesson was to use the hostname Cloudflare expects, rather than entering a full URL with `https://` into a DNS CNAME target.

I checked the result in a browser after the DNS and hosting configuration was in place. Getting the address to respond was only one part of the job: the next step is making sure the correct site build is being served and that changes to the repository make it through to the live site.

## Why this approach?

This setup gives me a few useful benefits:

- **Version history:** Git records changes to posts and site code.
- **Portable content:** Markdown files are easy to edit and can be moved to another platform.
- **A static site:** Pages can be served without running a database-backed content-management system.
- **A repeatable build:** The same script can generate the site locally or in a deployment pipeline.
- **A dedicated address:** The blog has its own subdomain while the main site remains at [Kiwiii.Stream](https://kiwiii.stream).

It also gives me a practical way to learn more about Git, deployment workflows, DNS and Cloudflare while building something I will actually use.

## What comes next

The initial site is in place; now I can improve the layout, check the publishing workflow end to end and start documenting the projects themselves. I plan to review the previous week's work on Sundays and publish a post at 10 pm when there is something useful to share.

This is the starting point: a simple publishing setup that I can understand, maintain and improve as the home lab grows.

---

**Visit the main site:** [Kiwiii.Stream](https://kiwiii.stream) · **Read future posts:** [Kiwiii.Stream/blog](https://kiwiii.stream/blog)
