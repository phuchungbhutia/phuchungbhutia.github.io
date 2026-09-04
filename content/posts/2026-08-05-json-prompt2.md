---
title: "Building a Reusable JSON Prompt Generator Template"
date: 2026-08-05 08:10:00 +0530
categories: [ai, automation]
tags: [json, templates, prompt-engineering, ai-video, workflow]
---

# Building a Reusable JSON Prompt Generator Template

Writing JSON manually works for a few scenes.

Writing hundreds of prompts quickly becomes repetitive.

The solution is a reusable template.

This article explains how to design a flexible JSON prompt generator that can be adapted to almost any AI video generation platform.

---

# Why Templates Matter

A reusable template offers several advantages:

- Consistency
- Speed
- Fewer mistakes
- Easier collaboration
- Simple automation

Instead of starting from scratch every time, you only fill in the required fields.

---

# Information to Collect

Before generating JSON, gather the following information.

## Platform

Examples:

- Google Veo
- Runway
- Pika
- Luma
- Custom renderer

---

## Output Type

Options include:

- Single scene
- Multiple scenes
- Template with placeholders

---

## Scene Description

One sentence describing the scene.

Example:

> A lone explorer reaches a snowy mountain summit during sunrise.

---

## Style

Examples:

- Documentary
- Commercial
- Cinematic
- Fantasy
- Noir

---

## Camera

Specify:

- Movement
- Angle
- Framing
- Transition

---

## Lighting

Specify:

- Mood
- Source
- Interaction

---

## Environment

Include:

- Location
- Weather
- Background
- Foreground

---

## Optional Fields

Depending on the project:

- Subject
- Motion
- Sound
- Text
- Keywords
- Negative prompts

---

# Reusable Fillable Template

```json
{
  "description": "{scene description}",

  "style": {
    "genre": "{genre}",
    "tone": "{tone}"
  },

  "camera": {
    "movement": "{movement}",
    "angle": "{angle}",
    "framing": "{framing}",
    "transition": "{transition}"
  },

  "lighting": {
    "mood": "{lighting mood}",
    "source": "{source}",
    "interaction": "{interaction}"
  },

  "environment": {
    "location": "{location}",
    "weather": "{weather}",
    "foreground": "{foreground}",
    "background": "{background}"
  },

  "subject": {
    "actor": "{main subject}",
    "action": "{action}"
  },

  "text": {
    "presence": true,
    "content": "{title}",
    "position": "{position}"
  },

  "sound": {
    "ambience": "{ambient sound}",
    "music_style": "{music}"
  },

  "motion": {
    "pace": "{pace}",
    "secondary": "{secondary motion}"
  },

  "keywords": [
    "{keyword1}",
    "{keyword2}"
  ],

  "negatives": [
    "{negative1}",
    "{negative2}"
  ],

  "ending": {
    "type": "{ending}",
    "duration_seconds": 1
  }
}
```

---

# Suggested Workflow

1. Copy the template.
2. Replace placeholders.
3. Validate JSON.
4. Render.
5. Adjust one section.
6. Render again.

Repeat until satisfied.

---

# ChatGPT Prompt Generator

You can also instruct ChatGPT to gather information interactively.

The process should ask:

1. Platform
2. Scene description
3. Style
4. Camera
5. Lighting
6. Environment
7. Subject
8. Motion
9. Sound
10. Ending

Only after collecting answers should the assistant generate the final JSON.

---

# Template Tips

Use variables whenever possible.

Instead of hardcoding:

```json
"location":"Mount Everest"
```

Use:

```json
"location":"{location}"
```

The same template can then generate videos for:

- Mountains
- Beaches
- Cities
- Forests
- Space
- Underwater scenes

---

# Automating at Scale

Once templates exist, scripts can automatically generate hundreds of JSON prompts by replacing variables from CSV or spreadsheet data.

Typical variables include:

- Location
- Time of day
- Camera movement
- Weather
- Subject
- Music style

This approach dramatically speeds up production for travel videos, product showcases, educational content, and marketing campaigns.

---

# Conclusion

A well-designed JSON template separates creative ideas from technical structure.

As projects grow, reusable templates save time, reduce errors, and make AI video production significantly easier.
