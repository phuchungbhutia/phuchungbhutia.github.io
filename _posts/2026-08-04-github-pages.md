---
title: "How to Create a Blog Using GitHub Pages and Jekyll: A Complete Guide"
date: 2026-08-04
categories: ["blogging", "github", "jekyll", "web development"]
tags: ["GitHub Pages", "Jekyll", "blog setup", "static site", "tutorial"]
---

# How to Create a Blog Using GitHub Pages and Jekyll: A Complete Guide

Creating a blog using GitHub Pages with a Jekyll theme is a popular, secure, and cost-effective way to publish content online. Because GitHub Pages provides free hosting for static sites, it is a favorite among developers and writers alike. This guide walks you through the entire process, from choosing a theme to deploying your blog live. It also includes tips, troubleshooting advice, and resources to help you succeed.

---

## 1. Choose and Create Your Site Repository

The foundation of your blog is the repository. Start by selecting a Jekyll theme or a starter repository. Popular choices include:

* **Minimal Mistakes:** Highly customizable and feature-rich.
* **al-folio:** Great for academic or portfolio-focused blogs.
* **Cayman:** A clean, simple theme for basic projects.

### Steps to start:
- Use the **"Use this template"** button on your chosen theme's GitHub page, or fork the starter repository.
- **Critical Step:** Name your new repository exactly as `username.github.io` (replace `username` with your actual GitHub username). This tells GitHub to host the site at your primary user URL.
- Commit the repository to your GitHub account.

---

## 2. Update the Site Configuration

Once your repository is created, you need to tell Jekyll who you are. Open the `_config.yml` file in the root directory and update the following:

* **title:** The name of your blog.
* **description:** A short bio or site summary for SEO.
* **url:** Set this to `https://username.github.io`.
* **baseurl:** Leave this as `""` (empty quotes) if your site is hosted at the root of your domain.
* **Social links/Avatar:** Add your links and image URLs as supported by your specific theme.

Example configuration snippet:

```yaml
title: My Developer Journey
description: "A blog about coding, life, and everything in between."
url: "[https://username.github.io](https://username.github.io)"
baseurl: ""
avatar: "[https://link-to-your-photo.jpg](https://link-to-your-photo.jpg)"

```

---

## 3. Enable GitHub Actions and Pages Build

Modern Jekyll themes often use GitHub Actions to build the site. This is more flexible than the legacy built-in Jekyll processor.

1. Go to the **Actions** tab in your repository. If you see a workflow running after your first push, your site is building!
2. Navigate to **Settings > Pages**.
3. Under **"Build and deployment,"** ensure the **Source** is set to **"GitHub Actions"** if your theme includes a `.github/workflows` folder.

---

## 4. Work Locally (Recommended)

While you can edit files directly on GitHub, working locally allows you to preview changes instantly.

1. **Clone your repo:**
```bash
git clone [https://github.com/username/username.github.io.git](https://github.com/username/username.github.io.git)

```


2. **Install Prerequisites:** You will need Ruby, Bundler, and Jekyll installed on your machine.
3. **Launch the server:**
```bash
bundle exec jekyll serve --livereload

```


4. **Preview:** Open `http://127.0.0.1:4000` in your browser. Any changes you save will refresh the page automatically.

---

## 5. Add Blog Posts

Content is king. To write a post, create a new Markdown file in the `_posts/` directory. The filename must follow the format: `YYYY-MM-DD-title.md`.

Every post needs **Front Matter** at the very top:

```yaml
---
title: "My First Blog Post"
date: 2026-08-04 10:00:00 +0000
categories: [tech]
tags: [tutorial, jekyll]
---

```

After the second `---`, write your content using standard Markdown syntax.

---

## 6. Commit and Deploy

When you are happy with your post or configuration changes:

1. Save the files.
2. Commit and push:
```bash
git add .
git commit -m "Add new post"
git push origin main

```


3. Watch the **Actions** tab. Once the green checkmark appears, your changes are live at `https://username.github.io`.

---

## 7. Troubleshooting and Tips

* **Build Failures:** If your site doesn't update, check the Actions log. Common errors include syntax mistakes in `_config.yml` or missing dependencies in your `Gemfile`.
* **Propagation Delay:** Sometimes it takes 1–2 minutes for GitHub's CDN to refresh. Be patient!
* **Images:** Store your images in an `assets/images` folder and link to them using relative paths to ensure they load correctly.

---

## 8. Optional: Add a Custom Domain

If you want a professional look (e.g., `www.yourname.com`):

1. Purchase a domain from a registrar (like Namecheap or Google Domains).
2. Point the A records to GitHub’s IP addresses and set up a CNAME record.
3. Add your domain in the **Settings > Pages** section of your repository.
4. Enforce **HTTPS** to ensure your site is secure.

---

## 9. Resources

* **YouTube:** Search for *"How to build your Blog for free on GitHub Pages using Jekyll"* for visual walkthroughs.
* **Jekyll Docs:** The official documentation is excellent for advanced customization.
* **GitHub Themes:** Browse the Jekyll Themes gallery for inspiration.

---

This guide consolidates the key steps needed to launch your site. By using GitHub Pages and Jekyll, you have full control over your data and a highly performant website.

Happy blogging!

> **Note:** Remember to replace `username` with your actual GitHub username throughout your setup.

```

```
