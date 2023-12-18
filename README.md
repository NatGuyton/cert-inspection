# cert-inspection

A tool to get the certificates on a website and validate them.

This tool is designed to be run either by command line or as a lambda function, and will output 
either formatted text or json, respectively.

## Required modules

You can use pip to install the required modules via:

```
pip3 install -r requirements.txt
```

### Virtual Environment

If you want to create a virtual environment, either because you don't have access to install in 
the normal python library directories, or because you want to keep things clean and isolated, you
can create a virtual environment dir in this directory and install them there:

```
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
deactivate
```

If you have created a virtual environment similar to above, the "run" script will source the venv, 
and then you can run the scripts like:

```
./run populateSKI.py
```

Alternatively, instead of using run, you can edit the #! line to use the venv/bin/python3 full path
instead of "/usr/bin/env python3" in each of the python files, and run them directly.

