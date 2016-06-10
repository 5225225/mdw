# Docs

## Installation

1. Checkout the code into any directory, but be sure to change the ROOT variable in `main.py` if you
   run the code anywhere but `~/src/mdw`.

2. Set up the directories. This can be done automatically using the `init.sh` script, or manually.

   1. Create the directories (`files`, `logs`, `wiki`).  `files` is used for uploaded files, `logs`
      is used for edit diffs, `wiki` is used to store wiki markdown files.

   2. Make a homepage. Currently, the server crashes if no homepage is set. This is a bug and will
      be fixed.

   3. (Optional) Download Mathjax. This is used to render LaTeX, and is not required. It can either
      be served locally (The default), or served from the mathjax CDN.
      
      Serving it locally requires downloading the MathJax-master from
      `https://github.com/mathjax/MathJax/archive/master.zip` and extracting it to `MathJax` in the
      root directory.

      Serving it from the CDN requires moving the path in `templates/base.html` to point to the CDN
      URL (Currently `https://cdn.mathjax.org/mathjax/latest/MathJax.js`). This requires acceptence
      of their TOS [here](https://www.mathjax.org/mathjax-cdn-terms-of-service/).

3. Execute `main.py` and navigate to http://localhost:8888.

## Requirements

* [Bottle](http://bottlepy.org/docs/dev/index.html): Python Web Framework.  
  Available on pip as `bottle`, on Arch Linux as `python-bottle`.

* [Hoep](https://github.com/Anomareh/Hoep): A python binding for the Hoedown Markdown library.  
  Used to render the markdown files to HTML.  
  Available on pip as `hoep`.

* [Pygments](http://pygments.org/): Python syntax highlighter.  
  Used to syntax highlight code blocks if a language is given.
  Available on pip as `Pygments`, on Arch Linux as `python-pygments`.

## Page Formatting

Pages are rendered to HTML using Hoep. Code blocks are denoted by fenced code like

    ```language|filename.txt
    code here
    ``` 

The language can be selected by putting it after the beginning line of triple backticks. A file name
can also be given by putting it after a pipe character. If neither are given, no highlighting is
used.

Headers will have an `id` set to their text (With spaces replaced with underscores), and a hash
symbol acting as an anchor to them. This allows you to make URL's which link to a specific part of
the page.
