from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from math import atan2, cos, floor, radians, sin, tan

try:
    import swisseph as swe
except ImportError:  # pragma: no cover - depends on local platform
    swe = None

try:
    import astronomy
except ImportError:  # pragma: no cover - fallback dependency may be absent in prod
    astronomy = None


SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

NAKSHATRAS = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

TITHIS = [
    "Pratipada",
    "Dwitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
    "Purnima",
    "Pratipada",
    "Dwitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
    "Amavasya",
]

YOGAS = [
    "Vishkambha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Shobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shoola",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyana",
    "Parigha",
    "Shiva",
    "Siddha",
    "Sadhya",
    "Shubha",
    "Shukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
]

KARANAS = [
    "Bava",
    "Balava",
    "Kaulava",
    "Taitila",
    "Gara",
    "Vanija",
    "Vishti",
]

# Vimshottari Dasha — standard 120-year cycle (BPHS)
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

# Nakshatra lord sequence repeats Ketu→Mercury for all 27 nakshatras
NAKSHATRA_LORD_MAP = (DASHA_ORDER * 3)[:27]

# Standard nakshatra details per BPHS / traditional Vedic texts
NAKSHATRA_DETAILS: dict[str, dict] = {
    "Ashwini":           {"lord": "Ketu",    "deity": "Ashwini Kumaras", "symbol": "Horse's head",        "gana": "Deva",     "varna": "Vaishya",  "quality": "Kshipra (Swift)"},
    "Bharani":           {"lord": "Venus",   "deity": "Yama",            "symbol": "Yoni",                "gana": "Manushya", "varna": "Mleccha",  "quality": "Ugra (Fierce)"},
    "Krittika":          {"lord": "Sun",     "deity": "Agni",            "symbol": "Razor / Flame",       "gana": "Rakshasa", "varna": "Brahmin",  "quality": "Sadhana (Mixed)"},
    "Rohini":            {"lord": "Moon",    "deity": "Brahma / Prajapati","symbol": "Chariot / Ox-cart", "gana": "Manushya", "varna": "Shudra",   "quality": "Sthira (Fixed)"},
    "Mrigashira":        {"lord": "Mars",    "deity": "Soma (Moon god)", "symbol": "Deer's head",         "gana": "Deva",     "varna": "Farmer",   "quality": "Mridu (Soft)"},
    "Ardra":             {"lord": "Rahu",    "deity": "Rudra",           "symbol": "Teardrop / Diamond",  "gana": "Manushya", "varna": "Butcher",  "quality": "Tikshna (Sharp)"},
    "Punarvasu":         {"lord": "Jupiter", "deity": "Aditi",           "symbol": "Bow / Quiver",        "gana": "Deva",     "varna": "Vaishya",  "quality": "Chara (Movable)"},
    "Pushya":            {"lord": "Saturn",  "deity": "Brihaspati",      "symbol": "Flower / Circle",     "gana": "Deva",     "varna": "Kshatriya","quality": "Laghu (Light)"},
    "Ashlesha":          {"lord": "Mercury", "deity": "Sarpa (Serpents)","symbol": "Coiled serpent",      "gana": "Rakshasa", "varna": "Mleccha",  "quality": "Tikshna (Sharp)"},
    "Magha":             {"lord": "Ketu",    "deity": "Pitrs (Ancestors)","symbol": "Throne / Palanquin", "gana": "Rakshasa", "varna": "Shudra",   "quality": "Ugra (Fierce)"},
    "Purva Phalguni":    {"lord": "Venus",   "deity": "Bhaga",           "symbol": "Fig tree / Hammock",  "gana": "Manushya", "varna": "Brahmin",  "quality": "Ugra (Fierce)"},
    "Uttara Phalguni":   {"lord": "Sun",     "deity": "Aryaman",         "symbol": "Bed / Fig tree",      "gana": "Manushya", "varna": "Kshatriya","quality": "Sthira (Fixed)"},
    "Hasta":             {"lord": "Moon",    "deity": "Savitar (Sun god)","symbol": "Palm / Hand",         "gana": "Deva",     "varna": "Vaishya",  "quality": "Laghu (Light)"},
    "Chitra":            {"lord": "Mars",    "deity": "Vishwakarma",     "symbol": "Bright jewel / Pearl", "gana": "Rakshasa", "varna": "Farmer",   "quality": "Mridu (Soft)"},
    "Swati":             {"lord": "Rahu",    "deity": "Vayu (Wind)",     "symbol": "Coral / Sword",        "gana": "Deva",     "varna": "Butcher",  "quality": "Chara (Movable)"},
    "Vishakha":          {"lord": "Jupiter", "deity": "Indra-Agni",      "symbol": "Triumphal arch / Potter's wheel", "gana": "Rakshasa", "varna": "Mleccha", "quality": "Sadhana (Mixed)"},
    "Anuradha":          {"lord": "Saturn",  "deity": "Mitra",           "symbol": "Lotus / Row of offerings", "gana": "Deva",  "varna": "Shudra",   "quality": "Mridu (Soft)"},
    "Jyeshtha":          {"lord": "Mercury", "deity": "Indra",           "symbol": "Circular amulet / Earring", "gana": "Rakshasa", "varna": "Farmer", "quality": "Tikshna (Sharp)"},
    "Mula":              {"lord": "Ketu",    "deity": "Nirriti / Alakshmi","symbol": "Tied roots / Lion's tail", "gana": "Rakshasa", "varna": "Butcher", "quality": "Tikshna (Sharp)"},
    "Purva Ashadha":     {"lord": "Venus",   "deity": "Apas (Water)",    "symbol": "Fan / Winnowing basket","gana": "Manushya","varna": "Brahmin",  "quality": "Ugra (Fierce)"},
    "Uttara Ashadha":    {"lord": "Sun",     "deity": "Vishvadevas",     "symbol": "Elephant's tusk / Bed","gana": "Manushya", "varna": "Kshatriya","quality": "Sthira (Fixed)"},
    "Shravana":          {"lord": "Moon",    "deity": "Vishnu",          "symbol": "Three footprints / Ear","gana": "Deva",    "varna": "Mleccha",  "quality": "Chara (Movable)"},
    "Dhanishta":         {"lord": "Mars",    "deity": "Ashta-Vasus",     "symbol": "Drum / Flute",         "gana": "Rakshasa","varna": "Farmer",   "quality": "Chara (Movable)"},
    "Shatabhisha":       {"lord": "Rahu",    "deity": "Varuna",          "symbol": "Empty circle / 1000 stars", "gana": "Rakshasa", "varna": "Butcher", "quality": "Chara (Movable)"},
    "Purva Bhadrapada":  {"lord": "Jupiter", "deity": "Ajaikapada",      "symbol": "Swords / Two faces",   "gana": "Manushya","varna": "Brahmin",  "quality": "Ugra (Fierce)"},
    "Uttara Bhadrapada": {"lord": "Saturn",  "deity": "Ahirbudhnya",     "symbol": "Twins / Back legs of cot","gana": "Manushya","varna": "Kshatriya","quality": "Sthira (Fixed)"},
    "Revati":            {"lord": "Mercury", "deity": "Pushan",          "symbol": "Fish / Drum",           "gana": "Deva",    "varna": "Shudra",   "quality": "Mridu (Soft)"},
}

