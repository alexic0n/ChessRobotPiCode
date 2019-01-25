# Notes on project structure

The structure for the files will be as follows:
```
root/
|
|-- classes/
|   |-- class1.py
|   |-- class2.py
|       ...
|
|-- functinos/
|   |-- function1.py
|   |-- function2.py
|       ...
|
|-- unittests/
|   |-- test1.py
|   |-- test2.py
|       ...
|
|-- folderX/
|-- folderY/
|   ...
|
|-- main.py
|-- runAllTests.py
```

# Importing files

If you are importing files then you need to import them as if you were at the root level. 
For example if you are in function1.py and you want to import class1.py:

In function1.py: `from classes.class1 import *`
In main.py: `from functions.function1 import *`

Then run main.py (or any other file at the root level).

The fact that main.py is at root level means that it enables imports from other folders 
for any file it imports itself. You will not be able to import a file from another 
directory without the root scope.
