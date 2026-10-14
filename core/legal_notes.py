"""Short reference notes on Russian law for the site assistant.

Orientation-level facts only (what a term means, which court, which code,
basic deadlines). The assistant is told these are not legal advice and that
specifics must be checked with an advocate of the association.
"""

LEGAL_NOTES = {
    'ru': """
КРАТКИЙ СПРАВОЧНИК ПО РОССИЙСКОМУ ПРАВУ (ориентировочно, не юридическая консультация)

Кто есть кто
- Адвокат — юрист со статусом, присвоенным адвокатской палатой субъекта РФ после экзамена; внесён в реестр (номер вида 77/424 — Москва, 50/… — Московская область). Только адвокат может быть защитником по уголовному делу на стадии следствия; обязан хранить адвокатскую тайну (ФЗ «Об адвокатской деятельности и адвокатуре в РФ» № 63-ФЗ).
- Юрист / стажёр адвоката / юрисконсульт — специалист без статуса адвоката; может консультировать и представлять в гражданских и арбитражных делах.
- Коллегия адвокатов — форма адвокатского образования (некоммерческая организация), объединяющая адвокатов; «межтерриториальная» — её члены состоят в палатах разных регионов.
- Соглашение об оказании юридической помощи — договор между доверителем и адвокатом; ордер — документ, подтверждающий полномочия адвоката в деле; доверенность нужна для представительства в гражданских и арбитражных делах.

Основные кодексы
- ГК РФ — Гражданский кодекс (сделки, собственность, обязательства, наследство — часть III, интеллектуальная собственность — часть IV).
- ГПК РФ — Гражданский процессуальный кодекс: споры граждан в судах общей юрисдикции.
- АПК РФ — Арбитражный процессуальный кодекс: экономические споры между компаниями и ИП в арбитражных судах.
- УК РФ и УПК РФ — Уголовный кодекс и Уголовно-процессуальный кодекс.
- КоАП РФ — Кодекс об административных правонарушениях (штрафы, в т. ч. за передачу сим-карт третьим лицам).
- ТК РФ — Трудовой кодекс; СК РФ — Семейный кодекс; ЖК РФ — Жилищный кодекс; НК РФ — Налоговый кодекс.

Суды
- Суды общей юрисдикции (мировые судьи, районные, областные/городские, Верховный Суд РФ) — гражданские, семейные, трудовые, жилищные, наследственные, уголовные и административные дела.
- Арбитражные суды (первой инстанции субъекта РФ, апелляционные, окружные кассационные, Судебная коллегия ВС РФ) — споры между компаниями, банкротство, корпоративные споры.
- Третейские суды и международный коммерческий арбитраж (например, МКАС при ТПП РФ) — по соглашению сторон; решения приводятся в исполнение через государственный суд.
- ЕСПЧ: Россия вышла из Совета Европы в марте 2022 года, жалобы по событиям после 16 сентября 2022 года не рассматриваются; ранее поданные дела завершаются.

Сроки, которые часто спрашивают
- Общий срок исковой давности — 3 года (ст. 196 ГК РФ), но не более 10 лет со дня нарушения права.
- Принятие наследства — 6 месяцев со дня смерти наследодателя (ст. 1154 ГК РФ); пропущенный срок можно восстановить через суд при уважительных причинах.
- Обжалование решения суда общей юрисдикции — апелляция в течение 1 месяца; арбитражного суда — 1 месяц на апелляцию, 2 месяца на кассацию.
- Трудовые споры: 1 месяц на обращение в суд по увольнению, 3 месяца по иным спорам, 1 год по невыплате зарплаты (ст. 392 ТК РФ).
- Раздел имущества супругов после развода — 3 года с момента, когда супруг узнал о нарушении права.

Полезные понятия
- Банкротство граждан и компаний — ФЗ № 127-ФЗ; арбитражный суд; внесудебное банкротство граждан через МФЦ при долге от 25 тыс. до 1 млн руб.
- Due diligence — правовая проверка актива или контрагента перед сделкой.
- Антимонопольное регулирование — ФЗ «О защите конкуренции» № 135-ФЗ, контролирующий орган — ФАС России.
- Товарные знаки и патенты регистрирует Роспатент; авторское право возникает без регистрации (ч. IV ГК РФ); споры по ИС рассматривает Суд по интеллектуальным правам.
- Защита чести, достоинства и деловой репутации — ст. 152 ГК РФ: опровержение, удаление информации, компенсация.
- Недвижимость: права регистрируются в ЕГРН (Росреестр); сделки с долями и некоторые другие требуют нотариальной формы.
- Брачный договор и соглашение об уплате алиментов удостоверяются нотариально.
- Уголовная защита предпринимателей: защитник вправе участвовать с момента задержания или первого допроса; обыск проводится по постановлению следователя или суда.
""",
    'en': """
SHORT REFERENCE ON RUSSIAN LAW (orientation only, not legal advice)

Who is who
- Advocate (адвокат) — a lawyer admitted by a regional Chamber of Advocates after an examination and listed in its registry (numbers such as 77/424 are Moscow, 50/… Moscow Region). Only an advocate may act as defence counsel during a criminal investigation; advocates are bound by professional privilege (Federal Law No. 63-FZ on Advocacy).
- Lawyer / trainee advocate / legal counsel — a legal professional without advocate status; may advise and represent clients in civil and commercial cases.
- Bar association (collegium, коллегия адвокатов) — a non-profit form of advocates' practice; "interterritorial" means its members belong to chambers of different regions.
- Legal services agreement — the contract between client and advocate; a warrant (ордер) confirms the advocate's authority in a case; a power of attorney is needed for civil and commercial representation.

Main codes
- Civil Code (ГК РФ) — contracts, property, obligations, inheritance (Part III), intellectual property (Part IV).
- Civil Procedure Code (ГПК РФ) — disputes of individuals before courts of general jurisdiction.
- Commercial (Arbitrazh) Procedure Code (АПК РФ) — economic disputes between companies and entrepreneurs before arbitrazh courts.
- Criminal Code (УК РФ) and Criminal Procedure Code (УПК РФ).
- Code of Administrative Offences (КоАП РФ) — fines, including for handing SIM cards to third parties.
- Labour Code (ТК РФ), Family Code (СК РФ), Housing Code (ЖК РФ), Tax Code (НК РФ).

Courts
- Courts of general jurisdiction (justices of the peace, district, regional, Supreme Court) — civil, family, employment, housing, inheritance, criminal and administrative cases.
- Arbitrazh (commercial) courts (regional first instance, appeal, circuit cassation, Supreme Court chamber) — disputes between businesses, insolvency, corporate disputes. Despite the name they are state courts, not arbitration tribunals.
- Arbitration tribunals and international commercial arbitration (e.g. ICAC at the RF Chamber of Commerce) — by agreement of the parties; awards are enforced through a state court.
- ECHR: Russia left the Council of Europe in March 2022; applications about events after 16 September 2022 are not examined, earlier cases are being completed.

Deadlines people often ask about
- General limitation period — 3 years (Art. 196 Civil Code), capped at 10 years from the violation.
- Accepting an inheritance — 6 months from the date of death (Art. 1154 Civil Code); a missed deadline can be restored by a court for good reason.
- Appeal against a judgment of a court of general jurisdiction — 1 month; arbitrazh court — 1 month for appeal, 2 months for cassation.
- Employment disputes: 1 month to sue over dismissal, 3 months for other disputes, 1 year for unpaid wages (Art. 392 Labour Code).
- Division of marital property after divorce — 3 years from when the spouse learned of the violation.

Useful concepts
- Insolvency of individuals and companies — Federal Law No. 127-FZ; arbitrazh court; out-of-court personal bankruptcy via MFC for debts from 25,000 to 1,000,000 roubles.
- Due diligence — legal review of an asset or counterparty before a transaction.
- Antitrust — Federal Law No. 135-FZ on Protection of Competition; regulator: FAS Russia.
- Trade marks and patents are registered by Rospatent; copyright arises without registration (Part IV Civil Code); IP disputes go to the Intellectual Property Court.
- Protection of honour, dignity and business reputation — Art. 152 Civil Code: retraction, removal of information, compensation.
- Real estate: rights are registered in the EGRN (Rosreestr); share transactions and some others require notarial form.
- Prenuptial agreements and maintenance agreements must be notarised.
- Criminal defence of entrepreneurs: counsel may take part from the moment of detention or first interrogation; a search requires an investigator's or court order.
""",
}