# Mahadasha × Antardasha combined effects (per BPHS karakatwas)
# Key format: "MD_lord/AD_lord"
MD_AD_EFFECTS: dict[str, str] = {
    # ── Sun Mahadasha ──────────────────────────────────────────────────────────
    "Sun/Sun":      "Strong self-expression and leadership peak. Government favour, vitality, and authority are highlighted. Father's health and support become prominent themes.",
    "Sun/Moon":     "Public life and emotional clarity merge. Recognition in career alongside domestic harmony. Mother's influence and public dealings both rise.",
    "Sun/Mars":     "Courage and initiative surge. Favourable for property, siblings, and legal victories. Conflicts with superiors are possible; channel energy through righteous action.",
    "Sun/Rahu":     "Ambition intensifies through unconventional routes. Foreign connections or technology-based gains are possible. Guard against ego inflation and health of the eyes.",
    "Sun/Jupiter":  "Wisdom and authority unite beautifully. Blessings from elders, teachers, and dharmic institutions. Excellent period for spiritual growth and career advancement.",
    "Sun/Saturn":   "Tension between ego and duty. Service-oriented effort is rewarded slowly but surely. Delays in recognition are likely; patience and humility are essential.",
    "Sun/Mercury":  "Intellect and authority combine. Communication-based careers, writing, trade, and advisory roles flourish. Good for negotiations and government dealings.",
    "Sun/Ketu":     "Detachment from ego and material ambition begins. Spiritual inclinations deepen. Past karma around authority or father resolves; health of eyes needs care.",
    "Sun/Venus":    "Comforts, arts, and relationships improve under solar protection. Possible tension between personal pride and partnership needs; creativity is well rewarded.",
    # ── Moon Mahadasha ─────────────────────────────────────────────────────────
    "Moon/Sun":     "Public recognition and emotional stability align. Career and home life find balance. Father's support or government connections bring favour.",
    "Moon/Moon":    "Deep emotional sensitivity and intuition are heightened. Mother's health, travel, and domestic comfort are central. Inner peace comes through nurturing others.",
    "Moon/Mars":    "Emotional drive and courage combine. Good for property acquisitions and domestic action. Mood swings are possible; channel energy into creative or physical work.",
    "Moon/Rahu":    "Restlessness and foreign influences increase. Mother's health needs attention. Avoid speculation and emotionally-driven decisions; seek grounding practices.",
    "Moon/Jupiter": "Prosperity and emotional wisdom expand together. Family flourishes, spiritual nourishment deepens, and financial stability grows. A blessed sub-period.",
    "Moon/Saturn":  "Emotional austerity and lessons in patience. Delays in domestic matters teach duty and resilience. Service to elders or community brings karmic reward.",
    "Moon/Mercury": "Intellectual and emotional intelligence combine. Writing, teaching, public communication, and business dealings all flourish. Good for studies.",
    "Moon/Ketu":    "Psychic sensitivity rises; withdrawal and introspection deepen. Spiritual progress through letting go. Past-life emotional karma gently resolves.",
    "Moon/Venus":   "Domestic happiness, beauty, and comfort are highlighted. Relationships improve, creative endeavours blossom, and material comforts increase naturally.",
    # ── Mars Mahadasha ─────────────────────────────────────────────────────────
    "Mars/Sun":     "Courage and authority peak together. Favourable for property, legal victories, and leadership. Conflicts with superiors are possible but can be overcome.",
    "Mars/Moon":    "Emotional drive and physical energy combine. Property acquisitions are favoured. Guard mother's health and avoid impulsive emotional decisions.",
    "Mars/Mars":    "Maximum Martian energy — physical vitality, courage, and determination surge. Property and siblings play key roles. Drive results with discipline.",
    "Mars/Rahu":    "Unpredictable energy with potential for accidents or foreign technical gains. Courage mixed with illusion; avoid rash decisions, especially in disputes.",
    "Mars/Jupiter": "Dharmic courage and righteous effort bring property gains, legal victories, and expansion. An excellent sub-period for decisive, ethical action.",
    "Mars/Saturn":  "Hard labour with slow rewards. Discipline in action eventually leads to success. Avoid disputes; industrial or technical work is best channelled here.",
    "Mars/Mercury": "Technical precision and communication excel. Engineering, law, debate, and sports can flourish. Energy is channelled through the mind effectively.",
    "Mars/Ketu":    "Spiritual warrior energy rises. Detachment from material possessions begins. Guard against accidents; moksha-oriented practices yield deep results.",
    "Mars/Venus":   "Passion, romance, and creative energy surge. Property and artistic projects both advance. Relationship tensions may arise if desires are unchecked.",
    # ── Rahu Mahadasha ─────────────────────────────────────────────────────────
    "Rahu/Sun":     "Authority through unconventional sources. Government dealings and foreign connections bring gains. Father's health needs attention; avoid ego-driven decisions.",
    "Rahu/Moon":    "Mental restlessness and foreign influences intensify. Mother's health is sensitive. Avoid speculation and emotionally erratic choices; seek mental calm.",
    "Rahu/Mars":    "Sudden energy surges with potential for accidents. Foreign or technical fields may bring gains through unconventional methods. Maintain caution in disputes.",
    "Rahu/Rahu":    "Peak Rahu period — maximum ambition, foreign gains, illusions, and life transformation. Results come fast but are often impermanent; discernment is key.",
    "Rahu/Jupiter": "Spiritual materialism and expansion through foreign or unconventional means. Wisdom may be distorted; seek genuine teachers to navigate this sub-period.",
    "Rahu/Saturn":  "Double shadow-planet period brings karmic delays and hard labour. Discipline and perseverance eventually yield rewards; health needs careful attention.",
    "Rahu/Mercury": "Clever, persuasive communication; gains in media, technology, and foreign languages. Guard against deceptive dealings; use intelligence ethically.",
    "Rahu/Ketu":    "Karmic axis fully activated. Confusion, spiritual crossroads, and surfacing of deep past karma. Major inner transformation; avoid hasty material decisions.",
    "Rahu/Venus":   "Unusual relationships and material desires intensify. Foreign luxury and unconventional partnerships may arise. Material gains are possible but transitory.",
    # ── Jupiter Mahadasha ──────────────────────────────────────────────────────
    "Jupiter/Sun":  "Wisdom and authority unite. Government blessings, dharmic recognition, and father's support are prominent. An excellent period for career and spiritual growth.",
    "Jupiter/Moon": "Emotional wisdom and family prosperity expand. Motherly blessings and spiritual nourishment are highlighted. Inner peace and outer abundance align.",
    "Jupiter/Mars": "Dharmic courage and righteous expansion. Legal victories, property gains, and decisive ethical action all succeed. Siblings and elders offer support.",
    "Jupiter/Rahu": "Expansion through unconventional or foreign paths. Spiritual materialism may cloud judgement; seek authentic wisdom and avoid hollow ambitions.",
    "Jupiter/Jupiter": "Peak wisdom and abundance. Spiritual, financial, and educational expansion are all highlighted. One of the most auspicious sub-periods in any chart.",
    "Jupiter/Saturn": "Structured, disciplined growth with karmic rewards. Service-oriented effort pays off slowly but surely. Dharmic patience brings lasting gains.",
    "Jupiter/Mercury": "Intellectual expansion at its finest. Teaching, law, finance, writing, and spiritual study all flourish. Excellent for higher education and counselling.",
    "Jupiter/Ketu": "Spiritual liberation and detachment from ego. A past-life teacher or guide may appear. Moksha-oriented practices deepen; material desires naturally soften.",
    "Jupiter/Venus": "Dharmic prosperity and harmony. Marriage, finance, arts, and spirituality all flourish together. One of the most auspicious sub-period combinations.",
    # ── Saturn Mahadasha ───────────────────────────────────────────────────────
    "Saturn/Sun":   "Authority earned through discipline and service. Ego slowly dissolves under Saturn's pressure. Father's health and government dealings require careful attention.",
    "Saturn/Moon":  "Emotional austerity and detachment from comfort. Service brings karmic reward. Mother's health and domestic stability may face testing during this time.",
    "Saturn/Mars":  "Hard labour and property gains after sustained struggle. Discipline in action eventually succeeds. Avoid disputes; industrial and technical work is rewarded.",
    "Saturn/Rahu":  "Double shadow period — karmic delays, foreign hardship, and heavy responsibilities. Perseverance through discipline will eventually yield lasting results.",
    "Saturn/Jupiter": "Structured wisdom and disciplined service bring karmic rewards. A slow but righteous progression; past good karma gradually ripens and bears fruit.",
    "Saturn/Saturn": "Peak Saturn period — karma ripens fully. Service, austerity, longevity, and discipline are dominant themes. Humility and duty bring deepest rewards.",
    "Saturn/Mercury": "Systematic, disciplined communication and research. Slow but steady intellectual progress. Publishing, research, and administrative work are well rewarded.",
    "Saturn/Ketu":  "Spiritual renunciation and karmic completion. Ascetic tendencies deepen; the soul orients toward moksha. Material detachment brings unexpected inner peace.",
    "Saturn/Venus": "Delayed but lasting relationship fulfilment. Artistic discipline and patient partnership are rewarded. Material comforts come slowly but endure.",
    # ── Mercury Mahadasha ──────────────────────────────────────────────────────
    "Mercury/Sun":  "Intellect meets authority. Government communication, business with state agencies, and intellectual leadership are all favoured during this sub-period.",
    "Mercury/Moon": "Emotional intelligence and public communication unite. Writing, teaching, counselling, and public-facing business all flourish with natural ease.",
    "Mercury/Mars": "Technical precision and energetic communication excel. Engineering, law, debate, and competitive business dealings all benefit from this combination.",
    "Mercury/Rahu": "Clever, innovative communication; gains through media, technology, and foreign languages. Guard against deception or unethical use of intelligence.",
    "Mercury/Jupiter": "Scholarly wisdom and intellectual breadth expand. Teaching, law, finance, and higher education all flourish. Excellent for students and advisors alike.",
    "Mercury/Saturn": "Systematic, patient communication brings rewards. Research, writing, administration, and structured business dealings succeed through sustained effort.",
    "Mercury/Mercury": "Peak intellectual period. Studies, business, writing, trade, and communication all perform at their highest. Decisions made now carry long-term benefit.",
    "Mercury/Ketu": "Analytical detachment and spiritual inquiry deepen. Occult studies may attract; past karma through intellect gently resolves. A time for inner study.",
    "Mercury/Venus": "Artistic communication, music, beauty, and writing flourish. Relationships through intellectual affinity; business in arts or luxury goods can thrive.",
    # ── Ketu Mahadasha ─────────────────────────────────────────────────────────
    "Ketu/Sun":     "Father's karmic lessons come to the fore; ego dissolves gradually. Spiritual authority deepens while material status recedes. Care for eyesight is advised.",
    "Ketu/Moon":    "Deep psychic sensitivity; mother's health may be delicate. Spiritual intuition peaks, but emotional withdrawal from the world is also characteristic.",
    "Ketu/Mars":    "Spiritual warrior energy with sudden events possible. Detachment from property and siblings begins. Moksha-oriented practices yield deep, lasting results.",
    "Ketu/Rahu":    "Karmic axis at full intensity — confusion, possible liberation, and deep past karma surfaces. A profound spiritual crossroads; avoid impulsive material choices.",
    "Ketu/Jupiter": "A spiritual teacher or guide may appear to resolve past-life dharma. Liberation through wisdom is near; detachment from worldly expansion brings grace.",
    "Ketu/Saturn":  "Karmic austerity and material detachment. Service to elders and the downtrodden brings moksha merit. A deeply introverted and spiritually potent period.",
    "Ketu/Mercury": "Analytical spirituality and occult studies deepen. Past karma through the intellect is resolving. Avoid over-intellectualising; trust inner knowing.",
    "Ketu/Ketu":    "Peak Ketu period — maximum spiritual withdrawal and liberation tendencies. Health of lower body and nervous system needs attention. Go inward.",
    "Ketu/Venus":   "Detachment from relationships and sensory pleasures. Spiritual love replaces material desire. Past-life relationship karma is gently but surely resolved.",
    # ── Venus Mahadasha ────────────────────────────────────────────────────────
    "Venus/Sun":    "Authority and comfort align. Government recognition, father's support in artistic or diplomatic fields, and creative leadership are all well aspected.",
    "Venus/Moon":   "Domestic harmony, beauty, and emotional flourishing peak. Motherly blessings and feminine energy are highlighted. A deeply comfortable sub-period.",
    "Venus/Mars":   "Passionate relationships and creative energy surge. Property and romance both advance. Discipline over desires prevents conflicts from arising.",
    "Venus/Rahu":   "Unusual relationships and foreign luxury arise. Material desires intensify through unconventional channels. Guard against excess; ground spiritual practice.",
    "Venus/Jupiter": "Dharmic prosperity and spiritual love unite. Marriage, finance, arts, and spirituality all flourish. Among the most auspicious sub-period combinations.",
    "Venus/Saturn": "Disciplined relationships and delayed but lasting partnerships. Artistic and creative austerity is rewarded. Mature love deepens through tested commitment.",
    "Venus/Mercury": "Artistic communication and intellectual beauty flourish. Music, writing, beauty business, and relationship through shared intellect all thrive.",
    "Venus/Ketu":   "Spiritual love and detachment from material pleasures. Past-life relationship karma resolves peacefully. Creative renunciation brings unexpected inner joy.",
    "Venus/Venus":  "Peak comfort, luxury, and harmony. Relationships, arts, finances, and sensory pleasures all flourish. One of the most pleasant sub-period combinations.",
}

