
setup.py is not usable. just download code and add
```python
np = 'whatever'
while np in sys.path:
    sys.path.remove(np)
sys.path.insert(0, np)
del np
```
code to your project