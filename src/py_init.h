#include <Python.h>
 /*
  * This code initializes Python threads and GIL, because RtMidi calls Python
  * from native threads.
  *
  * See http://permalink.gmane.org/gmane.comp.python.cython.user/5837
  *
  * *PyEval_InitThreads* is a no-op since Python.37 and deprecated since
  * Python 3.6. Now *Py_Initialize* initializes the GIL.
  *
  * The calls are in this separate C file instead of in the main .pyx file so
  * that we can use pre-compiler conditionals and don't get a compiler
  * deprecation warning on Python 3.9+ for including *PyEval_InitThreads*.
  */

 void py_init() {
     #if !defined(PYPY_VERSION) and PY_MAJOR_VERSION >= 3 and PY_MINOR_VERSION >= 7
         Py_Initialize();
     #else
         PyEval_InitThreads();
     #endif
 } 