MANGAL_DOSHA_HOUSES = {1, 2, 4, 7, 8, 12}

SIGN_LORDS: dict[str, str] = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

LAGNA_BODY: dict[str, str] = {
    "Aries": "head, brain, and eyes",
    "Taurus": "throat, neck, and face",
    "Gemini": "chest, lungs, shoulders, and arms",
    "Cancer": "chest, stomach, and digestive system",
    "Leo": "heart, spine, and upper back",
    "Virgo": "intestines, digestive system, and nervous system",
    "Libra": "kidneys, lower back, and skin",
    "Scorpio": "reproductive organs, bladder, and colon",
    "Sagittarius": "hips, thighs, and liver",
    "Capricorn": "knees, joints, and bones",
    "Aquarius": "ankles, calves, and circulatory system",
    "Pisces": "feet and lymphatic system",
}

LAGNA_NATURE: dict[str, str] = {
    "Aries": "bold, pioneering, and direct",
    "Taurus": "steady, patient, and comfort-seeking",
    "Gemini": "curious, communicative, and adaptable",
    "Cancer": "intuitive, nurturing, and emotionally perceptive",
    "Leo": "confident, generous, and naturally authoritative",
    "Virgo": "analytical, discerning, and service-minded",
    "Libra": "harmonious, aesthetic, and diplomatic",
    "Scorpio": "intense, perceptive, and inwardly powerful",
    "Sagittarius": "philosophical, expansive, and idealistic",
    "Capricorn": "disciplined, ambitious, and quietly determined",
    "Aquarius": "humanitarian, innovative, and independent",
    "Pisces": "compassionate, imaginative, and spiritually sensitive",
}

