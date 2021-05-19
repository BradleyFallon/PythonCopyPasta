



def append_txt(path, text)
    with open(path, 'a') as the_file:
        the_file.write(text + '\n')

def file_to_lines(path) -> list:
    with open(path) as f:
        lines = [line.strip() for line in f]
    return lines