==============================================
Prodigal: Yet Another Static Website Generator
==============================================

About
=====

Prodigal is a static website generator written in Python. You can use it to
generate static websites based on Jinja2 templates. Prodigal handles website
translations natively: this means that you can use Prodigal to generate
multiple versions of your website, one for each language.

Installing
==========

    pip install -e git+https://github.com/regisb/prodigal.git#egg=prodigal

Usage
=====

Prodigal generates content from Jinja2 templates. Content generation should proceed as follows:

1. Write your html/jinja2 content in src/
2. Generate a translation file in the target language:

    prodigal.py translate fr src/

3. Edit the generated src/fr.po file in order to produce translations for all your localized strings.
4. Generate the localized version of your content:

    prodigal generate -l fr src/ dst/

Example
=======

Consider the following content:

    example/
        \_ _base.html
        \_ blog
            \_ post1.html
            \_ post2.html

_base.html:

    <!DOCTYPE html>
    <html>
        <body>{% block content %}{% endblock %}</body>
    </html>

blog/post1.html:

    {% extends "_base.html" %}
    {% block content %}Hey, check it out! I just wrote a great blog post.{% endblock %}

blog/post2.html:

    <html>
        <body>{% trans %}Some entirely different (translated) content.{% endtrans %}</body>
    </html>

You can first generate the French translation file for this website:

    prodigal.py translate example/ fr

This command generated the file `example/fr.po`. You may now edit it in order
to provide the correct French translation for your content:

    #: ./example/post2.html:2
    msgid "Some entirely different (translated) content."
    msgstr "Un peu de contenu (traduit) complètement différent"

And finally, you can use this translation file to deploy a translated version of your website:

    prodigal.py generate -l fr ./example /var/www/
   
Development
===========

If you wish to write a contribution, don't forget to write unit tests! Tests can be run with:

    python -m unittest discover





    "Occasionally, members of the Institute of Arcane Study acquire a taste for
    worldly pleasures. Seldom do they have trouble finding employment."