MOON_INNER: dict[str, str] = {
    "Aries": "emotionally quick to act and slow to linger on hurt",
    "Taurus": "emotionally stable, deeply loyal, and comfort-oriented",
    "Gemini": "emotionally restless, seeking variety and conversation",
    "Cancer": "emotionally rich, protective, and home-centred",
    "Leo": "emotionally expressive, generous, and pride-conscious",
    "Virgo": "emotionally careful, self-critical, and service-inclined",
    "Libra": "emotionally balanced, harmony-seeking, and relationship-focused",
    "Scorpio": "emotionally intense, private, and deeply feeling",
    "Sagittarius": "emotionally optimistic, freedom-loving, and philosophical",
    "Capricorn": "emotionally disciplined, self-contained, and practically grounded",
    "Aquarius": "emotionally detached yet genuinely humanitarian",
    "Pisces": "emotionally fluid, empathetic, and spiritually attuned",
}

NAK_DEITY_WORSHIP: dict[str, str] = {
    "Ashwini": "Ashwini Kumaras; offer prayers at healing temples on Sundays",
    "Bharani": "Yama (lord of dharma); light a sesame lamp on Saturdays",
    "Krittika": "Agni (fire deity); offer ghee into a sacred fire on Sundays",
    "Rohini": "Brahma; offer white flowers and milk on Mondays",
    "Mrigashira": "Soma (Moon); chant Shiva mantras and offer bilva leaves on Mondays",
    "Ardra": "Rudra-Shiva; recite Rudrashtakam and offer bael on Mondays",
    "Punarvasu": "Aditi; offer yellow flowers to Jupiter on Thursdays",
    "Pushya": "Brihaspati; observe fasts on Thursdays and offer yellow cloth to Saturn on Saturdays",
    "Ashlesha": "Sarpa Devata; offer milk at Naga shrines on Panchami tithis",
    "Magha": "Pitrs (ancestors); perform Pitru Tarpan on Amavasya and Mahalaya",
    "Purva Phalguni": "Bhaga; offer flowers and sweets to Lakshmi on Fridays",
    "Uttara Phalguni": "Aryaman; perform acts of charitable giving on Sundays",
    "Hasta": "Savitar (Sun); offer water to the Sun at dawn daily",
    "Chitra": "Vishwakarma; light incense and chant skill-bestowing mantras on Wednesdays",
    "Swati": "Vayu (wind); light incense and offer blue flowers on Saturdays",
    "Vishakha": "Indra-Agni; chant the Gayatri mantra 108 times on Thursdays",
    "Anuradha": "Mitra; offer lotus flowers and maintain true friendships as sadhana",
    "Jyeshtha": "Indra; chant the Indra Gayatri and perform acts of courage on Thursdays",
    "Mula": "Nirriti; perform Ganesha puja to remove obstacles; visit Kali or Durga temples on Tuesdays",
    "Purva Ashadha": "Apas (water deity); offer water at rivers and pray to Lakshmi on Fridays",
    "Uttara Ashadha": "Vishvadevas; chant Om Namo Narayanaya and offer tulsi on Sundays",
    "Shravana": "Vishnu; recite Vishnu Sahasranama daily; pilgrimage to Tirupati or Vrindavan is especially auspicious",
    "Dhanishta": "Ashta-Vasus; play or listen to devotional music; offer water to the Moon on Mondays",
    "Shatabhisha": "Varuna; offer water and white flowers at water bodies on Saturdays",
    "Purva Bhadrapada": "Ajaikapada-Rudra; light a ghee lamp and chant Rudram on Mondays",
    "Uttara Bhadrapada": "Ahirbudhnya; offer sesame and water to ancestors; Saturn mantra on Saturdays",
    "Revati": "Pushan (guide of souls); offer yellow flowers and pray for journeys to be protected",
}


