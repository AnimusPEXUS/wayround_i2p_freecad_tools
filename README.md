
setup.py is not usable. package not intended to be installed via pip. just download code and add
```python
np = 'whatever'
while np in sys.path:
    sys.path.remove(np)
sys.path.insert(0, np)
del np
```
code to your project

example is here: ( wayround_i2p/freecad_tools/example ) . to run it, open FreeCAD, load file vice Ctrl+O and press Ctrl+F6
