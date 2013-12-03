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

::

    pip install -e git+https://github.com/regisb/prodigal.git#egg=prodigal

Usage
=====

Prodigal generates content from Jinja2 templates. Content generation should proceed as follows:

1. Write your html/jinja2 content in src/
2. Generate a translation file in the target language::

    prodigal translate fr src/

3. Edit the generated src/fr.po file in order to produce translations for all your localized strings.
4. Generate the localized version of your content::

    prodigal generate -l fr src/ dst/

While you are developing your website, you might want to skip the generation
step and see directly what your website looks like. Prodigal comes with an
embedded HTTP server which can serve your content from your source folder::

    prodigal serve -l fr src/

Example
=======

Consider the following content::

    example/
        _base.html
        blog/
            post1.html
            post2.html

_base.html::

    <!DOCTYPE html>
    <html>
        <body>{% block content %}{% endblock %}</body>
    </html>

blog/post1.html::

    {% extends "_base.html" %}
    {% block content %}Hey, check it out! I just wrote a great blog post.{% endblock %}

blog/post2.html::

    <html>
        <body>{% trans %}Some entirely different (translated) content.{% endtrans %}</body>
    </html>

You can first generate the French translation file for this website::

    prodigal translate example/ fr

This command generated the file `example/fr.po`. You may now edit it in order
to provide the correct French translation for your content::

    #: ./example/post2.html:2
    msgid "Some entirely different (translated) content."
    msgstr "Un peu de contenu (traduit) complètement différent"

And finally, you can use this translation file to deploy a translated version of your website::

    prodigal generate -l fr ./example /var/www/

In further iterations, you can serve your content directly from your source
folder thanks to the embedded HTTP server::
    
    prodigal serve -l fr ./example

Then head to http://127.0.0.1:8000 in your browser to see your rendered
templates. Note that translations will be recompiled on-the-fly as you modify
your .po file.
   
Development
===========

Install development dependencies::

    pip install -r requirements.txt

If you wish to write a contribution, don't forget to write unit tests! Tests can be run with::

    python -m unittest discover


F.A.Q
=====

Questions? Comments? Just open an issue request, tweet me at
`@regisb <https://twitter.com/#!/regisb>`_, or shoot me an email at
`regis@behmo.com <mailto:regis@behmo.com>`_.

Q. There are so many static website generators already, why did you create
another one?

A. None of the static website generators I found allowed me to generate two
versions of the same website in two different languages. I needed to do that
for `nulinu.li <http://nulinu.li>`_. I figured: how hard can it be? Existing
bricks where already present in Django, I only had to pull them out.



    "Occasionally, members of the Institute of Arcane Study acquire a taste for
    worldly pleasures. Seldom do they have trouble finding employment."
