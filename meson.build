project(
    'python-rtmidi',
    'cpp',
    version: '1.5.0rc1',
    license: 'MIT',
    default_options: [
        'warning_level=2'
    ],
    meson_version: '>=0.53.0'
)

# Dependencies
cpp = meson.get_compiler('cpp')
jack2_dep = dependency('jack', version: '>=1.9.11', required: false)
jack1_dep = dependency('jack', version: ['>=0.125.0', '<1.0'], required: false)
alsa_dep = dependency('alsa', required: false)
threads_dep = dependency('threads')
coremidi_dep = dependency(
    'appleframeworks',
    modules: ['coreaudio', 'coremidi', 'foundation'],
    required: false
)
winmm_dep = dependency('winmm', required: false)

if not jack2_dep.found() and jack1_dep.found()
    jack_dep = jack1_dep
elif jack2_dep.found()
    jack_dep = jack2_dep
else
    warning('No version of JACK found, which is recent enough (jack2>=1.9.11 or jack1>=0.125.0)')
endif

pymod = import('python')
python = pymod.find_installation(get_option('python'), required: true)

# Generate _rtmidi extension source
subdir('src')

# Build & install C++ extension module and Python package
subdir('rtmidi')

if not get_option('wheel')
    meson.add_install_script('meson_postinstall.py')
endif

summary({
    'Debug messages (verbose)': get_option('verbose'),
    'Build for wheel': get_option('wheel'),
    'ALSA support': host_machine.system() == 'linux' and alsa_dep.found() and get_option('alsa'),
    'CoreMIDI support': host_machine.system() == 'darwin' and coremidi_dep.found() and get_option('coremidi'),
    'JACK support': jack_dep.found() and get_option('jack'),
    'Window MM support': host_machine.system() == 'windows' and winmm_dep.found() and get_option('winmm'),
}, section: 'Configuration')