def generate_predictions(chart: dict) -> list[tuple[str, str]]:
    """Generate chart-specific predictions for each life area."""
    lagna = chart["ascendant"]["sign"]
    rashi = chart["rashi"]
    sun_sign = chart["sun_sign"]
    nak = chart["nakshatra"]
    pada = chart["nakshatra_pada"]
    nak_det = chart.get("nakshatra_details", {})
    nak_lord = nak_det.get("lord", "")
    nak_deity = nak_det.get("deity", "")

    planets = {p["planet"]: p for p in chart["planets"]}
    dasha = chart.get("vimshottari_dasha", {})
    current_md = dasha.get("current_mahadasha", {}) or {}
    current_ad = dasha.get("current_antardasha", {}) or {}
    md_lord = current_md.get("lord", "")
    ad_lord = current_ad.get("lord", "")

    lagna_nature = LAGNA_NATURE.get(lagna, "complex and multi-faceted")
    moon_inner = MOON_INNER.get(rashi, "emotionally nuanced")
    lagna_lord = SIGN_LORDS.get(lagna, "")
    lagna_lord_house = planets.get(lagna_lord, {}).get("house", 0)
    body_area = LAGNA_BODY.get(lagna, "the core body systems")

    tenth_sign_idx = (SIGNS.index(lagna) + 9) % 12
    tenth_lord = SIGN_LORDS[SIGNS[tenth_sign_idx]]
    tenth_lord_data = planets.get(tenth_lord, {})
    tenth_lord_house = tenth_lord_data.get("house", 0)
    tenth_lord_sign = tenth_lord_data.get("sign", "")

    second_sign_idx = (SIGNS.index(lagna) + 1) % 12
    second_lord = SIGN_LORDS[SIGNS[second_sign_idx]]
    second_lord_data = planets.get(second_lord, {})
    second_lord_house = second_lord_data.get("house", 0)

    eleventh_sign_idx = (SIGNS.index(lagna) + 10) % 12
    eleventh_lord = SIGN_LORDS[SIGNS[eleventh_sign_idx]]
    eleventh_lord_data = planets.get(eleventh_lord, {})
    eleventh_lord_house = eleventh_lord_data.get("house", 0)

    seventh_sign_idx = (SIGNS.index(lagna) + 6) % 12
    seventh_lord = SIGN_LORDS[SIGNS[seventh_sign_idx]]
    seventh_lord_data = planets.get(seventh_lord, {})
    seventh_lord_house = seventh_lord_data.get("house", 0)
    seventh_lord_sign = seventh_lord_data.get("sign", "")

    moon_house = planets.get("Moon", {}).get("house", 0)
    mars_house = planets.get("Mars", {}).get("house", 0)
    mars_sign = planets.get("Mars", {}).get("sign", "")
    jupiter_house = planets.get("Jupiter", {}).get("house", 0)
    jupiter_sign = planets.get("Jupiter", {}).get("sign", "")
    venus_house = planets.get("Venus", {}).get("house", 0)
    venus_sign = planets.get("Venus", {}).get("sign", "")
    saturn_house = planets.get("Saturn", {}).get("house", 0)
    saturn_sign = planets.get("Saturn", {}).get("sign", "")
    sun_house = planets.get("Sun", {}).get("house", 0)
    mercury_house = planets.get("Mercury", {}).get("house", 0)
    rahu_house = planets.get("Rahu", {}).get("house", 0)
    rahu_sign = planets.get("Rahu", {}).get("sign", "")
    ketu_house = planets.get("Ketu", {}).get("house", 0)

    # Count planets per house
    house_count: dict[int, list[str]] = {}
    for p in chart["planets"]:
        h = p["house"]
        house_count.setdefault(h, []).append(p["planet"])

    # ── PERSONALITY ──────────────────────────────────────────────────────────
    rahu_lagna_note = (
        f" Rahu's presence in the Lagna adds an unusual, magnetic quality to your persona — "
        f"others sense something distinctive about you, and your life path tends to deviate "
        f"interestingly from convention."
        if rahu_house == 1 else ""
    )
    lagna_lord_note = (
        f" Your Lagna lord {lagna_lord} is placed in House {lagna_lord_house}, "
        f"which colours the personality with themes of {'self-assertion and drive' if lagna_lord_house in {1,3,6,10} else 'relationship and receptivity' if lagna_lord_house in {4,7} else 'introspection and transformation' if lagna_lord_house in {8,12} else 'wisdom and fortune'}."
    )
    personality_text = (
        f"With {lagna} rising, you are {lagna_nature} by outward temperament. "
        f"Internally, the Moon in {rashi} makes you {moon_inner}. "
        f"This polarity — {lagna} presence meeting a {rashi} inner world — is the central creative tension of your character: "
        f"what the world sees and what you feel are distinct, and learning to bridge them with honesty is a lifelong gift."
        f"{rahu_lagna_note}"
        f"{lagna_lord_note} "
        f"Your Janma Nakshatra, {nak} Pada {pada}, ruled by {nak_lord} and presided over by {nak_deity}, "
        f"imbues your soul with the quality of deep listening, perseverance, and alignment with universal order — "
        f"qualities that become your greatest strengths when consciously developed."
    )

    # ── CAREER ───────────────────────────────────────────────────────────────
    h3_planets = house_count.get(3, [])
    h3_note = (
        f" Notably, {', '.join(h3_planets[:-1])} and {h3_planets[-1]} all occupy the 3rd house of skills and communication"
        if len(h3_planets) >= 3
        else f" {h3_planets[0]} in the 3rd house strengthens communication and creative output"
        if h3_planets else ""
    )
    tenth_lord_note = (
        f"The 10th house lord {tenth_lord} is placed in House {tenth_lord_house} ({tenth_lord_sign}), "
        f"indicating that career flourishes through "
        f"{'service, competition, health, or legal domains' if tenth_lord_house == 6 else 'public dealings, partnerships, and diplomacy' if tenth_lord_house == 7 else 'communication, media, siblings, or short ventures' if tenth_lord_house == 3 else 'personal initiative and leadership' if tenth_lord_house == 1 else 'home, property, or government work' if tenth_lord_house == 4 else 'dharmic pursuits, teaching, or foreign work' if tenth_lord_house == 9 else 'authority and public recognition' if tenth_lord_house == 10 else 'income, networks, and business gains' if tenth_lord_house == 11 else 'disciplined, sustained effort'}."
    )
    dasha_career = (
        f" The current {md_lord} Mahadasha / {ad_lord} Antardasha supports expansion through "
        f"{'advisory, teaching, or spiritual domains' if md_lord == 'Jupiter' else 'unconventional, foreign, or technology-related fields' if md_lord == 'Rahu' else 'disciplined service and structured roles' if md_lord == 'Saturn' else 'communication and intellectual work' if md_lord == 'Mercury' else 'creative and relationship-based work' if md_lord == 'Venus' else 'leadership and authoritative positions' if md_lord == 'Sun' else 'property, public, or home-based work' if md_lord == 'Moon' else 'competitive action and courage' if md_lord == 'Mars' else 'spiritual and non-material pursuits'}."
        if md_lord else ""
    )
    career_text = (
        f"{tenth_lord_note}"
        f"{h3_note}. "
        f"Fields that align naturally with this chart include writing, advisory work, teaching, "
        f"communication-driven business, healthcare or legal services, and roles involving analysis or precision. "
        f"Progress comes not through shortcuts but through the sustained development of a genuine skill — "
        f"this chart rewards the specialist who deepens mastery over time."
        f"{dasha_career}"
    )

    # ── FINANCE ──────────────────────────────────────────────────────────────
    wealth_notes = []
    if second_lord_house in {1, 2, 4, 5, 9, 10, 11}:
        wealth_notes.append(f"the 2nd lord {second_lord} in House {second_lord_house} supports stable wealth accumulation")
    if eleventh_lord_house in {1, 2, 5, 9, 10, 11}:
        wealth_notes.append(f"the 11th lord {eleventh_lord} in House {eleventh_lord_house} aids consistent income gains")
    if sun_house == 4 or mercury_house == 4:
        wealth_notes.append("Sun and Mercury in the 4th house favour property ownership and real estate")
    if venus_house in {1, 2, 5, 7, 9, 11}:
        wealth_notes.append(f"Venus in House {venus_house} brings income through creativity, arts, or relationships")
    wealth_str = "; ".join(wealth_notes) if wealth_notes else "the chart supports patient, ethical accumulation"
    finance_text = (
        f"This chart's financial strength lies in earned income through skill and persistent effort rather than speculation. "
        f"Key indicators: {wealth_str}. "
        f"Property, real estate, and long-term investments are particularly well-aspected for this Lagna. "
        f"Financial decisions made during periods of calm, after thorough review, consistently yield better outcomes "
        f"than those made under emotional or time pressure. "
        f"Avoiding surety bonds, informal lending, and high-risk ventures protects the chart's natural wealth potential."
    )

    # ── FAMILY AND RELATIONSHIPS ──────────────────────────────────────────────
    ketu_7th = ketu_house == 7
    moon_7th = moon_house == 7
    seventh_lord_note = (
        f"The 7th lord {seventh_lord} in House {seventh_lord_house} ({seventh_lord_sign}) suggests "
        f"that partnership deepens through "
        f"{'shared communication, sibling connections, or short journeys' if seventh_lord_house == 3 else 'home, family, and emotional security' if seventh_lord_house == 4 else 'mutual service, health awareness, and practical cooperation' if seventh_lord_house == 6 else 'shared dharmic values, wisdom, and spiritual aspiration' if seventh_lord_house == 9 else 'professional collaboration and public life' if seventh_lord_house == 10 else 'social networks, income, and common ambitions' if seventh_lord_house == 11 else 'personal presence and self-expression' if seventh_lord_house == 1 else 'shared resources and transformative experiences'}."
    )
    ketu_note = (
        f" Ketu in the 7th house indicates a deep past-life karmic bond with the spouse — "
        f"the relationship carries a quality of soul-recognition and spiritual purpose beyond ordinary partnership. "
        f"Patience and non-attachment are the keys to its flourishing."
        if ketu_7th else ""
    )
    moon_note = (
        f" Moon in the 7th brings the emotional world into the sphere of partnership — "
        f"relationships significantly shape the inner life, and the spouse or close partner "
        f"tends to be a mirror for emotional growth."
        if moon_7th else ""
    )
    family_text = (
        f"{seventh_lord_note}"
        f"{moon_note}"
        f"{ketu_note} "
        f"In family life, the Shravana nakshatra's core quality — deep listening and loyalty — "
        f"is the greatest relationship asset. Relationships flourish when there is consistent emotional "
        f"availability, clear communication of expectations, and shared spiritual or ethical values. "
        f"The 4th house indicators suggest the home environment is important to wellbeing; "
        f"investing in a stable, peaceful domestic space yields significant emotional returns."
    )

    # ── HEALTH ───────────────────────────────────────────────────────────────
    mars_6th = mars_house == 6
    rahu_1st = rahu_house == 1
    mars_sign_note = f" The sign {mars_sign} rules the hips, thighs, and sciatic nerve — these areas benefit from regular stretching and warmth." if mars_sign == "Sagittarius" else ""
    rahu_note = (
        f" Rahu in the Lagna can create nervous system sensitivity, tendency toward anxiety, "
        f"or unusual symptoms that are best addressed holistically alongside standard medical care."
        if rahu_1st else ""
    )
    mars_6_note = (
        f" Mars in the 6th house is a powerful indicator of strong immunity and the capacity "
        f"to recover well from illness. However, it also creates a tendency to push the body hard — "
        f"adequate rest and recovery time must be consciously honoured."
        if mars_6th else ""
    )
    health_text = (
        f"Vedic astrology identifies health tendencies, not diagnoses — always consult qualified medical professionals for health matters. "
        f"With {lagna} Lagna, special care is indicated for {body_area}. "
        f"Regular meals, adequate sleep, and digestive health are foundational practices for this Lagna type. "
        f"{mars_6_note}"
        f"{rahu_note}"
        f"{mars_sign_note} "
        f"Breath-based practices (pranayama), daily walks, and moderate exercise suit this constitution well. "
        f"Mental and emotional health are closely linked to physical health for {lagna} Lagna — "
        f"unresolved relationship stress or chronic worry tends to manifest first in the digestive system and chest."
    )

    # ── SPIRITUAL GUIDANCE ───────────────────────────────────────────────────
    worship = NAK_DEITY_WORSHIP.get(nak, f"offer prayers to {nak_deity} regularly")
    lagna_worship = {
        "Cancer": "Shiva and Parvati; Monday fasts and offering milk to a Shivalinga are deeply beneficial",
        "Leo": "Surya Narayana; daily Surya Namaskar and offering water to the Sun at dawn",
        "Virgo": "Vishnu and Saraswati; recitation of Vishnu Sahasranama and service through healing",
        "Libra": "Lakshmi; Friday fasts, offering white flowers, and acts of charitable giving",
        "Scorpio": "Kali and Ganesha; Tuesday prayers, removal of obstacles as spiritual discipline",
        "Sagittarius": "Brihaspati and Dakshinamurthy; Guru puja and pursuit of authentic knowledge",
        "Capricorn": "Shani and Hanuman; Saturday fasts, Hanuman Chalisa, and service to the elderly",
        "Aquarius": "Shani; humanitarian service as the highest form of worship for this Lagna",
        "Pisces": "Vishnu and Gurus; pilgrimage to Vishnu temples and study of sacred texts",
        "Aries": "Subrahmanya and Hanuman; Tuesdays are especially auspicious for prayer",
        "Taurus": "Lakshmi and Shiva; Friday and Monday observances bring grace",
        "Gemini": "Saraswati and Vishnu; recitation of sacred names and pursuit of genuine knowledge",
    }.get(lagna, "the presiding deity of your Lagna")
    md_spiritual = (
        f" The current {md_lord} Mahadasha is "
        f"{'an ideal time to find a genuine spiritual teacher (guru) and deepen formal practice' if md_lord == 'Jupiter' else 'a time when unconventional spiritual paths may attract — discern carefully before committing to a teacher or practice' if md_lord == 'Rahu' else 'a period of karmic ripening; service and austerity are the most rewarding spiritual activities' if md_lord == 'Saturn' else 'a period of intellectual spiritual inquiry — study of scripture is especially fruitful' if md_lord == 'Mercury' else 'a time when devotional practices, mantra, and beauty in worship bring the deepest nourishment' if md_lord == 'Venus' else 'a time for soul-searching and spiritual withdrawal from worldly ambition' if md_lord == 'Ketu' else 'a period when spiritual authority and clarity of purpose are both accessible and important'}."
        if md_lord else ""
    )
    spiritual_text = (
        f"The Janma Nakshatra {nak} prescribes specific worship: {worship}. "
        f"For {lagna} Lagna, devotion to {lagna_worship}. "
        f"A sattvic daily routine — rising before sunrise, a brief meditation or prayer, "
        f"conscious eating without distraction, and one act of selfless service per day — "
        f"aligns this chart's energy with its highest expression. "
        f"The Kaal Sarp Dosha in this chart makes consistent spiritual practice especially powerful: "
        f"the same karmic intensity that creates challenges becomes the fuel for rapid spiritual growth "
        f"when channelled through sincere, daily practice."
        f"{md_spiritual}"
    )

    return [
        ("Personality", personality_text),
        ("Career", career_text),
        ("Finance", finance_text),
        ("Family and Relationships", family_text),
        ("Health Tendencies", health_text),
        ("Spiritual Guidance", spiritual_text),
    ]

