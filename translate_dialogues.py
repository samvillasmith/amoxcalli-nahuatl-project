import sqlite3, os, json, asyncio
from pathlib import Path

for line in Path('.env').read_bytes().decode('utf-8').splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, _, v = line.partition('=')
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import anthropic

conn = sqlite3.connect('curriculum/fcn_master_lexicon_phase8_6_primer.sqlite')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('SELECT sample_id, lesson_number, speaker_label, utterance_original FROM primer_dialogues ORDER BY lesson_number, dialogue_order')
rows = [dict(r) for r in cur.fetchall()]

# These are already in English
ALREADY_EN = {
    'FCN-DS-02-01','FCN-DS-02-02','FCN-DS-04-01','FCN-DS-20-01','FCN-DS-20-02',
    'FCN-DS-21-01','FCN-DS-22-01','FCN-DS-22-02','FCN-DS-23-01','FCN-DS-23-02',
    'FCN-DS-24-01','FCN-DS-25-01'
}

async def main():
    client = anthropic.AsyncAnthropic()
    nahuatl_rows = [r for r in rows if r['sample_id'] not in ALREADY_EN]
    payload = [{'id': r['sample_id'], 'nahuatl': r['utterance_original']} for r in nahuatl_rows]
    resp = await client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=2048,
        system='Translate these EHN (Eastern Huasteca Nahuatl) utterances to natural English. Return JSON array: [{"id": "...", "en": "..."}]. Return ONLY the JSON array.',
        messages=[{'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
    )
    text = resp.content[0].text.strip()
    if text.startswith('```'):
        lines = text.splitlines()
        text = '\n'.join(lines[1:-1])
    results = json.loads(text)
    translations = {r['id']: r['en'] for r in results}
    for r in rows:
        if r['sample_id'] in ALREADY_EN:
            translations[r['sample_id']] = r['utterance_original']
    for sid, en in translations.items():
        conn.execute('UPDATE primer_dialogues SET translation_en = ? WHERE sample_id = ?', (en, sid))
    conn.commit()
    print(f'Updated {len(translations)} dialogue translations')
    for r in rows:
        en = translations.get(r['sample_id'], '')
        print(f"  L{r['lesson_number']} [{r['speaker_label']}]: {en[:80]}")

asyncio.run(main())
