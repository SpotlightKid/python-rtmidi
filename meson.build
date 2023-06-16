project(
    'python-rtmidi',
    'cpp',
    version: '1.5.2',
    license: 'MIT',
    default_options: [
        'warning_level=2'
    ],
    meson_version: '>=0.63.0'
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
if host_machine.system() == 'windows'
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
elif host_machine.system() == 'darwin'
    # OSX

    # Enable c++11 support
    add_project_arguments('-std=c++11', language: ['cpp'])

    # Enable cross compilation if host is x86 and target is arm64
    # Meson doesn't have env access support on purpose...
    cmd = run_command('sh', '-c', 'echo $ARCHFLAGS ', check: true)
    ARCHFLAGS = cmd.stdout().strip()

    if host_machine.cpu_family() == 'x86_64' and ARCHFLAGS == '-arch arm64'
        message('Crosscompiling from Intel to Apple Silicon')
        add_project_arguments('-arch', 'arm64', '--target=arm64-apple-macos', language: ['cpp', 'c'])
        add_project_link_arguments('-arch', 'arm64', '--target=arm64-apple-macos', language: ['cpp', 'c'])
    endif

    # API
    coremidi_dep = dependency(
        'appleframeworks',
        modules: ['coreaudio', 'coremidi', 'foundation'],
        required: jack_not_found
    )
else
    # LINUX

    # API
    alsa_dep = dependency('alsa', required: jack_not_found)
endif # Platform detection

jack_support = jack_dep.found() and get_option('jack')
alsa_support = host_machine.system() == 'linux' and alsa_dep.found() and get_option('alsa')
coremidi_support = host_machine.system() == 'darwin' and coremidi_dep.found() and get_option('coremidi')
winmm_support = host_machine.system() == 'windows' and winmm_dep.found() and get_option('winmm')

threads_dep = dependency('threads', required: alsa_support or jack_support)
have_semaphore = cpp.has_header('semaphore.h')

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
    'JACK support': jack_support,
    'ALSA support': alsa_support,
    'CoreMIDI support': coremidi_support,
    'Window MM support': winmm_support,
}, section: 'Configuration')