SWISS_PLANETS = []
if swe is not None:
    SWISS_PLANETS = [
        ("Sun", swe.SUN),
        ("Moon", swe.MOON),
        ("Mars", swe.MARS),
        ("Mercury", swe.MERCURY),
        ("Jupiter", swe.JUPITER),
        ("Venus", swe.VENUS),
        ("Saturn", swe.SATURN),
        ("Rahu", swe.MEAN_NODE),
    ]


@dataclass(frozen=True)
class BirthDetails:
    name: str
    gender: str
    birth_date: date
    birth_time: time
    place: str
    latitude: float
    longitude: float
    timezone_offset: float


def default_birth_details() -> BirthDetails:
    return BirthDetails(
        name="Vinay",
        gender="Male",
        birth_date=date(1980, 11, 14),
        birth_time=time(22, 24),
        place="Jamshedpur, India",
        latitude=22 + 48 / 60,
        longitude=86 + 10 / 60,
        timezone_offset=5.5,
    )


def validate_birth_details(details: BirthDetails) -> None:
    if not details.name.strip():
        raise ValueError("Name is required.")
    if details.birth_date > date.today():
        raise ValueError("Birth date cannot be in the future.")
    if not -90 <= details.latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90.")
    if not -180 <= details.longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180.")
    if not -12 <= details.timezone_offset <= 14:
        raise ValueError("Timezone offset must be between -12 and +14.")


def calculate_chart(details: BirthDetails) -> dict:
    validate_birth_details(details)
    if swe is not None:
        return _calculate_with_swiss(details)
    if astronomy is not None:
        return _calculate_with_astronomy_engine(details)
    raise RuntimeError("Install pyswisseph or astronomy-engine to calculate the chart.")


def _calculate_with_swiss(details: BirthDetails) -> dict:
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    local_dt = datetime.combine(details.birth_date, details.birth_time)
    utc_dt = local_dt - timedelta(hours=details.timezone_offset)
    jd_ut = julian_day(utc_dt)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    positions: dict[str, float] = {}
    for name, planet_id in SWISS_PLANETS:
        positions[name] = swe.calc_ut(jd_ut, planet_id, flags)[0][0] % 360
    positions["Ketu"] = (positions["Rahu"] + 180) % 360

    cusps, ascmc = swe.houses_ex(
        jd_ut,
        details.latitude,
        details.longitude,
        b"P",
        swe.FLG_SIDEREAL,
    )
    ascendant_longitude = ascmc[0] % 360
    ascendant_sign_index = sign_index(ascendant_longitude)

    planet_rows = []
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        longitude = positions[name]
        p_sign_index = sign_index(longitude)
        planet_rows.append(
            {
                "planet": name,
                "longitude": longitude,
                "sign": SIGNS[p_sign_index],
                "degree": degree_in_sign(longitude),
                "house": ((p_sign_index - ascendant_sign_index) % 12) + 1,
                "nakshatra": nakshatra_name(longitude),
                "pada": nakshatra_pada(longitude),
            }
        )

    return _chart_payload(
        details=details,
        engine="Swiss Ephemeris",
        jd_ut=jd_ut,
        local_dt=local_dt,
        utc_dt=utc_dt,
        ascendant_longitude=ascendant_longitude,
        positions=positions,
    )


