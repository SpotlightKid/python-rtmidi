# https://mesonbuild.com/Python-module.html

defines = []
dependencies = [python.dependency()]
link_args = []

if coremidi_support
    defines += ['-D__MACOSX_CORE__']
    #defines += ['-frtti']
    dependencies += [coremidi_dep]
    link_args += [
        '-framework', 'CoreAudio',
        '-framework', 'CoreMIDI',
        '-framework', 'CoreFoundation'
    ]
endif

if alsa_support or jack_support
    dependencies += [threads_dep]
endif

if alsa_support
    defines += ['-D__LINUX_ALSA__']
    dependencies += [alsa_dep]
endif

if winmm_support
    defines += ['-D__WINDOWS_MM__']
    if meson.get_compiler('cpp').get_id() != 'gcc'
        defines += ['/EHsc']
    endif
    dependencies += [winmm_dep]
endif

if jack_support
    defines += ['-D__UNIX_JACK__', '-DJACK_HAS_PORT_RENAME']
    if have_semaphore
        defines += ['-DHAVE_SEMAPHORE']
    endif
    dependencies += [jack_dep]
endif

if get_option('verbose')
    defines += ['-D__RTMIDI_DEBUG__']
else
    defines += ['-D__RTMIDI_SILENCE_WARNINGS__']
endif


# Build and install the extension module
module = python.extension_module(
    '_rtmidi',
    [rtmidi_cython, rtmidi_sources],
    dependencies: dependencies,
    cpp_args: defines,
    link_args: link_args,
    include_directories: rtmidi_inc,
    install: true,
    subdir: 'rtmidi',
)

# Generate version.py file
version_py = configure_file(
    input: 'version.py.in',
    output: 'version.py',
    configuration: {
        'VERSION': meson.project_version()
    }
)


# Pure Python sources
python_sources = files([
    '__init__.py',
    'midiconstants.py',
    'midiutil.py',
])


# Install pure Python modules
python.install_sources(
    python_sources,
    version_py,
    subdir: 'rtmidi',
)
