"""Per-track briefs extracted from the hand-built previews.

Every preview under preview/lab/music-v0/ is a distinct hand-authored world: its
own artist, title, kicker, thesis and ground. These are carried as data rather
than generated, because they are the point of the exercise -- two tracks must
never look alike. Resolved by the catalog id (ti01-ti16); ti16 has no preview
and falls back, while five previews predate the catalog and keep slug keys.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrackBrief:
    key: str
    artist: str = ""
    title: str = ""
    voice: str = ""
    thesis: str = ""
    paper: str = ""
    night: str = ""
    ink: str = ""
    accent: str = ""


# key -> the preview file the brief was read from
PREVIEW_STEM: dict[str, str] = {
    'ti01': 'night-train-v5',
    'ti02': 'kono-sekai-de-mitsuketa-mono-v1',
    'ti03': 'quruli-kohakuiro-v1',
    'ti04': 'kirinji-sweet-soul-v1',
    'ti05': 'forest-burning-beautifully-v1',
    'ti06': 'koromogae-v1',
    'ti07': 'lilb-orange-v1',
    'ti08': 'jane-doe-v1',
    'ti09': 'departures-v1',
    'ti10': 'juliet-re-edit-v4',
    'ti11': 'whos-theme-v1',
    'ti12': 'fukashigi-no-carte-v1',
    'ti13': 'lovely-summer-chan-suisei-v1',
    'ti14': 'hana-v1',
    'ti15': 'maica-n-himitsu-v1',
    'stay-with-me': 'miki-matsubara-stay-with-me-v1',
    'payung': 'payung-teduh-selalu-muda-v1',
    'ariamaru': 'sheena-ringo-ariamaru-tomi-v1',
    'kaede': 'spitz-kaede-v1',
    'you-and-i': 'tokyo-ska-you-and-i-v1',
}


BRIEFS: dict[str, TrackBrief] = {
    'ti01': TrackBrief(
        key='ti01',
        artist="Awesome City Club", title="夜汽車は走る",
        voice="Music DNA · Magnum Opus 01", thesis="Amaharashi coast · early night",
        paper="#070b10", night="#070b10", ink="#eee7db",
    ),
    'ti02': TrackBrief(
        key='ti02',
        artist="EGOIST", title="FOUND HERE",
        voice="WHAT I FOUND IN THIS WORLD / NIGHT WIND ARCHIVE", thesis="",
        paper="#07090c", night="#07090c", ink="#f4efe7",
    ),
    'ti03': TrackBrief(
        key='ti03',
        artist="MULTIMIND / MUSIC DNA", title="琥珀色の街、 上海蟹の朝",
        voice="01:14 → first light / amber fantasy city", thesis="",
        paper="#10120f", night="#10120f", ink="#fff7df",
    ),
    'ti04': TrackBrief(
        key='ti04',
        artist="KIRINJI", title="SWEET SOUL",
        voice="MIDNIGHT / QUIET MOON / HEARTBEAT ORBIT", thesis="",
        paper="#100d18", night="#100d18", ink="#f3eadf",
    ),
    'ti05': TrackBrief(
        key='ti05',
        artist="TOKYO SKA PARADISE ORCHESTRA × TAMIO OKU", title="Forest Burning Beautifully",
        voice="forest entrance · moon night · no-return journey", thesis="",
        paper="#090909", night="#090909", ink="#f0e9de",
    ),
    'ti06': TrackBrief(
        key='ti06',
        artist="MULTIMIND · NIGHT ROUTE", title="衣替え KOROMOGAE / a quieter kind of change",
        voice="PASSENGER VIEW · 23:41 · TOKYO", thesis="ARTIST / VOCALS TOFUBEATS",
        paper="", night="", ink="#eef2f4",
    ),
    'ti07': TrackBrief(
        key='ti07',
        artist="MULTIMIND / MUSIC DNA", title="Orange",
        voice="", thesis="",
        paper="#fff4e5", night="#29121d", ink="#29121d",
    ),
    'ti08': TrackBrief(
        key='ti08',
        artist="KENSHI YONEZU × HIKARU UTADA", title="JANE DOE",
        voice="UNIDENTIFIED / RED TRACE / 00:00", thesis="A world where almost every trace is erased, except the one line that still asks to be followed.",
        paper="#050608", night="#050608", ink="#f3f0eb",
    ),
    'ti09': TrackBrief(
        key='ti09',
        artist="EGOIST", title="DEPARTURES あなたにおくるアイの歌",
        voice="LAST PLATFORM / 00:17", thesis="",
        paper="#080b0f", night="#080b0f", ink="#eee9e1",
    ),
    'ti10': TrackBrief(
        key='ti10',
        artist="BASI & THE BASIC BAND", title="Re:Juliet",
        voice="", thesis="",
        paper="#090a0c", night="#f2ece5", ink="#f2ece5",
    ),
    'ti11': TrackBrief(
        key='ti11',
        artist="MINMI × NUJABES", title="WHO'S THEME",
        voice="WIND / MEMORY / FOUR SEASONS / DUSK", thesis="sunflower / waiting season / turning memory / unbound",
        paper="#1a1513", night="#1a1513", ink="#2d211a",
    ),
    'ti12': TrackBrief(
        key='ti12',
        artist="FUKASHIGI NO CARTE", title="UNREADABLE CARTE",
        voice="AFTER SCHOOL / SLEEPLESS / BOUNDARY / UNREADABLE CHART", thesis="",
        paper="#0a0c10", night="#0a0c10", ink="#f5efe8",
    ),
    'ti13': TrackBrief(
        key='ti13',
        artist="LOVELY SUMMER CHAN", title="水星",
        voice="SHINJUKU / TRANSIT / DATA / DANCE / MERCURY", thesis="signal / alive city / sampled mercury / maybe",
        paper="#090915", night="#090915", ink="#f7f6ff",
    ),
    'ti14': TrackBrief(
        key='ti14',
        artist="FUJII KAZE", title="花",
        voice="", thesis="the flower inside",
        paper="#161715", night="#161715", ink="#101313",
    ),
    'ti15': TrackBrief(
        key='ti15',
        artist="MAICA_N", title="Himitsu",
        voice="SMALL ROOM / WHISPER / TOUCH / UNSAID", thesis="room / close voice / low truth / unsaid",
        paper="#171113", night="#171113", ink="#f8f1ea",
    ),
    'stay-with-me': TrackBrief(
        key='stay-with-me',
        artist="MIKI MATSUBARA", title="STAY WITH ME",
        voice="MIDNIGHT / CITY LIGHTS / GROOVE / DOOR STILL OPEN", thesis="street / moving door / open pulse / locked",
        paper="#090812", night="#090812", ink="#fff5eb",
    ),
    'payung': TrackBrief(
        key='payung',
        artist="PAYUNG TEDUH", title="SELALU MUDA",
        voice="RUANG TUNGGU / MALAM / FAJAR / RINDU", thesis="a table that keeps one seat warm",
        paper="#1f1714", night="#1f1714", ink="#2b211c",
    ),
    'ariamaru': TrackBrief(
        key='ariamaru',
        artist="SHEENA RINGO", title="ARIAMARU TOMI",
        voice="AFTERNOON / VALUE / WHAT CANNOT BE TAKEN", thesis="price / finite value / uncounted wealth / still here",
        paper="#211914", night="#211914", ink="#2c241d",
    ),
    'kaede': TrackBrief(
        key='kaede',
        artist="SPITZ", title="楓",
        voice="AUTUMN / VOICE MEMORY / CARRIED FORWARD", thesis="",
        paper="#221714", night="#221714", ink="#241b18",
    ),
    'you-and-i': TrackBrief(
        key='you-and-i',
        artist="", title="You and I",
        voice="", thesis="",
        paper="", night="", ink="",
    ),
}