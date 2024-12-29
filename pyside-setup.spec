#
# Conditional build:
%bcond_with	doc	# API documentation, needs sphinx_design plugin
%bcond_with	tests	# unit tests (many are plain broken)

Summary:	Qt For Python
Name:		pyside-setup
Version:	6.8.1.1
Release:	0.1
License:	- (enter GPL/GPL v2/GPL v3/LGPL/BSD/BSD-like/other license name here)
Group:		Libraries/Python
Source0:	https://github.com/pyside/pyside-setup/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	e8b7aa9ee72299b82f1e434da7094944
Patch0:		disable-broken-example.patch
URL:		https://github.com/pyside/pyside-setup
BuildRequires:	Qt63D-devel
BuildRequires:	Qt6Bluetooth-devel
BuildRequires:	Qt6Charts-devel
BuildRequires:	Qt6Concurrent-devel
BuildRequires:	Qt6Core-devel
BuildRequires:	Qt6DataVisualization-devel
BuildRequires:	Qt6DBus-devel
BuildRequires:	Qt6Designer-devel
BuildRequires:	Qt6Graphs-devel
BuildRequires:	Qt6Gui-devel
BuildRequires:	Qt6Help-devel
BuildRequires:	Qt6HttpServer-devel
BuildRequires:	Qt6Location-devel
BuildRequires:	Qt6Multimedia-devel
BuildRequires:	Qt6NetworkAuth-devel
BuildRequires:	Qt6Network-devel
BuildRequires:	Qt6Nfc-devel
BuildRequires:	Qt6OpenGL-devel
BuildRequires:	Qt6Pdf-devel
BuildRequires:	Qt6Positioning-devel
BuildRequires:	Qt6PrintSupport-devel
BuildRequires:	Qt6Qml-devel
BuildRequires:	Qt6Quick3D-devel
BuildRequires:	Qt6Quick-devel
BuildRequires:	Qt6RemoteObjects-devel
BuildRequires:	Qt6Scxml-devel
BuildRequires:	Qt6Sensors-devel
BuildRequires:	Qt6SerialBus-devel
BuildRequires:	Qt6SerialPort-devel
BuildRequires:	Qt6SpatialAudio-devel
BuildRequires:	Qt6Sql-devel
BuildRequires:	Qt6Svg-devel
BuildRequires:	Qt6Test-devel
BuildRequires:	Qt6TextToSpeech-devel
BuildRequires:	Qt6UiTools-devel
BuildRequires:	Qt6WebChannel-devel
BuildRequires:	Qt6WebEngine-devel
BuildRequires:	Qt6WebSockets-devel
BuildRequires:	Qt6WebView-devel
BuildRequires:	Qt6Widgets-devel
BuildRequires:	Qt6Xml-devel
BuildRequires:	clang-devel
BuildRequires:	cups-devel
BuildRequires:	qt6-assistant
BuildRequires:	qt6-designer
BuildRequires:	qt6-qtdeclarative
BuildRequires:	qt6-qttools
BuildRequires:	qt6-quick3d
BuildRequires:	qt6-shadertools
BuildRequires:	patchelf
BuildRequires:	python3-devel >= 1:3.2
# if using noarch subpackage:
#BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
# when using /usr/bin/env or other in-place substitutions
#BuildRequires:        sed >= 4.0
%if %{with doc}
BuildRequires:	sphinx-pdg-3
%endif
# replace with other requires if defined in setup.py
Requires:	python3-modules >= 1:3.2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# unneeded missing libpython linkage
%define		skip_post_check_so	libshiboken6.*.so.* libpyside6.*.so.* libpyside6qml.*.so.*

%description
Qt For Python

%package -n python3-PySide6
Summary:	-
Group:		-

%description -n python3-PySide6

%package -n shiboken6
Summary:	-
Group:		-

%description -n shiboken6

%package -n shiboken6-generator
Summary:	-
Group:		-

%description -n shiboken6-generator

