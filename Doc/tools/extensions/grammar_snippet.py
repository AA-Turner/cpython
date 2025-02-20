"""Support for documenting Python's grammar."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.domains.std import token_xrefs
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import make_id

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Final

    from docutils.nodes import Node
    from sphinx.application import Sphinx
    from sphinx.util.typing import ExtensionMetadata


class snippet_string_node(nodes.inline):  # noqa: N801 (snake_case is fine)
    """Node for a string literal in a grammar snippet."""

    def __init__(
        self,
        rawsource: str = '',
        text: str = '',
        *children: Node,
        **attributes: Any,
    ) -> None:
        super().__init__(rawsource, text, *children, **attributes)
        # Use the Pygments highlight class for `Literal.String.Other`
        self['classes'].append('sx')


class GrammarSnippetBase(SphinxDirective):
    """Common functionality for GrammarSnippetDirective & CompatProductionList."""

    # The option/argument handling is left to the individual classes.

    grammar_re: Final = re.compile(
        r"""
            (?P<rule_name>^[a-zA-Z0-9_]+)     # identifier at start of line
            (?=:)                             # ... followed by a colon
        |
            (?P<rule_ref>`[^\s`]+`)           # identifier in backquotes
        |
            (?P<single_quoted>'[^']*')        # string in 'quotes'
        |
            (?P<double_quoted>"[^"]*")        # string in "quotes"
        """,
        re.VERBOSE,
    )

    def make_grammar_snippet(
        self, options: dict[str, Any], content: Sequence[str]
    ) -> list[nodes.paragraph]:
        """Create a literal block from options & content."""

        group_name = options['group']

        # Docutils elements have a `rawsource` attribute that is supposed to be
        # set to the original ReST source.
        # Sphinx does the following with it:
        # - if it's empty, set it to `self.astext()`
        # - if it matches `self.astext()` when generating the output,
        #   apply syntax highlighting (which is based on the plain-text content
        #   and thus discards internal formatting, like references).
        # To get around this, we set it to this non-empty string:
        rawsource = 'You should not see this.'

        literal = nodes.literal_block(
            rawsource,
            '',
            classes=['highlight'],
        )

        node_location = self.get_location()
        for line in content:
            self.make_production(
                line,
                group_name=group_name,
                literal=literal,
                location=node_location,
            )
        node = nodes.paragraph('', '', literal)
        return [node]

    def make_production(
        self,
        line: str,
        *,
        group_name: str,
        literal: nodes.literal_block,
        location: str,
    ):
        last_pos = 0
        for match in self.grammar_re.finditer(line):
            # Handle text between matches
            if match.start() > last_pos:
                literal += nodes.Text(line[last_pos : match.start()])
            last_pos = match.end()

            # Handle matches
            group_dict = {
                name: content
                for name, content in match.groupdict().items()
                if content is not None
            }
            match group_dict:
                case {'rule_name': name}:
                    literal += self.make_name_target(
                        name=name,
                        production_group=group_name,
                        location=location,
                    )
                case {'rule_ref': ref_text}:
                    literal += token_xrefs(ref_text, group_name)
                case {'single_quoted': name} | {'double_quoted': name}:
                    literal += snippet_string_node('', name)
                case _:
                    raise ValueError('unhandled match')
        literal += nodes.Text(line[last_pos:] + '\n')

    def make_name_target(
        self,
        *,
        name: str,
        production_group: str,
        location: str,
    ) -> addnodes.literal_strong:
        """Make a link target for the given production."""

        # Cargo-culted magic to make `name_node` a link target
        # similar to Sphinx `production`.
        # This needs to be the same as what Sphinx does
        # to avoid breaking existing links.

        name_node = addnodes.literal_strong(name, name)
        prefix = f'grammar-token-{production_group}'
        node_id = make_id(self.env, self.state.document, prefix, name)
        name_node['ids'].append(node_id)
        self.state.document.note_implicit_target(name_node, name_node)
        obj_name = f'{production_group}:{name}' if production_group else name
        std = self.env.domains.standard_domain
        std.note_object('token', obj_name, node_id, location=location)
        return name_node


class GrammarSnippetDirective(GrammarSnippetBase):
    """Transform a grammar-snippet directive to a Sphinx literal_block

    That is, turn something like:

        .. grammar-snippet:: file
           :group: python-grammar

           file: (NEWLINE | statement)*

    into something similar to Sphinx productionlist, but better suited
    for our needs:
    - Instead of `::=`, use a colon, as in `Grammar/python.gram`
    - Show the listing almost as is, with no auto-aligment.
      The only special character is the backtick, which marks tokens.

    Unlike Sphinx's productionlist, this directive supports options.
    The "group" must be given as a named option.
    The content must be preceded by a blank line (like with most ReST
    directives).
    """

    has_content = True
    option_spec = {
        'group': directives.unchanged_required,
    }

    # We currently ignore arguments.
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self) -> list[nodes.paragraph]:
        return self.make_grammar_snippet(self.options, self.content)


class CompatProductionList(GrammarSnippetBase):
    """Create grammar snippets from reST productionlist syntax

    This is intended to be a transitional directive, used while we switch
    from productionlist to grammar-snippet.
    It makes existing docs that use the ReST syntax look like grammar-snippet,
    as much as possible.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}

    def run(self) -> list[nodes.paragraph]:
        # The "content" of a productionlist is actually the first and only
        # argument. The first line is the group; the rest is the content lines.
        lines = self.arguments[0].splitlines()
        group = lines[0].strip()
        options = {'group': group}
        # We assume there's a colon in each line; align on it.
        align_column = max(line.index(':') for line in lines[1:]) + 1
        content = []
        for line in lines[1:]:
            rule_name, _colon, text = line.partition(':')
            rule_name = rule_name.strip()
            if rule_name:
                name_part = rule_name + ':'
            else:
                name_part = ''
            content.append(f'{name_part:<{align_column}}{text}')
        return self.make_grammar_snippet(options, content)


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive('grammar-snippet', GrammarSnippetDirective)
    app.add_directive_to_domain(
        'std', 'productionlist', CompatProductionList, override=True
    )
    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
