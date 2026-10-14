"""Build core/fixtures/site_content.json from the original static prototype.

Usage:  python tools/build_fixture.py
Reads prototype/Klishin Site.dc.html and prototype/_bio-en.json and writes a
Django fixture with lawyers, practices, cases, press items and the rest.
"""
import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTO = ROOT / 'prototype'
OUT = ROOT / 'core' / 'fixtures' / 'site_content.json'

TAG = re.compile(r'<[^>]+>')

SUMMARIES_EN = {
    'arb': 'Disputes between companies before commercial (arbitrazh) courts of all instances: debt recovery, challenging transactions, corporate and construction conflicts, insolvency.',
    'civ': 'Cases before courts of general jurisdiction: recovery of losses and damages, protection of property rights, challenging transactions of individuals.',
    'lab': 'Reinstatement, recovery of payments, disputes over liability for damage and over the dismissal of executives.',
    'crim': 'Defence in economic cases at every stage, from the pre-investigation check to cassation, including attendance at searches and interrogations.',
    'echr': 'Preparing applications and representing clients before the European Court of Human Rights.',
    'corp': 'Structuring businesses, share and equity transactions, shareholder agreements, resolving conflicts between participants.',
    'biz': 'Ongoing legal support: contracts, inspections, employment matters, dealings with regulators.',
    'dd': 'Legal review of assets and counterparties before a transaction, risk assessment and opinions for investors.',
    'bank': 'Credit and security transactions, currency regulation, disputes with banks, compliance matters.',
    'anti': 'Clearance of transactions with the FAS, defence during inspections, unfair competition and advertising cases.',
    'intl': 'Transactions and disputes with a foreign element, recognition and enforcement of foreign court and arbitral awards.',
    'ip': 'Copyright and neighbouring rights, trade marks, protection against unlawful use of IP, including online.',
    'ipc': '',
    'fam': 'Division of marital property, child-related disputes, prenuptial agreements, maintenance agreements.',
    'inh': 'Formalising and protecting inheritance rights, disputes over wills and the composition of an estate.',
    're': 'Property transactions, disputes with contractors and developers, land use and permitting matters.',
    'hous': 'Rights to residential premises, disputes with management companies, privatisation, eviction and alterations.',
}


def text(s):
    return unescape(TAG.sub('', s)).replace('\xa0', ' ').strip()


def load_html():
    html = (PROTO / 'Klishin Site.dc.html').read_text(encoding='utf-8')
    html = re.sub(r'\s(style|style-hover|aria-hidden|hint-placeholder-val)="[^"]*"', '', html)
    return html


def split_lang(html):
    ru_start = html.index('<sc-if value="{{ isRu }}"')
    en_start = html.index('<sc-if value="{{ isEn }}"')
    return html[ru_start:en_start], html[en_start:]


def page_block(section, flag):
    m = re.search(r'<sc-if value="\{\{ ' + flag + r' \}\}">(.*?)\n    </sc-if>', section, re.S)
    return m.group(1)


def parse_bio(block):
    """Parse one lawyer bio page of the prototype into a dict."""
    kicker = text(re.search(r'onClick="\{\{ goTeam \}\}">.*?</a>\s*<div>(.*?)</div>', block, re.S).group(1))
    name = text(re.search(r'<h1>(.*?)</h1>', block).group(1))
    role = text(re.search(r'</h1>\s*<p>(.*?)</p>', block).group(1))

    main, side = block.split('<div>\n              <div>', 1) if '<div>\n              <div>' in block else (block, '')
    # main column: ordered h2 / p sequence up to the side column
    main_part = re.search(r'<div>\s*<h2>.*?(?=\n            </div>\n            <div>)', block, re.S).group(0)
    sections, current = [], None
    for tag, inner in re.findall(r'<(h2|p)>(.*?)</\1>', main_part, re.S):
        if tag == 'h2':
            current = [text(inner), []]
            sections.append(current)
        elif current is not None:
            current[1].append(text(inner))

    # side column: leaf divs after the photo/silhouette
    side_part = block[main_part and block.index(main_part) + len(main_part):]
    side_part = side_part.split('</section>', 1)[0]
    heads = {'Реестр адвокатов', 'Специализация', 'Почётные грамоты и награды', 'Вид услуг', 'Знание языков', 'Иностранные языки'}
    side, current = {}, None
    order = []
    for inner in re.findall(r'<div>((?:(?!<div>).)*?)</div>', side_part, re.S):
        t = text(inner)
        if not t or 'image-slot' in inner or inner.strip().startswith('<svg viewBox'):
            continue
        if t in heads:
            current = t
            side[current] = []
            order.append(current)
        elif current:
            side[current].append(t)

    news = []
    news_part = re.search(r'<h2>Новости и публикации</h2>(.*?)</section>', block, re.S)
    if news_part:
        for date, title in re.findall(r'<span>([\d.]+)</span>\s*<span>(.*?)</span>', news_part.group(1), re.S):
            news.append([date, text(title)])

    return {
        'kicker': kicker, 'name': name, 'role': role,
        'sections': sections, 'side': side, 'side_order': order, 'news': news,
    }


