from app.nlp import train_and_evaluate
if __name__ == '__main__':
    stats = train_and_evaluate()
    for key, value in stats.items():
        if key != 'confusion_matrix':
            print(f'{key}: {value}')
