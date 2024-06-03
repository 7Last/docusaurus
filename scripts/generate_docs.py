import glob
import os
import re
import shutil
import string
from py_markdown_table.markdown_table import markdown_table

submodule_path = './docs_submodule'
docs_path = './docs'
metadata_file = 'variables.tex'
category_template = './scripts/category_template.json'
glossary_tex = '2_RTB/documentazione_interna/glossario/glossario.tex'
glossary_mdx = f'{docs_path}/rtb/documentazione-interna/glossario.mdx'
version_chip_import = 'import Chip from \'@mui/material/Chip\';'
version_chip = '<Chip label={{version}} sx={{margin: 1, backgroundColor: \'var(--ifm-color-primary)\', color: \'#000\'}}/>'
github_icon_import = 'import Button from \'@mui/material/Button\';\nimport GithubIcon from \'@mui/icons-material/GitHub\'';
github_button = '<Button variant="outlined" sx={{backgroundColor: \'black\'}} startIcon={<GithubIcon />} href={{href}}>Scarica da Github</Button>'
raw_content_url = 'https://raw.githubusercontent.com/7Last/docs/main'

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

            if version:
                repo_path = re.sub(rf'/(.*)/{metadata_file}', rf'/\1_{version}.pdf', variables_tex).replace(submodule_path, docs_path)
            else:
                repo_path = re.sub(rf'/(.*)/{metadata_file}', r'/\1.pdf', variables_tex).replace(submodule_path, docs_path)

            # from var_file, with regex, remove the folder before the variables.tex file and replace the extension
            document_path = variables_tex.replace(f'{submodule_path}/{submod_folder}', f'{docs_path}/{docs_folder}')
            document_path = re.sub(rf'/(.*)/{metadata_file}', r'/\1.mdx', document_path)
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
                content = create_mdx_file_content(
                    basename,
                    version,
                    authors,
                    latest_modification,
                    repo_path.replace(f'{docs_path}/', '')
                )
                f.write(content)

    # if glossary exists, parse it and write it to the glossary.mdx file
    if os.path.exists(f'{submodule_path}/{glossary_tex}'):
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


def create_mdx_file_content(title: str, version: str, authors: set[str], latest_modification: str,
                            repo_path: str) -> str:
    if re.search(r'\d{2}_\d{2}_\d{2}', title):  # yy-mm-dd date
        # old format
        title = re.sub(r'(\d{2})_(\d{2})_(\d{2})', r'\3-\2-\1', title) \
            .replace('_', ' ') \
            .replace('-', ' ')
    elif re.search(r'\d{4}-\d{2}-\d{2}', title):  # yyyy-mm-dd date
        # new format
        title = title.replace('-', ' ')
        title = re.sub(r'(\d{4}) (\d{2}) (\d{2})', r'\1-\2-\3', title)
    else:
        title = title.replace('_', ' ').replace('-', ' ')

    title = title.replace('.mdx', '')

    data = {}
    if authors:
        data['Autori'] = ', '.join(list(authors))

    if latest_modification:
        data['Ultima modifica'] = latest_modification

    title = title.title()

    if version:
        version_quote = f'"{version}"'
        mdx = f'{github_icon_import}\n\n{version_chip_import}\n\n# {title}\n\n{version_chip.replace("{version}", version_quote)}\n\n'
    else:
        mdx = f'{github_icon_import}\n\n# {title.title()}\n\n'

    href = f'"{raw_content_url}/{repo_path}"'
    button = github_button.replace("{href}", href)
    # if data is empty, return only the title
    if not data:
        return f'{mdx}{button}'
    table = markdown_table([data]).set_params(row_sep='markdown', quote=False).get_markdown()

    return f'{mdx}\n\n{table}\n\n{button}'


def extract_tex_table(tex_content) -> tuple[str, set[str]] or None:
    table = re.search(r'\\begin{tabular}(.*?)\\end{tabular}', tex_content, re.DOTALL)
    if not table:
        return None

    # new table format
    rows = re.findall(r'\d+\.\d+\s*&\s*(\d{4}-\d{2}-\d{2})\s*&\s*(\w+\s+\w+)\s*&\s*(\w+\s+\w+)', table.group(1))
    latest_modification = rows[0][0] if rows else None

    if not rows:
        # old table format
        rows = re.findall(r'\d+\.\d+\s*&\s*(\d{1,2}\/\d{1,2}\/\d{4})\s*&\s*(\w+\s+\w+)', table.group(1))
        latest_modification = re.sub(r'(\d{1,2})\/(\d{1,2})\/(\d{4})', r'\3-\2-\1', rows[0][0]) if rows else None

    if not rows:
        return None

    authors = set([row[1] for row in rows])
    # sort the authors by last name
    authors = sorted(authors)
    return authors, latest_modification


def parse_glossary():
    glossary_path = f'{submodule_path}/{glossary_tex}'
    file = open(glossary_path, 'r').read()
    file = re.sub(r'[\n\t\r]', '', file)

    pattern = r"\\newglossaryentry{([^{}]+)}\s*{\s*name={?[^,}]+}?,\s*description={([^{}]+)}"
    matches = re.findall(pattern, file)

    glossary = {}
    for word, definition in matches:
        first_letter = word[0].upper()
        if first_letter not in string.ascii_uppercase:
            first_letter = '#'
        if first_letter not in glossary:
            glossary[first_letter] = []
        glossary[first_letter].append((word, definition))

    return glossary


def write_glossary(glossary):
    # append the glossary to the glossary.mdx file
    with open(glossary_mdx, 'a+') as f:
        f.write('\n\n')
        for letter, entries in glossary.items():
            f.write(f'## {letter}\n\n')
            for entry in entries:
                f.write(f'### {entry[0]}\n\n{entry[1]}\n\n')


if __name__ == '__main__':
    main()