def _calculate_with_astronomy_engine(details: BirthDetails) -> dict:
    local_dt = datetime.combine(details.birth_date, details.birth_time)
    utc_dt = local_dt - timedelta(hours=details.timezone_offset)
    jd_ut = julian_day(utc_dt)
    astro_time = astronomy.Time(utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))
    ayanamsa = lahiri_ayanamsa(jd_ut)

    body_map = {
        "Sun": astronomy.Body.Sun,
        "Mars": astronomy.Body.Mars,
        "Mercury": astronomy.Body.Mercury,
        "Jupiter": astronomy.Body.Jupiter,
        "Venus": astronomy.Body.Venus,
        "Saturn": astronomy.Body.Saturn,
    }
    positions = {"Moon": (astronomy.EclipticGeoMoon(astro_time).lon - ayanamsa) % 360}
    for name, body in body_map.items():
        tropical = astronomy.Ecliptic(astronomy.GeoVector(body, astro_time, False)).elon
        positions[name] = (tropical - ayanamsa) % 360

    positions["Rahu"] = (mean_lunar_node(jd_ut) - ayanamsa) % 360
    positions["Ketu"] = (positions["Rahu"] + 180) % 360
    ascendant_longitude = (tropical_ascendant(astro_time, details.latitude, details.longitude) - ayanamsa) % 360

    return _chart_payload(
        details=details,
        engine="Astronomy Engine fallback",
        jd_ut=jd_ut,
        local_dt=local_dt,
        utc_dt=utc_dt,
        ascendant_longitude=ascendant_longitude,
        positions=positions,
    )


def _chart_payload(
    *,
    details: BirthDetails,
    engine: str,
    jd_ut: float,
    local_dt: datetime,
    utc_dt: datetime,
    ascendant_longitude: float,
    positions: dict[str, float],
) -> dict:
    ascendant_sign_index = sign_index(ascendant_longitude)

    planet_rows = []
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        longitude = positions[name]
        p_sign_index = sign_index(longitude)
        planet_rows.append(
            {
                "planet": name,
                "longitude": longitude,
                "sign": SIGNS[p_sign_index],
                "degree": degree_in_sign(longitude),
                "house": ((p_sign_index - ascendant_sign_index) % 12) + 1,
                "nakshatra": nakshatra_name(longitude),
                "pada": nakshatra_pada(longitude),
            }
        )

    moon_longitude = positions["Moon"]
    sun_longitude = positions["Sun"]

    nak_name = nakshatra_name(moon_longitude)
    payload = {
        "birth": details,
        "calculation_basis": "Nirayana Vedic chart using Lahiri/Chitrapaksha ayanamsa",
        "calculation_engine": engine,
        "julian_day_ut": jd_ut,
        "local_datetime": local_dt,
        "utc_datetime": utc_dt.replace(tzinfo=timezone.utc),
        "ascendant": {
            "longitude": ascendant_longitude,
            "sign": SIGNS[ascendant_sign_index],
            "degree": degree_in_sign(ascendant_longitude),
        },
        "rashi": SIGNS[sign_index(moon_longitude)],
        "sun_sign": SIGNS[sign_index(sun_longitude)],
        "nakshatra": nak_name,
        "nakshatra_pada": nakshatra_pada(moon_longitude),
        "nakshatra_details": NAKSHATRA_DETAILS.get(nak_name, {}),
        "panchang": calculate_panchang(sun_longitude, moon_longitude),
        "planets": planet_rows,
        "vimshottari_dasha": calculate_vimshottari_dasha(moon_longitude, details.birth_date),
        "doshas": detect_doshas(planet_rows, ascendant_sign_index),
        "predictions": [],  # filled below after dict is complete
    }
    payload["predictions"] = generate_predictions(payload)
    return payload


def calculate_vimshottari_dasha(moon_longitude: float, birth_date: date) -> dict:
    """Vimshottari Dasha per BPHS — standard 120-year cycle."""
    nak_index = floor((moon_longitude % 360) / (360 / 27))
    nak_lord = NAKSHATRA_LORD_MAP[nak_index]

    nak_span = 360 / 27
    nak_start = nak_index * nak_span
    fraction_elapsed = ((moon_longitude % 360) - nak_start) / nak_span

    # Balance of first dasha remaining at birth
    first_dasha_years = DASHA_YEARS[nak_lord]
    balance_years = first_dasha_years * (1 - fraction_elapsed)

    start_index = DASHA_ORDER.index(nak_lord)
    mahadashas = []
    cursor = birth_date

    for i in range(9):
        lord = DASHA_ORDER[(start_index + i) % 9]
        years = balance_years if i == 0 else DASHA_YEARS[lord]
        days = round(years * 365.25)
        end = cursor + timedelta(days=days)
        mahadashas.append({"lord": lord, "start": cursor, "end": end, "years": round(years, 2)})
        cursor = end

    today = date.today()
    current_md = next((d for d in mahadashas if d["start"] <= today < d["end"]), None)

    # Antardashas within current Mahadasha
    antardashas = []
    if current_md:
        md_lord = current_md["lord"]
        md_start_idx = DASHA_ORDER.index(md_lord)
        ad_cursor = current_md["start"]
        for j in range(9):
            ad_lord = DASHA_ORDER[(md_start_idx + j) % 9]
            ad_years = (current_md["years"] * DASHA_YEARS[ad_lord]) / 120
            ad_days = round(ad_years * 365.25)
            ad_end = ad_cursor + timedelta(days=ad_days)
            antardashas.append({"lord": ad_lord, "start": ad_cursor, "end": ad_end})
            ad_cursor = ad_end

    # Find currently active antardasha and its effect text
    today = date.today()
    current_ad = next((ad for ad in antardashas if ad["start"] <= today < ad["end"]), None)
    md_ad_effect = ""
    if current_md and current_ad:
        key = f"{current_md['lord']}/{current_ad['lord']}"
        md_ad_effect = MD_AD_EFFECTS.get(key, "")

    return {
        "mahadashas": mahadashas,
        "current_mahadasha": current_md,
        "antardashas": antardashas,
        "current_antardasha": current_ad,
        "md_ad_effect": md_ad_effect,
    }


