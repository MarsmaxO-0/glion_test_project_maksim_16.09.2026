# Klishin & Partners — law firm website

Static website for the Moscow bar collegium "Klishin & Partners" (klishin.ru),
built as a self-contained HTML document with a small client-side runtime.

## Files

| File | Purpose |
|------|---------|
| `Klishin Site.dc.html` | Main site: hero, practice areas, team, lawyer bios (RU/EN), news feed, contacts. |
| `Klishin Site-print.dc.html` | Print / PDF version of the site, paginated with `doc-page.js`. |
| `support.js` | Generated runtime (`dc-runtime`) that renders the `<x-dc>` document. Do not edit by hand. |
| `image-slot.js` | `<image-slot>` component for user-fillable photos; state lives in `.image-slots.state.json`. |
| `doc-page.js` | `<doc-page>` paged-document shell used by the print version. |
| `_bio-builder.js` | Template that builds a lawyer bio page from a JSON record. |
| `_bio-ru.json`, `_bio-en.json` | Lawyer biographies in Russian and English. |
| `themis.gif` | Animated hero illustration. |
| `uploads/` | Source images used while designing (not referenced by the pages). |

## Running locally

The pages load `support.js` and the data files relative to the HTML, so serve
the folder over HTTP rather than opening the file directly:

```sh
python3 -m http.server 8000
# then open http://localhost:8000/Klishin%20Site.dc.html
```

Lawyer photos and the news feed are pulled live from klishin.ru; the map is a
Yandex Maps embed.
