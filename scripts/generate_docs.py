import glob, re, os, shutil, string
from py_markdown_table.markdown_table import markdown_table

submodule_path = '../docs_submodule'
docs_path = '../docs'
metadata_file = 'variables.tex'
category_template = 'category_template.json'
glossary_tex = '2_RTB/glossario/glossario.tex'
glossary_md = f'{docs_path}/rtb/glossario.md'

folders = [
    # pairs of folders in the submodule and the corresponding name of the folder in the docs
    ('1_candidatura', 'candidatura'),
    ('2_RTB', 'rtb')
]


def main():
    for (submod_folder, docs_folder) in folders:
        cleanup_non_json(docs_folder)

        tex_variables_files = glob.glob(f'{submodule_path}/{submod_folder}/**/{metadata_file}', recursive=True)
        for variables_tex in tex_variables_files:
            tex = parse_tex(variables_tex)
            if not tex:
                continue

            title, version, authors, latest_modification = tex

            # from var_file, with regex, remove the folder before the variables.tex file and replace the extension

            document_path = re.sub(rf'/(.*)/{metadata_file}', r'/\1.md',
                                   variables_tex.replace(f'{submodule_path}/{submod_folder}',
                                                         f'{docs_path}/{docs_folder}'))

            document_path = document_path.replace('_', '-')
            document_path = re.sub(r'-v\d+\.\d+', '', document_path)  # replace version

            dirname = os.path.dirname(document_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True)
                # get the last dirname
                folder_title = os.path.basename(os.path.dirname(document_path)).replace('-', ' ').title()
                create_category_template(label=folder_title, description=folder_title, path=dirname)

            os.makedirs(os.path.dirname(document_path), exist_ok=True)  # create the folder if it doesn't exist
            with open(document_path, 'w') as f:
                print(f'Writing {document_path}')
                basename = os.path.basename(document_path)
                f.write(create_md_file_content(basename, version, authors, latest_modification))

    glossary = parse_glossary()
    write_glossary(glossary)

def cleanup_non_json(docs_folder):
    # remove anything in docs_path/docs_folder that is not json
    for file in glob.glob(f'{docs_path}/{docs_folder}/**'):
        if file.endswith('.json'):
            continue
        if os.path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)


def parse_tex(tex_path) -> tuple[str, str, set[str] or None, str or None]:
    # # in the same dir as variables.tex, get the only pdf file
    tex_content = open(tex_path, 'r').read()
    title = extract_tex_tag('Title', tex_content)
    version = extract_tex_tag('Version', tex_content)
    main_pdf = glob.glob(f'{os.path.dirname(tex_path)}/*.pdf')
    if not main_pdf:
        print(f'Main pdf found in {os.path.dirname(tex_path)}')
        return title, version, None, None

    main_tex_content = open(main_pdf[0].replace('.pdf', '.tex')).read()
    table_data = extract_tex_table(main_tex_content)
    if not table_data:
        print(f'Table not found in {main_pdf[0]}')
        return title, version, None, None

    authors, latest_modification = table_data
    return title, version, authors, latest_modification


def extract_tex_tag(tag, tex_content) -> str or None:
    match = re.search(rf'\\{tag}{{(.*)}}', tex_content)
    return match.group(1) if match else None


def create_category_template(label, description, path) -> None:
    template = (open(category_template, 'r').read()
                .replace('{label}', label)
                .replace('{description}', description))

    open(f'{path}/_category_.json', 'w').write(template)


def create_md_file_content(title: str, version: str, authors: set[str], latest_modification: str) -> str:
    title = re.sub(r'(\d{2})-(\d{2})-(\d{2})', r'\3/\2/\1', title).replace('-', ' ').replace('.md', '')

    data = {}
    if authors:
        data['Autori'] = ', '.join(list(authors))

    if latest_modification:
        data['Ultima modifica'] = latest_modification

    md = f'# {title.title()}\n\n'

    if version:
        md += f'## {version}'

    # if data is empty, return only the title
    if not data:
        return md
    table = markdown_table([data]).set_params(row_sep = 'markdown', quote = False).get_markdown()

    return f'{md}\n\n{table}'


def extract_tex_table(tex_content) -> tuple[str, set[str]] or None:
    table = re.search(r'\\begin{tabular}(.*?)\\end{tabular}', tex_content, re.DOTALL)
    if not table:
        return None

    rows = re.findall(r'\d+\.\d+\s*&\s*(\d{1,2}\/\d{1,2}\/\d{4})\s*&\s*(\w+\s+\w+)', table.group(1))
    if not rows:
        return None

    authors = set([row[1] for row in rows])
    # sort the authors by last name
    authors = sorted(authors)
    latest_modification = rows[0][0]
    return authors, latest_modification

def parse_glossary():
    glossary_path = f'{submodule_path}/{glossary_tex}'
    file = open(glossary_path, 'r').read()
    file = re.sub(r'[\n\t\r]', '', file)
    rows = re.findall(r'\\glossdef{(.*?)}{(.*?)}', file, re.MULTILINE)

    glossary = {}
    for word, definition in rows:
        first_letter = word[0].upper()
        if first_letter not in string.ascii_uppercase:
            first_letter = '#'
        if first_letter not in glossary:
            glossary[first_letter] = []
        glossary[first_letter].append((word, definition))

    return glossary

def write_glossary(glossary):
    # append the glossary to the glossary.md file
    with open(glossary_md, 'w') as f:
        f.write('# Glossario\n\n')
        for letter, entries in glossary.items():
            f.write(f'## {letter}\n\n')
            for entry in entries:
                f.write(f'### {entry[0]}\n\n{entry[1]}\n\n')

if __name__ == '__main__':
    main()