def parse_team(section):
    """name -> position caption from the team page, in page order."""
    block = page_block(section, 'isTeam')
    out = []
    for name, pos in re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>', block, re.S):
        out.append((text(name), text(pos)))
    return out


def main():
    html = load_html()
    ru_html, en_html = split_lang(html)
    bio_en = {p['photoId']: p for p in json.loads((PROTO / '_bio-en.json').read_text(encoding='utf-8'))}

    # Script data: lawyers → practices, photos, short roles.
    script = html[html.index('class Component extends DCLogic'):]
    lawyers_js = re.findall(
        r'\{ id: "(\w+)", ru: \["(.*?)", "(.*?)"\], en: \["(.*?)", "(.*?)"\], p: \[(.*?)\] \}', script)
    photos = json.loads(re.search(r'photos = (\{.*?\});', script).group(1))
    practice_keys = json.loads(re.search(r'practiceKeys = (\[.*?\]);', script).group(1))
    practice_group = json.loads(re.search(r'practiceGroup = (\{.*?\});', script).group(1))
    titles_m = re.search(r'practiceTitles = \{ ru: (\[.*?\]), en: (\[.*?\]) \};', script)
    titles_ru, titles_en = json.loads(titles_m.group(1)), json.loads(titles_m.group(2))
    press_fallback = json.loads(re.search(r'pressFallback = (\{.*?\});\n', script).group(1))

    team_ru = dict(parse_team(ru_html))
    team_en = dict(parse_team(en_html))
    team_order = [n for n, _ in parse_team(ru_html)]

    fixtures = []
    pk = {'group': 0, 'practice': 0, 'lawyer': 0, 'case': 0, 'hl': 0, 'press': 0, 'pub': 0, 'res': 0, 'ip': 0}

    # Practice groups and practices
    groups_ru = re.findall(r'<div>(\d\d)</div>\s*<h2>(.*?)</h2>', page_block(ru_html, 'isPractices'))
    groups_en = re.findall(r'<div>(\d\d)</div>\s*<h2>(.*?)</h2>', page_block(en_html, 'isPractices'))
    for i, ((num, t_ru), (_, t_en)) in enumerate(zip(groups_ru, groups_en), 1):
        fixtures.append({'model': 'core.practicegroup', 'pk': i,
                         'fields': {'order': i, 'number': num, 'title_ru': text(t_ru), 'title_en': text(t_en)}})

    def summaries(section):
        block = page_block(section, 'isPractices')
        return dict(re.findall(r'onClick="\{\{ openPractice_(\w+) \}\}">\s*<span><span>.*?</span><span>.*?</span></span>\s*<span>(.*?)</span>', block, re.S))
    sum_ru = summaries(ru_html)
    sum_en = SUMMARIES_EN  # the prototype's English practice tiles carry no summaries
    ip_link_ru = re.search(r'onClick="\{\{ goIp \}\}">\s*<span>(.*?)</span>\s*<span>(.*?)</span>', page_block(ru_html, 'isPractices'), re.S)

    practice_pk = {}
    for i, key in enumerate(practice_keys, 1):
        practice_pk[key] = i
        fixtures.append({'model': 'core.practice', 'pk': i, 'fields': {
            'key': key, 'group': practice_group[key], 'order': i,
            'title_ru': titles_ru[i - 1], 'title_en': titles_en[i - 1],
            'summary_ru': text(sum_ru.get(key, '')), 'summary_en': text(sum_en.get(key, '')),
            'links_to_ip_centre': key == 'ipc',
        }})

    # Lawyers
    group_of = {}
    for n in team_order:
        idx = team_order.index(n)
        group_of[n] = 'presidium' if idx < 4 else 'advocates' if idx < 10 else 'staff'
    flag_of = {lid: lid.capitalize() for lid, *_ in lawyers_js}

    for order, (lid, name_ru, short_ru, name_en, short_en, plist) in enumerate(lawyers_js, 1):
        ru = parse_bio(page_block(ru_html, 'is' + flag_of[lid]))
        en = bio_en[lid]
        side, so = ru['side'], ru['side_order']
        bio_ru = ru['sections'][0][1]
        extra_title_ru, extra_ru = '', []
        for title, paras in ru['sections'][1:]:
            if title != 'Новости и публикации':
                extra_title_ru, extra_ru = title, paras
        awards_head = next((h for h in so if h not in ('Реестр адвокатов', 'Специализация')), '')
        awards_title_ru = '' if awards_head == 'Почётные грамоты и награды' else awards_head
        if len(bio_ru) != len(en['bio']) or len(extra_ru) != len(en.get('extra', [])):
            print(f'warning: paragraph count differs for {lid}: ru {len(bio_ru)}/{len(extra_ru)} en {len(en["bio"])}/{len(en.get("extra", []))}', file=sys.stderr)
        fixtures.append({'model': 'core.lawyer', 'pk': order, 'fields': {
            'slug': lid, 'order': order, 'group': group_of[ru['name']],
            'on_home': group_of[ru['name']] == 'presidium',
            'photo_url': photos.get(lid, ''), 'silhouette': lid not in photos,
            'practices': [practice_pk[k.strip().strip('"')] for k in plist.split(',')],
            'name_ru': ru['name'], 'name_en': en['name'],
            'position_ru': team_ru[ru['name']], 'position_en': team_en[en['name']],
            'short_role_ru': short_ru, 'short_role_en': short_en,
            'kicker_ru': ru['kicker'], 'kicker_en': en['kicker'],
            'role_ru': ru['role'], 'role_en': en['role'],
            'registry_ru': (side.get('Реестр адвокатов') or [''])[0], 'registry_en': en.get('reg', ''),
            'bio_ru': bio_ru, 'bio_en': en['bio'],
            'extra_title_ru': extra_title_ru, 'extra_title_en': en.get('extraTitle', ''),
            'extra_ru': extra_ru, 'extra_en': en.get('extra', []),
            'specialisation_ru': side.get('Специализация', []), 'specialisation_en': en.get('spec', []),
            'awards_title_ru': awards_title_ru, 'awards_title_en': en.get('awardsTitle', ''),
            'awards_ru': side.get(awards_head, []) if awards_head else [], 'awards_en': en.get('awards', []),
            'news_ru': ru['news'], 'news_en': en.get('news', []),
        }})

    # Cases (full list) + home-page variants
    def cases(section):
        block = page_block(section, 'isCases')
        return re.findall(r'<div>(\d\d)</div>\s*<div>\s*<h2>(.*?)</h2>\s*<p>(.*?)</p>', block, re.S)

    def home_cases(section):
        block = page_block(section, 'isHome')
        part = block.split('onClick="{{ goCases }}"')[1].split('</section>')[0]
        return re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>', part, re.S)
    hc_ru, hc_en = home_cases(ru_html), home_cases(en_html)
    home_map = {'Правительства РФ': 1, 'Голден АДА': 2, 'социальных сетей': 3}  # fragment of case title → position on the home page
    for (num, t_ru, x_ru), (_, t_en, x_en) in zip(cases(ru_html), cases(en_html)):
        f = {'order': int(num), 'title_ru': text(t_ru), 'title_en': text(t_en), 'text_ru': text(x_ru), 'text_en': text(x_en), 'on_home': False,
             'home_order': 0, 'home_title_ru': '', 'home_title_en': '', 'home_text_ru': '', 'home_text_en': ''}
        for frag, idx in home_map.items():
            if frag in f['title_ru']:
                f.update(on_home=True, home_order=idx, home_title_ru=text(hc_ru[idx - 1][0]), home_text_ru=text(hc_ru[idx - 1][1]),
                         home_title_en=text(hc_en[idx - 1][0]), home_text_en=text(hc_en[idx - 1][1]))
        pk['case'] += 1
        fixtures.append({'model': 'core.case', 'pk': pk['case'], 'fields': f})

    # Home practice highlights
    def highlights(section):
        block = page_block(section, 'isHome')
        part = block.split('onClick="{{ goPractices }}"')[2].split('</section>')[0]
        return re.findall(r'<div>(\d\d · .*?)</div>\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>', part, re.S)
    for i, ((l_ru, t_ru, x_ru), (l_en, t_en, x_en)) in enumerate(zip(highlights(ru_html), highlights(en_html)), 1):
        fixtures.append({'model': 'core.practicehighlight', 'pk': i, 'fields': {
            'order': i, 'label_ru': text(l_ru), 'label_en': text(l_en), 'title_ru': text(t_ru), 'title_en': text(t_en),
            'text_ru': text(x_ru), 'text_en': text(x_en)}})

    # Press items (saved fallback list) with home bylines
    def home_press(section):
        block = page_block(section, 'isHome')
        part = block.split('onClick="{{ goPress }}"', 1)[1]
        return re.findall(r'<span>([\d.]+)</span>\s*<span>\s*<span>(.*?)</span>\s*<span>(.*?)</span>', part, re.S)
    hp_ru, hp_en = home_press(ru_html), home_press(en_html)
    for i, (ru, en) in enumerate(zip(press_fallback['ru'], press_fallback['en']), 1):
        d, m, y = ru['date'].split('.')
        fixtures.append({'model': 'core.pressitem', 'pk': i, 'fields': {
            'date': f'{y}-{m}-{d}', 'order': i,
            'title_ru': ru['title'], 'title_en': en['title'], 'text_ru': ru['text'], 'text_en': en['text'],
            'byline_ru': text(hp_ru[i - 1][2]), 'byline_en': text(hp_en[i - 1][2]),
            'source_ru': ru['source'], 'source_en': en['source'], 'url': ru['url'], 'on_home': True}})

    # Publications
    def pubs(section):
        block = page_block(section, 'isPress')
        return re.findall(r'<a href="(https?://[^"]+)" target="_blank" rel="noopener">\s*<span>(.*?)</span>\s*<span>(.*?)</span>', block, re.S)
    for i, ((url, a_ru, t_ru), (_, a_en, t_en)) in enumerate(zip(pubs(ru_html), pubs(en_html)), 1):
        fixtures.append({'model': 'core.publication', 'pk': i, 'fields': {
            'order': i, 'author_ru': text(a_ru), 'author_en': text(a_en), 'title_ru': text(t_ru), 'title_en': text(t_en), 'url': url}})

    # Research items
    def research(section):
        block = page_block(section, 'isPress')
        return re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>', block, re.S)
    for i, ((t_ru, x_ru), (t_en, x_en)) in enumerate(zip(research(ru_html), research(en_html)), 1):
        fixtures.append({'model': 'core.researchitem', 'pk': i, 'fields': {
            'order': i, 'title_ru': text(t_ru), 'title_en': text(t_en), 'text_ru': text(x_ru), 'text_en': text(x_en)}})

    # IP areas: home list (5 short) + IP page list (4 full)
    def ip_home(section):
        block = page_block(section, 'isHome')
        part = block.split('onClick="{{ goIp }}"', 1)[1].split('</section>', 1)[0]
        return [text(x) for x in re.findall(r'<div>([^<]+)</div>', part)][1:]  # [0] is the "Направления"/"Areas" heading

    def ip_page(section):
        block = page_block(section, 'isIp')
        part = block.split('</h2>')[1].split('</div>\n            </div>')[0]
        return [text(x) for x in re.findall(r'<div>(.*?)</div>', part) if text(x)]
    short_ru, short_en, full_ru, full_en = ip_home(ru_html), ip_home(en_html), ip_page(ru_html), ip_page(en_html)
    for i in range(len(short_ru)):
        fixtures.append({'model': 'core.iparea', 'pk': i + 1, 'fields': {
            'order': i + 1, 'short_ru': short_ru[i], 'short_en': short_en[i],
            'full_ru': full_ru[i] if i < len(full_ru) else '', 'full_en': full_en[i] if i < len(full_en) else '',
            'on_home': True}})

    OUT.write_text(json.dumps(fixtures, ensure_ascii=False, indent=1), encoding='utf-8')
    counts = {}
    for f in fixtures:
        counts[f['model']] = counts.get(f['model'], 0) + 1
    print(f'wrote {OUT.relative_to(ROOT)}: {counts}')


if __name__ == '__main__':
    main()
