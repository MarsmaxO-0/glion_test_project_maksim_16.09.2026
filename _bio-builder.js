(() => {
const H = 'font-family: Podkova, Georgia, serif';
const L = '#F0DFD7', INK = '#14315C', MUT = '#5B6472', ACC = '#BF4A3C';
const sideHead = (t) => `<div style="font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: ${ACC}; margin: 0 0 14px;">${t}</div>`;
const li = (t) => `<div style="font-size: 15px; line-height: 1.55; color: ${MUT}; padding: 9px 0; border-bottom: 1px solid ${L};">${t}</div>`;
const AWARD_ICON = '<svg width="13" height="16" viewBox="0 0 13 16" fill="none" aria-hidden="true" style="flex: 0 0 auto; margin-top: 3px; color: #B07F6B;"><circle cx="6.5" cy="4.6" r="3.9" stroke="currentColor" stroke-width="1.2"></circle><path d="M4.3 8.1 3.1 14.6l3.4-1.9 3.4 1.9-1.2-6.5" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"></path></svg>';
const awardLi = (t) => `<div style="display: flex; gap: 9px; align-items: flex-start; font-size: 15px; line-height: 1.55; color: ${MUT}; padding: 9px 0; border-bottom: 1px solid ${L};">${AWARD_ICON}<span>${t}</span></div>`;
const para = (t) => `<p style="font-size: 16px; line-height: 1.75; color: #1C2436; margin: 0 0 18px; max-width: 70ch;">${t}</p>`;
const newsRow = (date, t) => `<a href="#" style="display: block; padding: 18px 0; border-bottom: 1px solid ${L};" style-hover="background: #FBEDE6;">
                <span style="display: block; font-size: 13px; color: #7D5749; margin-bottom: 7px;">${date}</span>
                <span style="display: block; ${H}; font-size: 16px; line-height: 1.45; color: ${INK};">${t}</span>
              </a>`;
// p = {flag, kicker, name, role, photoId, reg, bio[], extraTitle, extra[], spec[], awards[], news[[date,title]]}
return (p) => `
    <sc-if value="{{ ${p.flag} }}">
      <div data-screen-label="${p.name}">
        <section style="background: ${INK}; color: #FFFFFF; border-radius: 0 0 32px 32px; padding: 56px 32px 60px;">
          <div style="max-width: 1180px; margin: 0 auto;">
            <a href="#" onClick="{{ goTeam }}" style="display: inline-block; font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: #F0A192; margin-bottom: 22px;">← Команда</a>
            <div style="font-size: 12px; letter-spacing: 0.2em; text-transform: uppercase; color: #F0A192; margin-bottom: 16px;">${p.kicker}</div>
            <h1 style="${H}; font-size: 42px; font-weight: 600; margin: 0 0 14px; line-height: 1.14;">${p.name}</h1>
            <p style="font-size: 17px; color: #C9D1DC; margin: 0;">${p.role}</p>
          </div>
        </section>
        <section style="max-width: 1180px; margin: 0 auto; padding: 56px 32px 0;">
          <div style="display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr); gap: 56px; align-items: start;">
            <div>
              <h2 style="${H}; font-size: 26px; font-weight: 500; margin: 0 0 22px; padding-bottom: 14px; border-bottom: 1px solid ${L};">Биография</h2>
${p.bio.map(para).map((s) => '              ' + s).join('\n')}
${(p.extra && p.extra.length) ? `              <h2 style="${H}; font-size: 26px; font-weight: 500; margin: 40px 0 22px; padding-bottom: 14px; border-bottom: 1px solid ${L};">${p.extraTitle}</h2>
${p.extra.map(para).map((s) => '              ' + s).join('\n')}` : ''}
            </div>
            <div style="display: flex; flex-direction: column; gap: 34px;">
              <div style="aspect-ratio: 4 / 5; background: #F7E4DC; border: 1px solid ${L}; border-radius: 18px; overflow: hidden; position: relative;"><image-slot id="photo-${p.photoId}"${p.photo ? ' src="' + p.photo + '"' : ''} shape="rect" fit="cover" placeholder="${p.name}" style="width: 100%; height: 100%;"></image-slot></div>
${p.reg ? `              <div>
                ${sideHead('Реестр адвокатов')}
                <div style="font-size: 16px; color: ${INK};">${p.reg}</div>
              </div>` : ''}
${(p.spec && p.spec.length) ? `              <div>
                ${sideHead(p.specTitle || 'Специализация')}
${p.spec.map(li).map((s) => '                ' + s).join('\n')}
              </div>` : ''}
${(p.awards && p.awards.length) ? `              <div>
                ${sideHead(p.awardsTitle || 'Почётные грамоты и награды')}
${p.awards.map(p.awardsTitle ? li : awardLi).map((s) => '                ' + s).join('\n')}
              </div>` : ''}
            </div>
          </div>
        </section>
${(p.news && p.news.length) ? `        <section style="max-width: 1180px; margin: 0 auto; padding: 56px 32px 0;">
          <h2 style="${H}; font-size: 26px; font-weight: 500; margin: 0 0 8px; padding-bottom: 14px; border-bottom: 1px solid ${L};">Новости и публикации</h2>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr)); gap: 0 44px;">
${p.news.map((n) => '            ' + newsRow(n[0], n[1])).join('\n')}
          </div>
        </section>` : ''}
        <div style="height: 96px;"></div>
      </div>
    </sc-if>
`;
})()
