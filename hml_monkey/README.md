# Lightweight HML parsing

# Generate Data

- Clone the repository 
```
        git clone https://github.com/mmaiers-nmdp/hml-monkey`
        cd hml-monkey
```

- Setup Python3 virtual environment
```
        virtualenv -p python3 venv
        source venv/bin/activate 
        pip install lxml
```

- Set up liftovergl
```
        cd ~/src/git/liftoverGL
        make 
        python setup.py install
```
- Set up the path  and
```
        (edit hml_monkey/hml_monkey.py)
        python hml_monkey/hml_monkey.py
```

