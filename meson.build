project(
    'python-rtmidi',
    'cpp',
    version: '1.5.0',
    license: 'MIT',
    default_options: [
        'warning_level=2'
    ],
    meson_version: '>=0.63.0'
)

cpp = meson.get_compiler('cpp')

## From https://github.com/numpy/numpy/blob/main/numpy/meson.build
# Platform detection
if host_machine.system() == 'windows' and cpp.get_id() == 'gcc'
  # For mingw-w64, link statically against the UCRT.
  gcc_link_args = ['-lucrt', '-static']

  add_project_link_arguments(gcc_link_args, language: ['c', 'cpp'])
  # Force gcc to float64 long doubles for compatibility with MSVC
  # builds, for C only.
  add_project_arguments('-mlong-double-64', language: 'c')
  # Make fprintf("%zd") work (see https://github.com/rgommers/scipy/issues/118)
  add_project_arguments('-D__USE_MINGW_ANSI_STDIO=1', language: ['c', 'cpp'])
  # Manual add of MS_WIN64 macro when not using MSVC.
  # https://bugs.python.org/issue28267
  add_project_arguments('-DMS_WIN64', language: ['c', 'cpp'])
endif
##

if host_machine.system() == 'darwin'
  # Enable c++11 support
  add_project_arguments('-std=c++11', language: ['cpp'])
endif

# Dependencies
jack2_dep = dependency('jack', version: '>=1.9.11', required: false)
jack1_dep = dependency('jack', version: ['>=0.125.0', '<1.0'], required: false)
alsa_dep = dependency('alsa', required: false)
threads_dep = dependency('threads')
coremidi_dep = dependency(
    'appleframeworks',
    modules: ['coreaudio', 'coremidi', 'foundation'],
    required: false
)
winmm_dep = cpp.find_library('winmm', required: false)

if not jack2_dep.found() and jack1_dep.found()
    jack_dep = jack1_dep
elif jack2_dep.found()
    jack_dep = jack2_dep
else
    warning('No version of JACK found, which is recent enough (jack2>=1.9.11 or jack1>=0.125.0)')
    jack_dep = disabler()
endif

pymod = import('python')
python = pymod.find_installation(get_option('python'), required: true)

# Generate _rtmidi extension source
subdir('src')

# Build & install C++ extension module and Python package
subdir('rtmidi')

if not get_option('wheel')
    postinstall_script = files('meson_postinstall.py')
    meson.add_install_script(python, postinstall_script)
endif

summary({
    'Debug messages (verbose)': get_option('verbose'),
    'Build for wheel': get_option('wheel'),
    'ALSA support': host_machine.system() == 'linux' and alsa_dep.found() and get_option('alsa'),
    'CoreMIDI support': host_machine.system() == 'darwin' and coremidi_dep.found() and get_option('coremidi'),
    'JACK support': jack_dep.found() and get_option('jack'),
    'Window MM support': host_machine.system() == 'windows' and winmm_dep.found() and get_option('winmm'),
}, section: 'Configuration')
