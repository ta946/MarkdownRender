import sublime
import sublime_plugin

import tempfile
import os
import shutil
import subprocess

from . import STATIC_FOLDER, STATIC_FILES_MAP
from .renderers import GitHubRenderer

PORT = 35729
RELOAD_JS = f"""<script async>
document.write(
  '<script src="http://' +
  (location.host || 'localhost').split(':')[0] +
  ':{PORT}/livereload.js?snipver=1" async></' +
  'script>')
</script>
"""
VIEW_SETTING_TEMP_PATH_KEY = "markdown_render-temp_path"

AUTO_RELOAD_ON = False


class MarkdownRenderCommand(sublime_plugin.TextCommand):
    def run(self, edit, update=False, path=None):
        self._init()

        self.renderer = GitHubRenderer()
        text = self.view.substr(sublime.Region(0, self.view.size()))
        md_content = self.renderer.render(text)

        md_html = self.compile(md_content)
        print('md_html')
        print(md_html)

        temp_path = self.write_temp(md_html, path=path)
        self.view.settings().set(VIEW_SETTING_TEMP_PATH_KEY, temp_path)

        if not update:
            subprocess.Popen(temp_path, shell=True)

    def _init(self):
        global AUTO_RELOAD_ON

        self._ensure_mermaidjs()

        if not AUTO_RELOAD_ON:
            sublime.run_command("live_reload_enable_plugin_by_name", {"name": 'SimpleRefresh', "enable": True})
            AUTO_RELOAD_ON = True

    def _static_file_path(self, name):
        filename = STATIC_FILES_MAP[name]
        path = os.path.join(STATIC_FOLDER, filename)
        return path

    def _ensure_mermaidjs(self):
        temp_dir = tempfile.gettempdir()
        mermaidjs_filename = STATIC_FILES_MAP["mermaidjs"]
        mermaidjs_filepath_temp = os.path.join(temp_dir, mermaidjs_filename)
        if not os.path.exists(mermaidjs_filepath_temp):
            mermaidjs_filepath = os.path.join(STATIC_FOLDER, mermaidjs_filename)
            shutil.copy2(mermaidjs_filepath, mermaidjs_filepath_temp)

    def _extract_files(self, files, tag):
        text_list = []
        for file in files:
            path = self._static_file_path(file)
            with open(path, 'r') as f:
                text = f.read()
            text = f'<{tag}>{text}</{tag}>'
            text_list.append(text)
        text = '\n'.join(text_list)
        return text


    def compile(self, md_content, theme_dark=True):
        style_files = [
            "md_css_dark" if theme_dark else "md_css",
        ]
        script_files = [
            "md_mermaid"
        ]

        template_path = self._static_file_path("template")
        with open(template_path, 'r') as f:
            template_html = f.read()

        md_html = template_html
        content = md_content
        data_color_mode = "dark" if theme_dark else "light"
        fn = self.view.file_name()
        title = 'untitled' if not fn else os.path.splitext(os.path.basename(fn))[0]
        styles = self._extract_files(style_files, "style")
        scripts = self._extract_files(script_files, "script")
        live_reload = RELOAD_JS

        replace_dict = {
            "data_color_mode": data_color_mode,
            "theme": data_color_mode,
            "title": title,
            "styles": styles,
            "scripts": scripts,
            "live_reload": live_reload,
            "content": content,
        }
        print('replace_dict')
        print(replace_dict)
        for key, val in replace_dict.items():
            replace_key = '{{ ' + str(key) + ' }}'
            print('replace_key', replace_key)
            md_html = md_html.replace(replace_key, val)
        return md_html

    def write_temp(self, html, path=None):
        if path is None:
            with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.html') as temp_file:
                temp_file.write(html)
                path = temp_file.name
        else:
            with open(path, mode='w', encoding='utf-8') as f:
                f.write(html)
        return path

        # # Optional: clean up
        # os.remove(temp_path)


class MarkdownRenderListener(sublime_plugin.EventListener):
    """Auto update the output HTML if markdown file has already been converted once."""

    def on_post_save(self, view):
        """Handle auto-reload on save."""
        global AUTO_RELOAD_ON
        if not AUTO_RELOAD_ON:
            return
        # settings = sublime.load_settings('MarkdownPreview.sublime-settings')
        filetypes = (".md", ".markdown", ".mdown")
        file_name = view.file_name()
        path = view.settings().get(VIEW_SETTING_TEMP_PATH_KEY)
        if not filetypes or file_name is  None or not file_name.endswith(tuple(filetypes)):
            return
        view.run_command('markdown_render', {
            'update': True,
            'path': path,
        })
        sublime.status_message('Markdown render file updated')
