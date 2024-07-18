from gpt4all import GPT4All

_name = "starcoder-newbpe-q4_0.gguf"
model = GPT4All(_name, device='cpu')

while True:
    _query = input(f'Say anything: ')
    if _query.lower() == 'exit':
        exit(1)

    res = model.generate(_query, max_tokens=2048)
    print('\n' + res + '\n')