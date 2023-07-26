project(
    'python-rtmidi',
    'cpp',
    version: '1.5.5',
    license: 'MIT',
    default_options: [
        'warning_level=2',
        'cpp_std=c++11'
    ],
    meson_version: '>=0.64.0'
)

cpp = meson.get_compiler('cpp')

# Jack API (portable)
jack2_dep = dependency('jack', version: '>=1.9.11', required: false)
jack1_dep = dependency('jack', version: ['>=0.125.0', '<1.0'], required: false)

if not jack2_dep.found() and jack1_dep.found()
    jack_dep = jack1_dep
elif jack2_dep.found()
    jack_dep = jack2_dep
else
    warning('No version of JACK found, which is recent enough (jack2>=1.9.11 or jack1>=0.125.0)')
    jack_dep = disabler()
endif

jack_not_found = jack_dep.found() ? false : true

## From https://github.com/numpy/numpy/blob/main/numpy/meson.build
# Platform dependent config
if host_machine.system().to_lower() == 'windows'
    # WINDOWS
    if cpp.get_id() == 'gcc'
        # For mingw-w64, link statically against the UCRT.
        gcc_link_args = ['-lucrtbase', '-static']
        add_project_link_arguments(gcc_link_args, language: ['c', 'cpp'])
        # Make fprintf("%zd") work (see https://github.com/rgommers/scipy/issues/118)
        add_project_arguments('-D__USE_MINGW_ANSI_STDIO=1', language: ['c', 'cpp'])
        # Manual add of MS_WIN64 macro when not using MSVC.
        # https://bugs.python.org/issue28267
        add_project_arguments('-DMS_WIN64', language: ['c', 'cpp'])
    elif cpp.get_id() == 'msvc'
        # Force gcc to float64 long doubles for compatibility with MSVC
        # builds, for C only.
        add_project_arguments('-mlong-double-64', language: 'c')
    endif

    # API
    winmm_dep = cpp.find_library('winmm', required: jack_not_found)
    alsa_dep = disabler()
elif host_machine.system().to_lower() == 'darwin'
    # OSX

    # API
    coremidi_dep = dependency(
        'appleframeworks',
        modules: ['coreaudio', 'coremidi', 'foundation'],
        required: jack_not_found
    )
    alsa_dep = disabler()
else
    # LINUX

    # API
    alsa_dep = dependency('alsa', required: jack_not_found)
endif # Platform detection

jack_support = jack_dep.found() and get_option('jack')
alsa_support = host_machine.system().to_lower() == 'linux' and alsa_dep.found() and get_option('alsa')
coremidi_support = host_machine.system().to_lower() == 'darwin' and coremidi_dep.found() and get_option('coremidi')
winmm_support = host_machine.system().to_lower() == 'windows' and winmm_dep.found() and get_option('winmm')

threads_dep = dependency('threads', required: alsa_support or jack_support)
have_semaphore = cpp.has_header('semaphore.h')

pymod = import('python')
python = pymod.find_installation(get_option('python'), required: true, pure: false)

# Generate _rtmidi extension source
subdir('src')

# Build & install C++ extension module and Python package
subdir('rtmidi')

if not get_option('wheel')
    postinstall_script = files('meson_postinstall.py')
    meson.add_install_script(python, postinstall_script)
endif

summary({
    'Host machine system': host_machine.system(),
    'Python version': python.language_version(),
    'Debug messages (verbose)': get_option('verbose'),
    'Build for wheel': get_option('wheel'),
    'JACK support': jack_support,
    'ALSA support': alsa_support,
    'CoreMIDI support': coremidi_support,
    'Window MM support': winmm_support,
}, section: 'Configuration')
