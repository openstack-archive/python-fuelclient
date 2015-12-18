%if 0%{?rhel} && 0%{?rhel} <= 7
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%define name python-fuelclient
%{!?version: %define version 8.0.0}
%{!?release: %define release 1}

Summary:    Console utility for working with fuel rest api
Name:       %{name}
Version:    %{version}
Release:    %{release}
Source0:    %{name}-%{version}.tar.gz
License:    Apache
Group:      Development/Libraries
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix:     %{_prefix}

BuildArch:  noarch

BuildRequires: python-setuptools
BuildRequires: python-pbr >= 1.8.0

%if 0%{!?rhel:0} == 6
Requires: python-argparse
%endif

Conflicts: python-requests == 2.8.0

Requires: perl
Requires: python-cliff >= 1.14.0
Requires: python-pbr >= 1.6
Requires: python-keystoneclient >= 1.6.0
Requires: PyYAML >= 3.1.0
Requires: python-requests >= 2.5.2
Requires: python-six >= 1.9.0


Requires: bash-completion

%description
Summary: Console utility for working with fuel rest api

%prep
%setup -cq -n %{name}-%{version}

%build
cd %{_builddir}/%{name}-%{version} && %{__python2} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
cd %{_builddir}/%{name}-%{version} && %{__python2} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT

%post
# FIXME(mkwiek): fix fuelclient to generate usable autocomplete bash
fuel2 complete | perl -pe "s/-(?=.*=')/_/g" | perl -pe 's;(?<=cmds_\$\{)proposed;proposed//-/_;g' | sed -e "s/local cur prev words/local -a words/g" > %{_datadir}/bash-completion/completions/fuel2

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{python2_sitelib}/*
%{_bindir}/*
%doc fuelclient/fuel_client.yaml

%changelog
* Thu Nov 19 2015 Aleksandr Mogylchenko <amogylchenko@mirantis.com> 8.0.0-1
- make spec compatible with CentOS 7
