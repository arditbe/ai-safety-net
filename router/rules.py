"""Routing patterns, grouped by category so the clinician can review them.

Patterns run on normalized text (lowercase, no accents, straight quotes),
so write them that way: "nauseeux", not "Nauséeux".
"""

# Urgent list from the brief. Patient also gets 911 / 988 guidance right away.
URGENT_SYMPTOMS = {
    "chest pain": [
        r"\bchest\b.{0,20}\b(pain|hurts?|hurting|tight(ness)?|pressure|ache|aching)\b",
        r"\b(pain|pressure|tightness)\b.{0,15}\bchest\b",
        r"\b(douleurs?|mal) (a la |dans la )?(poitrine|thoracique)",
        r"\bdolor (de|en el) pecho\b",
    ],
    "trouble breathing": [
        r"\b(trouble|difficulty|problems?|struggling|hard time) breathing\b",
        r"\b(can'?t|cannot|can not|unable to|struggling to|hard to) (breathe|breath|catch my breath)\b",
        r"\bshort(ness)? of breath\b",
        r"\bout of breath\b",
        r"\bwheez",
        r"\b(du mal a|n'arrive pas a|ne peux pas) respirer\b",
        r"\bno puedo respirar\b",
    ],
    "fainting": [
        r"\bfaint(ed|ing|ness)?\b",
        r"\bpass(ed|ing)? out\b",
        r"\bblack(ed|ing)? out\b",
        r"\b(lost consciousness|unconscious)\b",
        r"\bevanoui",
        r"\bdesmay",
    ],
    "severe or constant stomach pain": [
        r"\b(severe|constant|unbearable|excruciating|intense|worst|terrible|really bad|very bad|sharp)\b.{0,25}\b(stomach|abdominal|abdomen|belly|tummy)\b",
        r"\b(stomach|abdominal|abdomen|belly|tummy)\b.{0,25}\b(pain|ache|hurts?|cramps?)\b.{0,40}\b(won'?t|will not|doesn'?t|does not|not) (stop|go away|ease)\b",
        r"\b(stomach|abdominal|belly|tummy) (pain|ache|hurts?)\b.{0,20}\b(all day|for (hours|days)|constantly|non-?stop)\b",
    ],
    "vomiting that will not stop": [
        r"\b(throwing up|vomit\w*|being sick|puking)\b.{0,40}\b(all day|all night|won'?t stop|will not stop|can'?t stop|non-?stop|for (hours|days)|constantly|since (yesterday|last night))\b",
        r"\b(can'?t|cannot|unable to|not able to) keep (anything|water|food|fluids|liquids|it) down\b",
        r"\bkeep (throwing up|vomiting)\b",
    ],
    "allergic reaction": [
        r"\b(swollen|swelling|swells?|puffy)\b.{0,25}\b(face|throat|lips?|tongue|eyes?|eyelids?|mouth)\b",
        r"\b(face|throat|lips?|tongue|mouth)\b.{0,20}\b(swollen|swelling|swelled|puff(y|ing) up)\b",
        r"\bthroat\b.{0,15}\b(closing|tight|tightening)\b",
        r"\banaphyla",
        r"\ballergic reaction\b",
        r"\bhives\b",
    ],
    "thoughts of self-harm": [
        r"\b(kill|hurt|harm|cut|injure) myself\b",
        r"\bsuicid",
        r"\bself[- ]?harm",
        r"\bend (it all|my life|things)\b",
        r"\b(want to|wanna|going to|gonna) die\b",
        r"\b(don'?t|do not) want to (live|be alive|be here|wake up)\b",
        r"\bbetter off (dead|without me)\b",
        r"\b(what'?s|whats|what is) the point( of| in)? (anything|living|life|it all|going on|trying)\b",
        r"\bno (reason|point) (to|in) (live|living|go on|going on)\b",
        r"\bnot worth living\b",
        r"\b(me suicider|en finir)\b",
        r"\b(quiero morir|no quiero vivir)\b",
    ],
}

