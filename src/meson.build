fs = import('fs')

rtmidi_sources = files([
    'rtmidi/RtMidi.cpp',
])
rtmidi_inc = include_directories('.', 'rtmidi')
rtmidi_mod_pyx = '_rtmidi.pyx'
rtmidi_mod_cpp = '_rtmidi.cpp'

cython = find_program('cython3', 'cython', required: false)

if fs.exists(rtmidi_mod_cpp)
    rtmidi_cython = files(rtmidi_mod_cpp)
elif cython.found()
    rtmidi_cython = custom_target(
        'rtmidi_cython',
        output: rtmidi_mod_cpp,
        input: rtmidi_mod_pyx,
        depend_files: [rtmidi_sources],
        command: [cython, '-3', '--cplus', '-o', '@OUTPUT@', '@INPUT@'],
    )
else
    error('The \'cython\' program was not found but is required.\n' +
          'Please install Cython from: https://pypi.org/project/Cython/.')
endif

cythonize_dist_script = files('meson_dist_cython.py')
meson.add_dist_script(python, cythonize_dist_script, rtmidi_mod_cpp)
