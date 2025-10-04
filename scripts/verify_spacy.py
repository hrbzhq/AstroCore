import spacy

def main():
    print('spaCy version', spacy.__version__)
    try:
        nlp = spacy.load('en_core_web_sm')
    except Exception as e:
        print('Failed to load model en_core_web_sm:', e)
        return
    print('Model loaded:', nlp.meta.get('name'))
    doc = nlp('This is a test sentence for spaCy installation. Sampling rate 2000 Hz, data path C:\\data\\subject1\\recording.fif')
    print('Tokens:', [t.text for t in doc])
    print('POS (token, pos):', [(t.text,t.pos_) for t in doc if t.pos_!='PUNCT'])
    print('Entities:', [(ent.text, ent.label_) for ent in doc.ents])

if __name__ == '__main__':
    main()
