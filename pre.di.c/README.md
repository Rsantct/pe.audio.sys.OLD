## Requirements

- **Python** >= 3.6

```
python3 -m pip install numpy
python3 -m pip install pyaml
python3 -m pip install python-mpd2
```

- **https://jackclient-python.readthedocs.io**

```
    sudo python3 -m pip install --upgrade setuptools
    
    # maybe necessary:
        sudo apt install libffi-dev
    
    sudo python3 -m pip install cffi
    sudo python3 -m pip install JACK-Client
```

- Update your environment for instance by editing your **`.profile`** home file:

```
    export PYTHONPATH="$PYTHONPATH:$HOME/pre.di.c/bin:$HOME/pre.di.c/clients/bin"
    export PATH="$PATH:$HOME/pre.di.c/bin"
```