%package apidocs
Summary:	API documentation for Python %{module} module
Summary(pl.UTF-8):	Dokumentacja API modułu Pythona %{module}
Group:		Documentation
BuildArch:	noarch

%description apidocs
API documentation for Python %{module} module.

%description apidocs -l pl.UTF-8
Dokumentacja API modułu Pythona %{module}.

%prep
%setup -q
%patch -P 0 -p1

# fix #!/usr/bin/env python -> #!/usr/bin/python:
%{__sed} -E -i -e '1s,#!\s*/usr/bin/env\s+python(\s|$),#!%{__python3}\1,' \
	sources/pyside-tools/pyside_tool.py \
	sources/shiboken6/shiboken_tool.py

%build
# Can't use py3_* macros here and in install.
# The build system only pretends to be distutils compatible,
# but in reality it's FUBAR mix of cmake, ninja and custom python code.
LDFLAGS="${LDFLAGS:-%rpmldflags}"; export LDFLAGS; \
CFLAGS="${CFLAGS:-%rpmcppflags %rpmcflags}"; export CFLAGS; \
CXXFLAGS="${CXXFLAGS:-%rpmcppflags %rpmcxxflags}"; export CXXFLAGS; \
%{?__cc:CC="%{__cc}"; export CC;} \
%{?__cxx:CXX="%{__cxx}"; export CXX;} \
%{__python3} setup.py --no-user-cfg build \
	--qtpaths=%{_libdir}/qt6/bin/qtpaths \
	%{?with_tests:--build-tests} \
	%{?with_doc:--build-docs}

%if %{with tests}
# use explicit plugins list for reliable builds (delete PYTEST_PLUGINS if empty)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_PLUGINS= \
%{__python3} -m pytest
%endif

%install
rm -rf $RPM_BUILD_ROOT

LDFLAGS="${LDFLAGS:-%rpmldflags}"; export LDFLAGS; \
CFLAGS="${CFLAGS:-%rpmcppflags %rpmcflags}"; export CFLAGS; \
CXXFLAGS="${CXXFLAGS:-%rpmcppflags %rpmcxxflags}"; export CXXFLAGS; \
%{?__cc:CC="%{__cc}"; export CC;} \
%{?__cxx:CXX="%{__cxx}"; export CXX;} \
%{__python3} setup.py --no-user-cfg \
	install \
	%{py3_install_opts} \
	--root=$RPM_BUILD_ROOT \
	--qtpaths=%{_libdir}/qt6/bin/qtpaths \
	--no-strip \
	--skip-cmake \
	--reuse-build

# Atrocious (dereferencing all symlinks) copy of ffmpeg libs.
%{__rm} -r $RPM_BUILD_ROOT%{py3_sitedir}/PySide6/Qt/lib

%py3_ocomp $RPM_BUILD_ROOT%{py3_sitedir}

