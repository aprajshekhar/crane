%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name: python-crane
Version: 2.0.0
Release: 13%{?dist}
Summary: docker-registry-like API with redirection, as a wsgi app

License: GPLv2
URL: https://github.com/pulp/crane
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

BuildRequires: python2-devel
BuildRequires: python-setuptools

Requires: python(x86-64) >= 2.6
Requires: python-flask >= 0.9
Requires: python-setuptools
Requires: python-rhsm
Requires(post): policycoreutils-python
Requires(postun): policycoreutils-python

%description
This wsgi application exposes a read-only API similar to docker-registry, which
docker can use for "docker pull" operations. Requests for actual image files
are responded to with 302 redirects to a URL formed with per-repository
settings.


%prep
%setup -q -n %{name}-%{version}


%build
%{__python2} setup.py build


%install
%{__python2} setup.py install --skip-build --root %{buildroot}

mkdir -p %{buildroot}/%{_usr}/share/crane/
mkdir -p %{buildroot}/%{_var}/lib/crane/metadata/

cp deployment/crane.wsgi %{buildroot}/%{_usr}/share/crane/

%if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
cp deployment/apache24.conf %{buildroot}/%{_usr}/share/crane/apache.conf
cp deployment/crane.wsgi %{buildroot}/%{_usr}/share/crane/
%else
cp deployment/apache22.conf %{buildroot}/%{_usr}/share/crane/apache.conf
cp deployment/crane_el6.wsgi %{buildroot}/%{_usr}/share/crane/crane.wsgi
%endif

rm -rf %{buildroot}%{python2_sitelib}/tests


%files
%defattr(-,root,root,-)
%{python2_sitelib}/crane
%{python2_sitelib}/crane*.egg-info
%{_usr}/share/crane/
%dir %{_var}/lib/crane/
%dir %{_var}/lib/crane/metadata/
%doc AUTHORS COPYRIGHT LICENSE README.rst
