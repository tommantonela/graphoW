Install
=======

graphoW requires Python >= 3.6.  For instructions for installing the full `scientific Python stack, check: <https://scipy.org/install.html>`_.

This instructions assume that you have the default Python environment already configures and that you want to install ``graphow`` in it. To create a new Python virtual environments, check the instructions for venv <https://docs.python.org/3/library/venv.html>`_ and `virtual
environments <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

As a first step, check that you have installed the latest ``pip`` version. If you don't, check the `Pip documentation <https://pip.pypa.io/en/stable/installing/>`_ and install ``pip``.

Install the released version
----------------------------

Install the current release of ``graphow`` with ``pip``::

    $ pip install graphow

To upgrade to a newer release use the ``--upgrade`` flag::

    $ pip install --upgrade graphow

If you do not have permission to install software systemwide, you can
install into your user directory using the ``--user`` flag::

    $ pip install --user graphow

If you do not want to install our dependencies (e.g., ``numpy``, ``scipy``, etc.),
you can use::

    $ pip install graphow --no-deps

This may be helpful if you are using PyPy or you are working on a project that
only needs a limited subset of our functionality and you want to limit the
number of dependencies.

You can also manually download ``graphow`` from
`GitHub <https://github.com/tommantonela/graphoW/releases>`_  or
`PyPI <https://pypi.python.org/pypi/graphow>`_.

To install one of these versions, unpack it and run the following from the
top-level source directory using the Terminal::

    $ pip install .

Install the development version
-------------------------------

If you have `Git <https://git-scm.com/>`_ installed on your system, it is also
possible to install the development version of ``graphow``.

Before installing the development version, you may need to uninstall the
standard version of ``graphow`` using ``pip``::

    $ pip uninstall graphow

Then do::

    $ git clone https://github.com/tommantonela/graphoW.git
    $ cd graphow
    $ pip install -e .

The ``pip install -e .`` command allows you to follow the development branch as
it changes by creating links in the right places and installing the command
line scripts to the appropriate locations.

Then, if you want to update ``graphow`` at any time, in the same directory do::

    $ git pull