install -d $RPM_BUILD_ROOT%{_examplesdir}/python3-PySide6-%{version}
cp -a examples/* $RPM_BUILD_ROOT%{_examplesdir}/python3-PySide6-%{version}
find $RPM_BUILD_ROOT%{_examplesdir}/python3-PySide6-%{version} -name '*.py' \
	| xargs sed -i '1s|^#!.*python\b|#!%{__python3}|'

%clean
rm -rf $RPM_BUILD_ROOT

%files -n python3-PySide6
%defattr(644,root,root,755)
%doc LICENSES README.md README.pyside6*.md
%{_bindir}/pyside6-*
%{_bindir}/shiboken6
%{_bindir}/shiboken6-genpyi
%dir %{py3_sitedir}/PySide6
%dir %{py3_sitedir}/PySide6/Qt
%{py3_sitedir}/PySide6/Qt/lib64
%dir %{py3_sitedir}/PySide6/Qt/libexec
%attr(755,root,root) %{py3_sitedir}/PySide6/Qt/libexec/*
%{py3_sitedir}/PySide6/Qt/modules
%{py3_sitedir}/PySide6/QtAsyncio
%doc %{py3_sitedir}/PySide6/doc
%dir %{py3_sitedir}/PySide6/scripts
%{py3_sitedir}/PySide6/scripts/__pycache__
%{py3_sitedir}/PySide6/scripts/*_lib
%{py3_sitedir}/PySide6/scripts/project
%{py3_sitedir}/PySide6/scripts/*.txt
%{py3_sitedir}/PySide6/scripts/__init__.py
%{py3_sitedir}/PySide6/scripts/android_deploy.py
%{py3_sitedir}/PySide6/scripts/deploy.py
%{py3_sitedir}/PySide6/scripts/metaobjectdump.py
%{py3_sitedir}/PySide6/scripts/project.py
%attr(755,root,root) %{py3_sitedir}/PySide6/scripts/pyside_tool.py
%{py3_sitedir}/PySide6/scripts/qml.py
%{py3_sitedir}/PySide6/scripts/qtpy2cpp.py
%{py3_sitedir}/PySide6/support
%dir %{py3_sitedir}/PySide6/typesystems
%{py3_sitedir}/PySide6/typesystems/*.xml
%{py3_sitedir}/PySide6/*.pyi
%attr(755,root,root) %{py3_sitedir}/PySide6/Qt*.abi3.so
%attr(755,root,root) %{py3_sitedir}/PySide6/libpyside6*.abi3.so.6.8
%{py3_sitedir}/PySide6/*.py
%{py3_sitedir}/PySide6/py.typed
%{py3_sitedir}/PySide6/__pycache__
%{py3_sitedir}/PySide6/assistant
%{py3_sitedir}/PySide6/balsam
%{py3_sitedir}/PySide6/balsamui
%{py3_sitedir}/PySide6/designer
%{py3_sitedir}/PySide6/linguist
%{py3_sitedir}/PySide6/lrelease
%{py3_sitedir}/PySide6/lupdate
%{py3_sitedir}/PySide6/qmlformat
%{py3_sitedir}/PySide6/qmllint
%{py3_sitedir}/PySide6/qmlls
%{py3_sitedir}/PySide6/qsb
%{py3_sitedir}/PySide6/svgtoqml
%{py3_sitedir}/PySide6-%{version}-py*.egg-info

#devel?
%{py3_sitedir}/PySide6/glue
%{py3_sitedir}/PySide6/include
%{py3_sitedir}/PySide6/typesystems/glue

%{_examplesdir}/python3-PySide6-%{version}

%files -n shiboken6
%defattr(644,root,root,755)
%doc LICENSES README.shiboken6.md
%dir %{py3_sitedir}/shiboken6
%{py3_sitedir}/shiboken6/__pycache__
%{py3_sitedir}/shiboken6/*.py
%{py3_sitedir}/shiboken6/*.pyi
%{py3_sitedir}/shiboken6/py.typed
%attr(755,root,root) %{py3_sitedir}/shiboken6/Shiboken.abi3.so
%attr(755,root,root) %{py3_sitedir}/shiboken6/libshiboken6.abi3.so.6.8
%{py3_sitedir}/shiboken6-%{version}-py*.egg-info

%files -n shiboken6-generator
%defattr(644,root,root,755)
%doc LICENSES README.shiboken6-generator.md
%dir %{py3_sitedir}/shiboken6_generator
%{py3_sitedir}/shiboken6_generator/__pycache__
%{py3_sitedir}/shiboken6_generator/*.py
%attr(755,root,root) %{py3_sitedir}/shiboken6_generator/shiboken6
%dir %{py3_sitedir}/shiboken6_generator/scripts
%{py3_sitedir}/shiboken6_generator/scripts/__pycache__
%attr(755,root,root) %{py3_sitedir}/shiboken6_generator/scripts/shiboken_tool.py
%{py3_sitedir}/shiboken6_generator-%{version}-py*.egg-info

#devel?
%{py3_sitedir}/shiboken6_generator/include

%if %{with doc}
%files apidocs
%defattr(644,root,root,755)
%doc docs/_build/html/*
%endif