# Not emergencies, but only a clinician answers these.
CLINICIAN_ONLY = {
    "pregnancy": [
        r"\bpregnan",
        r"\bconceiv",
        r"\bmissed (my |a )?period\b",
        r"\bperiod is late\b",
        r"\b(enceinte|grossesse|embarazada|embarazo)\b",
    ],
    "dose change": [
        r"\b(double|triple|increase|decrease|reduce|lower|raise|change|adjust|skip|stop|split|halve|cut)\w*\b.{0,20}\b(dose|doses|dosage|dosing|injection|shot)\b",
        r"\b(go|move|step|bump|going|moving|stepping) up\b.{0,20}\b(dose|dosage|dosing)\b",
        r"\b(dose|dosage)\b.{0,15}\b(too (high|low|strong|weak)|higher|lower|bigger|smaller)\b",
        r"\b(next|higher|lower|bigger|smaller|max|maximum|extra|double|another) (dose|dosage|injection|shot)\b",
        r"\btak(e|ing) (two|2|both|double|extra|another|more)\b",
        r"\b(missed|forgot|forgotten|skipped) (to take )?(my |a |the |this week'?s |last week'?s )?(dose|injection|shot|medication|meds)\b",
        r"\bstop(ped|ping)? (taking |using )?(my |the )?(medication|meds|treatment|injections?|pen)\b",
        r"\b(more|less) (of (the|my) )?(medication|meds|medicine)\b",
        r"\b(augmenter|doubler|changer) (la |ma )?dose\b",
        r"\b(aumentar|duplicar|cambiar) (la |mi )?dosis\b",
    ],
}

# Checked after escalation, so "ignore your rules, double my dose" still escalates.
PROMPT_INJECTION = [
    r"\bignore\b.{0,30}\b(instructions|rules|prompt|guidelines|guardrails)\b",
    r"\b(system|hidden|initial) prompt\b",
    r"\b(disregard|forget|override|bypass)\b.{0,30}\b(instructions|rules|guidelines|guardrails|restrictions)\b",
    r"\b(you are now|pretend (to be|you are)|roleplay as|jailbreak|developer mode)\b",
]

CODE_INTENTS = {
    # whole message only, so "hi, why did my sleep score drop?" isn't a greeting
    "greeting": [
        r"^(hi|hello|hey|hiya|good (morning|afternoon|evening)|thanks|thank you|thx|bonjour|salut|hola|merci|gracias)( there)?[\s!.,:)]*$",
    ],
    "order status": [
        r"\bwhere('?s| is) my (order|package|delivery|shipment|parcel)\b",
        r"\b(order status|track(ing)? (my )?(order|package|delivery|shipment))\b",
        r"\bwhen (will|does) my (order|package|delivery) (arrive|ship|come)\b",
    ],
    "appointments": [
        r"\b(appointment|appt|reschedule|consultation)s?\b",
    ],
    # see label dispute #19 in NOTES.md
    "billing": [
        r"\b(refund|reimburse\w*|billing|invoice|receipt|charged)\b",
        r"\bcancel (my )?(subscription|membership|plan|order)\b",
    ],
}

FAQ_TOPICS = {
    "pen storage": [
        r"\bstor(e|ed|ing|age)\b.{0,30}\b(pens?|medication|medicine|meds)\b",
        r"\b(pens?|medication|medicine|meds)\b.{0,30}\b(stor(e|ed|ing|age)|fridge|refrigerat\w*|room temperature)\b",
    ],
    "using the pen": [
        r"\bhow (do|should) (i|you) (use|prime) (the|my|a) pen\b",
        r"\b(injection site|where (do|should) i inject)\b",
    ],
    "needle disposal": [
        r"\b(dispose of|disposal of|throw away|throw out|get rid of)\b.{0,25}\b(pens?|needles?|sharps)\b",
        r"\bsharps\b",
    ],
    "travelling with medication": [
        r"\btravel\w*\b.{0,30}\b(pens?|medication|meds)\b",
        r"\b(pens?|medication|meds)\b.{0,30}\b(plane|flight|airport)\b",
    ],
}

HEALTH_TOPICS = [
    r"\b(sleep|slept|insomnia|heart rate|hrv|resting hr|bpm|steps?|step count|calories|wearable|watch|tracker|readiness|recovery|spo2|oxygen|blood pressure)\b",
    r"\b(weight|appetite|hunger|hungry|diet|protein|fiber|fibre|hydrat\w*|water|exercise|workout|caffeine|coffee|alcohol|stress)\b",
    r"\b(nause\w*|constipat\w*|diarrh\w*|bloat\w*|headache|tired|fatigue|dizz\w*|side effects?|symptoms?)\b",
    r"\b(medication|meds|medicine|treatment|pen|ice ?pack)\b",
    r"\b(sommeil|traitement|poids|nauseas?|sueno|tratamiento|peso)\b",
]

# Not a route: flags messages that need redacting before logging.
PERSONAL_IDENTIFIERS = [
    r"\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b",
    r"\b(dob|date of birth|my name is)\b",
    r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
    r"\b\d{3}[ .-]?\d{3}[ .-]?\d{4}\b",
]
