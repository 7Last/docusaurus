import glob, re, os, shutil
from py_markdown_table.markdown_table import markdown_table

submodule_path = '../docs_submodule'
docs_path = '../docs'
metadata_file = 'variables.tex'
category_template = 'category_template.json'

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
                create_category_template(label=title, description=title, path=dirname)

            os.makedirs(os.path.dirname(document_path), exist_ok=True)  # create the folder if it doesn't exist
            with open(document_path, 'w') as f:
                print(f'Writing {document_path}')
                basename = os.path.basename(document_path)
                f.write(create_md_file_content(basename, version, authors, latest_modification))


def cleanup_non_json(docs_folder):
    # remove anything in docs_path/docs_folder that is not json
    for file in glob.glob(f'{docs_path}/{docs_folder}/**'):
        if file.endswith('.json'):
            continue
        if os.path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)


def parse_tex(tex_path) -> tuple[str, str, set[str], str]:
    # # in the same dir as variables.tex, get the only pdf file
    tex_content = open(tex_path, 'r').read()
    title = extract_tex_tag('Title', tex_content)
    version = extract_tex_tag('Version', tex_content)
    main_pdf = glob.glob(f'{os.path.dirname(tex_path)}/*.pdf')
    if not main_pdf:
        print(f'Main pdf found in {os.path.dirname(variables_tex)}')
        return title, version, None

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
    if version:
        data['Versione'] = version

    if authors:
        data['Autori'] = ', '.join(list(authors))

    if latest_modification:
        data['Ultima modifica'] = latest_modification

    # if data is empty, return only the title
    if not data:
        return f'# {title.title()}'
    table = markdown_table([data]).set_params(row_sep = 'markdown', quote = False).get_markdown()

    return f'''# {title.title()}\n\n{table}'''


def extract_tex_table(tex_content) -> tuple[str, set[str]] or None:
    table = re.search(r'\\begin{tabular}(.*?)\\end{tabular}', tex_content, re.DOTALL)
    if not table:
        return None

    rows = re.findall(r'\d+\.\d+\s*&\s*(\d{1,2}\/\d{1,2}\/\d{4})\s*&\s*(\w+\s+\w+)', table.group(1))
    if not rows:
        return None
    # set initializer
    authors = set([row[1] for row in rows])
    latest_modification = rows[0][0]
    return authors, latest_modification


if __name__ == '__main__':
    main()
