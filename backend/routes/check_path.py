from pathlib import Path
print('File:', __file__)
print('Parent:', Path(__file__).parent)
print('Parent.parent:', Path(__file__).parent.parent)
print('Parent.parent.parent:', Path(__file__).parent.parent.parent)