def detect_doshas(planets: list, ascendant_sign_index: int) -> list:
    """Detect standard Vedic doshas: Mangal Dosha and Kaal Sarp Dosha."""
    pos = {p["planet"]: p for p in planets}
    doshas = []

    # ── Mangal Dosha (Kuja Dosha) ─────────────────────────────────────────────
    mars = pos.get("Mars", {})
    moon = pos.get("Moon", {})
    venus = pos.get("Venus", {})

    mars_sign_idx = sign_index(mars.get("longitude", 0))
    moon_sign_idx = sign_index(moon.get("longitude", 0))
    venus_sign_idx = sign_index(venus.get("longitude", 0))

    house_from_lagna = ((mars_sign_idx - ascendant_sign_index) % 12) + 1
    house_from_moon  = ((mars_sign_idx - moon_sign_idx) % 12) + 1
    house_from_venus = ((mars_sign_idx - venus_sign_idx) % 12) + 1

    m_lagna  = house_from_lagna  in MANGAL_DOSHA_HOUSES
    m_moon   = house_from_moon   in MANGAL_DOSHA_HOUSES
    m_venus  = house_from_venus  in MANGAL_DOSHA_HOUSES

    if m_lagna or m_moon or m_venus:
        sources = []
        if m_lagna:  sources.append(f"House {house_from_lagna} from Lagna")
        if m_moon:   sources.append(f"House {house_from_moon} from Moon")
        if m_venus:  sources.append(f"House {house_from_venus} from Venus")
        severity = "Full" if m_lagna else "Partial"
        doshas.append({
            "name": "Mangal Dosha (Kuja Dosha)",
            "present": True,
            "severity": severity,
            "detail": f"Mars occupies: {'; '.join(sources)}",
            "effect": (
                "Mangal Dosha can introduce intensity, impatience, and conflict in partnerships and domestic life. "
                "In a Full Dosha (Mars from Lagna), the temperament itself is affected. "
                "In a Partial Dosha (from Moon or Venus), the emotional and relational spheres are primarily coloured by Martian energy. "
                "This is not a curse — it indicates a soul that learns through courage and confrontation rather than passivity."
            ),
            "remedy": (
                "Recite the Mangal Beej mantra (Om Kraam Kreem Kraum Sah Bhaumaya Namah) 108 times on Tuesdays. "
                "Offer red flowers and lentils at a Hanuman or Subramanya temple on Tuesdays. "
                "Fasting on Tuesdays and donating red items (lentils, coral) to those in need is also traditional."
            ),
        })
    else:
        doshas.append({
            "name": "Mangal Dosha (Kuja Dosha)",
            "present": False,
            "severity": "None",
            "detail": (
                f"Mars is in House {house_from_lagna} from Lagna, "
                f"House {house_from_moon} from Moon, "
                f"House {house_from_venus} from Venus — none are dosha-forming positions."
            ),
            "effect": "",
            "remedy": "",
        })

    # ── Kaal Sarp Dosha ───────────────────────────────────────────────────────
    rahu = pos.get("Rahu", {})
    ketu = pos.get("Ketu", {})
    rahu_lon = rahu.get("longitude", 0)
    ketu_lon  = ketu.get("longitude", 0)

    def _in_arc(lon: float, start: float, end: float) -> bool:
        """True if lon lies in the arc start → end going forward (increasing longitude)."""
        lon  = lon  % 360
        start = start % 360
        end   = end   % 360
        if start < end:
            return start < lon < end
        return lon > start or lon < end

    grahas = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    lons = [pos[g]["longitude"] for g in grahas if g in pos]

    all_rahu_to_ketu  = all(_in_arc(lon, rahu_lon, ketu_lon)  for lon in lons)
    all_ketu_to_rahu  = all(_in_arc(lon, ketu_lon, rahu_lon)  for lon in lons)

    if all_rahu_to_ketu or all_ketu_to_rahu:
        rahu_sign = rahu.get("sign", "")
        ketu_sign = ketu.get("sign", "")
        doshas.append({
            "name": "Kaal Sarp Dosha",
            "present": True,
            "severity": "Full",
            "detail": (
                f"All seven planets are hemmed between Rahu ({rahu_sign}) and Ketu ({ketu_sign}). "
                f"This is a {'Rahu-to-Ketu' if all_rahu_to_ketu else 'Ketu-to-Rahu'} (Anuloma) pattern."
            ),
            "effect": (
                "Kaal Sarp Dosha signifies that the soul carries intense karmic momentum from past lives. "
                "Life may feel like events are 'destined' or difficult to deflect — recurring patterns in career, "
                "relationships, or health are common. However, this dosha also intensifies focus and, when worked with "
                "consciously, can produce extraordinary spiritual and material achievement. "
                "Rahu in Cancer suggests that past-life desires relate to emotional security and home."
            ),
            "remedy": (
                "Perform Kaal Sarp Dosha puja at Trimbakeshwar (Nashik), Ujjain Mahakaleshwar, or Kalahasti — "
                "these are the principal temples recognised for this purpose in the Vedic tradition. "
                "Chanting the Maha Mrityunjaya mantra 108 times daily, observing Nag Panchami fasts, "
                "and offering milk to a Shivalinga on Mondays are traditional remedies."
            ),
        })
    else:
        doshas.append({
            "name": "Kaal Sarp Dosha",
            "present": False,
            "severity": "None",
            "detail": "Planets are distributed on both sides of the Rahu-Ketu axis. No Kaal Sarp Dosha is present.",
            "effect": "",
            "remedy": "",
        })

    return doshas


def calculate_panchang(sun_longitude: float, moon_longitude: float) -> dict[str, str]:
    moon_sun_diff = (moon_longitude - sun_longitude) % 360
    tithi_index = min(29, floor(moon_sun_diff / 12))
    yoga_index = floor(((sun_longitude + moon_longitude) % 360) / (360 / 27))
    karana_value = floor(moon_sun_diff / 6)

    if karana_value == 0:
        karana = "Kimstughna"
    elif karana_value >= 57:
        karana = ["Shakuni", "Chatushpada", "Naga"][min(karana_value - 57, 2)]
    else:
        karana = KARANAS[(karana_value - 1) % 7]

    return {
        "tithi": TITHIS[tithi_index],
        "paksha": "Shukla" if tithi_index < 15 else "Krishna",
        "yoga": YOGAS[yoga_index],
        "karana": karana,
    }


def sign_index(longitude: float) -> int:
    return floor((longitude % 360) / 30)


def julian_day(utc_dt: datetime) -> float:
    if swe is not None:
        return swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600,
        )

    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day + (utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600) / 24
    if month <= 2:
        year -= 1
        month += 12
    a = floor(year / 100)
    b = 2 - a + floor(a / 4)
    return floor(365.25 * (year + 4716)) + floor(30.6001 * (month + 1)) + day + b - 1524.5


def lahiri_ayanamsa(jd_ut: float) -> float:
    # Common Lahiri approximation, close enough for local demo fallback output.
    t = (jd_ut - 2415020.0) / 36525
    return (22.460148 + 1.396042 * t + 0.000308 * t * t) % 360


def mean_lunar_node(jd_ut: float) -> float:
    t = (jd_ut - 2451545.0) / 36525
    return (125.04452 - 1934.136261 * t + 0.0020708 * t * t + (t * t * t) / 450000) % 360


def tropical_ascendant(astro_time, latitude: float, longitude: float) -> float:
    sidereal_degrees = (astronomy.SiderealTime(astro_time) * 15 + longitude) % 360
    theta = radians(sidereal_degrees)
    phi = radians(latitude)
    epsilon = radians(23.4392911)
    return (
        atan2(
            cos(theta),
            -(sin(theta) * cos(epsilon) + tan(phi) * sin(epsilon)),
        )
        * 180
        / 3.141592653589793
    ) % 360


def degree_in_sign(longitude: float) -> str:
    value = longitude % 30
    degrees = floor(value)
    minutes_float = (value - degrees) * 60
    minutes = floor(minutes_float)
    seconds = round((minutes_float - minutes) * 60)
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1
    return f"{degrees:02d}deg {minutes:02d}' {seconds:02d}\""


def nakshatra_name(longitude: float) -> str:
    return NAKSHATRAS[floor((longitude % 360) / (360 / 27))]


def nakshatra_pada(longitude: float) -> int:
    return floor(((longitude % (360 / 27)) / (360 / 108))) + 1
